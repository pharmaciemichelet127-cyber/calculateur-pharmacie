// api/onedrive.js — v7.42
// Proxy Microsoft Graph (OneDrive) : le navigateur n'a plus aucun token
// Microsoft. Chaque requête exige la session app (X-Session). Le proxy
// obtient un access token en échangeant le refresh token chiffré stocké
// dans le repo (secrets/ms-refresh.enc) — rotation gérée : si Microsoft
// renvoie un nouveau refresh token, il est re-chiffré et re-stocké.
// Téléchargements : Graph répond 302 vers une URL directe — renvoyée au
// client (header X-Proxy-Redirect) qui la suit lui-même, aucune limite de
// taille côté Vercel. Uploads volumineux : gérés côté client par session
// d'upload Graph (voir intercepteur v7.42).
import crypto from 'crypto';
import zlib from 'zlib';

export const config = { api: { bodyParser: false } };

const OWNER = 'pharmaciemichelet127-cyber';
const REPO = 'calculateur-pharmacie';
const FICHIER_SECRET = 'secrets/ms-refresh.enc';
const MS_TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token';
const SCOPES = 'Files.ReadWrite offline_access User.Read';

let cacheAccess = null; // { token, exp } — cache par instance lambda

function jetonValide(tok, secret) {
  const parts = String(tok || '').split('.');
  if (parts.length !== 2 || !secret) return false;
  const exp = parseInt(parts[0], 10);
  if (isNaN(exp) || Date.now() > exp) return false;
  const attendu = crypto.createHmac('sha256', secret).update(parts[0]).digest('hex');
  const a = Buffer.from(parts[1]);
  const b = Buffer.from(attendu);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
function chiffrer(texte, cleHex) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(cleHex, 'hex'), iv);
  const data = Buffer.concat([cipher.update(texte, 'utf8'), cipher.final()]);
  return Buffer.concat([iv, cipher.getAuthTag(), data]).toString('base64');
}
function dechiffrer(b64, cleHex) {
  const brut = Buffer.from(b64, 'base64');
  const iv = brut.subarray(0, 12);
  const tag = brut.subarray(12, 28);
  const data = brut.subarray(28);
  const d = crypto.createDecipheriv('aes-256-gcm', Buffer.from(cleHex, 'hex'), iv);
  d.setAuthTag(tag);
  return Buffer.concat([d.update(data), d.final()]).toString('utf8');
}
async function lireCorpsBrut(req) {
  const morceaux = [];
  for await (const c of req) morceaux.push(c);
  return Buffer.concat(morceaux);
}

async function lireSecretGitHub(ghToken) {
  const url = 'https://api.github.com/repos/' + OWNER + '/' + REPO + '/contents/' + FICHIER_SECRET + '?t=' + Date.now();
  const r = await fetch(url, { headers: { 'Authorization': 'token ' + ghToken, 'Accept': 'application/vnd.github.raw', 'User-Agent': 'calculateur-pharmacie' } });
  if (!r.ok) return null;
  return (await r.text()).trim();
}
async function sauverSecretGitHub(contenu, ghToken) {
  const base = 'https://api.github.com/repos/' + OWNER + '/' + REPO + '/contents/' + FICHIER_SECRET;
  const headers = { 'Authorization': 'token ' + ghToken, 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'calculateur-pharmacie' };
  let sha = null;
  const g = await fetch(base + '?t=' + Date.now(), { headers });
  if (g.ok) { const j = await g.json(); sha = j.sha || null; }
  const body = { message: 'OneDrive refresh token (rotation)', content: Buffer.from(contenu, 'utf8').toString('base64'), branch: 'main' };
  if (sha) body.sha = sha;
  await fetch(base, { method: 'PUT', headers: Object.assign({ 'Content-Type': 'application/json' }, headers), body: JSON.stringify(body) });
}

