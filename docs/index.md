---
title: RTL-SDR
description: Pilote une clé RTL-SDR branchée en USB et expose signaux et réglages en entités Home Assistant.
ha_category:
  - Sensor
  - Binary Sensor
  - Number
  - Select
  - Switch
  - Button
ha_release: 2024.1
ha_iot_class: Local Polling
ha_config_flow: true
ha_codeowners:
  - '@Poisson48'
ha_domain: rtl_dsr
ha_integration_type: device
ha_platforms:
  - sensor
  - binary_sensor
  - number
  - select
  - switch
  - button
  - text
---

L'intégration **RTL-SDR** pilote une clé **RTL-SDR** (RTL2832U / R820T2) branchée en USB sur Home Assistant. Elle expose :

- des **capteurs** mesurant le spectre en temps réel (RSSI, bruit, pic spectral) ;
- des **entités de configuration** pour la fréquence centrale, l'échantillonnage, le gain, la PPM, la bande passante et le squelch ;
- des **boutons** de balayage rapide (FM, ISM 433/868, ADS-B 1090) ;
- des **services** exploitables depuis les automatisations.

## Prérequis

Une clé **RTL-SDR** (RTL2832U + R820T/R820T2) branchée en USB. Installez l'add-on **RTL_433** ou **rtl-sdr** sur Home Assistant OS pour que le conteneur Core voie la clé.

## Configuration

{% include integrations/config_flow.md %}

1. Allez dans **Paramètres → Appareils et services → Ajouter une intégration → RTL-SDR**.
2. Choisissez l'**index du périphérique** (0 pour la première clé).
3. Réglez la **fréquence d'échantillonnage**, la **fréquence centrale** et le **gain** initiaux.

## Services

Le domaine `rtl_dsr` expose les services suivants. Tous acceptent un `device_id` optionnel pour cibler une clé précise.

### `rtl_dsr.set_frequency`

Tune le récepteur sur une fréquence centrale en MHz (24–1766).

```yaml
service: rtl_dsr.set_frequency
data:
  frequency: 101.1
```

### `rtl_dsr.set_sample_rate`

Régle la fréquence d'échantillonnage en MHz (0.25–3.2).

### `rtl_dsr.set_gain`

Régle le gain (`"auto"` ou une valeur en dB).

### `rtl_dsr.set_ppm`

Applique une correction de fréquence en ppm.

### `rtl_dsr.set_mode`

Change le mode de démodulation (`off`, `spectrum`, `nfm`, `wfm`, `am`, `usb`, `lsb`, `raw`).

### `rtl_dsr.set_preamp`

Active/désactive le préampli.

### `rtl_dsr.set_bandwidth`

Régle la bande passante IF en MHz (0 = auto).

### `rtl_dsr.set_squelch`

Régle le seuil de détection de signal en dB.

### `rtl_dsr.reset`

Restaure les réglages par défaut et coupe la réception.

