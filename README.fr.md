# 🔗 SeroAI — Système de Défense contre les Deepfakes en Temps Réel

> **Détection avancée de deepfakes alimentée par l'IA avec analyse médico-légale à 5 axes, vérification de filigrane visuel et raisonnement holistique**

---

## 🎯 Caractéristiques de la Technologie Avancée de Détection de Deepfakes

Un système de détection de deepfakes prêt pour la production qui analyse les vidéos et les images en utilisant plusieurs axes de détection, combinant l'analyse du mouvement, les vérifications de réalisme biologique, la vérification de la logique de scène, la détection d'artefacts de texture/fréquence et la vérification avancée de filigrane/provenance. Construit pour les équipes de confiance et de sécurité, les journalistes et les chercheurs en IA qui ont besoin de résultats explicables et précis.

---

## 🌐 Disponible en

[**English**](README.md) • [**한국어**](README.ko.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md) • [**Español**](README.es.md) • [**Tiếng Việt**](README.vi.md) • **Français** (actuel)

---

## ✨ Caractéristiques Principales

### 🎯 **Système de Détection à 5 Axes**
- **Stabilité du Mouvement/Temporelle** (50% de poids): Détecte les incohérences entre les images, les anomalies de flux optique et les artefacts temporels
- **Réalisme Biologique/Physique** (20% de poids): Analyse les points de repère faciaux, les modèles de clignement, la cohérence anatomique et les mouvements corporels
- **Logique de Scène et d'Éclairage** (15% de poids): Valide la persistance des objets, la cohérence physique, la cohérence de l'éclairage et les limites de prise de vue
- **Artefacts de Texture et de Fréquence** (10% de poids): Identifie les empreintes GAN, les modèles spectraux, les artefacts de compression et les incohérences de texture
- **Filigranes et Provenance** (5-50% de poids): Correspondance de logo visuel pour les filigranes de modèles IA vérifiés (Sora, Gemini, Pika, Luma, Runway, HeyGen, D-ID)

### 🔍 **Capacités de Détection Avancées**
- **Correspondance de Logo Visuel**: Correspondance de modèle, correspondance de caractéristiques ORB, comparaison d'histogramme et SSIM pour la détection de filigrane vérifié
- **Raisonnement Holistique**: Combine intelligemment plusieurs signaux faibles pour réduire les faux positifs et augmenter la confiance
- **Détection d'Impossibilité Sémantique**: Signale les scénarios logiquement impossibles (par exemple, des célébrités décédées dans de nouvelles images)
- **Ajustement Dynamique du Poids**: Passe automatiquement aux poids dominants de filigrane (50%) lorsque des logos IA vérifiés sont détectés
- **Porte de Qualité**: Pré-filtre les médias de faible qualité pour prévenir les faux positifs

### 🎨 **Interface Web Moderne**
- **React + TypeScript + Vite**: Rapide, réactif et prêt pour la production
- **Animations Framer Motion**: Transitions fluides et micro-interactions
- **Mode Sombre/Clair**: Changement de thème automatique avec détection des préférences système
- **Suivi de Progrès en Temps Réel**: Mises à jour en direct pendant l'analyse avec indicateurs de statut par méthode
- **Tableau de Bord de Résultats Détaillé**: Répartition complète de l'analyse avec explications

### 🛡️ **Prêt pour la Production**
- **Local-First**: Tout le traitement se fait sur votre appareil; pas de téléchargements cloud
- **Traitement Rapide**: Temps d'exécution typique de 8-12 secondes pour les vidéos standard
- **Seuils Configurables**: Limites de décision ajustables via configuration JSON
- **Journalisation Structurée**: Journaux JSON avec enregistrements d'analyse détaillés
- **Sortie Terminal**: Résultats d'analyse en temps réel imprimés sur la console

---

## 🚀 Démarrage Rapide

### Prérequis

- **Python 3.9+** (3.10+ recommandé)
- **Node.js 18+** et npm
- **FFmpeg** (pour le traitement vidéo)
- **Tesseract OCR** (optionnel, pour la détection de filigrane basée sur le texte)

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Installer les dépendances Python
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Installer les dépendances frontend
cd webui
npm ci
npm run build
cd ..

# 5. Démarrer le serveur
python app.py
```

Le serveur démarrera sur `http://localhost:5000`

### Dépendances Système

**Windows (PowerShell)**:
```powershell
winget install ffmpeg
winget install tesseract  # Optionnel
```

**macOS**:
```bash
brew install ffmpeg
brew install tesseract  # Optionnel
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr  # Optionnel
```

---

> **Remarque**: Ce document est traduit automatiquement. La documentation complète sera bientôt disponible. Pour l'instant, veuillez consulter la version anglaise: [README.md](README.md)

---

## 📄 Licence

**MIT** © 2025 Contributeurs SeroAI

Consultez le fichier `LICENSE` pour plus de détails.

