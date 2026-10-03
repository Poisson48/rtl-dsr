# 🚀 Déploiement RTL-SDR + carte SDR++ — commandes à copier-coller

> **Où exécuter ?** Dans ton Home Assistant : **Paramètres → Modules complémentaires → Terminal & SSH → Ouvrir le Web UI**
>
> **Prérequis :** la clé RTL-SDR est branchée en USB sur le boîtier HA.

---

## 1️⃣ Vérifier que la clé RTL-SDR est visible

Copie-colle cette commande dans le Terminal & SSH :

```bash
echo "=== USB devices ===" && lsusb && echo "" && echo "=== RTL-SDR search ===" && (lsusb | grep -iE "realtek|rtl|283[28]" || echo "❌ Aucune clé RTL-SDR détectée") && echo "" && echo "=== rtl_test ===" && (rtl_test -t 2>&1 | head -20 || echo "rtl-test non installé")
```

**Attendu :** une ligne comme `0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T`

Si rien n'apparaît :
- Vérifie que la clé est bien branchée (essaie un autre port USB)
- Installe l'add-on **RTL_433** depuis le store HA (Paramètres → Modules complémentaires → Boutique des modules complémentaires)

---

## 2️⃣ Télécharger et installer l'intégration `rtl_dsr`

### Option A — Téléchargement depuis l'archive fournie

```bash
set -e
cd /config
echo "=== Création des dossiers ==="
mkdir -p custom_components/rtl_dsr
mkdir -p www/rtl_dsr

echo "=== Extraction de l'archive ==="
# Adapte le chemin selon où tu as téléversé l'archive (ex: /share/, /config/)
unzip -o /share/rtl-dsr-deploy.zip -d /tmp/rtl-dsr-deploy/
cp -r /tmp/rtl-dsr-deploy/custom_components/rtl_dsr/* /config/custom_components/rtl_dsr/
cp /tmp/rtl-dsr-deploy/panel/sdrplusplus/card.js /config/www/rtl_dsr/
cp /tmp/rtl-dsr-deploy/panel/sdrplusplus/sdr-plus-plus-card.js /config/www/rtl_dsr/

echo ""
echo "✅ Installation terminée !"
echo ""
echo "=== Vérification ==="
ls -la /config/custom_components/rtl_dsr/ | head -20
echo ""
ls -la /config/www/rtl_dsr/
```

> 💡 **Téléversement de l'archive** : utilise l'add-on **Samba share** ou **File editor** pour copier `rtl-dsr-deploy.zip` dans `/share/` ou `/config/` avant d'exécuter la commande.

### Option B — Si tu as poussé le code sur GitHub

```bash
set -e
cd /config
echo "=== Création des dossiers ==="
mkdir -p custom_components/rtl_dsr
mkdir -p www/rtl_dsr

echo "=== Téléchargement depuis GitHub ==="
if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o /tmp/rtl-dsr-deploy.zip https://github.com/<Poisson48>/rtl-dsr/releases/latest/download/rtl-dsr-deploy.zip
elif command -v wget >/dev/null 2>&1; then
  wget -q -O /tmp/rtl-dsr-deploy.zip https://github.com/<Poisson48>/rtl-dsr/releases/latest/download/rtl-dsr-deploy.zip
else
  echo "❌ Ni curl ni wget n'est installé. Utilise la méthode manuelle ci-dessous."
  exit 1
fi

echo "=== Extraction ==="
unzip -o /tmp/rtl-dsr-deploy.zip -d /tmp/rtl-dsr-deploy/
cp -r /tmp/rtl-dsr-deploy/custom_components/rtl_dsr/* /config/custom_components/rtl_dsr/
cp /tmp/rtl-dsr-deploy/panel/sdrplusplus/card.js /config/www/rtl_dsr/
cp /tmp/rtl-dsr-deploy/panel/sdrplusplus/sdr-plus-plus-card.js /config/www/rtl_dsr/

echo ""
echo "✅ Installation terminée !"
```

> ⚠️ Remplace `<Poisson48>` par ton pseudo GitHub une fois le repo créé.

---

## 3️⃣ Redémarrer Home Assistant

```bash
ha core restart
```

Ou via l'interface : **Paramètres → Système → Redémarrer**.

---

## 4️⃣ Ajouter l'intégration RTL-SDR

1. **Paramètres → Appareils et services → Ajouter une intégration** → cherche **RTL-SDR**
2. **Index du périphérique** : `0`
3. **Fréquence d'échantillonnage** : `2.048` MHz
4. **Fréquence centrale** : `100.0` MHz (bande FM — pour le test)
5. **Gain** : `auto`

L'appareil **RTL-SDR #0 (R820T)** apparaît avec ~18 entités.

---

## 5️⃣ Ajouter la carte SDR++ à ton dashboard

1. **Lovelace → ⋮ → Ressources → Ajouter une ressource**

   | Champ | Valeur |
   |---|---|
   | URL | `/local/rtl_dsr/card.js` |
   | Type | `JavaScript module` |

2. Sur ton dashboard, **Modifier → ➕ Ajouter une carte → Personnalisée: SDR++ Card**

3. YAML minimal :
   ```yaml
   type: custom:sdr-plus-plus-card
   fft_size: 512
   poll_interval: 250
   ```

4. **Enregistrer** → la carte affiche spectre + waterfall + tuning.

---

## 6️⃣ Vérification finale

Dans le Terminal & SSH :

```bash
echo "=== Vérification des fichiers ==="
ls -la /config/custom_components/rtl_dsr/
echo ""
ls -la /config/www/rtl_dsr/
echo ""
echo "✅ Si les deux listes ci-dessus ne sont pas vides, le plugin est installé."
echo "➡️  Ajoute maintenant la carte SDR++ à ton dashboard (section 5)."
```

---

## 📞 En cas de problème

| Symptôme | Solution |
|---|---|
| `cannot_connect` au setup | Installe l'add-on **RTL_433** |
| `ImportError: rtlsdr` | `pip install pyrtlsdr` dans le Terminal SSH, ou `apk add librtlsdr` |
| Carte SDR++ affiche `● déconnexion` | Redémarre HA après installation de l'intégration |
| Ressource Lovelace 404 | Vérifie que `card.js` est bien dans `/config/www/rtl_dsr/` |

