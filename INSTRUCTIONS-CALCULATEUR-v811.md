# CALCULATEUR PHARMACIE — Guide complet de l'application (état v8.11)

Pharmacie Michelet · 127 bd Michelet, 13009 Marseille · Maurice Sayag
App : **calculateur-pharmacie.vercel.app** · Repo : `pharmaciemichelet127-cyber/calculateur-pharmacie`
Dernière mise à jour : 17 juillet 2026 (v8.11)

---

## 1. PRINCIPES FONDAMENTAUX

- **GitHub = source de vérité unique.** Le navigateur n'est qu'un tampon.
  Fichiers indissociables : `index.html` + `app-vXXX.js` (version live : v8.11).
- **3 machines** (iMac pharmacie, MacBook Pro, MacBook Air) : localStorage
  indépendant par poste, jamais supposé synchronisé.
- **Les catalogues produits vivent EN MÉMOIRE** le temps de la session, MAIS
  le chargement est **AUTOMATIQUE et GARANTI à l'ouverture** (v7.99-v8.11) :
  proxy GitHub, puis repli public si le proxy échoue, puis nouvelle tentative
  automatique. Le bandeau (onglets Commande ET Conditions) est **honnête** :
  « ✓ 36 labos · 36 catalogues chargés à HH:MM » n'apparaît que si les données
  sont RÉELLEMENT en mémoire — sinon ⚠ explicite avec la conduite à tenir.
  Le bouton « ↑ Charger depuis GitHub » ne sert plus qu'à forcer un
  rechargement. Attendre le ✓ avant de générer une commande.
- **Le DERNIER stock LGPI importé est CONSERVÉ** (v7.99-v8.01) : l'import daté
  des Marchés équivalents (bouton 4) vit dans meq-data.json sur GitHub et
  s'applique automatiquement partout (Commande, rapport, Décision RDV) sur les
  3 machines, jusqu'au prochain import. Priorité : import de session (plus
  frais) > dernier stock LGPI daté > stock Ospharm.
- **Chargements automatiques au démarrage** : Ospharm (~2,5 s),
  Marchés équivalents / meq-data.json (~3 s).
- **Mot de passe partagé**, session 30 j par poste (jeton HMAC `app_session`).
  Aucun token dans le navigateur : tout passe par les proxys Vercel
  (`api/login`, `api/github`, `api/onedrive`, `api/claude`).
- **Le badge de version en bas à droite dit toujours la vérité.**
  S'il diffère de la version annoncée : Cmd+Shift+R.
- ⚠️ **Un onglet calculateur ouvert = des commits auto-save sur GitHub.**
  Fermer TOUS les onglets (toutes machines) avant tout `git push`.
- 📖 **RÈGLE DES BOUTONS ❓ WORKFLOW (obligatoire à chaque version)** :
  toute évolution fonctionnelle d'un onglet s'accompagne, DANS LA MÊME
  version, de la création ou mise à jour du/des bouton(s) ❓ Workflow de
  l'onglet — un bouton par fonctionnalité, plusieurs si le flux a beaucoup
  d'étapes (ex. onglet Commande : « ❓ Workflow » du simulateur + « ❓
  Workflow de validation » dans le bandeau 🛒 Ma commande). Le mode
  d'emploi vit dans l'application, pas dans la mémoire de l'utilisateur.

---

## 2. LES ONGLETS — VUE D'ENSEMBLE

| Onglet | Rôle |
|---|---|
| **Workflow / Guide** | Mode d'emploi général |
| **Conditions commerciales** | Conditions par labo (36 labos), catalogues produits, chargement/sauvegarde GitHub, documents OneDrive, opérations trade Notion |
| **⚡ Décision RDV** | Analyse labo sur ventes Ospharm (Qté N/N-1, CA, marges, stock), priorisation des RDV, guide ❓ |
| **Planning RDV** | Agenda des rendez-vous labos, statut OneDrive |
| **🎯 Marchés équivalents** | Regroupement des achats par sous-marchés, préconisations, plan 12 mois, budget annuel (voir §5) |
| **Catalogue** | Consultation des catalogues produits |
| **🛒 Commande** | Simulateur de commande + rapprochement avec le Moteur Sheets (voir §3 — le cœur des évolutions v7.81-v7.90) |
| **MAP Produits / Engagements / Précommande** | Référentiels et suivi des engagements labo |
| **Prix public** | Étiquetage, formules PV (ANATONIC ×1,6), prix manuels ✏️, simulation LPPR |

