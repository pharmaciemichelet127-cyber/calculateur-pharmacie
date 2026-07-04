#!/usr/bin/env python3
"""
Injection BAUSCH LOMB dans data-labos.json
- 117 produits depuis l'état des ventes labo (rotations + PA Cat + PA Net réels)
- 4 marchés 5/5 Cinq sur Cinq (paliers 80/170/350/500 unités)
- Remise de base 18%, franco 250€

À exécuter DEPUIS le dossier du repo :
  cd ~/Downloads/calculateur-pharmacie
  python3 inject_bausch_v567.py
"""

import json, sys

LABO_ID = "1782335509157"
SOURCE = "data-labos.json"

# ── 117 produits extraits de l'état des ventes BAUSCH au 20/06/2026 ───────────
# (ean, nom, pa_cat, pa_net, rem_cat, moy, colisage_defaut, [mois jan..dec])
PRODUITS_VENTES = [
    ("3400930145944","ALLERGIFLASH 0,05% COL FLACON 5ML",8.63,5.437,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400934691638","ALLERGIFLASH 0,05% COLLY DOS 10",8.63,4.747,45.0,2.08,1,[2,2,0,5,3,1,3,1,3,2,1,3]),
    ("3614790000613","AQUALARM INTENSIVE SPR 10ML",14.08,14.08,0.0,0.0,1,[0,0,0,0,0,3,0,0,0,0,0,0]),
    ("3401060060701","AQUALARM INTENSIVE SPRAY",13.8,8.418,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000606","AQUALARM INTENSIVE UD 0,5ML X30",9.95,9.95,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000088","AQUALARM TRIPLE ACTION J/N 10ML",13.35,13.35,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001030","AQUALARM UD YEUX SEC UNIDOSE 30",8.4,8.4,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000583","AQUALARM UP 2% S opht lubrif humidif Fl/10ml",7.6,7.6,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000590","AQUALARM UP INTEN SOL OPHT10ML",9.95,9.95,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("7391899856148","BIOTRUE MPS SOL LENTIL FLIGHT 100 ML",7.95,7.95,0.0,0.25,1,[0,1,2,0,1,0,0,0,0,0,0,0]),
    ("7391899845883","BIOTRUE SOL FLIGHT PACK 60MLX2",7.6,7.6,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("7391899850719","BIOTRUE SOL NETTOY LENTIL 300 ML",13.2,9.9,25.0,0.67,1,[0,0,1,0,1,1,0,2,1,0,1,2]),
    ("3614790000347","BLOXALLERGI FLACON 10ML",9.6,9.6,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000767","BLOXALLERGI SPRAY 10 ML",13.6,13.6,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000057","BLOXANG EPONG HEMOS STER BT 5",8.0,4.4,45.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000859","BLOXANG EPONGE HEMOS. BATON 4",8.2,4.51,45.0,0.42,1,[0,1,0,0,0,1,2,0,0,1,0,0]),
    ("3401051621676","BLOXANG TOPIC POM HEMOS 30 G",7.6,4.788,37.0,0.5,1,[0,1,1,0,0,1,1,0,0,1,0,0]),
    ("4049649000619","BLOXAPHTE GEL JUN EMB CANU10ML",7.7,4.697,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000002","BLOXAPHTE Gel Ad T/15ml",9.4,5.922,37.0,0.25,1,[0,0,0,0,0,0,0,0,0,0,1,2]),
    ("3614790000019","BLOXAPHTE Gel junior T/15ml",9.4,9.4,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000040","BLOXGEL BB 15 ML",9.1,5.733,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("4049649000749","BLOXOTO SOL AURIC FL 15 ML",6.4,3.904,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("4049649000732","BLOXRHUME SOL NASAL SPRAY 20ML",8.55,8.55,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401528548581","C'ZEN NUIT CP 30",10.5,6.405,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000729","CERUALGIE GOUTTE AURICULAIRE 7G",6.85,6.85,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000705","CERUCALM SOL AUR 15ML",7.35,4.631,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000743","CERUDROP+ SOL AUR 12ML",7.3,4.599,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400930200490","CERULYSE 10 ML",7.83,5.873,25.0,2.92,1,[4,3,3,1,7,1,1,1,1,4,2,8]),
    ("4030571008545","CERUSPRAY FL 50 ML",7.5,4.125,45.0,0.92,1,[0,0,1,1,3,1,0,0,4,1,0,0]),
    ("3614790000194","CINQ /CINQ DECOL LENTE 60ML+PEIGNE",13.0,13.0,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560216387","CINQ SUR CINQ Diff élect dble us moust",7.25,7.25,0.0,0.17,1,[0,0,0,0,0,0,0,0,0,0,0,1]),
    ("3401560750744","CINQ SUR CINQ FAMILLE 100ML",11.5,7.245,37.0,0.0,24,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401571198795","CINQ SUR CINQ LOT TROPIC 75ML",10.15,6.395,37.0,0.83,12,[0,0,0,0,0,0,0,0,0,0,2,2]),
    ("3401560216394","CINQ SUR CINQ Liq rech diffuseur Fl 35 ML",6.21,6.21,0.0,0.33,1,[0,0,0,0,0,0,0,0,0,0,2,2]),
    ("3401528548413","CINQ SUR CINQ MOUSSE SS RINCAGE 150 ML",15.35,9.364,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401563131779","CINQ SUR CINQ NATURA CR T 40G",7.9,4.74,40.0,0.0,12,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401581493163","CINQ SUR CINQ SHAMP GEL 100 ML",14.9,8.94,40.0,0.25,1,[0,0,0,0,0,0,0,0,0,2,1,0]),
    ("3614790001078","CINQ SUR CINQ Sol vêtem tiss Spray/100ml",9.7,5.82,40.0,0.0,6,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560221459","CINQ SUR CINQ Spray aéros tissus Fl/150ml",6.5,3.9,40.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401528503696","CINQ SUR CINQ Stick famille Bille/20ml",10.15,10.15,0.0,0.0,12,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560206708","CINQ SUR CINQ Stick tropic Bille/20ml",10.15,6.09,40.0,0.0,24,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560216370","CINQ SUR CINQ Tabl rech diffuseur B/30",6.21,6.21,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401597812231","CINQ SUR CINQ ZONES TEMPEREES Lot moust 100ml",11.5,7.245,37.0,0.0,24,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001221","CINQ/CINQ A/MOUST LOTION BB 100ML",11.5,7.245,37.0,0.33,12,[0,0,0,0,0,0,0,0,1,0,2,1]),
    ("3614790001344","CINQ/CINQ A/POUX SPR FLASH 150 ML",22.0,22.0,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000064","CINQ/CINQ A/TIQUE SPR 100 ML",11.5,7.245,37.0,0.33,1,[0,0,0,0,0,1,0,0,0,0,1,3]),
    ("3614790000422","CINQ/CINQ ENVIRON A/POUX/LENTE250",6.95,6.95,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001351","CINQ/CINQ FAMILLE SPRAY 100 ML X2",20.73,20.73,0.0,0.08,12,[0,0,0,0,0,0,0,0,0,0,0,1]),
    ("3614790000200","CINQ/CINQ KIT SPECIAL TIQUE",8.2,5.166,37.0,0.08,1,[0,0,1,0,0,0,0,0,0,0,0,0]),
    ("3401581492913","CINQ/CINQ LOT A/POUX+LENT 100ML",18.0,18.0,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560118148","CINQ/CINQ NATURA Bracelet techslap camoufl",10.5,6.3,40.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560118155","CINQ/CINQ NATURA Bracelet techslap motif",10.5,6.3,40.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401563131540","CINQ/CINQ NATURA Hle ess Roll-on/7ml",8.5,5.355,37.0,0.17,12,[0,0,0,0,0,0,0,0,0,0,0,1]),
    ("3401560038934","CINQ/CINQ NATURA Lot moust Spray/100ml",12.0,7.2,40.0,0.0,12,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000415","CINQ/CINQ REPULS POUX/LENTE SPR100",10.55,10.55,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001368","CINQ/CINQ ROLLON EFFET GLACON 15 ML",13.0,13.0,0.0,0.0,12,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000552","CINQ/CINQ SH LAVANDE A/POUX100ML",17.0,17.0,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000293","CINQ/CINQ SH NATURA A/POUX400ML",23.5,14.805,37.0,0.42,1,[1,0,0,0,1,1,3,0,0,0,0,0]),
    ("3614790000323","CINQ/CINQ TROPIC 75 ML+ CR APAIS",16.55,10.758,35.0,0.0,12,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401542172809","CINQ/CINQ TROPIC LOT 100 ML",11.5,7.245,37.0,0.33,24,[0,0,0,0,0,0,0,0,0,0,2,2]),
    ("3614790000835","CINQ/CINQ TROPIC SPRAY 75 ML X2",17.76,9.768,45.0,1.0,12,[0,0,0,0,0,0,2,0,2,3,0,5]),
    ("3614790000316","CINQ/CINQ ZONE TEMPERE SPR 100MLX2",17.25,11.213,35.0,0.0,12,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400930295304","DERMOCUIVRE POM T 25G",7.5,7.5,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001269","DESOCLEAN LINGETTE X20",10.76,6.779,37.0,0.58,1,[0,1,2,0,0,0,0,1,0,1,2,0]),
    ("3614790000699","DESODROP 8ML",11.54,11.54,0.0,0.67,1,[0,1,0,1,1,0,0,2,0,0,0,2]),
    ("3400930093832","DESOMEDINE 0,1% COL FL 10ML",7.14,7.14,0.0,1.0,1,[2,0,0,0,0,0,1,3,1,1,4,0]),
    ("3400933445621","DESOMEDINE SOL NAS 10 ML",6.47,3.559,45.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400934867996","DESOMEDINE UNIDOSES BT 10",7.14,3.927,45.0,1.33,1,[0,0,0,0,0,2,0,1,0,3,4,5]),
    ("3614790001276","DESOSEPT POMMADE OPHTALMIQ 15G",11.5,7.245,37.0,2.83,1,[3,5,2,5,2,4,4,1,4,3,2,1]),
    ("3614790001108","DEXPANTHENOL GEL OPHTALMIQ 10G",7.15,7.15,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401344302695","EYES SOIN APAIS 15ML",14.75,9.293,37.0,0.17,1,[0,0,0,0,0,0,0,0,0,0,1,0]),
    ("3401344302756","EYES SOIN CALMANT CONT/OEIL 15ML",14.75,14.75,0.0,0.58,1,[0,0,2,2,0,1,1,0,0,0,0,0]),
    ("3400930470312","HEC POM T 25G",8.8,6.6,25.0,1.08,1,[1,0,2,0,2,1,4,1,2,0,0,1]),
    ("3400935356703","OPHTACALM 2% COL UNIDOSE 0,35ML 10",7.83,7.83,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400934692178","OPHTACALMFREE 2% COLLY FL 10ML",7.64,4.66,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401053843182","OPHTAXIA SOL OCUL 5ML UNID 10",4.1,2.501,39.0,0.17,1,[0,0,0,0,0,0,0,0,2,0,0,0]),
    ("3614790000620","OPHTAXIA SOL OCUL FL 100ML",7.15,7.15,0.0,0.25,1,[0,1,0,0,1,0,0,0,0,0,0,0]),
    ("3614790000248","PRESERVISION 3 CAPS 180",58.13,58.13,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401246028716","PRESERVISION 3 CAPS 60",22.59,19.202,15.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000279","PRESERVISION 3 CAPS 60",23.27,19.78,15.0,0.5,1,[1,0,0,1,0,0,1,0,1,0,1,1]),
    ("3614790000255","PRESERVISION 3 FEMME CAPS 60",23.27,23.27,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401560197990","PRESERVISION 3 STICK 30",23.27,23.27,0.0,0.08,1,[1,0,0,0,0,0,0,0,0,0,0,0]),
    ("7391899857015","RENU AVANCED MULTIFONCTION 100ML",7.75,7.75,0.0,0.42,1,[0,0,2,3,0,1,0,0,0,0,0,0]),
    ("7391899856216","RENU FLIGHT PACK 100 ML",7.75,5.038,35.0,0.67,1,[2,0,0,0,0,0,0,0,2,0,2,1]),
    ("7391899848624","RENU PACK 4 FLACONS",25.5,19.125,25.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("7391899840062","RENU S lent sple multifon Fl/360ml",11.7,8.541,27.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("7391899857817","RENU SOL NET 360 ML",12.95,9.713,25.0,1.83,1,[2,1,1,4,2,2,2,2,1,2,4,1]),
    ("7391899840109","RENU SOL NET MULT PACK 3X360ML",31.5,25.83,18.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000378","SENSIOPTIC FLACON 10ML",9.2,9.2,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000385","SENSIOPTIC SPRAY 10ML",13.8,13.8,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001153","SENSIOPTIC UNIDOSES 10X0,4ML",10.05,10.05,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790001146","SENSIOPTIC YEUX IRRITE FLACON 10ML",10.05,10.05,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400934587160","SENSIVISION COLLY UNID 10",7.38,4.059,45.0,0.83,1,[0,0,0,2,1,3,1,0,0,2,2,0]),
    ("0814892021599","THERA PEARL KIDS DRAGON",8.72,5.494,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0814892021605","THERA PEARL KIDS HUSKY",8.72,5.494,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0814892021575","THERA PEARL KIDS KOALA",8.72,8.72,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0814892021582","THERA PEARL KIDS PONEY",8.72,8.72,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002769","THERAPEARL ARTICULATION",13.7,8.357,39.0,0.08,1,[0,0,0,0,2,1,0,0,0,0,0,0]),
    ("0814892021551","THERAPEARL COLOR MASQUE OCULAIRE",15.96,10.055,37.0,0.17,1,[0,0,0,0,0,0,1,0,0,0,1,0]),
    ("0814892021568","THERAPEARL COLOR POCHE CERVICAL",24.26,15.284,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0814892021544","THERAPEARL COLOR POCHE MULTI-ZONE",11.87,7.478,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0814892021117","THERAPEARL Compr mult zon pocket",8.3,5.063,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002721","THERAPEARL DOS",21.89,17.074,22.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002738","THERAPEARL EPAULE CERV",22.41,13.67,39.0,0.08,1,[0,1,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002776","THERAPEARL GENOU",21.89,21.89,0.0,0.08,1,[1,0,0,0,1,0,0,0,0,0,0,0]),
    ("0850803002745","THERAPEARL KIDS GRENAD BT 1",5.7,3.477,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002752","THERAPEARL KIDS MENTH BT 1",5.7,3.477,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002714","THERAPEARL MASQ OCUL",13.97,8.801,37.0,0.58,1,[0,0,0,0,1,0,1,1,0,2,1,0]),
    ("0814892021636","THERAPEARL MASQUE VISAGE",21.95,13.829,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("0850803002622","THERAPEARL MULTIZONES",10.29,6.483,37.0,0.25,1,[0,0,1,0,2,0,0,0,0,0,0,0]),
    ("0859754005928","THERAPEARL SPORT MULTI-ZON AV/SANG",13.7,8.357,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3614790000514","THERM-COOL GEL 100 ML",9.8,5.88,40.0,0.33,1,[2,1,0,0,0,0,0,0,1,0,0,0]),
    ("3401060121389","THERM-COOL Spray froid Fl/300ml",9.9,9.9,0.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401060051648","THERM-HOT Patch chauff cou/dos/epa/poi",9.45,5.954,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3401060051624","THERM-HOT Patch chauff multizones X2",7.3,4.453,39.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("4260196620024","VIDISAN EDO COLLY UNID BT10",6.6,4.158,37.0,0.0,1,[0,0,0,0,0,0,0,0,0,0,0,0]),
    ("3400936730182","VIT CHAU B12 0,2 MG COLLY 10",6.05,3.812,37.0,0.08,1,[1,0,0,0,0,0,0,0,0,0,0,0]),
]

# EANs de la gamme 5/5 (marchés SDAV)
EANS_MARCHE_55 = {
    "3401560038934","3614790001085","3614790000828","3614790001351","3614790000323",
    "3614790001535","3614790000835","3401560206708","3614790001221","3401528503696",
    "3401571198795","3401560750744","3401542172809",
    "3614790001177","3614790001184","3614790000774","3401560206838","3614790000316","3401597812231",
    "3614790001238","3614790001245","3614790000798","3614790001078",
    "3401563131779","3401560221473","3614790001368","3401563131540","3614790000781"
}

MARCHES = [
    {"id":"CINQ_SUR_CINQ_80U",  "label":"5/5 ≥80 unités (35%)",  "seuil":80,  "remise":35},
    {"id":"CINQ_SUR_CINQ_170U", "label":"5/5 ≥170 unités (40%)", "seuil":170, "remise":40},
    {"id":"CINQ_SUR_CINQ_350U", "label":"5/5 ≥350 unités (45%)", "seuil":350, "remise":45},
    {"id":"CINQ_SUR_CINQ_500U", "label":"5/5 ≥500 unités (50%)", "seuil":500, "remise":50},
]

# ── Chargement ─────────────────────────────────────────────────────────────────
print(f"Chargement de {SOURCE}...")
try:
    with open(SOURCE, encoding="utf-8") as f:
        labos = json.load(f)
except FileNotFoundError:
    print(f"ERREUR : {SOURCE} introuvable. Lance ce script depuis le dossier du repo.")
    sys.exit(1)
print(f"  Version: {labos.get('version')} — Date: {labos.get('date')}")

# ── Marchés ────────────────────────────────────────────────────────────────────
if LABO_ID not in labos["condMarchesCommerciaux"]:
    labos["condMarchesCommerciaux"][LABO_ID] = {}
for m in MARCHES:
    labos["condMarchesCommerciaux"][LABO_ID][m["id"]] = {
        "id": m["id"], "label": m["label"], "type_engagement": "volume",
        "seuil_unite": m["seuil"], "remise_atteinte": m["remise"],
        "debut": "2026-05-01", "fin": "2026-08-24",
        "eans": list(EANS_MARCHE_55),
    }
print(f"  {len(MARCHES)} marchés injectés")

# ── Produits ───────────────────────────────────────────────────────────────────
labo = labos["condLabos"][LABO_ID]
labo["conditions"] = [{"type": "PALIER", "seuil": 0, "remisePct": 18, "actif": True}]
labo["franco"] = 250

produits = []
for ean, nom, pa_cat, pa_net, rem_cat, moy, colisage, mois in PRODUITS_VENTES:
    marche_id = "CINQ_SUR_CINQ_80U" if ean in EANS_MARCHE_55 else ""
    produits.append({
        "ean": ean, "nom": nom,
        "marche": "CINQ_SUR_CINQ" if marche_id else "",
        "marche_id": marche_id,
        "pu_catalogue": pa_cat,
        "pa_net": pa_net,
        "pv_ttc": 0, "pv_ht": 0,
        "tva": 0,
        "colisage": colisage,
        "moy": moy,
        "mbu": 0, "mb_pct": 0,
        "rem_cat": rem_cat,
        "famille": "OPHTALMOLOGIE",
        "mois": mois,
    })

labo["produits"] = produits
print(f"  {len(produits)} produits injectés (rotations réelles depuis état des ventes 20/06/2026)")

# ── Sauvegarde ─────────────────────────────────────────────────────────────────
with open(SOURCE, "w", encoding="utf-8") as f:
    json.dump(labos, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

print(f"\n✅ data-labos.json mis à jour")
print("   → git add data-labos.json && git commit -m '...' && git pull --no-rebase origin main && git push origin main")
