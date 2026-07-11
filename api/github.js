// api/github.js — v7.38 (remplace l'ancien proxy qui faisait transiter le token client)
// Proxy GitHub sécurisé : le token vit dans la variable d'environnement Vercel
// GH_TOKEN, jamais côté navigateur. Chaque requête exige un jeton de session
// valide (header X-Session, délivré par /api/login, signé avec SESSION_SECRET).
// Périmètre strict : uniquement le repo calculateur-pharmacie, uniquement les
// endpoints utilisés par l'app (contents, git/blobs, git/refs, git/commits, git/trees).
import crypto from 'crypto';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};

const OWNER = 'pharmaciemichelet127-cyber';
const REPO = 'calculateur-pharmacie';
const PREFIXES_AUTORISES = ['contents/', 'git/blobs', 'git/refs/heads/', 'git/commits', 'git/trees'];

function sessionValide(req) {
  const secret = process.env.SESSION_SECRET || '';
  if (!secret) return false;
  const tok = String(req.headers['x-session'] || '');
  const parts = tok.split('.');
  if (parts.length !== 2) return false;
  const exp = parseInt(parts[0], 10);
  if (isNaN(exp) || Date.now() > exp) return false;
  const attendu = crypto.createHmac('sha256', secret).update(parts[0]).digest('hex');
  const a = Buffer.from(parts[1]);
  const b = Buffer.from(attendu);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

export default async function handler(req, res) {
  if (!sessionValide(req)) {
    return res.status(401).json({ message: 'Session invalide ou expirée — rechargez la page et reconnectez-vous.' });
  }
  const ghToken = process.env.GH_TOKEN || '';
  if (!ghToken) {
    return res.status(500).json({ message: 'GH_TOKEN non configuré dans les variables d\u2019environnement Vercel.' });
  }

  const chemin = String(req.query.path || '');
  if (chemin.includes('..') || !PREFIXES_AUTORISES.some(function (p) { return chemin.startsWith(p); })) {
    return res.status(400).json({ message: 'Chemin non autorisé : ' + chemin });
  }

  let url = 'https://api.github.com/repos/' + OWNER + '/' + REPO + '/' + chemin;
  const qp = [];
  if (req.query.ref) qp.push('ref=' + encodeURIComponent(req.query.ref));
  if (req.query.t) qp.push('t=' + encodeURIComponent(req.query.t));
  if (qp.length) url += '?' + qp.join('&');

  const headers = {
    'Authorization': 'token ' + ghToken,
    'Accept': req.headers['accept'] || 'application/vnd.github.v3+json',
    'User-Agent': 'calculateur-pharmacie'
  };

  const options = { method: req.method, headers: headers };
  if (req.method !== 'GET' && req.method !== 'HEAD' && req.body) {
    options.body = (typeof req.body === 'string') ? req.body : JSON.stringify(req.body);
    headers['Content-Type'] = 'application/json';
  }

  try {
    const gh = await fetch(url, options);
    const texte = await gh.text();
    res.status(gh.status);
    res.setHeader('Content-Type', gh.headers.get('content-type') || 'application/json');
    return res.send(texte);
  } catch (e) {
    return res.status(502).json({ message: 'Erreur proxy GitHub : ' + e.message });
  }
}