---

## 3. ONGLET 🛒 COMMANDE — LE FLUX COMPLET (v7.81 → v7.90)

### 3.1 Le simulateur

- **Labo (source produits)** : charge le catalogue du labo (préalable :
  « Charger depuis GitHub » dans Conditions).
- **Couverture cible** : 2 mois par défaut (rotation × mois = besoin).
- **Stock actuel** : « Déduire du besoin » recommandé.
- **Seuil rotation mini** : exclut les produits sous X u/mois.
- **Seuil colisage (%)** — *v7.81* : on ne commande un colis entier que si
  le manque atteint ce % du colisage (défaut 50 %). Besoin 0,2 / colisage 6
  → 0 au lieu de 6. Mettre 0 pour retrouver l'ancien comportement.
  Appliqué partout : lignes, paliers de références, cumuls par marché.

### 3.2 Les prix (TSRF COALIA) — *v7.82*

- Catalogue COALIA régénéré depuis le TSRF du 06/01/2026 (1 461 produits) :
  **vrai prix tarif HT** (`pu_catalogue`), **remise nette « rendue
  officine »** (`rem_cat`, ex. 38 %), **prix net rendu** (`prix_net_rendu`).
- Dans la commande : PA CAT = tarif · REM % = remise rendue · PA NET =
  tarif × (1 − remise) = net rendu. Étiquette « Remise TSRF x % ».
- Verrou anti-double remise : la remise TSRF ne s'applique JAMAIS si
  `pa_net` existe déjà (cas ARKOPHARMA : pa_net déjà net, rem_cat informatif).
- **L'import TSRF est corrigé** : les futurs réimports liront la colonne
  remise et n'écraseront plus le tarif par le prix net.

### 3.3 📋 Coller commande Moteur — *v7.83*

Bouton en haut de l'onglet. Dans le Sheet Moteur : sélectionner le tableau
du labo **avec sa ligne de titres** (EAN · Libellé · Labo · Qté à commander ·
Colisage · Segment · Stock RT · …) → Cmd+C → coller → **Charger**.
Le parseur est tolérant (colonnes en trop, lignes vides, en-têtes déplacés).
La bannière « ⚡ N produits chargés — commande Moteur / Analyse Zone »
apparaît. (L'URL `?az=BASE64` de l'export Apps Script fonctionne toujours.)

### 3.4 Le rapport Moteur vs Calculateur

Bouton **« 📊 Générer le rapport Moteur vs Calculateur »**. Croisement par
EAN de deux logiques indépendantes :

- **Qté Moteur** : besoin logistique du Sheet (PLS − stock, segments).
- **Qté Calc** : rotation × couverture, seuil colisage, prix nets.
- **Qté finale = max(Moteur, Calculateur)** — la règle de l'écosystème.

**Colonnes** : ☑ · EAN · Libellé · Segment · DN% · Alerte · **Stock** ·
Qté Moteur · Qté Calc · Écart · **Besoin réel** · **Colis.** · Qté finale ·
**Couv.** · **CA cde €** · Statut. En-tête **figé** au défilement (v7.93),
tableau dans sa propre zone (72 % de l'écran).

- **Stock** (*v7.89/v7.97*) : Stock RT de la source, MAIS le stock LGPI
  (import MEQ daté) PRIME sur les lignes à EAN remplacé ↻ et sert de
  repli ; 0 en rouge.
- **Besoin réel** (*v7.91*) : besoin NON arrondi au colisage =
  max(Besoin Théo source, rotation × couverture − stock). C'est le chiffre
  à comparer aux conditions d'un autre fournisseur (achat à l'unité).
  Sur une ligne ↻, le besoin de la source (périmé) est écarté (v7.97).
