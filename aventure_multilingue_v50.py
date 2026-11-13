"""V50: mini-aventure de survie, indépendante par langue et univers."""
import random
import html
import streamlit as st
from suivi_langues_v48 import enregistrer, enregistrer_phrases

LANGS={'es':('🇪🇸','Espagnol'),'en':('🇬🇧','Anglais'),'de':('🇩🇪','Allemand'),'it':('🇮🇹','Italien')}
# Chaque situation est une phrase française et ses quatre formulations naturelles.
WORLDS=[
('🚆','Transports',[
('Où est la gare ?', '¿Dónde está la estación de tren?', 'Where is the train station?', 'Wo ist der Bahnhof?', 'Dov’è la stazione?'),
('Un billet pour le centre-ville, s’il vous plaît.', 'Un billete al centro, por favor.', 'One ticket to the city centre, please.', 'Eine Fahrkarte ins Stadtzentrum, bitte.', 'Un biglietto per il centro, per favore.'),
('À quelle heure part le bus ?', '¿A qué hora sale el autobús?', 'What time does the bus leave?', 'Wann fährt der Bus ab?', 'A che ora parte l’autobus?'),
('Ce train va-t-il à la ville ?', '¿Este tren va a la ciudad?', 'Does this train go to the city?', 'Fährt dieser Zug in die Stadt?', 'Questo treno va in città?')]),
('🏙️','En ville',[
('Où sont les toilettes ?', '¿Dónde está el baño?', 'Where is the toilet?', 'Wo ist die Toilette?', 'Dov’è il bagno?'),
('Tournez à gauche.', 'Gire a la izquierda.', 'Turn left.', 'Biegen Sie links ab.', 'Giri a sinistra.'),
('C’est loin d’ici ?', '¿Está lejos de aquí?', 'Is it far from here?', 'Ist es weit von hier?', 'È lontano da qui?'),
('Où est l’ascenseur ?', '¿Dónde está el ascensor?', 'Where is the lift?', 'Wo ist der Aufzug?', 'Dov’è l’ascensore?')]),
('🌳','Campagne',[
('Où commence le sentier ?', '¿Dónde empieza el sendero?', 'Where does the trail start?', 'Wo beginnt der Wanderweg?', 'Dove inizia il sentiero?'),
('Est-ce qu’il va pleuvoir ?', '¿Va a llover?', 'Is it going to rain?', 'Wird es regnen?', 'Pioverà?'),
('Il neige.', 'Está nevando.', 'It is snowing.', 'Es schneit.', 'Sta nevicando.'),
('Où est le village ?', '¿Dónde está el pueblo?', 'Where is the village?', 'Wo ist das Dorf?', 'Dov’è il paese?')]),
('🏥','Santé',[
('J’ai besoin d’un médecin.', 'Necesito un médico.', 'I need a doctor.', 'Ich brauche einen Arzt.', 'Ho bisogno di un medico.'),
('Où est l’hôpital ?', '¿Dónde está el hospital?', 'Where is the hospital?', 'Wo ist das Krankenhaus?', 'Dov’è l’ospedale?'),
('J’ai mal à la tête.', 'Me duele la cabeza.', 'I have a headache.', 'Ich habe Kopfschmerzen.', 'Ho mal di testa.'),
('Appelez les secours, s’il vous plaît.', 'Llame a emergencias, por favor.', 'Please call emergency services.', 'Rufen Sie bitte den Rettungsdienst.', 'Chiami i soccorsi, per favore.')]),
('🍕','Restaurant',[
('Je voudrais une pizza, s’il vous plaît.', 'Quisiera una pizza, por favor.', 'I’d like a pizza, please.', 'Ich hätte gern eine Pizza, bitte.', 'Vorrei una pizza, per favore.'),
('Sans oignons, s’il vous plaît.', 'Sin cebolla, por favor.', 'No onions, please.', 'Ohne Zwiebeln, bitte.', 'Senza cipolla, per favore.'),
('L’addition, s’il vous plaît.', 'La cuenta, por favor.', 'The bill, please.', 'Die Rechnung, bitte.', 'Il conto, per favore.'),
('Je suis allergique aux noix.', 'Soy alérgico a los frutos secos.', 'I’m allergic to nuts.', 'Ich bin allergisch gegen Nüsse.', 'Sono allergico alla frutta a guscio.')]),
('☕','Café',[
('Un café au lait, s’il vous plaît.', 'Un café con leche, por favor.', 'A coffee with milk, please.', 'Einen Kaffee mit Milch, bitte.', 'Un caffè con latte, per favore.'),
('Je voudrais un thé.', 'Quisiera un té.', 'I’d like a tea.', 'Ich hätte gern einen Tee.', 'Vorrei un tè.'),
('À emporter, s’il vous plaît.', 'Para llevar, por favor.', 'To take away, please.', 'Zum Mitnehmen, bitte.', 'Da asporto, per favore.'),
('Combien ça coûte ?', '¿Cuánto cuesta?', 'How much is it?', 'Wie viel kostet das?', 'Quanto costa?')]),
('🌙','Bar et soirée',[
('Un verre d’eau, s’il vous plaît.', 'Un vaso de agua, por favor.', 'A glass of water, please.', 'Ein Glas Wasser, bitte.', 'Un bicchiere d’acqua, per favore.'),
('Où est la sortie ?', '¿Dónde está la salida?', 'Where is the exit?', 'Wo ist der Ausgang?', 'Dov’è l’uscita?'),
('Je vais rentrer à l’hôtel.', 'Voy a volver al hotel.', 'I’m going back to the hotel.', 'Ich gehe zurück zum Hotel.', 'Torno in albergo.'),
('Pouvez-vous appeler un taxi ?', '¿Puede llamar a un taxi?', 'Could you call a taxi?', 'Können Sie ein Taxi rufen?', 'Può chiamare un taxi?')]),
('🏨','Hôtel',[
('J’ai une réservation.', 'Tengo una reserva.', 'I have a reservation.', 'Ich habe eine Reservierung.', 'Ho una prenotazione.'),
('Où est ma chambre ?', '¿Dónde está mi habitación?', 'Where is my room?', 'Wo ist mein Zimmer?', 'Dov’è la mia camera?'),
('À quelle heure est le petit-déjeuner ?', '¿A qué hora es el desayuno?', 'What time is breakfast?', 'Wann gibt es Frühstück?', 'A che ora è la colazione?'),
('La clé ne fonctionne pas.', 'La llave no funciona.', 'The key doesn’t work.', 'Der Schlüssel funktioniert nicht.', 'La chiave non funziona.')]),
('🛒','Courses',[
('Combien coûte ce pain ?', '¿Cuánto cuesta este pan?', 'How much is this bread?', 'Wie viel kostet dieses Brot?', 'Quanto costa questo pane?'),
('Je voudrais deux pommes.', 'Quisiera dos manzanas.', 'I’d like two apples.', 'Ich hätte gern zwei Äpfel.', 'Vorrei due mele.'),
('Puis-je payer par carte ?', '¿Puedo pagar con tarjeta?', 'Can I pay by card?', 'Kann ich mit Karte zahlen?', 'Posso pagare con carta?'),
('Où est le supermarché ?', '¿Dónde está el supermercado?', 'Where is the supermarket?', 'Wo ist der Supermarkt?', 'Dov’è il supermercato?')]),
('🎭','Loisirs',[
('Où est le cinéma ?', '¿Dónde está el cine?', 'Where is the cinema?', 'Wo ist das Kino?', 'Dov’è il cinema?'),
('Deux billets, s’il vous plaît.', 'Dos entradas, por favor.', 'Two tickets, please.', 'Zwei Eintrittskarten, bitte.', 'Due biglietti, per favore.'),
('À quelle heure commence le spectacle ?', '¿A qué hora empieza el espectáculo?', 'What time does the show start?', 'Wann beginnt die Vorstellung?', 'A che ora inizia lo spettacolo?'),
('Où est le théâtre ?', '¿Dónde está el teatro?', 'Where is the theatre?', 'Wo ist das Theater?', 'Dov’è il teatro?')]),
('👨‍👩‍👧','Vie quotidienne',[
('Voici ma sœur.', 'Esta es mi hermana.', 'This is my sister.', 'Das ist meine Schwester.', 'Questa è mia sorella.'),
('Je travaille dans un bureau.', 'Trabajo en una oficina.', 'I work in an office.', 'Ich arbeite in einem Büro.', 'Lavoro in un ufficio.'),
('Je suis en vacances.', 'Estoy de vacaciones.', 'I’m on holiday.', 'Ich bin im Urlaub.', 'Sono in vacanza.'),
('Il fait beau aujourd’hui.', 'Hace buen tiempo hoy.', 'The weather is nice today.', 'Heute ist schönes Wetter.', 'Oggi fa bel tempo.')]),
('🆘','Imprévus',[
('J’ai perdu mon passeport.', 'He perdido mi pasaporte.', 'I’ve lost my passport.', 'Ich habe meinen Reisepass verloren.', 'Ho perso il passaporto.'),
('Je ne comprends pas.', 'No entiendo.', 'I don’t understand.', 'Ich verstehe nicht.', 'Non capisco.'),
('Pouvez-vous parler plus lentement ?', '¿Puede hablar más despacio?', 'Could you speak more slowly?', 'Können Sie bitte langsamer sprechen?', 'Può parlare più lentamente?'),
('Mon téléphone est déchargé.', 'Mi teléfono está descargado.', 'My phone battery is dead.', 'Mein Handy-Akku ist leer.', 'Il mio telefono è scarico.')])]

