export default async function handler(req, res) {
  const { path, t, ref } = req.query;
  const token = req.headers['authorization']?.replace('token ', '') || 
                req.headers['x-github-token'];
  
  const OWNER = 'pharmaciemichelet127-cyber';
  const REPO  = 'calculateur-pharmacie';
  
  let url = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${path}`;
  if (ref) url += `?ref=${ref}`;
  if (t)   url += (ref ? '&' : '?') + `t=${t}`;

  const headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'calculateur-pharmacie'
  };
  if (token) headers['Authorization'] = `token ${token}`;

  const ghResp = await fetch(url, { method: req.method, headers,
    body: req.method === 'PUT' ? JSON.stringify(req.body) : undefined
  });
  
  const data = await ghResp.json();
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Github-Token');
  res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS');
  if (req.method === 'OPTIONS') { res.status(200).end(); return; }
  res.status(ghResp.status).json(data);
}
