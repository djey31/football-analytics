import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import time
import os

# ========== CONFIGURATION ==========
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== STYLE CSS ==========
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
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .team-row {
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.2rem 0;
        transition: all 0.3s;
    }
    
    .team-row:hover {
        background-color: #f0f7ff;
        transform: translateX(5px);
    }
    
    .top-4 { background-color: #E8F5E9; }
    .europa { background-color: #E3F2FD; }
    .relegation { background-color: #FFEBEE; }
    
    .match-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin: 0.8rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    
    .status-live { color: #4CAF50; font-weight: bold; animation: pulse 2s infinite; }
    .status-finished { color: #2196F3; }
    .status-scheduled { color: #FF9800; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ========== TITRE ==========
st.markdown('<div class="main-header"><h1>⚽ Football Analytics Dashboard</h1><p>Analyse en temps réel des championnats européens</p></div>', unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'cache' not in st.session_state:
    st.session_state.cache = {}

# ========== SIDEBAR ==========
with st.sidebar:
    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=80)
    
    st.header("⚙️ Configuration")
    
    # Clé API
    api_key_input = st.text_input(
        "Clé API Football-Data.org",
        type="password",
        help="Obtenez une clé gratuite sur https://www.football-data.org/"
    )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ Clé API configurée")
    else:
        st.info("🔑 Mode démo activé")
        st.markdown("""
        **Pour obtenir une clé API :**
        1. Allez sur [Football-Data.org](https://www.football-data.org)
        2. Inscrivez-vous (gratuit)
        3. Récupérez votre clé API
        4. Collez-la ici
        """)
    
    # Sélection championnat
    st.header("🏆 Championnat")
    
    competitions = {
        "🇫🇷 Ligue 1": {"code": "FL1", "color": "#0055A4"},
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": {"code": "PL", "color": "#3D195B"},
        "🇪🇸 La Liga": {"code": "PD", "color": "#FF0000"},
        "🇩🇪 Bundesliga": {"code": "BL1", "color": "#D20026"},
        "🇮🇹 Serie A": {"code": "SA", "color": "#008C45"},
    }
    
    selected_comp = st.selectbox(
        "Sélectionnez un championnat",
        list(competitions.keys()),
        index=0
    )
    
    comp_info = competitions[selected_comp]
    
    # Options d'affichage
    st.header("📊 Options")
    show_advanced = st.checkbox("Statistiques avancées", True)
    show_matches = st.checkbox("Afficher les matchs", True)
    cache_enabled = st.checkbox("Activer le cache", True)
    
    # Auto-rafraîchissement
    auto_refresh = st.checkbox("Rafraîchissement auto", False)
    if auto_refresh:
        refresh_time = st.slider("Intervalle (secondes)", 30, 300, 60)
    
    # Pied de page
    st.divider()
    st.caption("**Football Analytics v1.0**")
    st.caption("Projet M2 Software Engineering 2025-2026")
    st.caption("Données : Football-Data.org")

# ========== CLASSES UTILITAIRES ==========
class FootballAPIClient:
    """Client pour l'API Football-Data.org"""
    
    def __init__(self, api_key=None):
        self.base_url = "https://api.football-data.org/v4"
        self.api_key = api_key
        self.headers = {"X-Auth-Token": api_key} if api_key else {}
    
    def fetch_standings(self, competition_code):
        """Récupère le classement d'un championnat"""
        try:
            url = f"{self.base_url}/competitions/{competition_code}/standings"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                st.warning("⚠️ Limite d'API atteinte. Utilisation des données en cache.")
                return None
            else:
                st.error(f"❌ Erreur API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"❌ Erreur de connexion: {str(e)}")
            return None
    
    def fetch_matches(self, competition_code, status="SCHEDULED", limit=10):
        """Récupère les matchs"""
        try:
            url = f"{self.base_url}/competitions/{competition_code}/matches"
            params = {"status": status, "limit": limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

# ========== FONCTIONS D'AFFICHAGE ==========
def display_demo_mode():
    """Affiche les données de démonstration"""
    st.info("""
    **🔑 MODE DÉMO**  
    Pour accéder aux données en temps réel, entrez une clé API valide dans la sidebar.
    """)
    
    # Données de démonstration
    sample_data = {
        "Ligue 1": {
            "teams": ["Paris SG", "Lens", "Marseille", "Monaco", "Rennes", 
                     "Lille", "Nice", "Lorient", "Reims", "Lyon"],
            "points": [44, 40, 39, 37, 34, 32, 31, 30, 29, 28]
        },
        "Premier League": {
            "teams": ["Manchester City", "Arsenal", "Manchester Utd", 
                     "Liverpool", "Chelsea", "Tottenham", "Newcastle",
                     "Aston Villa", "Brighton", "Fulham"],
            "points": [45, 43, 42, 40, 38, 37, 35, 33, 32, 31]
        },
        "La Liga": {
            "teams": ["Barcelona", "Real Madrid", "Atlético Madrid", "Sevilla",
                     "Real Sociedad", "Villarreal", "Betis", "Valencia",
                     "Athletic Bilbao", "Osasuna"],
            "points": [47, 45, 42, 38, 37, 35, 34, 32, 31, 30]
        }
    }
    
    # Sélection des données
    comp_name = selected_comp.split(" ")[-1]
    data = sample_data.get(comp_name, sample_data["Ligue 1"])
    
    # Création du DataFrame
    df = pd.DataFrame({
        "Position": range(1, 11),
        "Équipe": data["teams"],
        "Points": data["points"],
        "J": [19]*10,
        "G": [13, 12, 11, 10, 9, 8, 8, 7, 7, 6],
        "N": [5, 4, 6, 7, 7, 8, 7, 9, 8, 10],
        "P": [1, 3, 2, 2, 3, 3, 4, 3, 4, 3],
        "BP": [45, 38, 35, 32, 30, 28, 27, 26, 25, 24],
        "BC": [15, 18, 20, 22, 25, 26, 28, 29, 30, 32],
        "Diff": [30, 20, 15, 10, 5, 2, -1, -3, -5, -8]
    })
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["🏆 Classement", "📈 Statistiques", "ℹ️ Informations"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(f"Classement {selected_comp}")
            
            # Affichage stylisé du classement
            for _, row in df.iterrows():
                position_class = ""
                if row['Position'] <= 4:
                    position_class = "top-4"
                elif row['Position'] >= 8:
                    position_class = "relegation"
                elif row['Position'] <= 6:
                    position_class = "europa"
                
                st.markdown(f"""
                <div class="team-row {position_class}">
                    <strong>{int(row['Position'])}.</strong> {row['Équipe']}
                    <span style="float: right; font-weight: bold;">{row['Points']} pts</span>
                    <br>
                    <small>J:{row['J']} G:{row['G']} N:{row['N']} P:{row['P']} | Diff: {row['Diff']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.header("Métriques Clés")
            
            metrics = [
                ("Moyenne Points", f"{df['Points'].mean():.1f}"),
                ("Total Buts", f"{df['BP'].sum() + df['BC'].sum()}"),
                ("Meilleure Attaque", df.loc[df['BP'].idxmax(), 'Équipe']),
                ("Meilleure Défense", df.loc[df['BC'].idxmin(), 'Équipe']),
                ("Plus Diff", df.loc[df['Diff'].idxmax(), 'Équipe']),
                ("Matchs Total", df['J'].sum())
            ]
            
            for label, value in metrics:
                st.metric(label, value)
    
    with tab2:
        if show_advanced:
            st.header("Analyse des Données")
            
            # Graphique 1 : Distribution des points
            fig1 = px.bar(
                df,
                x='Équipe',
                y='Points',
                title='Distribution des Points',
                color='Points',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Graphique 2 : Attaque vs Défense
            fig2 = px.scatter(
                df,
                x='BP',
                y='BC',
                size='Points',
                color='Position',
                hover_name='Équipe',
                title='Analyse Attaque vs Défense',
                labels={'BP': 'Buts Pour', 'BC': 'Buts Contre'}
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.header("À Propos du Mode Démo")
        st.markdown("""
        ### 🎯 Ce que vous voyez :
        - **Données simulées** réalistes
        - **Interface complète** identique à la version réelle
        - **Visualisations interactives**
        
        ### 🔓 Ce que vous obtenez avec une clé API :
        - **Données en temps réel**
        - **Mises à jour automatiques**
        - **Statistiques détaillées**
        - **Historique des matchs**
        - **Informations des joueurs**
        
        ### 📊 Sources de données réelles :
        - **Football-Data.org** - API gratuite
        - **10 requêtes/minute** - Suffisant pour usage personnel
        - **100 requêtes/jour** - Parfait pour démonstrations
        
        ### 🚀 Comment obtenir une clé API :
        1. Visitez [Football-Data.org](https://www.football-data.org)
        2. Créez un compte gratuit
        3. Générez votre clé API
        4. Collez-la dans la sidebar
        5. Profitez des données en direct !
        """)

def display_real_data():
    """Affiche les données réelles avec l'API"""
    try:
        client = FootballAPIClient(st.session_state.api_key)
        
        # Cache key
        cache_key = f"standings_{comp_info['code']}"
        
        # Vérifier le cache
        if cache_enabled and cache_key in st.session_state.cache:
            cache_data = st.session_state.cache[cache_key]
            cache_time = cache_data['timestamp']
            
            if datetime.now() - cache_time < timedelta(minutes=30):
                st.info(f"📦 Données en cache ({cache_time.strftime('%H:%M')})")
                data = cache_data['data']
            else:
                data = client.fetch_standings(comp_info['code'])
                if data:
                    st.session_state.cache[cache_key] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
        else:
            data = client.fetch_standings(comp_info['code'])
            if data and cache_enabled:
                st.session_state.cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
        
        if not data:
            st.warning("Impossible de récupérer les données. Passage en mode démo.")
            display_demo_mode()
            return
        
        # Traitement des données
        standings_data = []
        for standing in data.get("standings", []):
            if standing["type"] == "TOTAL":
                for team in standing["table"]:
                    standings_data.append({
                        "position": team["position"],
                        "team": team["team"]["name"],
                        "short_name": team["team"]["shortName"],
                        "played": team["playedGames"],
                        "won": team["won"],
                        "draw": team["draw"],
                        "lost": team["lost"],
                        "points": team["points"],
                        "goals_for": team["goalsFor"],
                        "goals_against": team["goalsAgainst"],
                        "goal_difference": team["goalDifference"],
                        "form": team.get("form", "")
                    })
        
        if not standings_data:
            st.error("Aucune donnée disponible pour ce championnat.")
            return
        
        df = pd.DataFrame(standings_data)
        
        # Onglets principaux
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏆 Classement", 
            "📅 Matchs", 
            "📊 Analyse",
            "⚙️ Système"
        ])
        
        # TAB 1 : Classement
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.header(f"Classement {selected_comp}")
                
                # Affichage amélioré du classement
                for _, row in df.iterrows():
                    # Déterminer la classe CSS
                    position_class = ""
                    if row['position'] <= 4:
                        position_class = "top-4"
                        badge = "🏆 Ligue des Champions"
                    elif row['position'] <= 6:
                        position_class = "europa"
                        badge = "🌍 Ligue Europa"
                    elif row['position'] >= len(df) - 3:
                        position_class = "relegation"
                        badge = "⚠️ Relégation"
                    else:
                        badge = ""
                    
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
                    <div class="team-row {position_class}">
                        <strong>{int(row['position'])}.</strong> {row['team']}
                        <span style="float: right;">
                            <strong>{row['points']} pts</strong>
                            <br>
                            <small>Forme: {form_colored}</small>
                        </span>
                        <br>
                        <small>
                            J:{row['played']} V:{row['won']} N:{row['draw']} D:{row['lost']} | 
                            BP:{row['goals_for']} BC:{row['goals_against']} Diff:{row['goal_difference']}
                            <br>
                            <span style="color: #666;">{badge}</span>
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.header("📈 Métriques")
                
                # Calcul des statistiques
                metrics = [
                    ("Moyenne Points", f"{df['points'].mean():.1f}"),
                    ("Total Buts", f"{df['goals_for'].sum() + df['goals_against'].sum()}"),
                    ("Meilleure Attaque", df.loc[df['goals_for'].idxmax(), 'team']),
                    ("Meilleure Défense", df.loc[df['goals_against'].idxmin(), 'team']),
                    ("% Victoires", f"{(df['won'].sum() / df['played'].sum() * 100):.1f}%"),
                    ("Matchs Nuls", f"{df['draw'].sum()}")
                ]
                
                for label, value in metrics:
                    st.metric(label, value)
                
                # Graphique rapide
                if len(df) > 0:
                    fig = px.bar(
                        df.head(8),
                        x='team',
                        y='points',
                        title='Top 8 - Points',
                        color='points',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        
        # TAB 2 : Matchs
        with tab2:
            if show_matches:
                st.header("📅 Calendrier des Matchs")
                
                # Récupérer les matchs
                matches_data = client.fetch_matches(comp_info['code'], "SCHEDULED", 10)
                
                if matches_data and "matches" in matches_data:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("⏳ Prochains Matchs")
                        upcoming_count = 0
                        for match in matches_data["matches"]:
                            if match["status"] == "SCHEDULED" and upcoming_count < 5:
                                match_time = datetime.fromisoformat(
                                    match["utcDate"].replace("Z", "+00:00")
                                )
                                
                                st.markdown(f"""
                                <div class="match-card">
                                    <div style="font-weight: bold; margin-bottom: 5px;">
                                        {match_time.strftime('%A %d %B %H:%M')}
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 1.1em;">{match['homeTeam']['name']}</span>
                                        <span style="font-weight: bold; color: #1E88E5;">VS</span>
                                        <span style="font-size: 1.1em;">{match['awayTeam']['name']}</span>
                                    </div>
                                    <div style="margin-top: 8px; font-size: 0.9em; color: #666;">
                                        Journée {match.get('matchday', '?')} • {match['competition']['name']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                upcoming_count += 1
                    
                    with col2:
                        st.subheader("✅ Derniers Résultats")
                        finished_matches = client.fetch_matches(comp_info['code'], "FINISHED", 5)
                        
                        if finished_matches and "matches" in finished_matches:
                            for match in finished_matches["matches"][:5]:
                                score = f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}"
                                match_time = datetime.fromisoformat(
                                    match["utcDate"].replace("Z", "+00:00")
                                )
                                
                                # Déterminer le gagnant
                                home_score = match['score']['fullTime']['home']
                                away_score = match['score']['fullTime']['away']
                                
                                if home_score > away_score:
                                    result_style = "color: #4CAF50; font-weight: bold;"
                                    home_style = "font-weight: bold;"
                                    away_style = ""
                                elif away_score > home_score:
                                    result_style = "color: #4CAF50; font-weight: bold;"
                                    home_style = ""
                                    away_style = "font-weight: bold;"
                                else:
                                    result_style = "color: #FF9800;"
                                    home_style = ""
                                    away_style = ""
                                
                                st.markdown(f"""
                                <div class="match-card">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                        <span style="{home_style}">{match['homeTeam']['name']}</span>
                                        <span style="{result_style}">{score}</span>
                                        <span style="{away_style}">{match['awayTeam']['name']}</span>
                                    </div>
                                    <div style="font-size: 0.9em; color: #666; text-align: center;">
                                        {match_time.strftime('%d/%m/%Y')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
        
        # TAB 3 : Analyse
        with tab3:
            if show_advanced:
                st.header("📊 Analyse Avancée")
                
                # Calculer des métriques supplémentaires
                df['avg_goals_for'] = df['goals_for'] / df['played']
                df['avg_goals_against'] = df['goals_against'] / df['played']
                df['win_rate'] = (df['won'] / df['played']) * 100
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Graphique : Efficacité attaque/défense
                    fig1 = px.scatter(
                        df,
                        x='avg_goals_for',
                        y='avg_goals_against',
                        size='points',
                        color='position',
                        hover_name='team',
                        title='Efficacité Attaque vs Défense',
                        labels={
                            'avg_goals_for': 'Buts/match (attaque)',
                            'avg_goals_against': 'Buts/match (défense)'
                        }
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Distribution des points
                    fig2 = px.histogram(
                        df,
                        x='points',
                        nbins=10,
                        title='Distribution des Points',
                        color_discrete_sequence=['#1E88E5']
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                with col2:
                    # Taux de victoire par position
                    fig3 = px.scatter(
                        df,
                        x='position',
                        y='win_rate',
                        trendline='ols',
                        hover_name='team',
                        title='Position vs Taux de Victoire',
                        labels={
                            'position': 'Position au classement',
                            'win_rate': 'Taux de victoire (%)'
                        }
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    # Comparaison buts pour/contre
                    fig4 = go.Figure(data=[
                        go.Bar(
                            name='Buts Pour',
                            x=df['team'],
                            y=df['goals_for'],
                            marker_color='#2E7D32'
                        ),
                        go.Bar(
                            name='Buts Contre',
                            x=df['team'],
                            y=df['goals_against'],
                            marker_color='#C62828'
                        )
                    ])
                    fig4.update_layout(
                        barmode='group',
                        title='Buts Pour vs Buts Contre',
                        height=400
                    )
                    st.plotly_chart(fig4, use_container_width=True)
        
        # TAB 4 : Système
        with tab4:
            st.header("⚙️ Informations Système")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Cache")
                if cache_enabled:
                    cache_size = len(st.session_state.cache)
                    st.success(f"✅ Cache activé ({cache_size} entrées)")
                    
                    if st.button("🔄 Vider le cache"):
                        st.session_state.cache = {}
                        st.success("Cache vidé !")
                        st.rerun()
                else:
                    st.warning("⚠️ Cache désactivé")
                
                st.subheader("API Status")
                if st.session_state.api_key:
                    st.success("✅ Clé API valide")
                    st.code(f"Championnat: {comp_info['code']}")
                else:
                    st.error("❌ Aucune clé API")
            
            with col2:
                st.subheader("Performance")
                if st.session_state.last_update:
                    st.info(f"📅 Dernière mise à jour: {st.session_state.last_update}")
                
                st.metric("Équipes chargées", len(df))
                st.metric("Données en cache", len(st.session_state.cache))
                
                if st.button("🔄 Rafraîchir les données"):
                    st.rerun()
    
    except Exception as e:
        st.error(f"Une erreur est survenue: {str(e)}")
        st.info("Passage en mode démo...")
        display_demo_mode()

# ========== LOGIQUE PRINCIPALE ==========
if st.session_state.api_key:
    display_real_data()
else:
    display_demo_mode()

# ========== FOOTER ==========
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📊 Football Analytics Dashboard**
    
    Application de visualisation de données footballistiques
    """)

with col2:
    st.markdown("""
    **🔧 Technologies**
    
    • Streamlit • Pandas • Plotly
    • Docker • Football-Data.org API
    """)

with col3:
    st.markdown("""
    **📚 Projet Académique**
    
    M2 Software Engineering
    2025-2026
    """)

# ========== AUTO-REFRESH ==========
if auto_refresh and 'refresh_time' in locals():
    time.sleep(refresh_time)
    st.rerun()
