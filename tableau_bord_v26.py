import streamlit as st
import moteur as m
import parcours_v10 as pv
import arbre_competences_v18 as arbre
import aventure_v18 as aventure
import mini_jeux_v41 as games

def afficher():
    level=m.preference('niveau_suivi','A1')
    valid,total=pv.progression(level)
    try: xp=int(m.statistiques().get('xp',0) or 0)
    except Exception: xp=None
    a=aventure._state(); s=arbre.state()
    st.caption('Les XP historiques et les XP de mini-jeux sont deux compteurs distincts. Seules les validations du parcours mesurent les acquis CECRL.')
    c=st.columns(4)
    c[0].metric('🎯 Niveau suivi',level)
    c[1].metric('📚 Thèmes validés',f'{valid}/{total}')
    c[2].metric('⭐ XP historiques',f'{xp:,}'.replace(',',' ') if xp is not None else 'Indisponible')
    c[3].metric('🎮 XP aventure (session)',int(a.get('xp',0))+int(s.get('xp',0))+int(games.state().get('xp',0)))
    st.progress(min(1,valid/total) if total else 0)
    st.caption(f"🎒 Missions : {len(a.get('terminees',[]))}/{len(aventure.MISSIONS)} · 🪙 Pièces de session : {int(a.get('pieces',0))+int(s.get('coins',0))+int(games.state().get('coins',0))}")
