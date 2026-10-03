# RTL-SDR pour Home Assistant — Guide de déploiement rapide

> 🎯 **Objectif** : que ça marche parfaitement sur ton HA (mobile + PC) avec détection automatique du dongle RTL-SDR.

---

## 🚀 Installation en 1 commande

Ouvre **Terminal & SSH** sur ton HA et colle :

```bash
curl -fsSL https://raw.githubusercontent.com/<Poisson48>/rtl-dsr/main/deploy.sh | bash
```

**C'est tout !** Le script :
1. ✅ Télécharge tous les fichiers
2. ✅ Les place aux bons endroits
3. ✅ Redémarre Home Assistant

---

## 📋 Installation manuelle (si GitHub pas encore configuré)

### Étape 1 : Téléverser les fichiers

**Option A — Via Studio Code Server ou File Editor :**
1. Télécharge [`rtl-dsr-deploy.zip`](rtl-dsr-deploy.zip)
2. Téléverse-le dans `/config/`
3. Dans Terminal & SSH :
   ```bash
   cd /config
   unzip rtl-dsr-deploy.zip
   cp -r custom_components/rtl_dsr/* /config/custom_components/rtl_dsr/
   cp panel/sdrplusplus/card.js panel/sdrplusplus/sdr-plus-plus-card.js /config/www/rtl_dsr/
   ha core restart
   ```

**Option B — Via Samba share :**
1. Monte le partage `\\homeassistant.local\config`
2. Copie le dossier `custom_components/rtl_dsr/` dans `\custom_components\`
3. Copie `card.js` + `sdr-plus-plus-card.js` dans `\www\rtl_dsr\`
4. Redémarre HA

### Étape 2 : Vérifier la clé RTL-SDR

```bash
lsusb | grep -iE "realtek|rtl|283[28]"
```

✅ **Attendu** : `0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T`

**Si rien n'apparaît :**
- Installe l'add-on **RTL_433** depuis la boutique HA
- Redémarre HA
- Recommence

### Étape 3 : Ajouter l'intégration

1. **Paramètres → Appareils et services → Ajouter → RTL-SDR**
2. Index : `0`
3. Échantillonnage : `2.048` MHz
4. Fréquence : `100.0` MHz
5. Gain : `auto`

**Tu devrais voir** : `RTL-SDR #0 (R820T)` avec ~18 entités.

### Étape 4 : Ajouter la carte SDR++

1. **Lovelace → ⋮ → Ressources → Ajouter**
   - URL : `/local/rtl_dsr/card.js`
   - Type : `JavaScript module`

2. Sur ton dashboard : **➕ → Personnalisée → SDR++ Card**

3. YAML :
   ```yaml
   type: custom:sdr-plus-plus-card
   fft_size: 512
   poll_interval: 250
   ```

---

## ✅ Vérification finale

### Test 1 : Intégration
Va dans **Paramètres → Appareils et services → RTL-SDR** :
- ✅ L'appareil apparaît
- ✅ Les capteurs ont des valeurs (RSSI, bruit, pic)
- ✅ Pas d'erreur dans les logs

### Test 2 : Carte sur PC
- ✅ Spectre affiché
- ✅ Waterfall défilant
- ✅ Boutons fonctionnels (FM, ISM 433, etc.)
- ✅ Accents français corrects (Fréquence, Échantillonnage, etc.)

### Test 3 : Carte sur mobile
- ✅ Responsive (1 colonne)
- ✅ Boutons tactiles
- ✅ Pas de débordement horizontal

### Test 4 : Détection dongle
Dans les entités, vérifie :
- `binary_sensor.rtl_sdr_0_connected` → **on**
- `sensor.rtl_sdr_0_tuner_type` → **R820T** (ou similaire)

---

## 🐛 Dépannage

| Problème | Solution |
|---|---|
| `cannot_connect` | Installe l'add-on **RTL_433** |
| Carte : `● déconnexion` | Redémarre HA après installation |
| Ressource 404 | Vérifie que `card.js` est dans `/config/www/rtl_dsr/` |
| Pas d'entités | Vérifie les logs (`Paramètres → Système → Logs`) |
| Accents cassés | Re-télécharge les fichiers (UTF-8 BOM) |

---

## 📞 Support

Si ça ne marche toujours pas :
1. Va dans **Paramètres → Système → Logs**
2. Copie les erreurs contenant `rtl_dsr`
3. Envoie-les avec ton setup (HA OS ? Docker ? version ?)

---

## 🎉 Résultat attendu

Une fois installé, tu as :
- 📡 **Interface SDR++ complète** (spectre, waterfall, tuning)
- 📱 **Compatible mobile + PC** (responsive)
- 🎛 **18 entités** pour automatiser (fréquence, gain, mode, etc.)
- 🔘 **Raccourcis** FM, ISM 433/868, ADS-B
- 🌍 **Interface FR/EN**

**Amuse-toi bien avec ton SDR !** 🚀

