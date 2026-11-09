"""V21: accueil guidé, bilans transparents et recommandations CECRL."""
from collections import Counter
from datetime import date, timedelta
import streamlit as st
import moteur as m
import arbre_competences_v18 as arbre
import sauvegarde_v22

SLOTS=[('📚 Vocabulaire thématique',25),('🔤 Conjugaison progressive',25),('🎮 Mission et mini-jeu',25),('🎧 Écoute et expression',30),('🧠 Révision et bilan',15)]

def page():
    s=arbre.state()
    level=m.preference('niveau_suivi','A1')
    if level not in arbre.LEVELS: level='A1'
    st.subheader('🧭 Ma journée en espagnol')
    st.caption('Programme conseillé de 2 heures, adaptable et sans pénalité si tu fais moins.')
    minutes=st.slider('Temps disponible aujourd’hui (minutes)',15,120,120,15,key='v21_minutes')
    st.progress(minutes/120)
    st.caption(f'Programme personnalisé : {minutes} minutes · niveau suivi : {level}')
    for title,base in SLOTS:
        adjusted=round(base*minutes/120)
        st.write(f'**{title}** · environ {adjusted} min')
    st.divider()
    st.subheader('🎯 Mes prochaines compétences')
    themes=arbre.themes(level)
    done=s.get('completed',{})
    ranked=sorted(themes,key=lambda t:(-done.get(f'{level}|{t}',0),t))
    if ranked:
        current=next((t for t in ranked if done.get(f'{level}|{t}',0)<4),ranked[0])
        st.info(f'**{current}** · {len(arbre.words(level,current))} mots disponibles · étape {min(5,done.get(f"{level}|{current}",0)+1)}/5')
        st.caption('Ouvre « Arbre CECRL » pour continuer. Les étapes explorées ne remplacent pas une validation pédagogique.')
    else:
        st.warning('Pas de vocabulaire disponible pour ce niveau dans le lexique actuel.')
    st.divider()
    st.subheader('📈 Bilan des mini-défis')
    attempts=s.get('attempts',[])
    periods={'Aujourd’hui':1,'7 derniers jours':7,'30 derniers jours':30}
    for label,days in periods.items():
        cutoff=date.today()-timedelta(days=days-1)
        rows=[r for r in attempts if date.fromisoformat(r['date'])>=cutoff]
        rate=f'{sum(bool(r["correct"]) for r in rows)/len(rows):.0%}' if rows else '—'
        st.write(f'**{label}** · {len(rows)} réponses · réussite {rate}')
    if attempts:
        misses=Counter((r['level'],r['theme']) for r in attempts if not r['correct'])
        if misses:
            lv,theme=misses.most_common(1)[0][0]
            st.info(f'🧠 Révision conseillée : {lv} · {theme}')
    st.caption('Ces bilans concernent uniquement les mini-défis de la session. Ils ne mesurent pas encore l’oral, l’écrit ou un niveau CECRL certifié.')
    st.divider()
    sauvegarde_v22.panel(s)
