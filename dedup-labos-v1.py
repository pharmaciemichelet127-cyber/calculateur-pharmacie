#!/usr/bin/env python3
# dedup-labos-v1.py — Supprime les doublons DUCRAY et PODOWELL de data-labos.json
# À exécuter DEPUIS la racine du repo calculateur-pharmacie, onglets app FERMÉS.
# Analyse du 13/07/2026 :
#   DUCRAY   : garder 1781873680535 (plus récent, tarifValidite) — supprimer 1780849801715
#   PODOWELL : garder 1781874846872 (catalogueOfficiel + 2051 clés catalogue) — supprimer 1781526783718
# Vérifié : aucune référence aux IDs supprimés dans condMarchesCommerciaux,
# cipMapData, condMapProduitMarche, ni en dur dans app-v744.js.
import json, os, sys

SUPPRIMER = {
    '1780849801715': ('DUCRAY',   '1781873680535'),
    '1781526783718': ('PODOWELL', '1781874846872'),
}

assert os.path.exists('data-labos.json'), "Lancer depuis la racine du repo (data-labos.json introuvable)"
d = json.load(open('data-labos.json'))
cl = d['condLabos']

# Garde-fous : les 4 entrées existent, les noms correspondent, le gardé reste
for a_suppr, (nom, a_garder) in SUPPRIMER.items():
    assert a_suppr in cl, f"{a_suppr} ({nom}) absent — déjà nettoyé ? Abandon."
    assert a_garder in cl, f"{a_garder} ({nom} à GARDER) absent ! Abandon."
    assert (cl[a_suppr].get('nom') or '').upper() == nom, f"Nom inattendu pour {a_suppr} : {cl[a_suppr].get('nom')!r}"
    assert (cl[a_garder].get('nom') or '').upper() == nom, f"Nom inattendu pour {a_garder} : {cl[a_garder].get('nom')!r}"

avant = len(cl)
for a_suppr, (nom, a_garder) in SUPPRIMER.items():
    del cl[a_suppr]
    print(f"✓ {nom} : {a_suppr} supprimé (gardé : {a_garder})")

# Sanity : aucun NaN, nombre attendu
texte = json.dumps(d, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
with open('data-labos.json', 'w', encoding='utf-8') as f:
    f.write(texte)
apres = len(json.load(open('data-labos.json'))['condLabos'])
print(f"✓ condLabos : {avant} → {apres} labos")
assert apres == avant - 2

# Fichiers produits orphelins
for a_suppr in SUPPRIMER:
    p = f'produits/{a_suppr}.json'
    if os.path.exists(p):
        os.remove(p)
        print(f"✓ {p} supprimé (catalogue identique à celui du labo gardé)")

print("\nTerminé. Vérifier puis : git add -A && git commit -m 'data: dédoublonnage DUCRAY + PODOWELL' && git push origin main")
