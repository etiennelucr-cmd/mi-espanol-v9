"""V59: narrative choices with reactive characters; written comprehension only."""
import random
import streamlit as st
from aventure_multilingue_v50 import INDEX
from suivi_langues_v48 import enregistrer, enregistrer_phrases
from villes_interactives_v52 import _history, _save_history, _stage

PERSONAS={0:'🚉 Le contrôleur',1:'🧭 Une habitante',2:'🥾 Un guide',3:'💊 La pharmacienne',4:'🍕 Le serveur',5:'☕ La barista',6:'🎶 Le barman',7:'🛎️ La réceptionniste',8:'🛍️ La vendeuse',9:'🎟️ La billetterie',10:'🏠 Un voisin',11:'🆘 Une personne serviable'}
EVENTS={
 4:[('Le serveur te propose la carte.','Tu souhaites commander.'),('Le plat choisi est indisponible.','Tu dois trouver une autre formule.'),('Le serveur apporte l’addition.','Tu souhaites payer.')],
 5:[('La barista t’accueille.','Tu souhaites commander.'),('Il n’y a plus de place en terrasse.','Tu adaptes ta demande.'),('La barista te demande de régler.','Tu termines ta visite.')],
 7:[('Tu arrives à la réception.','Tu demandes ta chambre.'),('La clé ne fonctionne pas.','Tu expliques le problème.'),('Tu veux trouver l’ascenseur.','Tu demandes ton chemin.')],
 0:[('Tu arrives à la gare.','Tu cherches ton train.'),('Le quai a changé.','Tu demandes une précision.'),('Tu souhaites vérifier l’horaire.','Tu termines ton trajet.')],
}
FALLBACK=[('Tu rencontres un habitant.','Tu engages la conversation.'),('Une information manque.','Tu demandes une précision.'),('La situation change.','Tu trouves une solution.')]

def play(lang, ci, world, phrases, city):
    key=f'v59_{lang}_{ci}_{world}'
    if key not in st.session_state:
        st.session_state[key]={'step':0,'score':0,'answers':[],'variant':random.randrange(100000),'feedback':None,'done':False}
    s=st.session_state[key]
    history=_history(lang,ci,world)
    stage=_stage(history)
    st.info(f'🎭 Histoire interactive · {city} · Niveau : '+{1:'🌱 Découverte',2:'🧭 Autonomie',3:'🎲 Imprévu'}[stage])
    if st.button('🔄 Nouvelle histoire',key=key+'_restart'):
        st.session_state[key]={'step':0,'score':0,'answers':[],'variant':random.randrange(100000),'feedback':None,'done':False}
        st.rerun()
    if s['done']:
        st.success(f'🏆 Mission terminée : {s["score"]}/3 réponses adaptées !')
        st.caption('Cette mission mesure la reconnaissance de phrases écrites, pas une conversation orale libre.')
        return
    step=s['step']
    rng=random.Random(f'{lang}-{ci}-{world}-{s["variant"]}-{step}')
    row_idx=(s['variant']+step*3+ci+world)%len(phrases)
    if s['answers'] and not s['answers'][-1][3]:row_idx=(row_idx+1)%len(phrases)
    row=phrases[row_idx]
    target=row[INDEX[lang]]
    event=EVENTS.get(world,FALLBACK)[step]
    if stage==3 and step==1:
        event=('🎲 Imprévu ! Le personnage ne comprend pas immédiatement.','Tu reformules avec une phrase utile.')
    st.progress(step/3,text=f'Acte {step+1}/3')
    st.markdown(f'### {PERSONAS.get(world,"🧑 Un habitant")}')
    st.write('**'+event[0]+'** '+event[1])
    if s['answers']:
        st.caption('↪️ '+('Le personnage sourit et poursuit la discussion.' if s['answers'][-1][3] else 'Le personnage te demande de reformuler ; la scène s’adapte.'))
    st.write(f'🎯 **Ton intention :** {row[0]}')
    distractors=list(dict.fromkeys(r[INDEX[lang]] for i,r in enumerate(phrases) if i!=row_idx and r[INDEX[lang]]!=target))
    options=[target]+rng.sample(distractors,min(3 if stage==3 else 2,len(distractors)))
    rng.shuffle(options)
    if s['feedback'] is None:
        choice=st.radio('Que réponds-tu ?',options,index=None,key=f'{key}_{s["variant"]}_{step}')
        if st.button('💬 Répondre',disabled=choice is None,key=f'{key}_submit_{step}',type='primary'):
            good=choice==target
            s['answers'].append((target,row[0],choice,good))
            s['score']+=int(good)
            s['feedback']=good
            st.rerun()
    else:
        if s['feedback']:st.success('✨ Bonne réaction ! Le personnage te comprend.')
        else:
            st.warning('Le personnage hésite. Essaie de retenir cette formulation :')
            st.write('**'+target+'** — '+row[0])
        if st.button('➡️ Scène suivante' if step<2 else '🏁 Finir la mission',key=f'{key}_continue_{step}',type='primary'):
            s['feedback']=None
            if step==2:
                s['done']=True
                activity=f'v59:ville:{lang}:{ci}:lieu:{world}'
                enregistrer(lang,activity,s['score'],3)
                _save_history(lang,ci,world,s['score'])
                enregistrer_phrases(lang,activity,[(a,b) for a,b,_,_ in s['answers']],[c for _,_,c,_ in s['answers']])
            else:s['step']+=1
            st.rerun()
