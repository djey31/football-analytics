import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time
import json

# =====================================================
# CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Football Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# STYLE CSS
# =====================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1E88E5, #0D47A1);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.2);
    }
    
    .team-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    
    .team-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .team-row {
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.2rem 0;
        transition: all 0.3s;
        border-left: 4px solid #1E88E5;
    }
    
    .team-row:hover {
        background-color: #f0f7ff;
        transform: translateX(5px);
    }
    
    .top-4 { 
        background-color: #E8F5E9; 
        border-left-color: #4CAF50;
    }
    
    .europa { 
        background-color: #E3F2FD; 
        border-left-color: #2196F3;
    }
    
    .conference { 
        background-color: #FFF3E0; 
        border-left-color: #FF9800;
    }
    
    .relegation { 
        background-color: #FFEBEE; 
        border-left-color: #F44336;
    }
    
    .match-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin: 0.8rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    
    .demo-badge {
        background: linear-gradient(90deg, #FF9800, #FF5722);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
    
    .api-badge {
        background: linear-gradient(90deg, #4CAF50, #2E7D32);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
    
    .status-live { 
        color: #4CAF50; 
        font-weight: bold; 
        animation: pulse 2s infinite; 
    }
    
    .status-finished { 
        color: #2196F3; 
    }
    
    .status-scheduled { 
        color: #FF9800; 
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .metric-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        height: 500px;
        overflow-y: auto;
        margin-bottom: 20px;
    }
    
    .user-message {
        background: #1E88E5;
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .bot-message {
        background: #e9ecef;
        color: #333;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .prediction-badge {
        background: #FF9800;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.9em;
        margin: 5px;
        display: inline-block;
    }
    
    /* Styles pour le sélecteur d'onglets personnalisé */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITRE
# =====================================================
col_title1, col_title2, col_title3 = st.columns([1, 3, 1])
with col_title2:
    st.markdown(
        '<div class="main-header">'
        '<h1>⚽ Football Analytics Pro</h1>'
        "<p>Dashboard professionnel d'analyse footballistique</p>"
        "</div>",
        unsafe_allow_html=True
    )

# =====================================================
# CLIENT API
# =====================================================
class FootballAPIClient:
    def __init__(self, api_key=None):
        self.base_url = "https://api.football-data.org/v4"
        self.api_key = api_key
        self.headers = {"X-Auth-Token": api_key} if api_key else {}
    
    def fetch_standings(self, competition_code):
        """Récupère le classement d'une compétition"""
        try:
            url = f"{self.base_url}/competitions/{competition_code}/standings"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                st.warning("⚠️ Limite d'API atteinte")
                return None
            else:
                st.error(f"❌ Erreur API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"❌ Erreur de connexion: {str(e)}")
            return None
    
    def fetch_matches(self, competition_code, status="SCHEDULED", limit=10):
        """Récupère les matchs d'une compétition"""
        try:
            url = f"{self.base_url}/competitions/{competition_code}/matches"
            params = {"status": status, "limit": limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    def fetch_scorers(self, competition_code, limit=10):
        """Récupère les meilleurs buteurs"""
        try:
            url = f"{self.base_url}/competitions/{competition_code}/scorers"
            params = {"limit": limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def fetch_team_matches(self, team_id, limit=10):
        """Récupère les matchs d'une équipe spécifique"""
        try:
            url = f"{self.base_url}/teams/{team_id}/matches"
            params = {"limit": limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

# =====================================================
# CHATBOT DE PRÉDICTION - Version améliorée
# =====================================================
class FootballChatbot:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.context = {}
        
    def calculate_match_probabilities(self, team1_stats, team2_stats, home_advantage=True):
        """Calcule les probabilités de victoire basées sur les statistiques"""
        
        # Facteurs de pondération
        weights = {
            'points': 0.3,
            'win_rate': 0.25,
            'goals_for_per_match': 0.2,
            'goals_against_per_match': 0.15,
            'form': 0.1
        }
        
        # Calcul du score pour chaque équipe
        score1 = (
            team1_stats.get('points', 0) * weights['points'] +
            team1_stats.get('win_rate', 0) * weights['win_rate'] +
            team1_stats.get('goals_for_per_match', 0) * weights['goals_for_per_match'] -
            team1_stats.get('goals_against_per_match', 0) * weights['goals_against_per_match'] +
            team1_stats.get('form_score', 0) * weights['form']
        )
        
        score2 = (
            team2_stats.get('points', 0) * weights['points'] +
            team2_stats.get('win_rate', 0) * weights['win_rate'] +
            team2_stats.get('goals_for_per_match', 0) * weights['goals_for_per_match'] -
            team2_stats.get('goals_against_per_match', 0) * weights['goals_against_per_match'] +
            team2_stats.get('form_score', 0) * weights['form']
        )
        
        # Avantage domicile
        if home_advantage:
            score1 += 0.1
        
        # Normalisation
        total = score1 + score2
        if total > 0:
            prob1 = (score1 / total) * 100
            prob2 = (score2 / total) * 100
        else:
            prob1 = prob2 = 50
            
        # Probabilité de match nul (basée sur les statistiques historiques)
        draw_prob = 25  # valeur par défaut
        
        # Ajustement basé sur les défenses
        avg_defense = (team1_stats.get('goals_against_per_match', 1.5) + 
                      team2_stats.get('goals_against_per_match', 1.5)) / 2
        if avg_defense < 1:
            draw_prob += 10
        elif avg_defense > 2:
            draw_prob -= 10
            
        # Redistribuer les probabilités
        remaining = 100 - draw_prob
        adj_prob1 = (prob1 / (prob1 + prob2)) * remaining
        adj_prob2 = (prob2 / (prob1 + prob2)) * remaining
        
        return {
            'team1': round(adj_prob1, 1),
            'team2': round(adj_prob2, 1),
            'draw': round(draw_prob, 1)
        }
    
    def analyze_form(self, form_string):
        """Analyse la forme récente (WWDDL)"""
        if not form_string:
            return 0
            
        points = {'W': 3, 'D': 1, 'L': 0}
        recent_form = form_string[-5:] if len(form_string) >= 5 else form_string
        
        score = sum(points.get(char, 0) for char in recent_form)
        return score / (len(recent_form) * 3) * 100  # Normalisé à 100
    
    def predict_next_match(self, team1_name, team2_name, competition_data):
        """Prédit le prochain match"""
        try:
            # Trouver les statistiques des équipes
            team1_stats = {}
            team2_stats = {}
            
            for team in competition_data:
                if team['team'] == team1_name:
                    team1_stats = {
                        'points': team['points'],
                        'win_rate': (team['won'] / team['played']) * 100 if team['played'] > 0 else 0,
                        'goals_for_per_match': team['goals_for'] / team['played'] if team['played'] > 0 else 0,
                        'goals_against_per_match': team['goals_against'] / team['played'] if team['played'] > 0 else 0,
                        'form_score': self.analyze_form(team.get('form', ''))
                    }
                elif team['team'] == team2_name:
                    team2_stats = {
                        'points': team['points'],
                        'win_rate': (team['won'] / team['played']) * 100 if team['played'] > 0 else 0,
                        'goals_for_per_match': team['goals_for'] / team['played'] if team['played'] > 0 else 0,
                        'goals_against_per_match': team['goals_against'] / team['played'] if team['played'] > 0 else 0,
                        'form_score': self.analyze_form(team.get('form', ''))
                    }
            
            if not team1_stats or not team2_stats:
                return None
                
            probabilities = self.calculate_match_probabilities(team1_stats, team2_stats)
            
            # Déterminer le pronostic
            if probabilities['team1'] > probabilities['team2'] + 15:
                prediction = f"Victoire de {team1_name}"
            elif probabilities['team2'] > probabilities['team1'] + 15:
                prediction = f"Victoire de {team2_name}"
            else:
                prediction = "Match serré, possible match nul"
            
            return {
                'probabilities': probabilities,
                'prediction': prediction,
                'team1_stats': team1_stats,
                'team2_stats': team2_stats
            }
            
        except Exception as e:
            st.error(f"Erreur dans la prédiction: {str(e)}")
            return None
    
    def answer_question(self, question, competition_data, matches_data=None):
        """Répond aux questions de l'utilisateur avec suggestions"""
        question_lower = question.lower()
        
        # Questions suggérées pour aider l'utilisateur
        suggested_questions = [
            "Quel est le classement ?",
            "Qui va gagner entre PSG et Marseille ?",
            "Quels sont les prochains matchs ?",
            "Quelle est la forme du Real Madrid ?",
            "Qui sont les meilleurs buteurs ?",
            "Quelle équipe a la meilleure attaque ?"
        ]
        
        # Questions sur le classement
        if "classement" in question_lower or "position" in question_lower or "tableau" in question_lower:
            if competition_data:
                top_teams = sorted(competition_data, key=lambda x: x['position'])[:5]
                response = "🏆 **Top 5 du classement :**\n\n"
                for team in top_teams:
                    response += f"{team['position']}. {team['team']} - {team['points']} pts\n"
                return response
            else:
                return "❌ **Désolé, je n'ai pas accès aux données du classement pour le moment.**\n\n📋 **Essayez plutôt :**\n- Quel est le classement actuel ?\n- Qui est en tête du championnat ?"
        
        # Questions sur les buteurs
        elif "buteur" in question_lower or "score" in question_lower or "marqueur" in question_lower:
            return "⚽ **Meilleurs buteurs :**\nUtilisez l'onglet '🎯 Buteurs' pour voir la liste complète des meilleurs marqueurs avec leurs statistiques détaillées."
        
        # Questions sur les matchs
        elif "match" in question_lower or "rencontre" in question_lower or "calendrier" in question_lower:
            if matches_data and 'matches' in matches_data:
                next_matches = matches_data['matches'][:3]
                response = "📅 **Prochains matchs :**\n\n"
                for match in next_matches:
                    home = match.get('homeTeam', {}).get('name', 'Inconnu')
                    away = match.get('awayTeam', {}).get('name', 'Inconnu')
                    date = utc_to_local(match.get('utcDate', 'Date inconnue'))
                    response += f"• **{home} vs {away}**\n  📅 {date}\n"
                return response
            else:
                return "❌ **Je n'ai pas d'information sur les prochains matchs pour le moment.**\n\n📋 **Essayez plutôt :**\n- Quels sont les prochains matchs de la semaine ?\n- Quel est le calendrier du championnat ?"
        
        # Questions de prédiction
        elif "qui va gagner" in question_lower or "prédiction" in question_lower or "gagnera" in question_lower or "pronostic" in question_lower:
            # Essayer d'extraire les noms d'équipes
            if "entre" in question_lower and "et" in question_lower:
                parts = question_lower.split("entre")[1].split("et")
                if len(parts) == 2:
                    team1 = parts[0].strip()
                    team2 = parts[1].strip().replace("?", "").strip()
                    
                    # Chercher les équipes correspondantes
                    found_team1 = None
                    found_team2 = None
                    
                    for team in competition_data:
                        if team['team'].lower().startswith(team1[:3]):
                            found_team1 = team['team']
                        if team['team'].lower().startswith(team2[:3]):
                            found_team2 = team['team']
                    
                    if found_team1 and found_team2:
                        prediction = self.predict_next_match(found_team1, found_team2, competition_data)
                        if prediction:
                            return f"🔮 **Prédiction pour {found_team1} vs {found_team2}:**\n\n{prediction['prediction']}\n\n**Probabilités :**\n• {found_team1}: {prediction['probabilities']['team1']}%\n• Match nul: {prediction['probabilities']['draw']}%\n• {found_team2}: {prediction['probabilities']['team2']}%"
            
            return "🤖 **Pour obtenir une prédiction, précisez les deux équipes.**\n\n📋 **Exemple :**\n- Qui va gagner entre PSG et Marseille ?\n- Prédiction pour Real Madrid vs Barcelona ?"
        
        # Questions générales
        elif "bonjour" in question_lower or "hello" in question_lower or "salut" in question_lower or "hi" in question_lower or "coucou" in question_lower:
            return "👋 **Bonjour !** Je suis l'assistant Football Analytics.\n\nJe peux vous aider avec :\n• Les classements et statistiques\n• Les prédictions de matchs\n• Les prochains matchs\n• Les analyses d'équipes\n\n**N'hésitez pas à me poser une question !**"
        
        # Questions sur l'application
        elif "aide" in question_lower or "fonction" in question_lower or "help" in question_lower or "que peux-tu" in question_lower:
            return "📚 **Je peux vous aider avec :**\n\n• **Classements** : Voir le classement complet\n• **Prédictions** : Analyser les chances de victoire\n• **Matchs** : Consulter le calendrier\n• **Statistiques** : Analyser les performances\n• **Équipes** : Voir la forme et les stats\n\n📋 **Questions suggérées :**\n- Quel est le classement ?\n- Qui va gagner entre PSG et Marseille ?\n- Quels sont les prochains matchs ?"
        
        # Analyse spécifique d'équipe
        elif "forme" in question_lower:
            team_found = False
            for team in competition_data:
                team_name_lower = team['team'].lower()
                if any(word in team_name_lower for word in question_lower.split()):
                    form = team.get('form', 'N/A')[-5:]
                    form_display = ""
                    for char in form:
                        if char == 'W':
                            form_display += "🟢"
                        elif char == 'D':
                            form_display += "🟡"
                        elif char == 'L':
                            form_display += "🔴"
                        else:
                            form_display += "⚪"
                    
                    team_found = True
                    return f"📊 **Forme de {team['team']} :** {form_display}\n\n**Statistiques actuelles :**\n• Position: {team['position']}ème\n• Points: {team['points']}\n• Buts: {team['goals_for']} pour, {team['goals_against']} contre\n• Différence: {team['goal_difference']:+}"
            
            if not team_found:
                return "❌ **Je n'ai pas trouvé d'information sur cette équipe.**\n\n📋 **Essayez plutôt :**\n- Quelle est la forme du PSG ?\n- Comment va l'équipe de Marseille ?\n- Quel est l'état de forme du Real Madrid ?"
        
        # Questions sur le championnat
        elif "championnat" in question_lower or "compétition" in question_lower or "ligue" in question_lower:
            if competition_data:
                leader = sorted(competition_data, key=lambda x: x['position'])[0]
                return f"🏆 **Championnat en cours :**\n\n• Leader actuel: **{leader['team']}** avec {leader['points']} points\n• Nombre d'équipes: {len(competition_data)}\n• Matchs joués: {leader['played']} par équipe\n\n**Top 3 :**\n1. {leader['team']} ({leader['points']} pts)\n2. {sorted(competition_data, key=lambda x: x['position'])[1]['team']}\n3. {sorted(competition_data, key=lambda x: x['position'])[2]['team']}"
        
        # Questions sur les buts
        elif "but" in question_lower and ("meilleur" in question_lower or "plus" in question_lower):
            if competition_data:
                best_attack = max(competition_data, key=lambda x: x['goals_for'])
                return f"⚡ **Meilleure attaque :**\n\n**{best_attack['team']}** avec {best_attack['goals_for']} buts marqués\n• Position: {best_attack['position']}ème\n• Buts/match: {best_attack['goals_for']/best_attack['played']:.2f}"
        
        # Questions sur la défense
        elif "défense" in question_lower or "encaiss" in question_lower:
            if competition_data:
                best_defense = min(competition_data, key=lambda x: x['goals_against'])
                return f"🛡️ **Meilleure défense :**\n\n**{best_defense['team']}** avec {best_defense['goals_against']} buts encaissés\n• Position: {best_defense['position']}ème\n• Buts/match: {best_defense['goals_against']/best_defense['played']:.2f}"
        
        # Questions sur les points
        elif "point" in question_lower and ("plus" in question_lower or "meilleur" in question_lower):
            if competition_data:
                leader = sorted(competition_data, key=lambda x: x['position'])[0]
                return f"🏅 **Équipe avec le plus de points :**\n\n**{leader['team']}** avec {leader['points']} points\n• Buts: {leader['goals_for']} pour, {leader['goals_against']} contre\n• Différence: {leader['goal_difference']:+}"
        
        # Par défaut - Réponse quand on ne sait pas
        else:
            import random
            suggestions = random.sample(suggested_questions, 3)
            suggestion_text = "\n".join([f"• {q}" for q in suggestions])
            
            return f"❌ **Désolé, je n'ai pas compris votre question.**\n\n🤔 **Je suis spécialisé dans l'analyse footballistique.**\n\n📋 **Essayez plutôt une de ces questions :**\n{suggestion_text}\n\n💡 **Ou posez-moi une question sur :**\n- Le classement\n- Une prédiction de match\n- La forme d'une équipe\n- Les statistiques du championnat"

# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================
def get_team_class(position, competition_code, total_teams=20):
    """Détermine la classe CSS selon la position"""
    if position <= 4:
        return "top-4"
    elif position <= 6 and competition_code != "CL":
        return "europa"
    elif position <= 8 and competition_code == "CL":
        return "top-4"
    elif position <= 16 and competition_code == "CL":
        return "europa"
    elif position <= 24 and competition_code == "CL":
        return "conference"
    elif position >= total_teams - 3 and competition_code != "CL":
        return "relegation"
    return ""

def get_badge_text(position, competition_code, total_teams=20):
    """Retourne le texte du badge"""
    if position <= 4 and competition_code != "CL":
        return "🏆 UCL"
    elif position <= 6 and competition_code != "CL":
        return "🌍 UEL"
    elif position <= 8 and competition_code == "CL":
        return "🏆 1/8"
    elif position <= 16 and competition_code == "CL":
        return "🌍 1/16"
    elif position <= 24 and competition_code == "CL":
        return "🔶 1/24"
    elif position >= total_teams - 3 and competition_code != "CL":
        return "⚠️ Rel"
    return ""

def utc_to_local(utc_date_str):
    """Convertit une date UTC en heure locale"""
    try:
        if "Z" in utc_date_str:
            utc_date_str = utc_date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(utc_date_str)
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return utc_date_str

def display_competition_overview(df, comp_name):
    """Affiche un aperçu général de la compétition"""
    if df.empty:
        return
    
    st.subheader("📊 Aperçu général de la compétition")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_points = df['points'].mean()
        st.metric("Points moyens", f"{avg_points:.1f}")
    
    with col2:
        total_goals = df['goals_for'].sum() + df['goals_against'].sum()
        st.metric("Total buts", total_goals)
    
    with col3:
        avg_goals_per_match = (df['goals_for'].sum() + df['goals_against'].sum()) / df['played'].sum() * 2
        st.metric("Buts/match", f"{avg_goals_per_match:.2f}")
    
    with col4:
        win_rate = (df['won'].sum() / df['played'].sum()) * 100
        st.metric("% Victoires", f"{win_rate:.1f}%")
    
    # Meilleure attaque et défense
    col_a, col_b = st.columns(2)
    
    with col_a:
        best_attack = df.loc[df['goals_for'].idxmax()]
        st.info(f"⚡ **Meilleure attaque:** {best_attack['team']} ({best_attack['goals_for']} buts)")
    
    with col_b:
        best_defense = df.loc[df['goals_against'].idxmin()]
        st.info(f"🛡️ **Meilleure défense:** {best_defense['team']} ({best_defense['goals_against']} buts encaissés)")
    
    # Graphique des points
    st.subheader("📈 Distribution des points")
    fig = px.histogram(df, x='points', nbins=15, 
                      title=f'Distribution des points - {comp_name}',
                      color_discrete_sequence=['#1E88E5'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 5 des équipes
    st.subheader("🏅 Top 5 des équipes")
    top5 = df.head()
    fig2 = px.bar(top5, x='team', y='points', 
                 color='points', title='Top 5 - Points',
                 color_continuous_scale='Viridis')
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# DONNÉES DE DÉMONSTRATION
# =====================================================
def get_demo_standings(competition_name):
    """Retourne des données de démonstration"""
    demo_data = {
        "Ligue 1": [
            {"position": 1, "team": "Paris SG", "played": 19, "won": 14, "draw": 2, "lost": 3, 
             "points": 44, "goals_for": 45, "goals_against": 15, "goal_difference": 30},
            {"position": 2, "team": "Lens", "played": 19, "won": 13, "draw": 1, "lost": 5, 
             "points": 40, "goals_for": 38, "goals_against": 18, "goal_difference": 20},
            {"position": 3, "team": "Marseille", "played": 19, "won": 12, "draw": 3, "lost": 4, 
             "points": 39, "goals_for": 35, "goals_against": 20, "goal_difference": 15},
            {"position": 4, "team": "Monaco", "played": 19, "won": 11, "draw": 4, "lost": 4, 
             "points": 37, "goals_for": 32, "goals_against": 22, "goal_difference": 10},
            {"position": 5, "team": "Rennes", "played": 19, "won": 10, "draw": 4, "lost": 5, 
             "points": 34, "goals_for": 30, "goals_against": 25, "goal_difference": 5},
        ],
        "Premier League": [
            {"position": 1, "team": "Manchester City", "played": 19, "won": 14, "draw": 3, "lost": 2, 
             "points": 45, "goals_for": 48, "goals_against": 16, "goal_difference": 32},
            {"position": 2, "team": "Arsenal", "played": 19, "won": 13, "draw": 4, "lost": 2, 
             "points": 43, "goals_for": 42, "goals_against": 18, "goal_difference": 24},
            {"position": 3, "team": "Manchester Utd", "played": 19, "won": 13, "draw": 3, "lost": 3, 
             "points": 42, "goals_for": 40, "goals_against": 20, "goal_difference": 20},
            {"position": 4, "team": "Liverpool", "played": 19, "won": 12, "draw": 4, "lost": 3, 
             "points": 40, "goals_for": 38, "goals_against": 22, "goal_difference": 16},
            {"position": 5, "team": "Chelsea", "played": 19, "won": 11, "draw": 5, "lost": 3, 
             "points": 38, "goals_for": 36, "goals_against": 24, "goal_difference": 12},
        ],
        "La Liga": [
            {"position": 1, "team": "Barcelona", "played": 19, "won": 15, "draw": 2, "lost": 2, 
             "points": 47, "goals_for": 40, "goals_against": 10, "goal_difference": 30},
            {"position": 2, "team": "Real Madrid", "played": 19, "won": 14, "draw": 3, "lost": 2, 
             "points": 45, "goals_for": 42, "goals_against": 16, "goal_difference": 26},
            {"position": 3, "team": "Atlético Madrid", "played": 19, "won": 13, "draw": 3, "lost": 3, 
             "points": 42, "goals_for": 38, "goals_against": 18, "goal_difference": 20},
            {"position": 4, "team": "Sevilla", "played": 19, "won": 11, "draw": 5, "lost": 3, 
             "points": 38, "goals_for": 35, "goals_against": 20, "goal_difference": 15},
            {"position": 5, "team": "Real Sociedad", "played": 19, "won": 10, "draw": 7, "lost": 2, 
             "points": 37, "goals_for": 32, "goals_against": 22, "goal_difference": 10},
        ]
    }
    
    comp_simple = competition_name.split(" ")[-1]
    return demo_data.get(comp_simple, demo_data["Ligue 1"])

# =====================================================
# SESSION STATE
# =====================================================
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "demo"
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = None
if 'cache' not in st.session_state:
    st.session_state.cache = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'prediction_request' not in st.session_state:
    st.session_state.prediction_request = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "🏆 Classement"

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=80)
    
    st.header("⚙️ Configuration")
    
    # Mode sélection
    mode = st.radio(
        "Mode d'application",
        ["Mode Démo", "Mode Complet (API)"],
        index=0 if st.session_state.app_mode == "demo" else 1
    )
    
    if mode == "Mode Démo":
        st.session_state.app_mode = "demo"
        st.success("🎮 Mode Démo activé")
    else:
        st.session_state.app_mode = "full"
        
        # Configuration API
        st.subheader("🔑 Configuration API")
        
        api_key_input = st.text_input(
            "Clé API Football-Data.org",
            value=st.session_state.api_key,
            type="password",
            help="Clé API fournie pour la correction"
        )
        
        col_val1, col_val2 = st.columns([2, 1])
        with col_val1:
            if st.button("✅ Valider", use_container_width=True):
                if api_key_input:
                    st.session_state.api_key = api_key_input
                    
                    # Tester l'API
                    try:
                        test_client = FootballAPIClient(api_key_input)
                        test_data = test_client.fetch_standings("FL1")
                        if test_data:
                            st.success("✅ Clé API valide")
                        else:
                            st.warning("⚠️ Clé API valide mais erreur de données")
                    except Exception as e:
                        st.error(f"❌ Erreur de connexion: {str(e)}")
                else:
                    st.error("⚠️ Veuillez entrer une clé API")
        
        with col_val2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.api_key = ""
                st.session_state.cache = {}
                st.rerun()
    
    # Sélection championnat
    st.header("🏆 Compétition")
    
    competitions = {
        "🇫🇷 Ligue 1": {"code": "FL1", "id": 2015, "color": "#0055A4"},
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": {"code": "PL", "id": 2021, "color": "#3D195B"},
        "🇪🇸 La Liga": {"code": "PD", "id": 2014, "color": "#FF0000"},
        "🇩🇪 Bundesliga": {"code": "BL1", "id": 2002, "color": "#D20026"},
        "🇮🇹 Serie A": {"code": "SA", "id": 2019, "color": "#008C45"},
        "🇪🇺 Ligue des Champions": {"code": "CL", "id": 2001, "color": "#FFD700"},
    }
    
    selected_comp = st.selectbox(
        "Sélectionnez une compétition",
        list(competitions.keys()),
        index=0
    )
    
    comp_info = competitions[selected_comp]
    
    # Options
    st.header("📊 Options")
    show_matches = st.checkbox("Afficher les matchs", True)
    show_scorers = st.checkbox("Afficher les buteurs", True)
    show_chatbot = st.checkbox("Activer le chatbot", True)
    cache_enabled = st.checkbox("Activer le cache", True)
    
    # Auto-rafraîchissement
    if st.session_state.app_mode == "full" and st.session_state.api_key:
        auto_refresh = st.checkbox("Auto-rafraîchissement", False)
        if auto_refresh:
            refresh_interval = st.slider("Intervalle (secondes)", 30, 300, 60)
    
    # Footer
    st.divider()
    st.caption("**Football Analytics Pro v2.0**")
    st.caption("Projet M2 Software Engineering 2025-2026")
    st.caption("Données : Football-Data.org")

# =====================================================
# FONCTION POUR MODE DÉMO
# =====================================================
def display_demo_mode():
    """Affiche le mode démo"""
    st.markdown('<div class="demo-badge">🎮 MODE DÉMO - DONNÉES SIMULÉES</div>', unsafe_allow_html=True)
    
    # Obtenir les données de démo
    standings_data = get_demo_standings(selected_comp)
    df = pd.DataFrame(standings_data)
    
    # Gestion des onglets avec état
    tab_names = ["🏆 Classement", "📅 Matchs", "📊 Statistiques"]
    
    # Créer les onglets
    selected_tab = st.radio(
        "Navigation",
        tab_names,
        index=tab_names.index(st.session_state.active_tab) if st.session_state.active_tab in tab_names else 0,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Mettre à jour l'état
    st.session_state.active_tab = selected_tab
    
    # Afficher le contenu de l'onglet sélectionné
    if selected_tab == "🏆 Classement":
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader(f"Classement {selected_comp}")
            
            for _, row in df.iterrows():
                team_class = get_team_class(row['position'], comp_info['code'])
                badge_text = get_badge_text(row['position'], comp_info['code'])
                
                st.markdown(f"""
                <div class="team-row {team_class}">
                    <strong>{int(row['position'])}.</strong> {row['team']}
                    <span style="float: right; font-weight: bold;">{row['points']} pts</span>
                    <br>
                    <small>
                        J:{row['played']} V:{row['won']} N:{row['draw']} D:{row['lost']} | 
                        Diff: {row['goal_difference']:+}
                        <span style="color: #666; margin-left: 10px;">{badge_text}</span>
                    </small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Sélectionner {row['team']}", key=f"demo_{row['team']}", use_container_width=True):
                    st.session_state.selected_team = row['team']
        
        with col2:
            # AFFICHAGE DES STATISTIQUES GÉNÉRALES PAR DÉFAUT
            display_competition_overview(df, selected_comp)
            
            if st.session_state.selected_team:
                st.divider()
                team_data = df[df['team'] == st.session_state.selected_team].iloc[0]
                
                st.markdown(f"""
                <div class="metric-highlight">
                    <h3>🔍 {team_data['team']}</h3>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                        <div>
                            <div style="font-size: 0.9rem; opacity: 0.9;">Position</div>
                            <div style="font-size: 2rem; font-weight: bold;">#{team_data['position']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; opacity: 0.9;">Points</div>
                            <div style="font-size: 2rem; font-weight: bold;">{team_data['points']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; opacity: 0.9;">Différence</div>
                            <div style="font-size: 2rem; font-weight: bold;">{team_data['goal_difference']:+}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Métriques
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Matchs joués", team_data['played'])
                col_b.metric("Victoires", team_data['won'])
                col_c.metric("Nuls", team_data['draw'])
                col_d.metric("Défaites", team_data['lost'])
                
                col_e, col_f = st.columns(2)
                goals_per_match = team_data['goals_for'] / team_data['played']
                col_e.metric("Buts marqués", team_data['goals_for'], f"{goals_per_match:.2f}/match")
                
                goals_against_per_match = team_data['goals_against'] / team_data['played']
                col_f.metric("Buts encaissés", team_data['goals_against'], f"{goals_against_per_match:.2f}/match")
    
    elif selected_tab == "📅 Matchs":
        if show_matches:
            st.subheader("📅 Matchs (Démo)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⏳ Prochains matchs")
                
                demo_upcoming = [
                    {"home": "Paris SG", "away": "Marseille", "date": "2024-02-15 21:00"},
                    {"home": "Lens", "away": "Monaco", "date": "2024-02-16 19:00"},
                    {"home": "Rennes", "away": "Lille", "date": "2024-02-17 17:00"},
                ]
                
                for match in demo_upcoming:
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="font-weight: bold; color: #666;">{match['date']}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                            <span>{match['home']}</span>
                            <span style="font-weight: bold; color: #1E88E5;">VS</span>
                            <span>{match['away']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### ✅ Derniers résultats")
                
                demo_results = [
                    {"home": "Paris SG", "away": "Lens", "score": "2-1", "date": "2024-02-10"},
                    {"home": "Marseille", "away": "Monaco", "score": "1-1", "date": "2024-02-09"},
                    {"home": "Lille", "away": "Rennes", "score": "0-2", "date": "2024-02-08"},
                ]
                
                for match in demo_results:
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>{match['home']}</span>
                            <span style="font-weight: bold;">{match['score']}</span>
                            <span>{match['away']}</span>
                        </div>
                        <div style="font-size: 0.9em; color: #666; text-align: center; margin-top: 5px;">
                            {match['date']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif selected_tab == "📊 Statistiques":
        st.subheader("📊 Statistiques avancées")
        
        # Calculer des métriques avancées
        df['points_per_match'] = df['points'] / df['played']
        df['goals_for_per_match'] = df['goals_for'] / df['played']
        df['goals_against_per_match'] = df['goals_against'] / df['played']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des points
            fig1 = px.histogram(df, x='points', nbins=10, title='Distribution des points')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Taux de victoire
            df['win_rate'] = (df['won'] / df['played']) * 100
            fig3 = px.scatter(df, x='position', y='win_rate', trendline='ols',
                             hover_name='team', title='Position vs Taux de victoire')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Attaque vs Défense
            fig2 = px.scatter(df, x='goals_for_per_match', y='goals_against_per_match',
                             size='points', color='position', hover_name='team',
                             title='Attaque vs Défense par match')
            st.plotly_chart(fig2, use_container_width=True)
            
            # Comparaison buts pour/contre
            fig4 = go.Figure(data=[
                go.Bar(name='Buts Pour', x=df['team'], y=df['goals_for'], marker_color='#2E7D32'),
                go.Bar(name='Buts Contre', x=df['team'], y=df['goals_against'], marker_color='#C62828')
            ])
            fig4.update_layout(barmode='group', title='Buts Pour vs Buts Contre', height=400)
            st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# FONCTION POUR MODE API - AMÉLIORÉE POUR LE CHATBOT
# =====================================================
def display_api_mode():
    """Affiche le mode API avec données réelles"""
    if not st.session_state.api_key:
        st.warning("⚠️ Veuillez entrer et valider une clé API dans la sidebar")
        return
    
    st.markdown('<div class="api-badge">🔓 MODE API - DONNÉES EN TEMPS RÉEL</div>', unsafe_allow_html=True)
    
    # Créer le client API
    client = FootballAPIClient(st.session_state.api_key)
    
    # Vérifier le cache
    cache_key = f"standings_{comp_info['code']}"
    data = None
    
    if cache_enabled and cache_key in st.session_state.cache:
        cache_data = st.session_state.cache[cache_key]
        cache_time = cache_data['timestamp']
        
        if datetime.now() - cache_time < timedelta(minutes=5):
            st.info(f"📦 Données en cache ({cache_time.strftime('%H:%M')})")
            data = cache_data['data']
    
    # Récupérer les données si pas en cache
    if not data:
        with st.spinner(f"Chargement du classement {selected_comp}..."):
            data = client.fetch_standings(comp_info['code'])
        
        if data and cache_enabled:
            st.session_state.cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            st.success("✅ Données chargées avec succès")
    
    if not data:
        st.error("❌ Impossible de charger les données")
        st.info("Passage en mode démo...")
        display_demo_mode()
        return
    
    # Traiter les données du classement
    standings_data = []
    for standing in data.get("standings", []):
        if standing.get("type") == "TOTAL":
            for team in standing.get("table", []):
                standings_data.append({
                    "position": team.get("position"),
                    "team": team.get("team", {}).get("name"),
                    "team_id": team.get("team", {}).get("id"),
                    "played": team.get("playedGames"),
                    "won": team.get("won"),
                    "draw": team.get("draw"),
                    "lost": team.get("lost"),
                    "points": team.get("points"),
                    "goals_for": team.get("goalsFor"),
                    "goals_against": team.get("goalsAgainst"),
                    "goal_difference": team.get("goalDifference"),
                    "form": team.get("form", "")
                })
    
    if not standings_data:
        st.warning("Aucune donnée disponible pour ce championnat")
        return
    
    df = pd.DataFrame(standings_data)
    
    # Créer le chatbot
    chatbot = FootballChatbot(client)
    
    # Définir les onglets
    tab_names = ["🏆 Classement", "📅 Matchs", "🎯 Buteurs", "📊 Analyse"]
    if show_chatbot:
        tab_names.append("🤖 Chatbot Prédictions")
    
    # Gestion personnalisée des onglets
    selected_tab = st.radio(
        "Navigation",
        tab_names,
        index=tab_names.index(st.session_state.active_tab) if st.session_state.active_tab in tab_names else 0,
        horizontal=True,
        label_visibility="collapsed",
        key="tab_selector"
    )
    
    # Mettre à jour l'état
    st.session_state.active_tab = selected_tab
    
    # Afficher le contenu basé sur l'onglet sélectionné
    if selected_tab == "🏆 Classement":
        display_classement_tab(df, comp_info, selected_comp, standings_data)
    
    elif selected_tab == "📅 Matchs":
        display_matches_tab(client, comp_info, show_matches, df)
    
    elif selected_tab == "🎯 Buteurs":
        display_scorers_tab(client, comp_info, show_scorers)
    
    elif selected_tab == "📊 Analyse":
        display_analysis_tab(df)
    
    elif selected_tab == "🤖 Chatbot Prédictions" and show_chatbot:
        display_chatbot_tab(chatbot, client, comp_info, standings_data, df)

def display_classement_tab(df, comp_info, selected_comp, standings_data):
    """Affiche l'onglet Classement"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(f"Classement {selected_comp}")
        st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
        
        for _, row in df.iterrows():
            team_class = get_team_class(row['position'], comp_info['code'], len(df))
            badge_text = get_badge_text(row['position'], comp_info['code'], len(df))
            
            # Formater la forme (derniers matchs)
            form = row['form'][-5:] if row['form'] else "-----"
            form_colored = ""
            for char in form:
                if char == 'W':
                    form_colored += "🟢"
                elif char == 'D':
                    form_colored += "🟡"
                elif char == 'L':
                    form_colored += "🔴"
                else:
                    form_colored += "⚪"
            
            st.markdown(f"""
            <div class="team-row {team_class}">
                <strong>{row['position']}.</strong> {row['team']}
                <span style="float: right; font-weight: bold;">{row['points']} pts</span>
                <br>
                <small>
                    J:{row['played']} V:{row['won']} N:{row['draw']} D:{row['lost']} | 
                    Diff: {row['goal_difference']:+}
                    <span style="color: #666; margin-left: 10px;">{badge_text}</span>
                    <br>
                    Forme: {form_colored}
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Sélectionner {row['team']}", key=f"api_{row['team_id']}", use_container_width=True):
                st.session_state.selected_team = row['team_id']
    
    with col2:
        # AFFICHER LES STATISTIQUES GÉNÉRALES PAR DÉFAUT
        display_competition_overview(df, selected_comp)
        
        if st.session_state.selected_team:
            st.divider()
            team_data = df[df['team_id'] == st.session_state.selected_team].iloc[0]
            
            st.markdown(f"""
            <div class="metric-highlight">
                <h3>🔍 {team_data['team']}</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Position</div>
                        <div style="font-size: 2rem; font-weight: bold;">#{team_data['position']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Points</div>
                        <div style="font-size: 2rem; font-weight: bold;">{team_data['points']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Différence</div>
                        <div style="font-size: 2rem; font-weight: bold;">{team_data['goal_difference']:+}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques de base
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("Matchs joués", team_data['played'])
            col_b.metric("Victoires", team_data['won'])
            col_c.metric("Nuls", team_data['draw'])
            col_d.metric("Défaites", team_data['lost'])
            
            # Métriques avancées
            if team_data['played'] > 0:
                col_e, col_f = st.columns(2)
                goals_per_match = team_data['goals_for'] / team_data['played']
                col_e.metric("Buts marqués", team_data['goals_for'], f"{goals_per_match:.2f}/match")
                
                goals_against_per_match = team_data['goals_against'] / team_data['played']
                col_f.metric("Buts encaissés", team_data['goals_against'], f"{goals_against_per_match:.2f}/match")

def display_matches_tab(client, comp_info, show_matches, df):
    """Affiche l'onglet Matchs - Version corrigée"""
    if show_matches:
        st.subheader("📅 Matchs (API)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⏳ Prochains matchs")
            
            with st.spinner("Chargement des matchs programmés..."):
                upcoming_matches = client.fetch_matches(comp_info['code'], "SCHEDULED", 5)
            
            if upcoming_matches and "matches" in upcoming_matches:
                for match in upcoming_matches["matches"]:
                    match_date = utc_to_local(match.get("utcDate", ""))
                    
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="font-weight: bold; color: #666;">{match_date}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                            <span style="font-weight: 500;">{match.get('homeTeam', {}).get('name', 'N/A')}</span>
                            <span style="font-weight: bold; color: #1E88E5;">VS</span>
                            <span style="font-weight: 500;">{match.get('awayTeam', {}).get('name', 'N/A')}</span>
                        </div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                            📅 Journée {match.get('matchday', 'N/A')} • 🏟️ {match.get('stage', 'Championnat')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun match programmé disponible")
        
        with col2:
            st.markdown("### ✅ Derniers résultats")
            
            with st.spinner("Chargement des derniers résultats..."):
                # Récupérer les matchs terminés
                finished_matches = client.fetch_matches(comp_info['code'], "FINISHED", 5)
            
            if finished_matches and "matches" in finished_matches:
                for match in finished_matches["matches"]:
                    match_date = utc_to_local(match.get("utcDate", ""))
                    home_team = match.get('homeTeam', {}).get('name', 'N/A')
                    away_team = match.get('awayTeam', {}).get('name', 'N/A')
                    
                    # Récupérer le score
                    score = match.get('score', {})
                    full_time = score.get('fullTime', {})
                    home_goals = full_time.get('home', 0)
                    away_goals = full_time.get('away', 0)
                    
                    # Déterminer la couleur du résultat
                    if home_goals > away_goals:
                        home_style = "font-weight: bold; color: #4CAF50;"
                        away_style = ""
                    elif away_goals > home_goals:
                        home_style = ""
                        away_style = "font-weight: bold; color: #4CAF50;"
                    else:
                        home_style = "font-weight: bold; color: #FF9800;"
                        away_style = "font-weight: bold; color: #FF9800;"
                    
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="font-weight: bold; color: #666;">{match_date}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                            <span style="{home_style}">{home_team}</span>
                            <span style="font-weight: bold; font-size: 1.1em;">
                                {home_goals} - {away_goals}
                            </span>
                            <span style="{away_style}">{away_team}</span>
                        </div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                            📅 Journée {match.get('matchday', 'N/A')} • 
                            📊 Statut: {match.get('status', 'Terminé')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun résultat récent disponible")
            
            # Petit encart statistique
            st.markdown("---")
            st.markdown("### 📈 Dernières tendances")
            
            if len(df) > 0:
                # Calculer quelques stats simples
                total_matches = df['played'].sum() // 2  # Divisé par 2 car chaque match compte pour 2 équipes
                total_goals = df['goals_for'].sum()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if total_matches > 0:
                        goals_per_match = total_goals / total_matches
                        st.metric("Buts/match", f"{goals_per_match:.2f}")
                
                with col_b:
                    if len(df) > 0:
                        avg_points = df['points'].mean()
                        st.metric("Points moyens", f"{avg_points:.1f}")
def display_scorers_tab(client, comp_info, show_scorers):
    """Affiche l'onglet Buteurs"""
    if show_scorers:
        st.subheader("🎯 Meilleurs buteurs")
        
        with st.spinner("Chargement des buteurs..."):
            scorers_data = client.fetch_scorers(comp_info['code'], 10)
        
        if scorers_data and "scorers" in scorers_data:
            scorers_list = []
            for scorer in scorers_data["scorers"]:
                player = scorer.get("player", {})
                team = scorer.get("team", {})
                scorers_list.append({
                    "Joueur": player.get("name", "N/A"),
                    "Équipe": team.get("name", "N/A"),
                    "Buts": scorer.get("goals", 0),
                    "Penalties": scorer.get("penalties", 0),
                    "Assists": scorer.get("assists", 0)
                })
            
            scorers_df = pd.DataFrame(scorers_list)
            st.dataframe(scorers_df, use_container_width=True, height=400)
            
            # Graphique des buteurs
            if len(scorers_df) > 0:
                fig = px.bar(scorers_df.head(8), x='Joueur', y='Buts', 
                            color='Buts', title='Top 8 buteurs')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données des buteurs non disponibles")

def display_analysis_tab(df):
    """Affiche l'onglet Analyse"""
    st.subheader("📊 Analyse avancée")
    
    if len(df) > 0:
        # Calculer des métriques avancées
        df['points_per_match'] = df['points'] / df['played']
        df['goals_for_per_match'] = df['goals_for'] / df['played']
        df['goals_against_per_match'] = df['goals_against'] / df['played']
        df['win_rate'] = (df['won'] / df['played']) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Attaque vs Défense
            fig1 = px.scatter(df, x='goals_for_per_match', y='goals_against_per_match',
                             size='points', color='position', hover_name='team',
                             title='Efficacité Attaque vs Défense',
                             labels={'goals_for_per_match': 'Buts/match (attaque)',
                                     'goals_against_per_match': 'Buts/match (défense)'})
            st.plotly_chart(fig1, use_container_width=True)
            
            # Distribution des points
            fig3 = px.histogram(df, x='points', nbins=15, 
                               title='Distribution des points',
                               color_discrete_sequence=['#1E88E5'])
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Position vs Taux de victoire
            fig2 = px.scatter(df, x='position', y='win_rate', trendline='ols',
                             hover_name='team', 
                             title='Position vs Taux de victoire (%)',
                             labels={'position': 'Position', 'win_rate': 'Taux de victoire'})
            st.plotly_chart(fig2, use_container_width=True)
            
            # Comparaison buts pour/contre
            fig4 = go.Figure(data=[
                go.Bar(name='Buts Pour', x=df['team'].head(10), 
                      y=df['goals_for'].head(10), marker_color='#2E7D32'),
                go.Bar(name='Buts Contre', x=df['team'].head(10), 
                      y=df['goals_against'].head(10), marker_color='#C62828')
            ])
            fig4.update_layout(barmode='group', title='Top 10 - Buts Pour vs Buts Contre',
                             height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig4, use_container_width=True)

def display_chatbot_tab(chatbot, client, comp_info, standings_data, df):
    """Affiche l'onglet Chatbot"""
    st.subheader("🤖 Assistant Football Analytics")
    st.caption("Posez des questions sur le championnat ou demandez des prédictions de matchs")
    
    # Container pour l'historique du chat
    chat_container = st.container()
    
    with chat_container:
        # Afficher l'historique du chat
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                # Formater la réponse pour un meilleur affichage
                content = message["content"]
                # Remplacer les sauts de ligne par des balises HTML
                content = content.replace('\n', '<br>')
                st.markdown(f'<div class="bot-message">🤖 {content}</div>', unsafe_allow_html=True)
    
    # Interface de prédiction de match
    st.markdown("---")
    st.subheader("🎯 Prédiction de match")
    
    col_team1, col_team2 = st.columns(2)
    with col_team1:
        team1_options = [team['team'] for team in standings_data]
        team1 = st.selectbox("Équipe 1", team1_options, key="pred_team1")
    
    with col_team2:
        team2_options = [team['team'] for team in standings_data if team['team'] != team1]
        team2 = st.selectbox("Équipe 2", team2_options, key="pred_team2")
    
    if st.button("🔮 Prédire le résultat", use_container_width=True):
        with st.spinner("Analyse en cours..."):
            prediction = chatbot.predict_next_match(team1, team2, standings_data)
            
            if prediction:
                st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
                st.markdown(f"### ⚽ {team1} vs {team2}")
                
                # Affichage des probabilités
                col_proba1, col_proba2, col_proba3 = st.columns(3)
                with col_proba1:
                    st.metric(f"{team1}", f"{prediction['probabilities']['team1']}%")
                with col_proba2:
                    st.metric("Match nul", f"{prediction['probabilities']['draw']}%")
                with col_proba3:
                    st.metric(f"{team2}", f"{prediction['probabilities']['team2']}%")
                
                # Pronostic
                st.success(f"**Pronostic :** {prediction['prediction']}")
                
                # Détails des statistiques
                with st.expander("📊 Voir les statistiques détaillées"):
                    st.write(f"**Statistiques de {team1}:**")
                    st.write(f"- Points: {prediction['team1_stats']['points']}")
                    st.write(f"- Taux de victoire: {prediction['team1_stats']['win_rate']:.1f}%")
                    st.write(f"- Buts/match: {prediction['team1_stats']['goals_for_per_match']:.2f}")
                    st.write(f"- Buts encaissés/match: {prediction['team1_stats']['goals_against_per_match']:.2f}")
                    
                    st.write(f"**Statistiques de {team2}:**")
                    st.write(f"- Points: {prediction['team2_stats']['points']}")
                    st.write(f"- Taux de victoire: {prediction['team2_stats']['win_rate']:.1f}%")
                    st.write(f"- Buts/match: {prediction['team2_stats']['goals_for_per_match']:.2f}")
                    st.write(f"- Buts encaissés/match: {prediction['team2_stats']['goals_against_per_match']:.2f}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Ajouter à l'historique
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"Prédiction pour {team1} vs {team2} : {prediction['prediction']} (Probabilités: {team1} {prediction['probabilities']['team1']}%, Nul {prediction['probabilities']['draw']}%, {team2} {prediction['probabilities']['team2']}%)"
                })
            else:
                st.error("Impossible de faire une prédiction pour ces équipes.")
    
    # Interface de chat textuel
    st.markdown("---")
    st.subheader("💬 Chat avec l'assistant")
    
    # Utiliser un formulaire pour éviter les rechargements intempestifs
    with st.form(key="chat_form", clear_on_submit=True):
        question = st.text_input("Posez votre question:", 
                                placeholder="Ex: Quel est le classement ? Qui va gagner entre PSG et Marseille ?",
                                key="question_input")
        
        col_q1, col_q2 = st.columns([4, 1])
        with col_q2:
            submit_button = st.form_submit_button("Envoyer", use_container_width=True)
        
        if submit_button and question:
            # Ajouter la question à l'historique
            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })
            
            # Obtenir une réponse
            with st.spinner("Recherche..."):
                # Récupérer les données des matchs pour le chatbot
                matches_data = client.fetch_matches(comp_info['code'], "SCHEDULED", 3)
                response = chatbot.answer_question(question, standings_data, matches_data)
                
                # Formater la réponse pour un meilleur affichage
                response_lines = response.split('\n')
                formatted_response = ""
                for line in response_lines:
                    if line.startswith("❌") or line.startswith("🤖") or line.startswith("📋") or line.startswith("📊") or line.startswith("🏆") or line.startswith("⚽") or line.startswith("📅") or line.startswith("🔮") or line.startswith("👋") or line.startswith("📚") or line.startswith("⚡") or line.startswith("🛡️") or line.startswith("🏅"):
                        formatted_response += f"**{line}**\n"
                    else:
                        formatted_response += f"{line}\n"
                
                # Ajouter la réponse à l'historique
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": formatted_response
                })
            
            # Forcer le rafraîchissement pour afficher la nouvelle réponse
            st.rerun()
    
    # Boutons de questions rapides - dans des colonnes séparées pour éviter les conflits
    st.markdown("**Questions rapides:**")
    
    # Utiliser des callbacks pour les boutons de questions rapides
    if 'quick_question' not in st.session_state:
        st.session_state.quick_question = None
    
    col_qr1, col_qr2, col_qr3 = st.columns(3)
    
    with col_qr1:
        if st.button("Classement ?", use_container_width=True, key="btn_classement"):
            st.session_state.quick_question = "Quel est le classement ?"
    
    with col_qr2:
        if st.button("Prochains matchs ?", use_container_width=True, key="btn_matchs"):
            st.session_state.quick_question = "Quels sont les prochains matchs ?"
    
    with col_qr3:
        if st.button("Aide", use_container_width=True, key="btn_aide"):
            st.session_state.quick_question = "Aide"
    
    # Traiter la question rapide si définie
    if st.session_state.quick_question:
        question = st.session_state.quick_question
        
        # Ajouter la question à l'historique
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        # Obtenir une réponse
        with st.spinner("Recherche..."):
            matches_data = client.fetch_matches(comp_info['code'], "SCHEDULED", 3)
            response = chatbot.answer_question(question, standings_data, matches_data)
            
            # Formater la réponse
            response_lines = response.split('\n')
            formatted_response = ""
            for line in response_lines:
                if line.startswith("❌") or line.startswith("🤖") or line.startswith("📋") or line.startswith("📊") or line.startswith("🏆") or line.startswith("⚽") or line.startswith("📅") or line.startswith("🔮") or line.startswith("👋") or line.startswith("📚") or line.startswith("⚡") or line.startswith("🛡️") or line.startswith("🏅"):
                    formatted_response += f"**{line}**\n"
                else:
                    formatted_response += f"{line}\n"
            
            # Ajouter la réponse à l'historique
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": formatted_response
            })
        
        # Réinitialiser la question rapide
        st.session_state.quick_question = None
        st.rerun()
    
    # Bouton pour effacer l'historique
    if st.button("🧹 Effacer l'historique", use_container_width=True, key="btn_clear"):
        st.session_state.chat_history = []
        st.session_state.quick_question = None
        st.rerun()

# =====================================================
# LOGIQUE PRINCIPALE
# =====================================================
if st.session_state.app_mode == "demo":
    display_demo_mode()
else:
    display_api_mode()

# =====================================================
# AUTO-REFRESH
# =====================================================
if (st.session_state.app_mode == "full" and 
    st.session_state.api_key and 
    'auto_refresh' in locals() and 
    auto_refresh and 
    'refresh_interval' in locals()):
    time.sleep(refresh_interval)
    st.rerun()

# =====================================================
# FOOTER
# =====================================================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📊 Football Analytics Pro**
    
    Version 2.0
    Interface professionnelle
    """)

with col2:
    st.markdown("""
    **🔧 Technologies**
    
    • Streamlit • Pandas
    • Plotly • Requests
    • Football-Data.org API
    """)

with col3:
    st.markdown("""
    **📚 Projet Académique**
    
    M2 Software 
    2025-2026
    Université de Marseille
    """)

st.caption("Données fournies par Football-Data.org - API utilisée avec permission")