"""Examens blancs pédagogiques, non certificatifs."""
import random,time
import streamlit as st
import moteur as m

def page():
    st.title('🎓 Examens blancs — A1 à C2')
    st.caption('Évaluation indicative du vocabulaire et de la grammaire sous forme de QCM. Ce module ne certifie pas le niveau CECRL et ne remplace pas les épreuves orales et écrites officielles.')
    n=st.selectbox('Niveau à évaluer',m.NIVEAUX,key='v17_examen_niveau')
    cle='v17_examen_'+n
    if st.button('🔀 Commencer un nouvel examen de 20 questions',key=cle+'_new'):
        qs=m.banque(n,limite=1000,mode='aleatoire')
        if len(qs)<20:st.warning('Pas assez de questions pour constituer un examen de 20 questions.');return
        st.session_state[cle]=random.sample(qs,20)
        st.session_state[cle+'_start']=time.monotonic()
        st.session_state.pop(cle+'_result',None)
        st.rerun()
    resultat=st.session_state.get(cle+'_result')
    if resultat:
        st.metric('Résultat du dernier examen blanc',f'{resultat[0]}/20')
        st.caption('Ce score ne valide pas automatiquement un niveau CECRL.')
        with st.expander('Voir les corrections',expanded=True):
            for q,reponse in resultat[1]:
                if reponse!=q['bonne']:
                    st.error(q['enonce']);st.write('Réponse attendue :',q['bonne'])
                    if q.get('explication'):st.caption(q['explication'])
    qs=st.session_state.get(cle)
    if not qs:st.info('Clique sur « Commencer un nouvel examen » pour commencer.');return
    with st.form(cle+'_form'):
        reponses={}
        for i,q in enumerate(qs):
            reponses[q['id']]=st.radio(f'{i+1}. {q["enonce"]}',q['options'],index=None,key=cle+'_'+str(i))
        envoyer=st.form_submit_button('Terminer et corriger mon examen')
    if envoyer:
        if any(v is None for v in reponses.values()):st.warning('Réponds aux 20 questions avant de valider.');return
        score=sum(reponses[q['id']]==q['bonne'] for q in qs)
        duree=max(1,min(7200,int(time.monotonic()-st.session_state.get(cle+'_start',time.monotonic()))))
        # Séparé des contrôles de validation : pas de modification des compétences CECRL.
        m.enregistrer_session('Examen blanc',duree/60,n,note=f'Résultat {score}/20')
        st.session_state[cle+'_result']=(score,[(q,reponses[q['id']]) for q in qs])
        del st.session_state[cle]
        st.rerun()
