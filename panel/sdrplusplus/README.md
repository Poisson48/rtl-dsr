# SDR++ Card (panel)

Interface **SDR++** pour Home Assistant — spectre temps réel, waterfall, S‑mètre, tuning et sélecteur de démodulation. Conçue **responsive** (mobile & desktop).

## Fonctionnalités

| Zone | Contenu |
|---|---|
| **Headline** | Fréquence centrale, état de connexion, mode + gain |
| **Spectre** | FFT en temps réel avec grille et marqueur de pic |
| **Waterfall** | Historique défilant du spectre (256 px × 220 px) |
| **S‑mètre** | Barre gradient RSSI –110 → 0 dB |
| **Réglages** | Fréquence, échantillonnage, gain, mode (nfm/wfm/am/usb/lsb/raw/spectrum/off) |
| **Raccourcis** | FM 101.1, ISM 433.92, ISM 868.3, ADS‑B 1090, Reset |
| **Lecture** | RSSI, pic, fréquence du pic, niveau de bruit |

## Structure des fichiers

```
panel/sdrplusplus/
├── card.js                      # Point d'entrée principal (à déployer dans /local/rtl_dsr/)
├── sdr-plus-plus-card.js        # Implémentation complète
├── README.md
└── sdr-plus-plus-card/translations/
    ├── fr.json
    └── en.json
```

## Installation

1. Installe d'abord la custom integration [`rtl_dsr`](../../custom_components/rtl_dsr/) (voir [README racine](../../README.md)).
2. Crée le dossier `/config/www/rtl_dsr/` dans Home Assistant.
3. Copie **`card.js`** **et** **`sdr-plus-plus-card.js`** dedans (les deux fichiers sont requis).
4. Dans **Lovelace → ⋮ → Ressources → Ajouter** :

   | Champ | Valeur |
   |---|---|
   | URL | `/local/rtl_dsr/card.js` |
   | Type | `module` |

5. Sur un dashboard, **Ajouter une carte → Personnalisée: SDR++ Card**.

> **Alternative** (auto‑hébergé) — utilise le plugin [`hass-web-terminal`](https://github.com/sherazahmed76/hass-web-terminal) ou [Card Tools](https://github.com/thomasloven/lovelace-card-tools) pour la ressource.

## Configuration YAML

```yaml
type: custom:sdr-plus-plus-card
fft_size: 512          # 64–4096 bins (défaut 512)
poll_interval: 250     # ms entre chaque requête FFT (défaut 250)
```

| Option | Type | Défaut | Description |
|---|---|---|---|
| `fft_size` | `int` | `512` | Nombre de bins FFT à demander (64–4096) |
| `poll_interval` | `int` | `250` | Intervalle de rafraîchissement en ms |

## Services utilisés

La carte consomme les services de [`rtl_dsr`](../../custom_components/rtl_dsr/):

- `rtl_dsr.get_fft` — renvoie `{ bins, peak_db, peak_freq, noise_floor, rssi, center_freq, sample_rate, mode, gain }`
- `rtl_dsr.set_frequency`, `rtl_dsr.set_sample_rate`, `rtl_dsr.set_gain`, `rtl_dsr.set_mode`, `rtl_dsr.set_preamp`, `rtl_dsr.reset`

## Responsive

- `< 720 px` : une colonne (spectre au‑dessus, réglages dessous), contrôle tactile, boutons ≥ 38 px
- `≥ 720 px` : deux colonnes (scope à gauche, panneau de contrôle à droite)
- Inputs en `type="number"` pour ouvrir le clavier numérique sur mobile
- Lecture en grille `repeat(auto-fit, minmax(120px, 1fr))`

## État de développement

- [x] FFT & waterfall temps réel
- [x] Tuning, gain, mode, préampli
- [x] Raccourcis de bande (FM, ISM 433/868, ADS‑B 1090)
- [x] S‑mètre gradient
- [x] Service `rtl_dsr.get_fft` (support `fft_size`, retour JSON structuré)
- [x] Mode démo `MockSdr` pour tester sans matériel
- [ ] Sauvegarde des préférences dans l'interface
- [ ] Marqueurs de fréquences mémorisées
- [ ] Audio streaming (WFM/NFM démodulé)
