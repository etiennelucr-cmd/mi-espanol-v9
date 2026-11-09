"""V41 single home, character portraits, CECRL roadmap and real metrics."""
from pathlib import Path
import streamlit as st
from v18_style import apply_v19
import tableau_bord_v26 as bilan
import aventure_v18 as aventure
import progression_v40
import projection_cecrl_v25 as projection
import sauvegarde_aventure_v27 as sauvegarde
import sync_aventure_v29 as sync
import mini_jeux_v41 as games
import bilan_unifie_v41 as dashboard

ASSETS=Path(__file__).parent/'assets'

def page():
    apply_v19()
    st.markdown('<div class="v18-hero"><h1>🇪🇸 ¡Hola, aventurero!</h1><p>Avec Lucía, Carlos et Sofía, apprends, joue et mesure tes progrès réels.</p></div>',unsafe_allow_html=True)
    bilan.afficher()
    st.subheader('🌞 Tes compagnons de voyage')
    cols=st.columns(3, gap="medium")
    for col,(name,role,photo) in zip(cols,[('Lucía','Salutations et missions','lucia.png'),('Carlos','Dialogues du quotidien','carlos.png'),('Sofía','Défis et révisions','sofia.png')]):
        with col:
            with st.container(border=True):
                st.image(str(ASSETS/photo),use_container_width=True)
                st.markdown(f'**{name}**')
                st.caption(role)
    choice=st.radio('Que veux-tu faire maintenant ?', ['🎭 Missions illustrées','🎲 Nouveaux mini-jeux','🗺️ Carte CECRL','📊 Bilan pédagogique','📅 Mes objectifs','💾 Sauvegarder'],horizontal=True,key='v42_home')
    if choice.startswith('🎭'):aventure.page(compact=True)
    elif choice.startswith('🎲'):games.page()
    elif choice.startswith('🗺️'):progression_v40.page()
    elif choice.startswith('📊'):dashboard.page()
    elif choice.startswith('📅'):projection.page()
    else:
        sauvegarde.page();sync.panel()
