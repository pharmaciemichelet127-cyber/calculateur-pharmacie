#!/bin/bash
# ══════════════════════════════════════════════════════════════════════
# deploy.sh — Déploiement d'une version du calculateur-pharmacie
#
# Usage :   ./deploy.sh 811 "description du commit"
#
# Le script fait tout : vérification du fichier téléchargé, fetch/reset,
# copie du JS, bascule d'index.html par sed (plus jamais dépendant du
# fichier index téléchargé), commit, push avec 3 tentatives si un
# auto-save le rejette, et vérification finale sur origin.
#
# PRÉREQUIS : app-vXXX.js téléchargé dans ~/Downloads
#             (indexXXX.html inutile — la bascule se fait par sed)
# ══════════════════════════════════════════════════════════════════════
set -e
V="$1"
MSG="${2:-mise à jour}"

if [ -z "$V" ]; then
  echo "Usage : ./deploy.sh 811 \"description du commit\""
  exit 1
fi

VERSION_AFFICHEE="v${V:0:1}.${V:1}"
JS="$HOME/Downloads/app-v$V.js"
cd "$(dirname "$0")"

echo "══════════════════════════════════════════"
echo "  Déploiement $VERSION_AFFICHEE"
echo "══════════════════════════════════════════"
echo ""
echo "⚠️  FERMEZ tous les onglets du calculateur (toutes machines, y compris"
echo "    celui où vous venez de tester) — un onglet ouvert = push rejeté."
echo ""
read -p "Onglets fermés ? [Entrée pour continuer, Ctrl+C pour annuler] " _

if [ ! -f "$JS" ]; then
  echo "❌ $JS introuvable."
  echo "   Fichiers app-v* présents dans Downloads :"
  ls -la "$HOME/Downloads"/app-v*.js 2>/dev/null || echo "   (aucun)"
  echo "   ⚠️  Attention aux doublons « app-v$V (1).js » — renommez si besoin."
  exit 1
fi
echo "✓ Fichier trouvé : $(ls -la "$JS")"
echo ""

OK=0
for essai in 1 2 3; do
  echo "── Tentative $essai/3 ─────────────────────"
  git fetch origin
  git reset --hard origin/main
  cp "$JS" .
  sed -i '' -E "s/app-v[0-9]+\.js/app-v$V.js/" index.html
  echo "   index.html → $(grep -o 'app-v[0-9]*\.js' index.html | head -1)"
  git add .
  if git diff --cached --quiet; then
    echo "   ℹ️  Rien à committer (déjà à jour ?) — vérification d'origin…"
  else
    git commit -m "$VERSION_AFFICHEE : $MSG"
  fi
  if git push origin main; then
    OK=1
    break
  fi
  echo "   ⚠️  Push rejeté — un auto-save est passé entre-temps."
  echo "      Vérifiez qu'AUCUN onglet calculateur n'est ouvert, nouvel essai dans 5 s…"
  sleep 5
done

echo ""
REF=$(git show origin/main:index.html 2>/dev/null | grep -o 'app-v[0-9]*\.js' | head -1)
echo "── Origin référence : $REF"
if [ "$REF" = "app-v$V.js" ]; then
  echo ""
  echo "✅ $VERSION_AFFICHEE DÉPLOYÉE."
  echo "   Rouvrez le calculateur → Cmd+Shift+R → vérifiez le badge $VERSION_AFFICHEE en bas à droite."
else
  echo ""
  echo "❌ Origin est encore sur $REF."
  echo "   Fermez TOUS les onglets calculateur et relancez : ./deploy.sh $V \"$MSG\""
  exit 1
fi
