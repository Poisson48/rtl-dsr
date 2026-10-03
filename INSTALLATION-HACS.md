# 📦 Installation via HACS — Guide pas-à-pas

Ce plugin est **installable via HACS** (Home Assistant Community Store), le gestionnaire de plugins intégré à Home Assistant.

---

## 🎯 Prérequis

1. **HACS installé** sur ton Home Assistant
   - Si ce n'est pas fait : [hacs.xyz/docs/use/download/download](https://hacs.xyz/docs/use/download/download)
2. **Un compte GitHub** (gratuit) pour héberger le plugin
3. **La clé RTL-SDR branchée** en USB sur ton boîtier HA

---

## 📍 Étape 1 — Créer le repository GitHub

1. Va sur [github.com](https://github.com) et connecte-toi
2. Clique sur **New** (bouton vert, en haut à droite)
3. Remplis :
   - **Repository name** : `rtl-dsr`
   - **Description** : `RTL-SDR integration for Home Assistant with SDR++ interface`
   - **Public** ✅ (obligatoire pour HACS)
   - **Add a README file** ✅
4. Clique sur **Create repository**

✅ **Dis-moi quand le repository est créé.**

---

## 📍 Étape 2 — Pousser le code sur GitHub

**Option A — Via GitHub Desktop (plus simple) :**

1. Télécharge [GitHub Desktop](https://desktop.github.com/)
2. Clone ton repository `rtl-dsr`
3. Copie tous les fichiers du projet dans le dossier cloné
4. Dans GitHub Desktop : **Commit to main** puis **Push origin**

**Option B — Via la ligne de commande :**

```bash
cd D:\git\rtl-dsr
git init
git add .
git commit -m "Initial release - RTL-SDR v0.2.0"
git remote add origin https://github.com/TON-UTILISATEUR/rtl-dsr.git
git push -u origin main
```

✅ **Dis-moi quand le code est poussé sur GitHub.**

---

## 📍 Étape 3 — Créer une Release GitHub

1. Va sur ton repository GitHub
2. Clique sur **Releases** (à droite, sous "About")
3. Clique sur **Create a new release**
4. Remplis :
   - **Tag version** : `v0.2.0`
   - **Release title** : `RTL-SDR v0.2.0`
   - **Description** : `Première version - Intégration RTL-SDR avec interface SDR++`
5. **Attach binaries** : glisse-dépose [`rtl-dsr.zip`](rtl-dsr.zip)
6. Clique sur **Publish release**

✅ **Dis-moi quand la release est publiée.**

---

## 📍 Étape 4 — Ajouter le repository dans HACS

1. Ouvre **HACS** dans ton Home Assistant
2. Va dans **Intégrations**
3. Clique sur le menu **⋮** (en haut à droite) → **Repositories personnalisés**
4. Dans **Repository**, colle :
   ```
   https://github.com/TON-UTILISATEUR/rtl-dsr
   ```
5. Dans **Catégorie**, choisis **Integration**
6. Clique sur **Ajouter**

✅ **Dis-moi quand le repository est ajouté dans HACS.**

---

## 📍 Étape 5 — Installer l'intégration via HACS

1. Recherche **RTL-SDR** dans HACS
2. Clique dessus
3. Clique sur **Télécharger** (en bas à droite)
4. **Redémarre Home Assistant** (Paramètres → Système → Redémarrer)

✅ **Dis-moi quand HA a redémarré.**

---

## 📍 Étape 6 — Ajouter l'intégration RTL-SDR

1. Va dans **Paramètres → Appareils et services**
2. Clique sur **Ajouter une intégration**
3. Recherche **RTL-SDR**
4. Remplis :
   - **Index du périphérique** : `0`
   - Clique sur **Soumettre**
5. Deuxième écran :
   - **Fréquence d'échantillonnage** : `2.048`
   - **Fréquence centrale** : `100.0`
   - **Gain** : `auto`
   - Clique sur **Soumettre**

**Attendu :** L'appareil **RTL-SDR #0 (R820T)** apparaît avec ~18 entités.

✅ **Dis-moi si l'intégration s'ajoute.**

---

## 📍 Étape 7 — Ajouter la carte SDR++ (interface visuelle)

### 7.1 Déployer les fichiers de la carte

Dans **Studio Code Server** (ou Terminal & SSH) :

```bash
mkdir -p /config/www/rtl_dsr
cp /config/custom_components/rtl_dsr/panel/sdrplusplus/*.js /config/www/rtl_dsr/
```

Ou manuellement : copie `card.js` et `sdr-plus-plus-card.js` dans `/config/www/rtl_dsr/`.

### 7.2 Ajouter la ressource Lovelace

1. Va dans ton **dashboard** (Lovelace)
2. Clique sur **⋮ → Ressources → Ajouter une ressource**
3. Remplis :
   - **URL** : `/local/rtl_dsr/card.js`
   - **Type** : `JavaScript module`
4. Clique sur **Créer**

### 7.3 Ajouter la carte

1. Sur ton dashboard : **➕ Ajouter une carte**
2. Choisis **Personnalisée: SDR++ Card**
3. Clique sur **Ajouter**

**Attendu :** La carte SDR++ s'affiche avec spectre, waterfall et contrôles.

✅ **Dis-moi si la carte s'affiche.**

---

## 📍 Étape 8 — Tester la détection du dongle

1. Ouvre **Terminal & SSH** (Paramètres → Modules complémentaires → Terminal & SSH → Ouvrir le Web UI)
2. Colle cette commande :
   ```bash
   lsusb | grep -iE "realtek|rtl|283[28]"
   ```

**Attendu :** `0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T`

✅ **Dis-moi le résultat de `lsusb`.**

---

## 📋 Résumé

| Étape | Action | Résultat attendu |
|---|---|---|
| 1 | Créer repository GitHub | ✅ `rtl-dsr` créé |
| 2 | Pousser le code | ✅ Fichiers sur GitHub |
| 3 | Créer une release | ✅ `v0.2.0` avec `rtl-dsr.zip` |
| 4 | Ajouter dans HACS | ✅ Repository ajouté |
| 5 | Installer via HACS | ✅ Intégration téléchargée |
| 6 | Ajouter l'intégration | ✅ 18 entités créées |
| 7 | Ajouter la carte SDR++ | ✅ Interface visuelle |
| 8 | Tester la détection | ✅ Dongle détecté |

---

## 🆘 Si tu bloques

Dis-moi simplement :
- **À quelle étape tu es**
- **Ce que tu vois à l'écran**
- **Le message d'erreur exact** (s'il y en a un)

Je t'aiderai à débloquer ! 🚀

---

## 📞 Support

Si ça ne marche toujours pas après toutes les étapes :
1. Va dans **Paramètres → Système → Logs**
2. Copie les erreurs contenant `rtl_dsr`
3. Envoie-les avec ton setup (HA OS ? Docker ? version ?)