INDEX={'es':1,'en':2,'de':3,'it':4}

def page():
    st.markdown('''<style>
    .v51-banner{background:linear-gradient(110deg,#ffe6a9,#ffece1,#d6f4e8);border-radius:24px;padding:25px;text-align:center;margin-bottom:16px;color:#5a3826}
    .v51-banner h1{font-size:2.1rem;margin:0}.v51-banner p{margin:7px 0 0}
    .v51-story{background:#fff8e8;border:2px solid #f0d8a8;border-radius:20px;padding:20px;color:#533a2e;font-size:1.15rem}
    .v51-story small{display:block;color:#826e5c;margin-bottom:8px}
    </style><div class="v51-banner"><h1>🧭 Le grand voyage des langues</h1><p>Explore · rencontre · réponds · progresse</p></div>''',unsafe_allow_html=True)
    st.caption('12 univers · 4 langues · défis courts et renouvelables · une seule langue affichée à la fois')
    language=st.selectbox('🌍 Ma langue de jeu',list(LANGS),format_func=lambda x:' '.join(LANGS[x]),key='v50_lang')
    st.info('🎯 Choisis un lieu. Chaque univers est accessible immédiatement, sans mission à débloquer.')
    st.markdown('### 🗺️ Choisis ton prochain arrêt')
    cols=st.columns(3)
    for i,(emoji,name,_) in enumerate(WORLDS):
        with cols[i%3]:
            if st.button(f'{emoji}  {name}',key=f'v50_world_{i}',use_container_width=True):
                st.session_state.v50_world=i
                st.session_state.pop('v50_quiz',None)
                st.session_state.pop('v50_result',None)
                st.rerun()
    if 'v50_world' not in st.session_state:
        st.session_state.v50_world=0
    i=st.session_state.v50_world
    emoji,name,phrases=WORLDS[i]
    st.divider()
    st.subheader(f'{emoji} {name}')
    tabs=st.tabs(['🎭 Mini-aventure','📖 Découvrir','🎲 Mini-défi','🆘 Phrases express'])
    with tabs[0]:
        _story(language,i,phrases)
    with tabs[1]:
        st.caption('Lis les phrases, puis entraîne-toi avec un défi.')
        for french,*translations in phrases:
            st.markdown(f'**{translations[INDEX[language]-1]}**')
            st.caption(f'🇫🇷 {french}')
    with tabs[2]:
        st.caption('4 questions différentes par série, choix mélangés. Tu peux rejouer avec une nouvelle série.')
        quizkey=(language,i)
        if st.session_state.get('v50_quiz_key')!=quizkey or 'v50_quiz' not in st.session_state:
            st.session_state.v50_quiz_key=quizkey
            st.session_state.v50_quiz=_new_quiz(phrases,language)
            st.session_state.pop('v50_result',None)
        if st.button('🔄 Nouveau défi',key='v50_new'):
            st.session_state.v50_quiz=_new_quiz(phrases,language)
            st.session_state.pop('v50_result',None)
            st.rerun()
        with st.form(f'v50_form_{language}_{i}'):
            chosen=[]
            for j,q in enumerate(st.session_state.v50_quiz):
                chosen.append(st.radio(f'{j+1}. {q[0]}',q[1],index=None,key=f'v50_answer_{language}_{i}_{st.session_state.v50_quiz_id}_{j}'))
            submitted=st.form_submit_button('✨ Corriger mon défi',type='primary')
        if submitted:
            correct=[ans==q[2] for ans,q in zip(chosen,st.session_state.v50_quiz)]
            score=sum(correct)
            st.session_state.v50_result=(score,correct)
            activity=f'v50:{i}:{language}'
            enregistrer(language,activity,score,len(correct))
            # La reconnaissance est suivie par phrase, sans prétendre évaluer la production orale.
            pairs=[(p[INDEX[language]],p[0]) for p in phrases]
            by_id={q[3]:ans for q,ans in zip(st.session_state.v50_quiz,chosen)}
            enregistrer_phrases(language,activity,pairs,[by_id.get(k) for k in range(len(phrases))])
        if 'v50_result' in st.session_state:
            score,correct=st.session_state.v50_result
            (st.success if score==4 else st.info)(f'⭐ {score}/4 — '+('Bravo, univers réussi !' if score==4 else 'Continue, tu progresses !'))
            for q,ok in zip(st.session_state.v50_quiz,correct):
                st.write(('✅ ' if ok else '💡 ')+q[0]+' → '+q[2])
    with tabs[3]:
        st.caption('À consulter directement pendant ton voyage, sans évaluation.')
        for french,*translations in phrases:
            with st.container(border=True):
                st.markdown(f'### {translations[INDEX[language]-1]}')
                st.write(f'🇫🇷 {french}')
    st.caption('Les résultats alimentent ton suivi par langue. Ces QCM évaluent la reconnaissance de phrases, pas à eux seuls un niveau CECRL.')