- **Colis.** (*v7.94*) : colisage COALIA/TSRF (« ×6 »), entre Besoin réel
  et Qté finale — on lit « besoin 2 → ×20 → obligé de prendre 20 ».
- **Couv.** (*v7.91/v7.92*) : mois de stock si on commande la qté finale =
  (stock + qté) ÷ rotation. Rotation : catalogue → ligne calc → **cache
  Ospharm par EAN** (max par EAN, jamais la somme — un même EAN figure
  sous son fabricant ET sous COALIA). **Plafond cash ≈ 2,5 mois** : toute
  couverture au-delà = ligne à réduire, décocher ou acheter ailleurs.

**Les 4 statuts et quoi en faire :**

| Statut | Signification | Action |
|---|---|---|
| 🟠 Moteur seul | Pas de rotation côté calculateur | Commander tel quel |
| ✅ OK | Les deux logiques convergent | Commander tel quel |
| 📉 Moteur > Calc | Urgence stock détectée par le Moteur | Prendre la qté Moteur |
| 🔵 Calc seul | Non demandé par le Moteur | **À arbitrer** : saisonnalité + stock + règle du cash |

### 3.4bis Rapport universel & libellés dynamiques — *v7.95-v7.96*

- Bouton **« 📊 Rapport de commande »** (à côté de Calculer) : le masque
  complet fonctionne pour TOUS les labos, même sans collage — statut
  🧮 Calc, tout pré-coché, titre « Rapport de commande — Calculateur ».
- **Libellés dynamiques selon la source** : import URL Analyse Zone →
  « Qté Analyse Zone », « 🟠 Analyse Zone seul »… ; collage → « Moteur ».
  Titre, bannière, badges, cartes, légende et impression suivent.

### 3.4ter Remplacements d'EAN (Cycle de vie) — *v7.96-v7.97*

