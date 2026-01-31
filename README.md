# ⚽ Football Analytics Pro Dashboard

Projet académique réalisé dans le cadre du **Master 2 Software – Année 2025-2026**  
Université de Marseille

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://football-analytics-final-exam-26.streamlit.app/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🐳 Docker Hub
Image disponible sur : https://hub.docker.com/r/djey31/football-analytics

## Run the container
```bash
# Clone the repository
git clone https://github.com/djey31/football-analytics.git
cd football-analytics

# Configure environment variables
cp .env.example .env
# Edit .env and add your API key
# FOOTBALL_DATA_API_KEY=your_api_key_here

# Build and run the application with Docker Compose
docker compose up --build

# Open the application in your browser
# http://localhost:8501

# Stop the application
docker compose down
```
---

## 👥 Membres du Groupe

- **BALDE Ibrahima Sory**
- **COULIBALY Adja Djeneba**
- **D'OLIVEIRA Johnny**

---

## 🎯 Objectif du Projet

Développer une **application logicielle complète** permettant :
- l’analyse de données footballistiques en temps réel,
- l’exploitation d’une **API REST externe**,
- la visualisation interactive de données,
- le déploiement d’une application **reproductible et containerisée**.
### Clé Api
A destination du professeur : 2fe021622649492f893588cfd2889dec
---

## 🧩 Description Générale

**Football Analytics Pro Dashboard** est une application Streamlit utilisant l’API  
**Football-Data.org (REST API v4)** pour fournir :

- des classements actualisés des grands championnats européens,
- des statistiques détaillées par équipe,
- un module de prédiction de matchs basé sur des indicateurs statistiques,
- une interface interactive orientée utilisateur.

---

## 🔗 Ressources en Ligne

- **Application Streamlit** :  
  https://football-analytics-final-exam-26.streamlit.app/

- **Image Docker** :  
  https://hub.docker.com/r/djey31/football-analytics

- **API utilisée** :  
  https://www.football-data.org/

---

## ✨ Fonctionnalités Principales

### 📊 Classements
- Ligue 1, Premier League, La Liga, Bundesliga, Serie A, Ligue des Champions
- Classement complet avec statistiques (points, buts, forme récente)
- Indicateurs visuels (qualification européenne, relégation)

### 🤖 Module de Prédiction
- Calcul de probabilités de victoire
- Analyse basée sur :
  - classement
  - forme récente
  - buts marqués / encaissés
- Interface conversationnelle simple

### 📈 Visualisation de Données
- Graphiques interactifs (Plotly)
- Comparaison attaque / défense
- Analyse des performances

---

## 🛠️ Technologies Utilisées

- **Langage** : Python 3.11
- **Backend / Data** : Pandas, NumPy
- **Frontend** : Streamlit, Plotly
- **API** : Football-Data.org
- **Containerisation** : Docker, Docker Compose
- **Déploiement** : Streamlit Cloud

---


