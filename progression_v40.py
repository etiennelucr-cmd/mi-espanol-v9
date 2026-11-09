"""Tableau de bord CECRL V40 : ne confond pas XP et validation."""
import streamlit as st
import moteur as m
import parcours_v10 as pv
import tableau_bord_v26 as dashboard

LEVELS=['A1','A2','B1','B2','C1','C2']

def accessible_levels():
    """Débloque chaque niveau uniquement si tous les niveaux antérieurs sont validés."""
    accessible=['A1']
    for level in LEVELS[1:]:
        try:
            if not m.niveau_debloque(level): break
        except Exception: break
        accessible.append(level)
    return accessible

def page():
    st.title('🇪🇸 Mon parcours CECRL')
    st.caption('Progression pédagogique réelle : les XP et les heures ne débloquent pas de niveaux.')
    allowed=accessible_levels()
    st.markdown('<div class="v40-road">'+''.join(
        '<div class="v40-step '+('v40-available' if lv in allowed else 'v40-closed')+'">'
        + ('🔓' if lv in allowed else '🔒')+'<strong>'+lv+'</strong><small>'
        +('Accessible' if lv in allowed else 'À débloquer')+'</small></div>' for lv in LEVELS)+'</div>',unsafe_allow_html=True)
    level=m.preference('niveau_suivi','A1')
    if level not in allowed: level=allowed[-1]
    st.subheader(f'📍 Ton niveau accessible : {level}')
    valid,total=pv.progression(level)
    c1,c2,c3=st.columns(3)
    c1.metric('Thèmes validés',f'{valid}/{total}')
    c2.metric('Progression du niveau',f'{100*valid/total:.0f}%' if total else '—')
    c3.metric('Prochain niveau',LEVELS[LEVELS.index(level)+1] if level!='C2' else 'C2 atteint')
    st.progress(min(1,valid/total) if total else 0)
    if level!='C2':
        if total and valid==total:
            st.info('Thèmes du parcours terminés. Le déblocage dépend aussi de la règle de validation du moteur (leçons et évaluations).')
        else:
            st.info(f'Encore {max(0,total-valid)} thème(s) à valider dans le parcours {level}.')
    st.divider()
    st.subheader('📚 Mes compétences par niveau')
    for lv in LEVELS:
        if lv not in allowed:
            st.caption(f'🔒 {lv} — verrouillé jusqu’à validation des niveaux précédents')
            continue
        count,total=pv.progression(lv)
        with st.expander(f'🔓 {lv} · {count}/{total} thèmes validés',expanded=lv==level):
            st.progress(min(1,count/total) if total else 0)
            try:
                for item in m.themes_valides(lv):
                    st.write(('✅ ' if item['valide'] else '⬜ ')+item['titre'])
            except Exception:
                st.caption('Détail des évaluations indisponible.')
    st.divider()
    st.subheader('⭐ Mes récompenses')
    dashboard.afficher()
    st.caption('Les résultats d’aventure et les thèmes CECRL sont volontairement séparés.')
