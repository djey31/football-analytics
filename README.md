# ⚽ Football Analytics Dashboard

## 🚀 Application en Ligne
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://football-analytics.streamlit.app)

## 📋 Aperçu du Projet
Application complète d'analyse de données football en temps réel. Récupère, traite et visualise les données des championnats européens via l'API Football-Data.org.

## ✨ Fonctionnalités
- **Classements en direct** (Ligue 1, Premier League, etc.)
- **Statistiques détaillées** des équipes
- **Visualisations interactives** avec Plotly
- **Mode démo** sans API key requise
- **Cache intelligent** pour optimiser les appels API
- **Interface responsive** et moderne

## 🛠️ Installation Rapide

### Avec Docker (recommandé)
```bash
# 1. Clonez le dépôt
git clone https://github.com/votre-username/football-analytics.git
cd football-analytics

# 2. Configurez l'environnement
cp .env.example .env
# Éditez .env avec votre clé API

# 3. Lancez avec Docker Compose
docker-compose up -d

# 4. Accédez à l'application
# http://localhost:8501
