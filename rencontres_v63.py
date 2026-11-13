"""V63 : simulation sociale légère, locale, sans service IA externe."""
import json, os, re, uuid, hashlib, html
from datetime import date, timedelta
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

# Daily events are deterministic per session and date: no rerun duplicates.
PERSONALITY={'Lucía':('attentionnée',2),'Carlos':('spontané',1),'Elena':('réservée',5),'Pablo':('drôle',3),'Oliver':('sociable',2),'Emily':('réservée',4),'Jack':('spontané',2),'Lena':('attentionnée',3),'Felix':('spontané',2),'Mia':('réservée',4),'Giulia':('sociable',2),'Marco':('drôle',3),'Sofia':('attentionnée',3)}
EVENT_NAMES=['🎉 Soirée entre amis','🤝 Réconcilier deux amis','🐶 Promenade avec les animaux','👨‍👩‍👧 Rencontre en famille','🚆 Invitation dans une autre ville']

def stable_number(*values):
    return int(hashlib.sha256('|'.join(map(str,values)).encode()).hexdigest()[:10],16)

def daily_update(world,lang,people,cities):
    today=date.today()
    days=world.setdefault('last_social_day',{})
    # A first visit starts today; returning after a date change advances the world.
    previous=date.fromisoformat(days.get(lang,today.isoformat()))
    if previous>today: previous=today
    gap=min((today-previous).days,14)
    for delta in range(1,gap+1):
        day=previous+timedelta(days=delta)
        for person in people:
            name=person[0]; key=f'{lang}:{name}'
            log=world['log'].get(key,[])
            if not log: continue
            last=log[-1]
            personality,wait=PERSONALITY.get(name,('sociable',3))
            # One gentle follow-up at most per unanswered conversation, not daily spam.
            if last['who']!='you' and not any(x.get('followup_for')==last.get('id') for x in log):
                last_date=date.fromisoformat(last.get('day',previous.isoformat()))
                if (day-last_date).days>=wait and stable_number(lang,name,day,'follow')%5<3:
                    line={'es':'¡Hola! Espero que estés bien 😊','en':'Hi! Hope you are doing well 😊','de':'Hallo! Hoffentlich geht es dir gut 😊','it':'Ciao! Spero che tu stia bene 😊'}[lang]
                    if personality=='réservée': line={'es':'¡Hola! ¿Todo bien?','en':'Hi! Everything okay?','de':'Hallo! Alles gut?','it':'Ciao! Tutto bene?'}[lang]
                    record(world,lang,name,name,line)
                    world['log'][key][-1].update(day=day.isoformat(),followup_for=last.get('id','initial'))
        # Some days are quiet. Events can appear without manual selection.
    days[lang]=today.isoformat()
    events=[]
    current=world['city'].get(lang,0)
    for offset in range(5):
        day=today+timedelta(days=offset)
        seed=stable_number(lang,cities[current][0],day.isoformat())
        if seed%5 in (0,1):continue
        idx=(seed//5)%len(EVENT_NAMES)
        friend=people[(seed//31)%len(people)][0]
        events.append({'id':f'{lang}:{current}:{day}:{idx}','date':day,'name':EVENT_NAMES[idx],'friend':friend,'idx':idx})
    return events

def record(world,lang,name,speaker,text):
    key=f'{lang}:{name}'
    world['log'].setdefault(key,[]).append({'who':speaker,'text':text,'day':date.today().isoformat(),'id':uuid.uuid4().hex[:10]})
    world['log'][key]=world['log'][key][-60:]


# Posts are generated deterministically for each city and date; comments remain
# interactive and are shared with the session's story state.
POST_LINES={
'es': [('¡Qué tarde tan bonita! ☀️','¡Qué bien!','¿Dónde estás?'),('Hoy salgo con mis amigos. ¿Quién viene? 🎉','¡Yo voy!','¿A qué hora?'),('Paseo con mi mascota 🐾','¡Qué bonito!','¿Cómo se llama?')],
'en': [('What a lovely afternoon! ☀️','Looks great!','Where are you?'),('I am going out with friends tonight! 🎉','Count me in!','What time?'),('A walk with my pet 🐾','So cute!','What is its name?')],
'de': [('Was für ein schöner Nachmittag! ☀️','Wie schön!','Wo bist du?'),('Heute treffe ich meine Freunde! 🎉','Ich komme!','Um wie viel Uhr?'),('Ein Spaziergang mit meinem Haustier 🐾','Wie süß!','Wie heißt es?')],
'it': [('Che bel pomeriggio! ☀️','Che bello!','Dove sei?'),('Stasera esco con gli amici! 🎉','Vengo anch’io!','A che ora?'),('Una passeggiata con il mio animale 🐾','Che carino!','Come si chiama?')]
}
POST_B1={
'es':[ 'Después de una semana intensa, necesitaba un poco de aire. ¿Vosotros cómo os relajáis?','Estoy pensando en organizar una cena improvisada. ¿Alguna sugerencia?','Hoy mi mascota me ha hecho reír muchísimo. ¡Menuda aventura!'],
'en':[ 'After a hectic week, I really needed some fresh air. How do you unwind?','I am thinking of hosting an impromptu dinner. Any suggestions?','My pet made me laugh so much today. What an adventure!'],
'de':[ 'Nach einer anstrengenden Woche brauchte ich frische Luft. Wie entspannt ihr euch?','Ich überlege, spontan ein Abendessen zu organisieren. Habt ihr Ideen?','Mein Haustier hat mich heute wirklich zum Lachen gebracht!'],
'it':[ 'Dopo una settimana intensa, avevo proprio bisogno di uscire. Voi come vi rilassate?','Sto pensando di organizzare una cena improvvisata. Avete suggerimenti?','Oggi il mio animale mi ha fatto ridere tantissimo!']
}

def social_band(lang):
    # This is a presentation band, not a CEFR certification. Do not derive
    # a level from repeated multiple-choice successes.
    from suivi_langues_v48 import lire
    rows=lire(lang)
    distinct=sum(1 for activity,score,total,*_ in rows if total and score/total>=0.8)
    free=st.session_state.get('v65_free_messages',{}).get(lang,0)
    if distinct>=12 and free>=12:return 'B1',False
    if distinct>=5 and free>=4:return 'A2',False
    return 'A1',True

def social_post(world,lang,people,city,day,band):
    seed=stable_number(lang,city,day.isoformat(),'feed')
    person=people[seed%len(people)]
    topic=(seed//7)%3
    base=POST_LINES[lang][topic]
    text=POST_B1[lang][topic] if band=='B1' else base[0]
    if band=='A2' and topic==1:text=WORDS[lang]['invite']
    pid=f'{lang}:{city}:{day.isoformat()}:{topic}'
    world.setdefault('post_comments',{}).setdefault(pid,[{'who':people[(seed+1)%len(people)][0],'text':base[1]},{'who':people[(seed+2)%len(people)][0],'text':base[2]}])
    return pid,person,topic,text

def page():
    world=store(); keys=list(CITIES)
    default=next((i for i,k in enumerate(keys) if k==st.session_state.get('v57_lang')),0)
    with st.container(key='rencontres_social'):
        st.markdown('''<style>
        /* Restricted to the social page: the rest of Mi Español keeps its theme. */
        .st-key-rencontres_social{--social-blue:#0866ff;--social-pale:#e9f1ff}
        .st-key-rencontres_social [data-testid="stButton"] button[kind="primary"],
        .st-key-rencontres_social button[data-testid="stBaseButton-primary"]{background:#0866ff!important;border-color:#0866ff!important;color:white!important}
        .st-key-rencontres_social [data-testid="stButton"] button:hover{border-color:#0866ff!important;color:#0866ff!important}
        .st-key-rencontres_social [data-testid="stButton"] button[kind="primary"]:hover{color:white!important;background:#0055d8!important}
        .st-key-rencontres_social [data-testid="stTextInput"] input:focus,
        .st-key-rencontres_social textarea:focus{border-color:#0866ff!important;box-shadow:0 0 0 1px #0866ff!important}
        .v65-head{background:linear-gradient(105deg,#0866ff,#6d83ff);color:white;padding:12px 16px;border-radius:16px;margin:4px 0 12px}
        .v65-head h2{color:white!important;margin:0!important;font-size:1.45rem!important}
        .v65-head small{color:#f1f5ff}
        .v65-person{background:#fff;border:1px solid #d9e5ff;border-radius:12px;padding:6px 10px;margin:3px 0;color:#1b315a;font-size:14px}
        .v65-bubble{border-radius:18px;padding:11px 14px;margin:8px 0;max-width:88%;line-height:1.5;overflow-wrap:anywhere;font-size:15px}
        .v65-them{background:#f0f2f5;margin-right:auto;color:#1c1e21}
        .v65-me{background:#0866ff;margin-left:auto;color:white}
        .v65-post{background:#fff;border:1px solid #d9e5ff;border-radius:16px;padding:13px 15px;margin:9px 0;color:#172d51}
        .v65-small{color:#65758f;font-size:12px}
        .v65-comment{background:#edf2fa;border-radius:13px;padding:8px 11px;margin:5px 0;color:#23334c}
        .v65-event{background:#fff;border:1px solid #d9e5ff;border-radius:14px;padding:12px 14px;margin:9px 0;color:#1b315a}
        @media(max-width:700px){.v65-head{padding:14px}.v65-bubble{max-width:96%}}
        </style>''',unsafe_allow_html=True)
        lang_label=st.selectbox('🌍 Langue de ton immersion',keys,index=default,format_func=lambda k:{'es':'🇪🇸 Espagnol','en':'🇬🇧 Anglais','de':'🇩🇪 Allemand','it':'🇮🇹 Italien'}.get(language_key(k),str(k)),key='v65_lang')
        lang=language_key(lang_label);cities=CITIES[lang_label];people=PEOPLE[lang]
        current=world['city'].setdefault(lang,st.session_state.get('v57_city',0) if lang_label==st.session_state.get('v57_lang') else 0)
        current=max(0,min(current,len(cities)-1));city=cities[current][0]
        band,provisional=social_band(lang)
        st.markdown(f'<div class="v65-head"><h2>💬 Mes rencontres · {html.escape(city)}</h2><small>📅 {date.today().strftime("%d/%m/%Y")} · Immersion {html.escape(lang.upper())} · Difficulté {band}{" (provisoire)" if provisional else " (indicative)"}</small></div>',unsafe_allow_html=True)
        with st.expander('🚆 Voyager ou déménager'):
            dest=st.selectbox('Destination',range(len(cities)),index=current,format_func=lambda i:cities[i][0],key=f'v65_dest_{lang}')
            a,b=st.columns(2)
            for column,action in ((a,'Voyager'),(b,'Déménager')):
                with column:
                    if st.button(('🧳 ' if action=='Voyager' else '🏡 ')+action,key=f'v65_{action}_{lang}',use_container_width=True):
                        world['city'][lang]=dest;st.session_state.v57_lang=lang_label;st.session_state.v57_city=dest;st.session_state.pop('v57_place',None);st.rerun()
        events=daily_update(world,lang,people,cities)
        left,right=st.columns([1.08,.92],gap='large')
        with left:
            st.markdown('### 💬 Messages privés')
            selected=min(st.session_state.get(f'v65_selected_{lang}',0),len(people)-1)
            for i,person in enumerate(people):
                name,emoji,home,animal,pet=person;key=f'{lang}:{name}'
                if not world['log'].get(key):record(world,lang,name,name,WORDS[lang]['hello'])
                last=world['log'][key][-1]['text']
                st.markdown(f'<div class="v65-person">{emoji} <b>{html.escape(name)}</b> · 🐾 {html.escape(pet)}<div class="v65-small">{html.escape(last[:90])}</div></div>',unsafe_allow_html=True)
                if st.button(('🔵 ' if selected==i else '💬 ')+f'Discuter avec {name}',key=f'v65_pick_{lang}_{i}',use_container_width=True):
                    st.session_state[f'v65_selected_{lang}']=i;st.rerun()
            person=people[selected];name=person[0];key=f'{lang}:{name}'
            st.markdown(f'#### {person[1]} {name}')
            with st.container(height=240,border=True):
                for item in world['log'][key][-18:]:
                    css='v65-me' if item['who']=='you' else 'v65-them'
                    st.markdown(f'<div class="v65-bubble {css}">{html.escape(item["text"])}</div>',unsafe_allow_html=True)
            with st.form(key=f'v65_message_{lang}_{selected}',clear_on_submit=True):
                msg=st.text_input('Écrire un message',placeholder='Ton message dans la langue apprise…')
                send=st.form_submit_button('📨 Envoyer',type='primary',use_container_width=True)
            if send and msg.strip():
                record(world,lang,name,'you',msg.strip()[:500]);record(world,lang,name,name,reply(lang,msg.strip(),person,world))
                counts=st.session_state.setdefault('v65_free_messages',{});counts[lang]=counts.get(lang,0)+1
                st.rerun()
            with st.expander('💡 Je bloque : phrases utiles'):
                for i,phrase in enumerate(GUIDES[lang]):
                    if st.button(phrase,key=f'v65_guide_{lang}_{selected}_{i}',use_container_width=True):
                        record(world,lang,name,'you',phrase);record(world,lang,name,name,reply(lang,phrase,person,world));st.rerun()
        with right:
            st.markdown('### 📸 Fil de vie & commentaires')
            st.caption('Les amis publient et se répondent, même sans toi. Tu peux simplement regarder.')
            for offset in range(2):
                day=date.today()-timedelta(days=offset)
                pid,person,topic,post=social_post(world,lang,people,city,day,band)
                st.markdown(f'<div class="v65-post"><b>{person[1]} {html.escape(person[0])}</b> <span class="v65-small">· {day.strftime("%d/%m")}</span><p>{html.escape(post)}</p><span class="v65-small">{"🎉 Sortie entre amis" if topic==1 else "🐾 Vie quotidienne" if topic==2 else "☀️ Dans la ville"}</span></div>',unsafe_allow_html=True)
                likes=world.setdefault('post_likes',{})
                if st.button(('💙 Aimé' if likes.get(pid) else '🤍 J’aime'),key=f'v65_like_{pid}'):
                    likes[pid]=not likes.get(pid,False);st.rerun()
                comments=world['post_comments'][pid]
                with st.expander(f'💬 {len(comments)} commentaires · Lire / répondre',expanded=(offset==0)):
                    for j,item in enumerate(comments[-20:]):
                        st.markdown(f'<div class="v65-comment"><b>{html.escape(item["who"])}</b> · {html.escape(item["text"])}</div>',unsafe_allow_html=True)
                        if item['who']!='Toi' and st.button('↪ Répondre',key=f'v65_replyto_{pid}_{j}'):
                            st.session_state[f'v65_replytarget_{pid}']=item['who'];st.rerun()
                    target=st.session_state.get(f'v65_replytarget_{pid}')
                    if target:st.caption(f'↪ Réponse à {target}')
                    with st.form(f'v65_comment_form_{pid}',clear_on_submit=True):
                        comment=st.text_input('Ton commentaire',key=f'v65_comment_{pid}',placeholder='Commenter dans la langue apprise…')
                        posted=st.form_submit_button('Publier',type='primary')
                    if posted and comment.strip():
                        body=(f'@{target} ' if target else '')+comment.strip()[:350]
                        comments.append({'who':'Toi','text':body})
                        st.session_state.pop(f'v65_replytarget_{pid}',None)
                        counts=st.session_state.setdefault('v65_free_messages',{});counts[lang]=counts.get(lang,0)+1
                        st.rerun()
                    with st.expander('💡 Une idée de commentaire ?'):
                        for i,suggestion in enumerate(POST_LINES[lang][topic][1:]):
                            if st.button(suggestion,key=f'v65_suggest_{pid}_{i}'):
                                comments.append({'who':'Toi','text':suggestion});st.rerun()
            st.markdown(f'### 🎉 À {city}')
            st.caption('Invitations selon la date. Certains jours, rien de prévu.')
            if not events:st.info('🌤️ Rien de prévu pour le moment.')
            for e in events[:4]:
                day=e['date'];label='Aujourd’hui' if day==date.today() else 'Demain' if day==date.today()+timedelta(days=1) else day.strftime('%d/%m')
                st.markdown(f'<div class="v65-event"><b>{html.escape(e["name"])}</b><div class="v65-small">📅 {label} · {html.escape(e["friend"])} · {html.escape(city)}</div></div>',unsafe_allow_html=True)
                if st.button('✨ Participer',key='v65_event_'+e['id'],use_container_width=True):
                    friend=next(p for p in people if p[0]==e['friend']);idx=e['idx'];prompt=['invite','conflict','pet','family','trip'][idx];message=WORDS[lang][prompt]
                    if idx==4:message=message.format(city=cities[(current+1)%len(cities)][0])
                    if idx==2:message=message.format(pet=friend[4])
                    done=world.setdefault('event_done',[])
                    if e['id'] not in done:record(world,lang,friend[0],friend[0],message);done.append(e['id'])
                    st.session_state[f'v65_selected_{lang}']=people.index(friend);st.rerun()
        st.caption('ℹ️ Simulation locale scénarisée : les réponses libres sont reconnues de façon limitée. Les niveaux affichés sont indicatifs, non certifiés. Messages et publications conservés pendant la session ; un stockage externe est nécessaire pour une mémoire durable sur Streamlit Cloud.')
