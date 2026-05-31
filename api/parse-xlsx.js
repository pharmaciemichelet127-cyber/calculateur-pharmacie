import { read, utils } from 'xlsx';

export const config = { api: { bodyParser: false } };

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    // Read raw body
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const buffer = Buffer.concat(chunks);

    const wb   = read(buffer, { type: 'buffer' });
    const ws   = wb.Sheets[wb.SheetNames[0]];
    const rows = utils.sheet_to_json(ws, { header: 1, defval: '' });

    // Find header row
    let headerRow = -1;
    for (let i = 0; i < Math.min(5, rows.length); i++) {
      if (rows[i].some(c => String(c).toLowerCase().includes('sensibilit'))) {
        headerRow = i; break;
      }
    }
    if (headerRow < 0) return res.status(400).json({ error: 'Colonne Sensibilite introuvable' });

    const headers = rows[headerRow].map(h => String(h).toLowerCase().trim());
    const iNom  = headers.findIndex(h => h.includes('nom') || h.includes('produit'));
    const iSens = headers.findIndex(h => h.includes('sensibilit'));
    const iEAN  = headers.findIndex(h => h === 'ean');
    const iCIP  = headers.findIndex(h => h === 'cip13');

    const produits = [];
    for (let j = headerRow + 1; j < rows.length; j++) {
      const row  = rows[j];
      const nom  = iNom  >= 0 ? String(row[iNom]  || '').trim() : '';
      const sens = iSens >= 0 ? String(row[iSens] || '').trim() : '';
      const ean  = iEAN  >= 0 ? String(row[iEAN]  || '').trim() : '';
      const cip  = iCIP  >= 0 ? String(row[iCIP]  || '').trim() : '';
      if (!nom && !ean) continue;
      produits.push({ libelle: nom, sensibilite: sens, ean: ean !== '-' ? ean : '', cip13: cip !== '-' ? cip : '' });
    }

    return res.status(200).json({ produits });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
