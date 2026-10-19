"""Deux entraînements complémentaires au parcours oral existant."""
import html, random
import streamlit as st
import streamlit.components.v1 as components
import moteur as m
import pedagogie as p
import parcours_v10 as pv

def _tirage(n):
    l=pv.theme(n)
    banque=p.banque_orale(n,lecon=l)
    if not banque:return None
    return random.choice(banque)

def _audio(phrase, cle):
    phrase=html.escape(phrase,quote=True)
    components.html(f'''<button onclick="let s=new SpeechSynthesisUtterance(document.getElementById('v').textContent);s.lang='es-ES';s.rate=.83;speechSynthesis.cancel();speechSynthesis.speak(s)">▶ Écouter la phrase</button><span id="v" style="display:none">{phrase}</span>''',height=50)

def _phrase(n,cle):
    if cle not in st.session_state:st.session_state[cle]=_tirage(n)
    return st.session_state[cle]

def comprehension():
    st.subheader('👂 Compréhension orale — questions')
    st.caption('Écoute sans lire la phrase espagnole, puis choisis la traduction correcte parmi quatre propositions.')
    n=m.preference('niveau_suivi','A1');l=pv.theme(n)
    banque=p.banque_orale(n,lecon=l)
    if len(banque)<4:st.warning('Il faut au moins quatre phrases pour cet entraînement.');return
    cle='v17_comprehension_'+n+'_'+(l['id'] if l else '')
    if cle not in st.session_state:
        correct=random.choice(banque)
        autres=random.sample([x for x in banque if x[1]!=correct[1]],min(3,len(banque)-1))
        options=list(dict.fromkeys([correct[1]]+[x[1] for x in autres]))
        if len(options)<4:st.info('Traductions distinctes insuffisantes pour le QCM.');return
        random.shuffle(options);st.session_state[cle]=(correct,options)
    (es,fr),options=st.session_state[cle]
    _audio(es,cle)
    with st.form(cle+'_form'):
        choix=st.radio('Que signifie cette phrase ?',options,index=None)
        duree=st.number_input('Minutes de pratique',min_value=1,max_value=60,value=5)
        valider=st.form_submit_button('Corriger')
    if valider:
        if choix is None:st.warning('Choisis une réponse.');return
        st.session_state[cle+'_retour']=(choix==fr,es,fr,choix)
        m.enregistrer_session('Compréhension orale — questions',duree,n)
        del st.session_state[cle];st.rerun()
    retour=st.session_state.pop(cle+'_retour',None)
    if retour:
        st.success('Bonne réponse !' if retour[0] else 'À revoir.')
        st.write('**Espagnol :**',retour[1]);st.write('**Traduction :**',retour[2]);st.write('**Ta réponse :**',retour[3])

def expression():
    st.subheader('🎙️ Expression orale — prise de parole')
    st.caption('Lis la consigne française, prononce sa traduction en espagnol, puis compare avec le modèle. L’enregistrement peut être réécouté, mais la prononciation n’est pas notée automatiquement.')
    n=m.preference('niveau_suivi','A1');l=pv.theme(n)
    cle='v17_expression_'+n+'_'+(l['id'] if l else '')
    tirage=_phrase(n,cle)
    if not tirage:st.warning('Aucune phrase disponible pour ce thème.');return
    es,fr=tirage
    st.info('**À dire en espagnol :** '+fr)
    if hasattr(st,'audio_input'):
        son=st.audio_input('Enregistre ta réponse à voix haute',key=cle+'_audio')
        if son:st.audio(son)
    else:st.caption('Prononce la réponse à voix haute. Ton navigateur ne permet pas l’enregistrement ici.')
    with st.expander('Afficher la réponse modèle'):
        st.write('**Espagnol :**',es)
        _audio(es,cle)
    with st.form(cle+'_form'):
        minutes=st.number_input('Minutes réellement pratiquées',min_value=1,max_value=60,value=5)
        suivant=st.form_submit_button('Enregistrer le temps et passer à la phrase suivante')
    if suivant:
        m.enregistrer_session('Expression orale',minutes,n)
        del st.session_state[cle]
        st.rerun()