async function obtenirAccessToken() {
  if (cacheAccess && Date.now() < cacheAccess.exp - 60000) return cacheAccess.token;
  const ghToken = process.env.GH_TOKEN || '';
  const encKey = process.env.MS_ENC_KEY || '';
  const chiffre = await lireSecretGitHub(ghToken);
  if (!chiffre) throw new Error('ONEDRIVE_NON_CONNECTE');
  let refresh;
  try { refresh = dechiffrer(chiffre, encKey); }
  catch (e) { throw new Error('Déchiffrement impossible — MS_ENC_KEY a-t-elle changé ? Relancez la connexion OneDrive.'); }
  const form = new URLSearchParams({
    client_id: process.env.MS_CLIENT_ID || '',
    client_secret: process.env.MS_CLIENT_SECRET || '',
    grant_type: 'refresh_token',
    refresh_token: refresh,
    scope: SCOPES
  });
  const t = await fetch(MS_TOKEN_URL, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: form.toString() });
  const tok = await t.json();
  if (!t.ok || !tok.access_token) {
    if (tok.error === 'invalid_grant') throw new Error('ONEDRIVE_NON_CONNECTE');
    throw new Error('Renouvellement Microsoft refusé : ' + (tok.error_description || tok.error || t.status));
  }
  cacheAccess = { token: tok.access_token, exp: Date.now() + (tok.expires_in || 3600) * 1000 };
  if (tok.refresh_token && tok.refresh_token !== refresh) {
    try { await sauverSecretGitHub(chiffrer(tok.refresh_token, process.env.MS_ENC_KEY), ghToken); } catch (e) { /* non bloquant */ }
  }
  return cacheAccess.token;
}

export default async function handler(req, res) {
  if (!jetonValide(req.headers['x-session'], process.env.SESSION_SECRET || '')) {
    return res.status(401).json({ error: { message: 'Session invalide ou expirée — rechargez la page et reconnectez-vous.' } });
  }
  const chemin = String(req.query.path || '');
  if (!chemin.startsWith('me/drive') || chemin.includes('..')) {
    return res.status(400).json({ error: { message: 'Chemin Graph non autorisé : ' + chemin } });
  }

  let access;
  try { access = await obtenirAccessToken(); }
  catch (e) {
    if (e.message === 'ONEDRIVE_NON_CONNECTE') {
      return res.status(428).json({ error: { code: 'onedrive_non_connecte', message: 'OneDrive n\u2019est pas encore connecté — cliquez sur le bouton de connexion OneDrive.' } });
    }
    return res.status(502).json({ error: { message: e.message } });
  }

  const url = 'https://graph.microsoft.com/v1.0/' + chemin;
  const headers = { 'Authorization': 'Bearer ' + access };
  if (req.headers['accept']) headers['Accept'] = req.headers['accept'];

  const options = { method: req.method, headers, redirect: 'manual' };
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    let corps = await lireCorpsBrut(req);
    if (corps.length) {
      if (req.headers['x-gzip'] === '1') {
        try { corps = zlib.gunzipSync(corps); } catch (e) { return res.status(400).json({ error: { message: 'Décompression gzip impossible' } }); }
      }
      options.body = corps;
      headers['Content-Type'] = req.headers['content-type'] || 'application/json';
    }
  }

  try {
    const g = await fetch(url, options);
    // Téléchargement : Graph répond 302 → on transmet l'URL directe au client
    if (g.status >= 300 && g.status < 400) {
      const loc = g.headers.get('location') || '';
      res.setHeader('X-Proxy-Redirect', '1');
      return res.status(200).json({ downloadUrl: loc });
    }
    const buf = Buffer.from(await g.arrayBuffer());
    res.status(g.status);
    res.setHeader('Content-Type', g.headers.get('content-type') || 'application/json');
    return res.send(buf);
  } catch (e) {
    return res.status(502).json({ error: { message: 'Erreur proxy OneDrive : ' + e.message } });
  }
}
