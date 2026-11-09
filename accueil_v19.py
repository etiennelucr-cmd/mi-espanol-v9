"""Accueil ludique V19 : raccourcis vers les modules historiques, sans modifier leurs données."""
from datetime import date, timedelta
from html import escape
import streamlit as st
import moteur as m
import arbre_competences_v18 as arbre
import aventure_v18 as aventure
from v18_style import apply_v19


def page():
    apply_v19()
    level = m.preference('niveau_suivi', 'A1')
    s = arbre.state()
    a = aventure._state()
    st.markdown('''<div class="v18-hero"><h1>🇪🇸 ¡Hola, aventurero!</h1>
    <p>Une petite victoire aujourd'hui, une nouvelle compétence demain.</p></div>''', unsafe_allow_html=True)
    st.caption(f'🎯 Parcours suivi : {level} · les XP ne remplacent pas les validations CECRL')
    c1,c2,c3=st.columns(3)
    c1.metric('⭐ XP aventure', a['xp']+s['xp'])
    c2.metric('🎒 Missions terminées', f"{len(a['terminees'])}/{len(aventure.MISSIONS)}")
    c3.metric('🌳 Étapes explorées', sum(s['completed'].values()))
    st.subheader('✨ Que veux-tu faire maintenant ?')
    options=['🎮 Mission avec un personnage','🌳 Continuer mon arbre CECRL','📊 Voir mes progrès']
    choice=st.segmented_control('Choisir une activité', options, default=options[0], key='v19_home_action')
    if choice==options[0]:
        st.markdown('<div class="v19-action">👩🏽 <b>Retrouve Lucía et ses amis</b><p>Des dialogues très courts, des défis et des récompenses. Rejoue sans pression.</p></div>',unsafe_allow_html=True)
        aventure.page()
    elif choice==options[1]:
        arbre.tree()
    else:
        arbre.progress()
    st.divider()
    st.subheader('🧭 Explorer librement')
    cols=st.columns(3)
    cards=[('🏠','Maison','Objets, pièces et logement'),('👨‍👩‍👧','Famille','Parents, cousins et relations'),('🍎','Alimentation','Courses, cuisine et restaurant')]
    for col,(icon,title,desc) in zip(cols,cards):
        with col:
            st.markdown(f'<div class="v19-topic"><div class="v19-topic-icon">{icon}</div><b>{escape(title)}</b><p>{escape(desc)}</p></div>',unsafe_allow_html=True)
    st.caption('Les thèmes sont des exemples de découverte. Pour les leçons et validations officielles du parcours, utilise les rubriques CECRL historiques.')