def _new_quiz(phrases,language):
    idx=INDEX[language]
    indices=list(range(len(phrases)))
    random.shuffle(indices)
    result=[]
    for n in indices:
        correct=phrases[n][0]
        alternatives=[p[0] for k,p in enumerate(phrases) if k!=n]
        options=[correct]+random.sample(alternatives,2)
        random.shuffle(options)
        result.append((phrases[n][idx],options,correct,n))
    st.session_state.v50_quiz_id=st.session_state.get('v50_quiz_id',0)+1
    return result


# V51 : parcours narratif de trois étapes par univers, avec variantes
# L'activité est évaluée en compréhension écrite uniquement.
def _story(language, world, phrases):
    key=f'v51_story_{language}_{world}'
    state=st.session_state.get(key)
    if state is None:
        state={'step':0,'score':0,'order':random.sample(range(len(phrases)),3),'answers':[],'finished':False}
        st.session_state[key]=state
    st.caption('🎬 Trois scènes courtes · réponses variées · sans pénalité')
    if st.button('🔀 Nouvelle histoire',key=f'{key}_restart'):
        st.session_state[key]={'step':0,'score':0,'order':random.sample(range(len(phrases)),3),'answers':[],'finished':False}
        st.rerun()
    if state['finished']:
        st.success(f"🏆 Histoire terminée : {state['score']}/3 scènes réussies !")
        st.write('Tu as terminé cette aventure. Rejoue pour rencontrer d’autres situations du même lieu.')
        return
    step=state['step']
    idx=state['order'][step]
    phrase=phrases[idx]
    translated=phrase[INDEX[language]]
    french=phrase[0]
    # Scène contextualisée sans prétendre à une conversation générative.
    roles=['🧑‍💼 Une personne te parle','🧑‍🍳 Tu dois répondre','🧳 Un petit imprévu arrive']
    st.progress(step/3,text=f'Scène {step+1} sur 3')
    st.markdown(f'<div class="v51-story"><small>{roles[step]}</small>💬 <strong>{html.escape(translated)}</strong></div>',unsafe_allow_html=True)
    st.write('**Que signifie cette phrase ?**')
    alternatives=[p[0] for j,p in enumerate(phrases) if j!=idx]
    options=[french]+random.Random(f'{language}-{world}-{idx}-{step}').sample(alternatives,2)
    random.Random(f'order-{language}-{world}-{idx}-{step}').shuffle(options)
    selection=st.radio('Choisis la bonne interprétation :',options,index=None,key=f'{key}_answer_{step}',label_visibility='collapsed')
    feedback_key=f'{key}_feedback_{step}'
    if st.button('✨ Vérifier ma réponse',disabled=selection is None,key=f'{key}_verify_{step}'):
        st.session_state[feedback_key]=selection==french
        state['answers'].append(selection)
        if selection==french: state['score']+=1
        st.rerun()
    if feedback_key in st.session_state:
        ok=st.session_state[feedback_key]
        if ok: st.success('🌟 Bravo ! Tu as compris la situation.')
        else: st.info(f'💡 La bonne interprétation est : {french}')
        if st.button('➡️ Continuer l’aventure' if step<2 else '🏁 Terminer mon aventure',key=f'{key}_next_{step}',type='primary'):
            if step==2:
                state['finished']=True
                enregistrer(language,f'v51:histoire:{world}',state['score'],3)
                # Les réponses sont liées aux phrases exactes de la scène.
                pairs=[(phrases[n][INDEX[language]],phrases[n][0]) for n in state['order']]
                enregistrer_phrases(language,f'v51:histoire:{world}',pairs,state['answers'])
            else:
                state['step']+=1
            st.session_state.pop(feedback_key,None)
            st.rerun()
