export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Github-Token');
  res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS');
  if (req.method === 'OPTIONS') { res.status(200).end(); return; }

  const { path, t, ref } = req.query;
  const token = (req.headers['authorization'] || '').replace('token ', '').replace('Bearer ', '');
  
  const OWNER = 'pharmaciemichelet127-cyber';
  const REPO  = 'calculateur-pharmacie';
  
  let url = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${decodeURIComponent(path)}`;
  const params = [];
  if (ref) params.push(`ref=${ref}`);
  if (t)   params.push(`t=${t}`);
  if (params.length) url += '?' + params.join('&');

  const headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'calculateur-pharmacie'
  };
  if (token) headers['Authorization'] = `token ${token}`;

  const options = { method: req.method, headers };
  if (req.method === 'PUT') {
    options.body = JSON.stringify(req.body);
    options.headers['Content-Type'] = 'application/json';
  }

  const ghResp = await fetch(url, options);
  const data = await ghResp.json();
  res.status(ghResp.status).json(data);
}
