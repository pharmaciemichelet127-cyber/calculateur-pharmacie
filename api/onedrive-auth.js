// api/onedrive-auth.js — v7.42
// Connexion OneDrive UNIQUE (compte Microsoft personnel /consumers).
// 1er passage (?session=...) : vérifie la session app puis redirige vers la
//   page de connexion Microsoft (flux authorization code + offline_access).
// Retour (?code=...&state=...) : échange le code contre un refresh token,
//   le chiffre (AES-256-GCM, clé MS_ENC_KEY) et le stocke dans le repo GitHub
//   (secrets/ms-refresh.enc) via GH_TOKEN. Ensuite /api/onedrive renouvelle
//   les accès silencieusement — plus jamais d'identifiant à saisir.
import crypto from 'crypto';

const OWNER = 'pharmaciemichelet127-cyber';
const REPO = 'calculateur-pharmacie';
const FICHIER_SECRET = 'secrets/ms-refresh.enc';
const APP_URL = 'https://calculateur-pharmacie.vercel.app';
const REDIRECT_URI = APP_URL + '/api/onedrive-auth';
const MS_TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token';
const MS_AUTH_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize';
const SCOPES = 'Files.ReadWrite offline_access User.Read';

function hmac(valeur, secret) {
  return crypto.createHmac('sha256', secret).update(String(valeur)).digest('hex');
}
function jetonValide(tok, secret) {
  const parts = String(tok || '').split('.');
  if (parts.length !== 2 || !secret) return false;
  const exp = parseInt(parts[0], 10);
  if (isNaN(exp) || Date.now() > exp) return false;
  const a = Buffer.from(parts[1]);
  const b = Buffer.from(hmac(parts[0], secret));
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
function chiffrer(texte, cleHex) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(cleHex, 'hex'), iv);
  const data = Buffer.concat([cipher.update(texte, 'utf8'), cipher.final()]);
  return Buffer.concat([iv, cipher.getAuthTag(), data]).toString('base64');
}

async function sauverSurGitHub(contenuB64Chiffre, ghToken) {
  const url = 'https://api.github.com/repos/' + OWNER + '/' + REPO + '/contents/' + FICHIER_SECRET;
  const headers = { 'Authorization': 'token ' + ghToken, 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'calculateur-pharmacie' };
  let sha = null;
  const g = await fetch(url + '?t=' + Date.now(), { headers });
  if (g.ok) { const j = await g.json(); sha = j.sha || null; }
  const body = { message: 'OneDrive refresh token (chiffré)', content: Buffer.from(contenuB64Chiffre, 'utf8').toString('base64'), branch: 'main' };
  if (sha) body.sha = sha;
  const p = await fetch(url, { method: 'PUT', headers: Object.assign({ 'Content-Type': 'application/json' }, headers), body: JSON.stringify(body) });
  if (!p.ok) { const e = await p.json().catch(function () { return {}; }); throw new Error('Stockage GitHub : ' + (e.message || p.status)); }
}

export default async function handler(req, res) {
  const secret = process.env.SESSION_SECRET || '';
  const clientId = process.env.MS_CLIENT_ID || '';
  const clientSecret = process.env.MS_CLIENT_SECRET || '';
  const encKey = process.env.MS_ENC_KEY || '';
  const ghToken = process.env.GH_TOKEN || '';
  if (!secret || !clientId || !clientSecret || !encKey || !ghToken) {
    return res.status(500).send('Configuration incomplète : vérifier SESSION_SECRET, MS_CLIENT_ID, MS_CLIENT_SECRET, MS_ENC_KEY, GH_TOKEN dans Vercel.');
  }

  // ── Retour de Microsoft avec le code d'autorisation ──
  if (req.query.code) {
    if (!jetonValide(req.query.state, secret)) {
      return res.status(403).send('État de sécurité invalide ou expiré — relancez la connexion depuis le calculateur.');
    }
    try {
      const form = new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        grant_type: 'authorization_code',
        code: String(req.query.code),
        redirect_uri: REDIRECT_URI,
        scope: SCOPES
      });
      const t = await fetch(MS_TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString()
      });
      const tok = await t.json();
      if (!t.ok || !tok.refresh_token) {
        return res.status(502).send('Échange du code refusé par Microsoft : ' + (tok.error_description || tok.error || t.status));
      }
      await sauverSurGitHub(chiffrer(tok.refresh_token, encKey), ghToken);
      res.setHeader('Location', APP_URL + '/?onedrive=ok');
      return res.status(302).end();
    } catch (e) {
      return res.status(500).send('Erreur pendant la connexion OneDrive : ' + e.message);
    }
  }

  // ── Erreur renvoyée par Microsoft (refus utilisateur, etc.) ──
  if (req.query.error) {
    return res.status(400).send('Microsoft a renvoyé une erreur : ' + (req.query.error_description || req.query.error));
  }

  // ── Premier passage : lancer la connexion (session app exigée) ──
  if (!jetonValide(req.query.session, secret)) {
    return res.status(401).send('Session du calculateur invalide — ouvrez cette page depuis le bouton de connexion OneDrive de l\u2019application.');
  }
  const etatExp = Date.now() + 10 * 60 * 1000; // état anti-falsification, 10 min
  const state = etatExp + '.' + hmac(etatExp, secret);
  const url = MS_AUTH_URL
    + '?client_id=' + encodeURIComponent(clientId)
    + '&response_type=code'
    + '&redirect_uri=' + encodeURIComponent(REDIRECT_URI)
    + '&response_mode=query'
    + '&scope=' + encodeURIComponent(SCOPES)
    + '&prompt=select_account'
    + '&state=' + encodeURIComponent(state);
  res.setHeader('Location', url);
  return res.status(302).end();
}
