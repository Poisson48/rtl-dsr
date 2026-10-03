#!/bin/bash
# RTL-SDR + SDR++ Card - Script de déploiement automatique
# Usage: curl -fsSL https://raw.githubusercontent.com/<ton-user>/rtl-dsr/main/deploy.sh | bash

set -e

echo "🚀 Déploiement RTL-SDR + SDR++ Card"
echo "===================================="

cd /config

echo ""
echo "📁 Création des dossiers..."
mkdir -p custom_components/rtl_dsr/translations
mkdir -p www/rtl_dsr

echo ""
echo "📥 Téléchargement des fichiers..."

# Download integration files
FILES=(
  "custom_components/rtl_dsr/manifest.json"
  "custom_components/rtl_dsr/const.py"
  "custom_components/rtl_dsr/config_flow.py"
  "custom_components/rtl_dsr/coordinator.py"
  "custom_components/rtl_dsr/model.py"
  "custom_components/rtl_dsr/entity.py"
  "custom_components/rtl_dsr/__init__.py"
  "custom_components/rtl_dsr/sensor.py"
  "custom_components/rtl_dsr/binary_sensor.py"
  "custom_components/rtl_dsr/number.py"
  "custom_components/rtl_dsr/select.py"
  "custom_components/rtl_dsr/switch.py"
  "custom_components/rtl_dsr/button.py"
  "custom_components/rtl_dsr/text.py"
  "custom_components/rtl_dsr/services.py"
  "custom_components/rtl_dsr/services.yaml"
  "custom_components/rtl_dsr/strings.json"
  "custom_components/rtl_dsr/websocket_api.py"
  "custom_components/rtl_dsr/translations/fr.json"
  "panel/sdrplusplus/card.js"
  "panel/sdrplusplus/sdr-plus-plus-card.js"
)

BASE_URL="https://raw.githubusercontent.com/<ton-user>/rtl-dsr/main"

for file in "${FILES[@]}"; do
  echo "  ↓ $file"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "$file" "$BASE_URL/$file"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$file" "$BASE_URL/$file"
  else
    echo "❌ Ni curl ni wget disponible"
    exit 1
  fi
done

echo ""
echo "✅ Fichiers téléchargés !"
echo ""
echo "📋 Vérification..."
ls -la /config/custom_components/rtl_dsr/ | head -5
echo "..."
ls -la /config/www/rtl_dsr/

echo ""
echo "🔄 Redémarrage de Home Assistant..."
if command -v ha >/dev/null 2>&1; then
  ha core restart
else
  echo "⚠️  Commande 'ha' non trouvée. Redémarre manuellement via l'interface."
fi

echo ""
echo "✨ Déploiement terminé !"
echo ""
echo "Prochaines étapes :"
echo "  1. Va dans Paramètres → Appareils et services → Ajouter → RTL-SDR"
echo "  2. Ajoute la ressource Lovelace : /local/rtl_dsr/card.js (module)"
echo "  3. Ajoute une carte : type: custom:sdr-plus-plus-card"
