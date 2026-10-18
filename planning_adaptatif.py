"""Planning hebdomadaire adaptatif, basé sur les contrôles enregistrés."""
from datetime import date,timedelta
import streamlit as st
import moteur as m
import coach_parcours as coach
import conjugaison_parcours as conj

JOURS=['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']

def priorites(n):
    lecons=m.COURS[n]
    i=next((i for i,l in enumerate(lecons) if not coach.valide(n,l)),None)
    theme=lecons[i]['titre'] if i is not None else 'Tous les thèmes validés'
    temps=conj.PARCOURS[n]
    j=next((j for j,(code,_) in enumerate(temps) if conj.statut(n,code)[0]<.95),None)
    temps_nom=temps[j][1] if j is not None else 'Tous les temps validés'
    return theme,temps_nom,i,j

def page():
    st.title('📅 Planning hebdomadaire adaptatif')
    st.caption('Le thème et le temps prioritaires restent identiques tant que leurs contrôles respectifs n’atteignent pas 95 % (19/20). Le planning est recalculé à chaque consultation.')
    niveaux=[n for n in m.NIVEAUX if coach.accessible(n) and n in conj.autorisations()]
    n=st.selectbox('Niveau du planning',niveaux,key='planning_niveau')
    theme,temps,i,j=priorites(n)
    st.info(f'📘 Thème à maîtriser : **{theme}**  |  📗 Temps à maîtriser : **{temps}**')
    if i is None and j is None:st.success('Tous les objectifs de ce niveau sont validés.')
    lundi=date.today()-timedelta(days=date.today().weekday())
    jours=[('Leçon et exemples','Fiche de conjugaison'),('Exercices guidés','Conjugaisons en contexte'),('QCM adaptatif','QCM de conjugaison'),('Correction détaillée et remédiation','Révision des formes difficiles'),('Entraînement ciblé','Contrôle blanc'),('Contrôle de 20 questions','Contrôle de conjugaison /20'),('Bilan et reprise des erreurs','Révision espacée')]
    for k,(activite,conj_activite) in enumerate(jours):
        with st.container(border=True):
            st.markdown(f'**{JOURS[k]} { (lundi+timedelta(days=k)).strftime("%d/%m") }**')
            st.write(f'📘 {activite} : {theme}')
            st.write(f'📗 {conj_activite} : {temps}')
    st.warning('Si un contrôle reste sous 95 %, le même thème ou temps est maintenu la semaine suivante. Une validation débloque la prochaine notion automatiquement.')
    st.caption('Les jours sont des recommandations, pas des rendez-vous obligatoires. Ce planning reflète tes résultats enregistrés et ne prédit pas ta date de réussite.')
