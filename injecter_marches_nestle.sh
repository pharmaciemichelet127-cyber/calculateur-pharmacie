#!/bin/bash
cd ~/calculateur-pharmacie || { echo "ERREUR : dossier calculateur-pharmacie introuvable"; exit 1; }

python3 << 'EOF'
import json, time

with open('data-labos.json', encoding='utf-8') as f:
    d = json.load(f)

cl = d.get('condLabos', {})
nestle_id = '1782563205795'
labo = cl.get(nestle_id)

if not labo:
    print(f"ERREUR : ID {nestle_id} introuvable")
    exit(1)

print(f"Labo : {labo.get('nom')} — {len(labo.get('produits',[]))} produits")

produits = labo.get('produits', [])

# Classer les EANs par groupe
eans_renutryl, eans_protibis, eans_autres = [], [], []
for p in produits:
    ean   = str(p.get('ean', '')).strip()
    if not ean: continue
    nom_p = (p.get('nom','') + ' ' + p.get('designation','')).upper()
    if 'RENUTRYL' in nom_p:
        eans_renutryl.append(ean)
    elif 'PROTIBIS' in nom_p:
        eans_protibis.append(ean)
    else:
        eans_autres.append(ean)

print(f"  RENUTRYL BOOSTER : {len(eans_renutryl)} EANs → 53%")
print(f"  PROTIBIS         : {len(eans_protibis)} EANs → 26.2%")
print(f"  Autres CLINUTREN : {len(eans_autres)} EANs → 48%")

# Structure correcte : marches_negocies (array)
# { label, marche_id, rem, paliers:[], palier_actif, eans }
nouveaux_marches = [
    {
        'label': 'RENUTRYL BOOSTER',
        'marche_id': 'renutryl_booster',
        'rem': 53.0,
        'paliers': [{'seuil': 0, 'rem': 53.0}],
        'palier_actif': None,
        'eans': eans_renutryl
    },
    {
        'label': 'PROTIBIS',
        'marche_id': 'protibis',
        'rem': 26.2,
        'paliers': [{'seuil': 0, 'rem': 26.2}],
        'palier_actif': None,
        'eans': eans_protibis
    },
    {
        'label': 'CLINUTREN (autres)',
        'marche_id': 'clinutren_autres',
        'rem': 48.0,
        'paliers': [{'seuil': 0, 'rem': 48.0}],
        'palier_actif': None,
        'eans': eans_autres
    }
]

# Remplacer les marches_negocies (on écrase pour repartir propre)
labo['marches_negocies'] = nouveaux_marches

# Mettre à jour remise + marche sur chaque produit
for p in produits:
    ean = str(p.get('ean','')).strip()
    if ean in eans_renutryl:
        p['rem_cat'] = 53.0;  p['marche'] = 'RENUTRYL BOOSTER'
    elif ean in eans_protibis:
        p['rem_cat'] = 26.2;  p['marche'] = 'PROTIBIS'
    elif ean in eans_autres:
        p['rem_cat'] = 48.0;  p['marche'] = 'CLINUTREN (autres)'

cl[nestle_id] = labo
d['condLabos'] = cl

with open('data-labos.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, separators=(',', ':'))

print("\n✓ marches_negocies injectés avec succès")
print("  RENUTRYL BOOSTER → 53%  |  PROTIBIS → 26.2%  |  Autres → 48%")
EOF

if [ $? -eq 0 ]; then
    git add data-labos.json
    git commit -m "Marchés NESTLE CLINUTREN dans marches_negocies : Renutryl 53%, Protibis 26.2%, Autres 48%"
    git push origin main && echo "✓ Poussé sur GitHub"
else
    echo "ERREUR — data-labos.json non modifié"
fi
