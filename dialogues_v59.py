"""V61: contextual, progressive written travel conversations (four languages)."""
import random
import streamlit as st
from aventure_multilingue_v50 import INDEX, WORLDS
from suivi_langues_v48 import enregistrer, enregistrer_phrases
from villes_interactives_v52 import _history, _save_history, _stage

PERSONAS={0:'🚉 Le contrôleur',1:'🧭 Une habitante',2:'🥾 Un guide',3:'💊 La pharmacienne',4:'👨‍🍳 Le serveur',5:'☕ La barista',6:'🎶 Le barman',7:'🛎️ La réceptionniste',8:'🛍️ La vendeuse',9:'🎟️ La billetterie',10:'🏠 Un voisin',11:'🆘 Une personne serviable'}
# Each scene asks for a contextually appropriate utterance. Ordering is intentional.
ORDERS={4:[0,1,3,2],5:[0,1,2,3],7:[0,1,3,2],0:[0,1,2,3],8:[0,1,2,3]}
CONTEXT={
4:['Tu arrives à la pizzeria. Le serveur attend ta commande.','Le serveur demande si tu veux modifier la pizza.','Le serveur vérifie si tu as une allergie alimentaire.','Le repas est terminé. Tu souhaites payer.'],
5:['Tu arrives au café et souhaites commander.','La boisson choisie est indisponible : tu prends autre chose.','La barista demande si tu restes sur place. Tu veux emporter ta boisson.','La barista annonce le total : tu demandes le prix.'],
7:['Tu arrives à la réception pour récupérer ta chambre.','Tu veux savoir où se trouve ta chambre.','La clé ne marche pas : signale-le.','Tu veux connaître l’heure du petit-déjeuner.'],
0:['Tu arrives à la gare et cherches ton chemin.','Tu veux acheter un billet pour le centre-ville.','Le départ approche : demande l’horaire du bus.','Tu vérifies que tu prends le bon train.'],
8:['Tu regardes les produits au marché et demandes le prix du pain.','Tu commandes des fruits.','Tu arrives à la caisse et souhaites payer par carte.','Tu veux savoir où trouver un supermarché.']}
REPLIES={
'es':['¡Muy bien!','Entiendo.','Perfecto, gracias.','De acuerdo.'],
'en':['Very good!','I understand.','Perfect, thank you.','All right.'],
'de':['Sehr gut!','Verstanden.','Perfekt, danke.','In Ordnung.'],
'it':['Molto bene!','Capisco.','Perfetto, grazie.','Va bene.']}
ASK={
'es':['¡Hola! ¿En qué puedo ayudarte?','¿Puedes decirme qué necesitas?','¿Algo más?','¿Cómo quieres continuar?'],
'en':['Hello! How can I help?','Could you tell me what you need?','Anything else?','How would you like to continue?'],
'de':['Hallo! Wie kann ich helfen?','Kannst du sagen, was du brauchst?','Noch etwas?','Wie möchtest du weitermachen?'],
'it':['Ciao! Come posso aiutarti?','Puoi dirmi di cosa hai bisogno?','Altro?','Come vuoi continuare?']}
REPAIR={
'es':'Perdona, no entiendo. ¿Puedes repetirlo?',
'en':'Sorry, I don’t understand. Can you repeat that?',
'de':'Entschuldigung, ich verstehe nicht. Kannst du das wiederholen?',
'it':'Scusa, non capisco. Puoi ripetere?'}

def _new():
    return {'step':0,'score':0,'answers':[],'variant':random.randrange(1_000_000),'feedback':None,'done':False}

