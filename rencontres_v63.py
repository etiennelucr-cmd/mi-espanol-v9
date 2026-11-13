"""V63 : simulation sociale légère, locale, sans service IA externe."""
import json, os, re, uuid
from pathlib import Path
import streamlit as st
from villes_interactives_v52 import CITIES

PEOPLE={
 'es': [('Lucía','👩🏻',0,'chat','Mimi'),('Carlos','👨🏽',0,'dog','Max'),('Elena','👩🏽',1,'cat','Nube'),('Pablo','🧑🏼',1,'dog','Luna')],
 'en': [('Oliver','🧑🏻',0,'dog','Buddy'),('Emily','👩🏽',1,'cat','Mochi'),('Jack','👨🏼',2,'dog','Archie')],
 'de': [('Lena','👩🏼',0,'cat','Minka'),('Felix','👨🏻',1,'dog','Bello'),('Mia','👩🏽',2,'dog','Lotte')],
 'it': [('Giulia','👩🏻',0,'cat','Luna'),('Marco','👨🏽',1,'dog','Pippo'),('Sofia','👩🏼',2,'cat','Micio')],
}
# Discover actual language keys from existing CITIES without changing the game's language registry.
def language_key(value):
    if value in PEOPLE:return value
    t=str(value).lower()
    for k, fragments in {'es':('esp','span','españ'),'en':('ang','engl','english'),'de':('all','deut','germ'),'it':('ita','ital')}.items():
        if any(f in t for f in fragments):return k
    return 'es'

WORDS={
 'es':{'hello':'¡Hola! ¿Cómo estás hoy?','help':'¿Quieres hablar de ello?','invite':'¡Te invito a una fiesta este fin de semana!','trip':'¿Quieres visitarme en {city}?','pet':'Mi mascota {pet} está muy contenta.','thanks':'¡Gracias por escucharme!','fallback':'¡Qué interesante! Cuéntame más.','conflict':'Estoy enfadado/a con un amigo. ¿Puedes ayudarnos?','family':'Mi familia está bien. Tenemos muchas cosas que hacer.','ask':'¿Qué hiciste ayer?'},
 'en':{'hello':'Hi! How are you today?','help':'Would you like to talk about it?','invite':'I am having a party this weekend!','trip':'Would you like to visit me in {city}?','pet':'My pet {pet} is very happy.','thanks':'Thanks for listening!','fallback':'That sounds interesting! Tell me more.','conflict':'I argued with a friend. Can you help us?','family':'My family is doing well. We have lots to do.','ask':'What did you do yesterday?'},
 'de':{'hello':'Hallo! Wie geht es dir heute?','help':'Möchtest du darüber sprechen?','invite':'Ich mache am Wochenende eine Party!','trip':'Möchtest du mich in {city} besuchen?','pet':'Mein Haustier {pet} ist sehr glücklich.','thanks':'Danke fürs Zuhören!','fallback':'Das klingt interessant! Erzähl mir mehr.','conflict':'Ich habe mich mit einem Freund gestritten. Kannst du helfen?','family':'Meiner Familie geht es gut. Wir haben viel zu tun.','ask':'Was hast du gestern gemacht?'},
 'it':{'hello':'Ciao! Come stai oggi?','help':'Vuoi parlarne?','invite':'Organizzo una festa questo fine settimana!','trip':'Vuoi venire a trovarmi a {city}?','pet':'Il mio animale {pet} è molto felice.','thanks':'Grazie per avermi ascoltato!','fallback':'Che interessante! Raccontami di più.','conflict':'Ho litigato con un amico. Puoi aiutarci?','family':'La mia famiglia sta bene. Abbiamo tante cose da fare.','ask':'Che cosa hai fatto ieri?'},
}
GUIDES={'es':['¿Cómo estás?','¿Qué ha pasado?','¿Puedo ayudarte?','¿Vamos a tomar un café?'], 'en':['How are you?','What happened?','Can I help you?','Shall we get coffee?'], 'de':['Wie geht es dir?','Was ist passiert?','Kann ich dir helfen?','Gehen wir ins Café?'], 'it':['Come stai?','Che cosa è successo?','Posso aiutarti?','Andiamo al bar?']}

def store():
    # Session isolation: no shared anonymous profile, and no assumption of durable cloud storage.
    if 'v63_world' not in st.session_state: st.session_state.v63_world={'city':{},'friends':{},'log':{},'events':[],'xp':{}}
    return st.session_state.v63_world

def record(world,lang,name,speaker,text):
    key=f'{lang}:{name}'
    world['log'].setdefault(key,[]).append({'who':speaker,'text':text})
    world['log'][key]=world['log'][key][-40:]

def reply(lang,text,person,world):
    lower=text.lower(); d=WORDS[lang]; name,emoji,home,pettype,pet=person
    if any(x in lower for x in ['aide','help','ayud','helf','aiut','désolé','sorry','perdón','scusa']):
        world['friends'][f'{lang}:{name}']=min(10,world['friends'].get(f'{lang}:{name}',2)+1)
        return d['thanks']
    if any(x in lower for x in ['perro','chien','dog','hund','cane','chat','cat','katze','gatto','animal']):return d['pet'].format(pet=pet)
    if any(x in lower for x in ['famil','enfant','child','kind','bambin']):return d['family']
    if any(x in lower for x in ['voyag','travel','viaj','reis','viagg','visit']):return d['trip'].format(city=CITIES[next(k for k in CITIES if language_key(k)==lang)][(home+1)%3][0])
    if any(x in lower for x in ['disput','argu','litig','streit','enfad','angry']):return d['conflict']
    if any(x in lower for x in ['fiest','party','soirée','fest','festa']):return d['invite']
    if '?' in text:return d['ask']
    return d['fallback']

