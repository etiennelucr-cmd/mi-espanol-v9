"""One read-only display for existing historic and session data; no invented combined grade."""
from datetime import date,timedelta
import streamlit as st
import moteur as m
import parcours_v10 as pv
import arbre_competences_v18 as arbre
import aventure_v18 as aventure
import mini_jeux_v41 as games
import progression_v40

def _safe(f,default):
    try:return f()
    except Exception:return default

def page():
    st.title('📊 Mon tableau de bord pédagogique')
    st.caption('Données issues des leçons et tests historiques, du parcours CECRL et des activités ludiques. Chaque source garde sa signification.')
    level=m.preference('niveau_suivi','A1')
    if level not in progression_v40.accessible_levels():level=progression_v40.accessible_levels()[-1]
    valid,total=_safe(lambda:pv.progression(level),(0,0))
    stats=_safe(m.statistiques,{})
    a=aventure._state(); b=arbre.state(); g=games.state()
    cols=st.columns(4)
    cols[0].metric('Niveau suivi',level)
    cols[1].metric('Thèmes validés',f'{valid}/{total}')
    cols[2].metric('XP historiques',stats.get('xp','—'))
    cols[3].metric('XP ludiques (session)',int(a.get('xp',0))+int(b.get('xp',0))+int(g.get('xp',0)))
    st.progress(min(1,valid/total) if total else 0)
    st.caption('La validation CECRL est déterminée par le moteur historique, jamais par les XP ou le temps passé.')
    st.subheader('📝 Entraînements et contrôles')
    cols=st.columns(3)
    cols[0].metric('Tests du jour',stats.get('tests','—'))
    cols[1].metric('Réponses justes du jour',f"{stats.get('bons',0)}/{stats.get('total',0)}")
    cols[2].metric('Minutes du jour',stats.get('minutes','—'))
    st.subheader('🎮 Jeux et missions')
    attempts=g.get('attempts',[])
    other=b.get('attempts',[])
    cols=st.columns(3)
    cols[0].metric('Missions terminées',f"{len(a.get('terminees',[]))}/{len(aventure.MISSIONS)}")
    cols[1].metric('Mini-jeux V41',len(attempts))
    cols[2].metric('Défis de l’arbre',len(other))
    if attempts:
        st.write(f"**Précision des mini-jeux V41 :** {sum(bool(x.get('correct')) for x in attempts)/len(attempts):.0%}")
        for mode in games.MODES:
            sub=[x for x in attempts if x.get('mode')==mode]
            if sub:st.write(f"{mode} : {sum(bool(x.get('correct')) for x in sub)}/{len(sub)} réponses correctes")
    st.subheader('📆 Mes sept derniers jours')
    recent=[]
    for i in range(6,-1,-1):
        day=(date.today()-timedelta(days=i)).isoformat()
        recent.append({'Jour':day,'Mini-jeux V41':sum(x.get('date','')[:10]==day for x in attempts),
                       'Défis arbre':sum(x.get('date','')[:10]==day for x in other)})
    st.bar_chart(recent,x='Jour',y=['Mini-jeux V41','Défis arbre'])
    st.caption('Le graphique représente les tentatives des mini-jeux, pas les cours historiques. Pour les bilans pédagogiques complets, consulte également Mes progrès et les examens.')