Quand une référence change d'EAN (ex. BD MICRO-FINE 4mm :
3401321104311 → 0383017056230) :
1. Onglet **Cycle de vie** → labo → « + Ajouter une correspondance » :
   ancien EAN → nouvel EAN (⚠️ le code de la FICHE LGPI fait foi —
   vérifier sur la fiche, un chiffre d'écart = 76 boîtes invisibles) →
   **Sauvegarder**.
2. Statut « Confirmé » + « ⚡ Appliquer les confirmés au catalogue »
   (produits chargés au préalable) = bascule définitive du catalogue.
3. Le rapport fait le reste : fusion ancien+nouveau en UNE ligne
   (marqueur **↻**), rotations Ospharm de l'ancien héritées, stock LGPI
   prioritaire, besoin réel recalculé sur le vrai stock.
   Message « 0 appliqué / introuvables » après coup = normal (déjà appliqué).

### 3.5 Segmentation SOCLE / CŒUR / COMPLÉMENT — *v7.87-v7.88*

- Segments du **Moteur** (via le collage) affichés tels quels.
- Lignes sans segment (Calc seul) : segment **calculé** automatiquement,
  marqué d'une **étoile** (ex. `SOCLE*`).
- Règle = celle du Moteur : contribution au **CA annuel cumulé** (ventes
  Ospharm, tous labos, périmètre = produits du labo) :
  **SOCLE ≤ 80 % · CŒUR 80-95 % · COMPLÉMENT au-delà ou jamais vendu.**
  Fiabilité vérifiée : 41/44 concordances sur commande réelle (écarts =
  produits en frontière, bases de CA légèrement différentes).

### 3.6 Filtres, sélection, sortie — *v7.84, v7.86, v7.90*

- **Badges de statut = filtres cliquables** (re-clic ou « Tous » = retirer).
- **Badges de segment = filtres cliquables** (*v7.90*), **cumulables** avec
  le statut : « 🔵 Calc seul + SOCLE » = la short-list d'arbitrage.
  « Tous » réinitialise les deux filtres.
- **Cases à cocher** par ligne. Pré-cochage : tout SAUF 🔵 Calc seul.
  Lignes décochées grisées. La sélection survit aux changements de filtre.
- **☑/☐ Tout cocher / décocher (lignes affichées)** : respecte les filtres
  actifs (ex. « COMPLÉMENT → Tout décocher » en deux clics).
- **Bandeau 🛒 Ma commande** : produits · unités · € HT cochés, en direct.
- **📋 Copier la sélection** : EAN · Libellé · Qté · CA → presse-papier
  (Sheets, LGPI, mail).
- **🖨 Imprimer la commande** : bon de commande des lignes cochées, trié
  SOCLE → CŒUR → COMPLÉMENT puis CA décroissant, avec PU net, totaux,
  en-tête Pharmacie Michelet. (Autoriser les popups si rien ne s'ouvre.)
- **❓ Workflow de validation** (*v7.98*, dans le bandeau 🛒) — la routine
  en 2 passes de 30 s : Passe 1 sur les cochés (balayer Couv., se méfier
  au-delà de 2,5-3 mois : rupture fantôme ↻, saisonnalité, colisage
  disproportionné) · Passe 2 sur les décochés (filtre 🔵 Calc seul +
  segment, cocher ce qui se vend avant 45 j fin de mois) · Finaliser
  (« Tous » → bandeau 🛒 → Copier ou Imprimer).
- **📋 Copier la sélection** exporte EAN · Libellé · **Qté (colisage)** ·
  **Besoin réel** · CA — le besoin réel se colle directement dans une
  demande de prix à un autre fournisseur.

### 3.6bis Ajustement des quantités & règle du cash — *v8.03-v8.10*

- **Qté finale ÉDITABLE** sur chaque ligne du rapport : la couverture, le CA
  de ligne et le bandeau 🛒 se recalculent **pendant la frappe** (v8.10, sans
  Entrée) ; la validation rafraîchit totaux et badges. Copie et impressions
  suivent les quantités ajustées.
- **⚡ Couv. > 3 mois → 1 colis** (v8.03-v8.07) : sur TOUTES les lignes
  (cochées ou non), ramène au colisage minimum celles dont la couverture
  dépasse 3 mois. Retour détaillé : « ✓ N ramenées à 1 colis · ⚠ M déjà au
  minimum (colisage structurellement trop gros → garder 1 colis, décocher, ou
  acheter à l'unité ailleurs) ».
- **Colonne Couv. colorée** (v8.04) : ROUGE > 3 mois · ambre 2,5-3 · normal
  en dessous — la passe 1 de validation = balayer les rouges.
- **🖨 Non retenus (besoin réel)** (v8.08-v8.09) : imprime les lignes
  DÉCOCHÉES dont le stock couvre MOINS de 3 mois — ruptures (stock 0 🔴) en
  tête — avec besoin réel non arrondi, colisage refusé et PU net de référence :
  la liste à négocier chez un autre fournisseur, sans colisage imposé.
- **Confirmation du collage Moteur** (v8.06) : « ✓ Collage réussi : N produits
  · U unités — LABO » + défilement automatique vers la bannière.

### 3.7 Le workflow en 6 étapes (bouton ❓ de l'onglet)

1. **Charger les prix** : Conditions → ↑ Charger depuis GitHub (chaque session).
2. **Régler** : labo · stock « Déduire » · couverture 2 mois · seuil colisage 50 %.
3. **Coller la commande Moteur** (recommandé).
4. **Générer** le rapport. Qté finale = max des deux ; tout pré-coché sauf Calc seul.
5. **Filtrer et arbitrer** : commencer par 🔵 Calc seul (+ filtre segment) ;
   ne garder que ce qui se vend avant l'échéance 45 j fin de mois.
6. **Finaliser** : bandeau 🛒 → Copier la sélection ou Imprimer.

---

## 4. ⚡ DÉCISION RDV & DONNÉES OSPHARM

- **Import Ospharm** (export « Toutes les ventes », 12 mois glissants) :
  analyse par labo — Qté N/N-1, évolution, CA, marges (seuil de marge
  paramétrable v7.78), stock, période affichée 📅.
- **☁ Charger Ospharm depuis GitHub** : recharge le cache partagé.
- **☁ Sauvegarder sur GitHub** — *v7.81* : pérennise l'import courant dans
  `ospharm-cache.json` (format v2 compact) pour les 3 machines.
  **À cliquer après chaque import mensuel.**
- Stock LGPI dédié importable, daté, prioritaire sur le stock Ospharm.
- COOPER dispatché automatiquement SANTÉ / SOINS.
- Ces mêmes données Ospharm alimentent la **segmentation ABC** de l'onglet
  Commande et les rotations de secours.

---

## 5. 🎯 MARCHÉS ÉQUIVALENTS (résumé — détail dans WORKFLOW-MEQ)

- Toutes les données vivent dans `meq-data.json` : **sauvegarde auto**
  (~1,5 s après chaque import/clic, badge ☁️) et **rechargement auto** au
  démarrage. Aucun réimport de routine.
- 6 imports : MAP maître (⚠️ remplacement INTÉGRAL — toujours le fichier
  complet), Ventes N (mensuel), Ventes N-1, Stock daté, Saisonnalité
  (fusion mensuelle), TOP zone Ospharm.
- 5 vues : 🗂 Par sous-marché (bouton RETENIR), 🏭 Par labo,
  💡 Préconisation (leaders + colonne Zone), 🗺 Zone (trous d'assortiment),
  📆 Plan 12 mois (scénarios A/B, volume annuel par produit, 💶 budget HT
  au PA unitaire — l'argumentaire chiffré du RDV).
- Règle TVA 2,1 % avec exceptions (TADALAFIL…) ; bandeau de rappels
  (ventes mensuelles, saisonnalité).

---

## 6. RÈGLES MÉTIER CLÉS

- **Règle du cash** : les encaissements doivent couvrir la facture avant
  l'échéance **45 j fin de mois** — critère central de tout arbitrage.
- **Qté finale = max(Qté Moteur/AZ, Qté Calculateur)**, arrondie au colisage.
- **Segmentation** : SOCLE ≤ 80 % du CA cumulé · CŒUR 80-95 % · COMPLÉMENT 5 % restants.
- **DN zone** : SOCLE ≥ 20 % · CŒUR ≥ 30 % · COMPLÉMENT ≥ 50 %.
- **ANATONIC** : PV TTC = tarif × 1,6 arrondi € supérieur (PAS de TVA en plus).
- **pv_ttc_manuel (✏️)** prioritaire sur toute formule ; un réimport de
  catalogue l'écrase — signaler avant réimport.
- **KENVUE** : DIGESTIF 30 % · SEVRAGE 14,6 % · HEXTRIL 24 % · LISTERINE 30 % · BIAFINE 26 %.
- **PODOWELL** : Chut-Chup 42,4 %. **COALIA** : remises TSRF par produit (~38-47 %).

---

## 7. FICHIERS DE DONNÉES (repo GitHub)

| Fichier | Contenu |
|---|---|
| `data-labos.json` | Conditions commerciales des 36 labos (~2,8 Mo) |
| `produits/LABOID.json` | Catalogues par labo. COALIA = `1780852343540` (tarif + remise + net rendu TSRF) |
| `ospharm-cache.json` | Ventes Ospharm partagées, format v2 compact |
| `meq-data.json` | Toutes les données Marchés équivalents |
| `trade-ops.json` | Opérations trade Notion (GitHub Action / 2 h) |
| `secrets/ms-refresh.enc` | Token OneDrive chiffré (preuve de connexion réelle) |

---

## 8. DÉPLOIEMENT D'UNE NOUVELLE VERSION — `./deploy.sh`

**Méthode officielle depuis la v8.10** : le script `deploy.sh` à la racine du
repo fait tout (mise en place : le copier à la racine, `chmod +x deploy.sh`,
le committer une fois — commit infra, sans bump).

```
# 0. FERMER TOUS LES ONGLETS CALCULATEUR (toutes machines)
# 1. Télécharger app-vXXX.js dans ~/Downloads (indexXXX.html INUTILE)
cd ~/Downloads/calculateur-pharmacie
./deploy.sh 811 "description du commit"
```

Le script : vérifie le fichier dans Downloads (et signale les doublons
« (1).js »), fetch + reset, copie le JS, **bascule index.html par sed** (plus
jamais dépendant du fichier index téléchargé — c'était la cause des trois
blocages « je suis bloqué à la vXX »), commit, push avec **3 tentatives** si
un auto-save le rejette, et vérifie qu'origin référence bien la nouvelle
version. Puis : rouvrir → Cmd+Shift+R → badge.

Méthode manuelle de secours : l'ancienne séquence git reste valable ; en cas
de « nothing to commit » avec origin en retard, la bascule se fait par
`sed -i '' 's/app-vAAA\.js/app-vBBB.js/' index.html`. Numéros sautés jamais
réutilisés (v7.29, v7.33, v7.84-85, v7.87, v8.02-03 selon déploiements).

---

## 9. HISTORIQUE v7.81 → v7.90 (session du 15-16/07/2026)

| Version | Apport |
|---|---|
| v7.81 | Bouton ☁ Sauvegarder Ospharm · seuil colisage · PA de repli net rendu |
| v7.82 | Remise TSRF affichée · import TSRF corrigé · catalogue COALIA régénéré |
| v7.83 | 📋 Coller commande Moteur · ❓ Workflow Commande · rapport : segments, CA, wording Moteur |
| v7.86 | Filtres par statut · cases à cocher · 🛒 Ma commande · 📋 Copier · 🖨 Imprimer (v7.84-85 sautées) |
| v7.88 | Segmentation ABC automatique, règle Moteur 80/95, suffixe * (v7.87 sautée) |
| v7.89 | Colonne Stock dans le rapport |
| v7.90 | Filtre par segment, cumulable avec le filtre statut |
| v7.91 | Besoin réel non arrondi + couverture en mois au colisage |
| v7.92 | Rotation de secours depuis le cache Ospharm (max par EAN) |
| v7.93 | En-tête du rapport figé au défilement |
| v7.94 | Colonne Colis. (colisage COALIA/TSRF) |
| v7.95 | 📊 Rapport de commande universel (tous labos, statut 🧮 Calc) |
| v7.96 | Remplacements EAN Cycle de vie dans le rapport (↻) + libellés dynamiques Moteur/Analyse Zone |
| v7.97 | Stock LGPI prioritaire sur lignes ↻, besoin réel recalculé |
| v7.98 | ❓ Workflow de validation dans le bandeau 🛒 Ma commande |
| v7.99 | Auto-chargement GitHub visible et garanti + stock LGPI persistant (calculs) |
| v8.00 | Stock persistant affiché dans le simulateur |
| v8.01 | Stock persistant appliqué à Décision RDV + bandeau d'état |
| v8.04 | Retour détaillé du bouton ⚡ 1 colis + colonne Couv. colorée (v8.02-03 : colisage impression/copie, qté éditable) |
| v8.05 | Statut du chargement auto visible dans Conditions |
| v8.06 | Confirmation du collage Moteur + défilement vers la bannière |
| v8.07 | La règle ⚡ 1 colis traite toutes les lignes, cochées ou non |
| v8.08 | 🖨 Non retenus (besoin réel) — liste à passer hors plateforme |
| v8.09 | Non retenus filtrés : couverture stock < 3 mois, ruptures 🔴 en tête |
| v8.10 | Couverture recalculée EN DIRECT pendant la frappe + deploy.sh |
| v8.11 | Chargement auto GARANTI : repli public réel, vérification réelle du résultat, retry automatique, bandeau honnête |

À suivre : EAN 3578835504842 (ARKOFLUIDE ULT DRAINEUR) absent du TSRF du
06/01 — à ajouter au prochain tarif COALIA ; vérifier sur facture que le
prix payé = net rendu ; BD MICRO-FINE 4mm : 76 en stock sous
0383017056230, ne PAS recommander (rupture fantôme évitée le 16/07) ;
26 références COALIA au colisage structurellement trop gros (couv > 3 mois
même à 1 colis) — liste imprimable via 🖨 Non retenus, argumentaire de
négociation (colisages réduits ou achat à l'unité ailleurs).
