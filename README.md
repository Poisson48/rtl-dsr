# RTL-SDR pour Home Assistant

> 📡 **Intégration complète pour clé RTL-SDR** avec interface **SDR++** responsive (mobile & PC).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/your-user/rtl-dsr)](https://github.com/your-user/rtl-dsr/releases)

---

## ✨ Fonctionnalités

- 🔍 **Détection automatique** du dongle RTL-SDR (RTL2832U / R820T2)
- 📊 **Interface SDR++** complète : spectre FFT, waterfall, S-mètre, tuning
- 📱 **Responsive** : mobile (1 colonne) et desktop (2 colonnes)
- 🎛 **18 entités** : fréquence, gain, mode, RSSI, bruit, pic spectral, etc.
- 🔘 **Raccourcis** : FM 101.1, ISM 433.92, ISM 868.3, ADS-B 1090 MHz
- 🌍 **Interface FR/EN**
- 🔌 **10 services** exploitables dans les automatisations

---

## 📦 Installation via HACS (recommandé)

### 1. Ajouter le repository personnalisé

1. Ouvre **HACS** dans ton Home Assistant
2. Va dans **Intégrations**
3. Clique sur le menu **⋮** (en haut à droite) → **Repositories personnalisés**
4. Dans **Repository**, colle :
   ```
   https://github.com/your-user/rtl-dsr
   ```
5. Dans **Catégorie**, choisis **Integration**
6. Clique sur **Ajouter**

### 2. Installer l'intégration

1. Recherche **RTL-SDR** dans HACS
2. Clique dessus puis sur **Télécharger**
3. **Redémarre Home Assistant** (Paramètres → Système → Redémarrer)

### 3. Ajouter l'intégration

1. **Paramètres → Appareils et services → Ajouter une intégration**
2. Recherche **RTL-SDR**
3. Index : `0`, échantillonnage : `2.048`, fréquence : `100.0`, gain : `auto`

---

## 🖥️ Ajouter la carte SDR++ (interface visuelle)

### 1. Télécharger la carte

La carte est incluse dans l'archive `rtl-dsr.zip` téléchargée par HACS.

### 2. Déployer les fichiers

Copie ces 2 fichiers dans `/config/www/rtl_dsr/` :
- `card.js`
- `sdr-plus-plus-card.js`

**Via Studio Code Server :**
```bash
mkdir -p /config/www/rtl_dsr
cp /config/custom_components/rtl_dsr/panel/sdrplusplus/*.js /config/www/rtl_dsr/
```

### 3. Ajouter la ressource Lovelace

1. **Lovelace → ⋮ → Ressources → Ajouter une ressource**
2. URL : `/local/rtl_dsr/card.js`
3. Type : `JavaScript module`

### 4. Ajouter la carte

1. Sur ton dashboard : **➕ Ajouter une carte**
2. Choisis **Personnalisée: SDR++ Card**
3. YAML :
   ```yaml
   type: custom:sdr-plus-plus-card
   fft_size: 512
   poll_interval: 250
   ```

---

## 📋 Entités créées

| Domaine | Entité | Rôle |
|---|---|---|
| `sensor` | `sensor.rtl_sdr_0_rssi` | Signal RSSI |
| `sensor` | `sensor.rtl_sdr_0_noise_floor` | Plancher de bruit |
| `sensor` | `sensor.rtl_sdr_0_peak_freq` | Fréquence du pic |
| `sensor` | `sensor.rtl_sdr_0_peak_power` | Puissance du pic |
| `sensor` | `sensor.rtl_sdr_0_tuner_type` | Type de tuner |
| `sensor` | `sensor.rtl_sdr_0_serial` | N° de série |
| `binary_sensor` | `binary_sensor.rtl_sdr_0_connected` | Connecté ? |
| `binary_sensor` | `binary_sensor.rtl_sdr_0_signal_detected` | Signal détecté ? |
| `number` | `number.rtl_sdr_0_frequency` | Fréquence (MHz) |
| `number` | `number.rtl_sdr_0_sample_rate` | Échantillonnage (MHz) |
| `number` | `number.rtl_sdr_0_ppm` | Correction PPM |
| `number` | `number.rtl_sdr_0_bandwidth` | Bande passante (MHz) |
| `number` | `number.rtl_sdr_0_squelch` | Squelch (dB) |
| `select` | `select.rtl_sdr_0_mode` | Mode (off/spectrum/nfm/wfm/am/usb/lsb/raw) |
| `select` | `select.rtl_sdr_0_gain` | Gain (auto/manuel) |
| `switch` | `switch.rtl_sdr_0_preamp` | Préampli |
| `switch` | `switch.rtl_sdr_0_reception` | Allumage réception |
| `button` | `button.rtl_sdr_0_scan_fm` | Scan FM |
| `button` | `button.rtl_sdr_0_scan_ism_433` | Scan ISM 433 |
| `button` | `button.rtl_sdr_0_scan_ism_868` | Scan ISM 868 |
| `button` | `button.rtl_sdr_0_scan_adsb` | Scan ADS-B |
| `button` | `button.rtl_sdr_0_reset` | Reset |
| `text` | `text.rtl_sdr_0_set_frequency_text` | Saisie fréquence |

---

## 🛠 Services

Tous les services acceptent un `device_id` optionnel.

### `rtl_dsr.set_frequency`
```yaml
service: rtl_dsr.set_frequency
data:
  frequency: 101.1  # MHz
```

### `rtl_dsr.set_sample_rate`
```yaml
service: rtl_dsr.set_sample_rate
data:
  sample_rate: 2.048  # MHz
```

### `rtl_dsr.set_gain`
```yaml
service: rtl_dsr.set_gain
data:
  gain: "28.0"  # ou "auto"
```

### `rtl_dsr.set_ppm`
```yaml
service: rtl_dsr.set_ppm
data:
  ppm: -2
```

### `rtl_dsr.set_mode`
```yaml
service: rtl_dsr.set_mode
data:
  mode: wfm  # off, spectrum, nfm, wfm, am, usb, lsb, raw
```

### `rtl_dsr.set_preamp`
```yaml
service: rtl_dsr.set_preamp
data:
  preamp: true
```

### `rtl_dsr.set_bandwidth`
```yaml
service: rtl_dsr.set_bandwidth
data:
  bandwidth: 0.2  # MHz, 0 = auto
```

### `rtl_dsr.set_squelch`
```yaml
service: rtl_dsr.set_squelch
data:
  level: -90  # dB
```

### `rtl_dsr.reset`
```yaml
service: rtl_dsr.reset
```

### `rtl_dsr.get_fft`
```yaml
service: rtl_dsr.get_fft
data:
  fft_size: 512
```

---

## 💡 Automatisations d'exemple

### Alerte quand un signal ISM 433 est détecté
```yaml
automation:
  - alias: "Alerte signal ISM 433"
    trigger:
      - platform: state
        entity_id: binary_sensor.rtl_sdr_0_signal_detected
        to: "on"
    condition:
      - condition: numeric_state
        entity_id: sensor.rtl_sdr_0_peak_freq
        above: 433.5
        below: 434.5
    action:
      - service: notify.mobile_app
        data:
          title: "Signal ISM 433 MHz"
          message: "Pic détecté à {{ states('sensor.rtl_sdr_0_peak_freq') }} MHz"
```

### Balayage automatique de la bande FM
```yaml
script:
  scan_fm:
    sequence:
      - service: rtl_dsr.set_frequency
        data: { frequency: 87.6 }
      - service: rtl_dsr.set_mode
        data: { mode: wfm }
      - delay: "00:00:05"
      - service: rtl_dsr.set_frequency
        data: { frequency: 107.9 }
```

---

## 🧰 Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `cannot_connect` | Clé non vue | Installe l'add-on **RTL_433** |
| `ImportError: rtlsdr` | `librtlsdr` manquant | Installe l'add-on **RTL_433** |
| RSSI toujours à -120 dB | Mauvais gain/fréquence | Monte le gain, vérifie la fréquence |
| Carte : `● déconnexion` | Intégration non chargée | Redémarre HA |
| Ressource 404 | Fichiers manquants | Vérifie que `card.js` est dans `/config/www/rtl_dsr/` |

---

## 🧪 Mode démo

Si `pyrtlsdr` n'est pas disponible, l'intégration utilise un **MockSdr** qui génère des données simulées. Utile pour tester les cartes et automatisations avant de brancher la clé.

---

## 📄 Licence

MIT © your-name

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Ouvre une issue ou une pull request sur [GitHub](https://github.com/your-user/rtl-dsr).
