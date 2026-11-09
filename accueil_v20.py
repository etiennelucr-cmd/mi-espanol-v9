"""Accueil V20 : parcours CECRL, missions, vocabulaire et bilans réunis."""
from datetime import date
from html import escape
import streamlit as st
import moteur as m
import arbre_competences_v18 as arbre
import aventure_v18 as aventure
import tableau_v21
from v18_style import apply_v19

THEMES_ICONS={'maison':'🏠','famille':'👨‍👩‍👧','restaurant':'☕','ville':'🏙️','aliment':'🍎','voyage':'🧳','travail':'💼','santé':'🩺'}

def icon_for(theme):
    low=theme.lower()
    return next((icon for name,icon in THEMES_ICONS.items() if name in low),'📚')

def page():
    apply_v19()
    st.markdown('''<style>
    .v20-hero{padding:1.6rem 1.8rem;border-radius:22px;background:linear-gradient(115deg,#287cba,#36b49b);color:white;margin-bottom:1rem}
    .v20-hero h1{color:white!important;font-size:2rem;margin:0}.v20-hero p{color:#fff;margin:.4rem 0 0}
    .v20-note{padding:1rem;border:1px solid #cbd9e8;border-radius:16px;margin:.4rem 0 1rem}
    </style>''',unsafe_allow_html=True)
    level=m.preference('niveau_suivi','A1')
    if level not in arbre.LEVELS: level='A1'
    s=arbre.state(); a=aventure._state()
    st.markdown('<div class="v20-hero"><h1>🇪🇸 Mi Español V21 · ¡Vamos!</h1><p>Ton aventure, ton rythme, tes progrès.</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    c1.metric('🎯 Niveau suivi',level)
    c2.metric('⭐ XP de session',s['xp']+a['xp'])
    c3.metric('🏆 Missions terminées',f"{len(a['terminees'])}/{len(aventure.MISSIONS)}")
    st.caption('Les XP sont ludiques et ne certifient pas un niveau CECRL. Les résultats du nouveau module sont conservés pendant la session.')
    options=['🧭 Ma journée','🚀 Ma mission','🌳 Arbre CECRL','📚 Vocabulaire','📊 Mes bilans']
    selected=st.radio('Mon espace',options,horizontal=True,key='v20_navigation')
    if selected==options[0]:
        tableau_v21.page()
    elif selected==options[1]:
        st.subheader('✨ Continuer mon aventure')
        st.info('Une mission courte avec des personnages. Les mini-jeux restent disponibles sans pression.')
        aventure.page()
    elif selected==options[2]:
        arbre.tree()
    elif selected==options[3]:
        st.subheader('📚 Les mots utiles, par thème et niveau')
        lv=st.selectbox('Niveau du vocabulaire',arbre.LEVELS,index=arbre.LEVELS.index(level),key='v20_lex_level')
        themes=arbre.themes(lv)
        if not themes: st.info('Aucun thème disponible pour ce niveau.')
        else:
            theme=st.selectbox('Thème',themes,key='v20_lex_theme')
            pool=arbre.words(lv,theme)
            st.markdown(f'### {icon_for(theme)} {escape(theme)} · {lv}')
            st.caption(f'{len(pool)} entrées disponibles dans le lexique existant')
            for w in pool:
                with st.expander(w['es']):
                    st.write('🇫🇷 '+w['fr'])
                    if w.get('exemple'): st.caption('💬 '+w['exemple'])
            st.info('Pour t’entraîner sur ces mots, ouvre l’onglet Arbre CECRL et choisis ce thème.')
    else:
        arbre.progress()
    st.divider()
    st.caption('Les cours, examens, conjugaisons, contrôles et le coach historique restent accessibles depuis la navigation existante.')