def page():
    st.markdown('## 💬 Mes rencontres')
    st.caption('🏡 Des amis, des animaux, des soirées et des voyages. Conversations dans la langue choisie, aides facultatives.')
    world=store(); keys=list(CITIES)
    default=next((i for i,k in enumerate(keys) if k==st.session_state.get('v57_lang')),0)
    lang_label=st.selectbox('🌍 Langue de mes rencontres',keys,index=default,key='v63_lang')
    lang=language_key(lang_label)
    cities=CITIES[lang_label]
    current=world['city'].setdefault(lang,st.session_state.get('v57_city',0) if lang_label==st.session_state.get('v57_lang') else 0)
    st.info(f'🏠 Tu vis à **{cities[current][0]}** · Tes amis restent en contact quand tu voyages.')
    left,right=st.columns(2)
    with left:
        city=st.selectbox('🚆 Destination',range(3),index=current,format_func=lambda i:cities[i][0],key=f'v63_dest_{lang}')
        if st.button('🧳 Voyager ici',use_container_width=True,key=f'v63_visit_{lang}'):
            world['city'][lang]=city
            st.session_state.v57_lang=lang_label
            st.session_state.v57_city=city
            st.session_state.pop('v57_place',None)
            st.success('Voyage effectué ! Tu peux aussi explorer cette ville sur la carte.')
    with right:
        if st.button('🏡 Déménager dans cette ville',use_container_width=True,key=f'v63_move_{lang}'):
            world['city'][lang]=city
            st.session_state.v57_lang=lang_label
            st.session_state.v57_city=city
            st.session_state.pop('v57_place',None)
            st.success(f'Ton nouveau chez-toi est à {cities[city][0]} !')
    st.markdown('### 👥 Mes amis')
    people=PEOPLE[lang]
    cols=st.columns(min(len(people),4))
    for i,(name,emoji,home,animal,pet) in enumerate(people):
        with cols[i]:
            score=world['friends'].get(f'{lang}:{name}',2)
            st.markdown(f'### {emoji} {name}')
            st.caption(f'📍 {cities[home][0]} · ❤️ {score}/10 · 🐾 {pet}')
    selected=st.selectbox('💬 Parler à',range(len(people)),format_func=lambda i:people[i][0],key=f'v63_person_{lang}')
    person=people[selected];name=person[0];key=f'{lang}:{name}'
    if not world['log'].get(key):record(world,lang,name,name,WORDS[lang]['hello'])
    for item in world['log'][key][-12:]:
        with st.chat_message('user' if item['who']=='you' else 'assistant'):
            st.write(item['text'])
    with st.expander('💡 Je bloque : réponses guidées et traductions'):
        st.caption('Les suggestions sont dans la langue cible. Utilise-les ou écris librement.')
        for i,phrase in enumerate(GUIDES[lang]):
            if st.button(phrase,key=f'v63_guide_{lang}_{selected}_{i}',use_container_width=True):
                record(world,lang,name,'you',phrase)
                record(world,lang,name,name,reply(lang,phrase,person,world))
                st.rerun()
    msg=st.chat_input('Écris librement dans la langue que tu apprends…',key=f'v63_chat_{lang}_{selected}')
    if msg and msg.strip():
        record(world,lang,name,'you',msg.strip()[:500])
        record(world,lang,name,name,reply(lang,msg.strip(),person,world))
        st.rerun()
    st.markdown('### 🎉 Des événements qui font vivre la ville')
    event=st.selectbox('Choisis une aventure', ['🎉 Soirée entre amis','🤝 Réconcilier deux amis','🐶 Promenade avec les animaux','👨‍👩‍👧 Rencontre en famille','🚆 Invitation dans une autre ville'],key=f'v63_event_{lang}')
    if st.button('▶️ Vivre cet événement',key=f'v63_start_{lang}',use_container_width=True):
        prompts=['invite','conflict','pet','family','trip'];idx=['🎉 Soirée entre amis','🤝 Réconcilier deux amis','🐶 Promenade avec les animaux','👨‍👩‍👧 Rencontre en famille','🚆 Invitation dans une autre ville'].index(event)
        message=WORDS[lang][prompts[idx]]
        if idx==4:message=message.format(city=cities[(current+1)%3][0])
        elif idx==2:message=message.format(pet=person[4])
        record(world,lang,name,name,message)
        world['events'].append({'lang':lang,'event':event,'friend':name})
        st.success('Événement lancé ! Reprends la conversation avec ton ami.')
    st.caption('ℹ️ V63 : dialogues scénarisés à reconnaissance simple, pas une IA générative. Les souvenirs sont conservés pendant cette session. Sur Streamlit Cloud, une base externe sera nécessaire pour les conserver après redémarrage.')
