// api/login.js — v7.37
// Vérifie le mot de passe partagé (variable d'environnement Vercel APP_PASSWORD)
// et délivre un jeton de session "expiration.signatureHMAC" (SESSION_SECRET),
// valable 30 jours. Le jeton sera exigé par le proxy /api/github (v7.38).
import crypto from 'crypto';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const expected = process.env.APP_PASSWORD || '';
  const secret = process.env.SESSION_SECRET || '';
  if (!expected || !secret) {
    return res.status(500).json({ error: 'Serveur non configuré : définir APP_PASSWORD et SESSION_SECRET dans Vercel.' });
  }

  const pass = (req.body && req.body.password) || '';

  // Comparaison en temps constant (via hachage pour neutraliser les longueurs différentes)
  const a = crypto.createHash('sha256').update(String(pass)).digest();
  const b = crypto.createHash('sha256').update(expected).digest();
  if (!crypto.timingSafeEqual(a, b)) {
    return res.status(401).json({ error: 'Mot de passe incorrect' });
  }

  const exp = Date.now() + 30 * 24 * 3600 * 1000; // 30 jours
  const sig = crypto.createHmac('sha256', secret).update(String(exp)).digest('hex');
  return res.status(200).json({ token: exp + '.' + sig, exp: exp });
}