def play(lang,ci,world,phrases,city):
    key=f'v61_{lang}_{ci}_{world}'
    if key not in st.session_state: st.session_state[key]=_new()
    s=st.session_state[key]
    stage=_stage(_history(lang,ci,world))
    persona=PERSONAS.get(world,'🧑 Une personne du quartier')
    st.markdown('<style>@media(max-width:640px){div[data-testid="stRadio"] label{padding:.3rem 0}div[data-testid="stVerticalBlock"]{gap:.45rem}}</style>',unsafe_allow_html=True)
    a,b=st.columns([3,1])
    with a: st.caption(f'🎭 {city} · {persona} · '+{1:'🌱 Découverte',2:'🧭 Autonomie',3:'🎲 Imprévu'}[stage])
    with b:
        if st.button('🔄 Rejouer',key=key+'_restart',use_container_width=True):
            st.session_state[key]=_new();st.rerun()
    if s['done']:
        st.success(f'🏆 Mission terminée : {s["score"]}/4 réponses adaptées !')
        st.caption('Résultat de compréhension écrite, sans évaluation de l’expression orale.')
        return
    step=s['step']; order=ORDERS.get(world,[0,1,2,3]); idx=order[step]
    row=phrases[idx]; target=row[INDEX[lang]]
    contexts=CONTEXT.get(world,[
        'Tu rencontres un habitant et cherches une information.',
        'La situation avance : tu dois exprimer une nouvelle demande.',
        'Un détail inattendu apparaît : précise ton besoin.',
        'La conversation touche à sa fin : trouve une réponse utile.'])
    # At higher difficulty, an unexpected change is announced, without changing the correct intent.
    twist=(stage==3 and step==2)
    st.progress((step+1)/4,text=f'🎬 Acte {step+1}/4')
    st.markdown(f'**{persona} :** « {ASK[lang][step]} »')
    st.write(('🎲 **Imprévu !** ' if twist else '')+contexts[step])
    if s['answers']:
        prev=s['answers'][-1]
        st.markdown('💬 **'+(REPLIES[lang][(step-1)%4] if prev[3] else REPAIR[lang])+'**')
        if not prev[3]: st.caption('Le personnage n’a pas compris ta dernière réponse. Il t’a aidé à reformuler.')
    if stage==1: st.caption('🇫🇷 Ta mission : '+row[0])
    else: st.write('🎯 **Ta mission :** '+row[0])
    rng=random.Random(f'{lang}:{ci}:{world}:{s["variant"]}:{step}')
    other=[r[INDEX[lang]] for j,r in enumerate(phrases) if j!=idx]
    # Distractors are plausible language utterances but wrong for the current moment.
    options=[target]+rng.sample(other,k=min(3 if stage>=2 else 2,len(other)))
    rng.shuffle(options)
    if s['feedback'] is None:
        choice=st.radio('Que dis-tu ?',options,index=None,key=f'{key}_{s["variant"]}_{step}')
        if st.button('💬 Parler au personnage',disabled=choice is None,key=f'{key}_submit_{step}',type='primary',use_container_width=True):
            good=choice==target
            s['answers'].append((target,row[0],choice,good));s['score']+=int(good);s['feedback']=good
            st.rerun()
    else:
        if s['feedback']:
            st.success('✨ '+REPLIES[lang][step]+' — Le personnage a compris ta demande.')
        else:
            st.warning('💬 '+REPAIR[lang])
            st.write('💡 **Formulation utile :** '+target)
            st.caption('🇫🇷 '+row[0])
        if st.button('➡️ Continuer la conversation' if step<3 else '🏁 Terminer la mission',key=f'{key}_next_{step}',type='primary',use_container_width=True):
            s['feedback']=None
            if step==3:
                s['done']=True
                activity=f'v61:ville:{lang}:{ci}:lieu:{world}'
                enregistrer(lang,activity,s['score'],4)
                # Existing progression threshold is 2/3; map 4-step score to a 3-point scale.
                _save_history(lang,ci,world,round(s['score']*3/4))
                enregistrer_phrases(lang,activity,[(a,b) for a,b,_,_ in s['answers']],[c for _,_,c,_ in s['answers']])
            else:s['step']+=1
            st.rerun()
