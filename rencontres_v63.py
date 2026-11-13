"""V63 : simulation sociale légère, locale, sans service IA externe."""
import json, os, re, uuid, hashlib, html
from datetime import date, timedelta
from pathlib import Path
import streamlit as st
import social_v80 as v80
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

def remembered_pet(world,lang,name):
    """Read explicitly stated pet names from saved chat; no external AI."""
    key=f'{lang}:{name}'
    patterns=(
        r'\b(?:mi|my|mein(?:e)?|il mio|la mia)\s+(?:gato|gata|chat|cat|katze|gatto|gatta|perro|dog|hund|cane)\s+(?:que\s+)?(?:se\s+llama|s\x27appelle|is called|named|heisst|heißt|si chiama)\s+([A-Za-zÀ-ÿ][\wÀ-ÿ-]{1,24})',
        r'\b(?:mi|my|mein(?:e)?|il mio|la mia)\s+(?:gato|gata|chat|cat|katze|gatto|gatta|perro|dog|hund|cane)\s+(?:es|is|ist|è)\s+(?:llamado|named)\s+([A-Za-zÀ-ÿ][\wÀ-ÿ-]{1,24})',
    )
    for item in reversed(world.get('log',{}).get(key,[])):
        if item.get('who')!='you':continue
        for pattern in patterns:
            match=re.search(pattern,item.get('text',''),flags=re.IGNORECASE)
            if match:return match.group(1)
    return None

def reply(lang,text,person,world):
    lower=text.lower(); d=WORDS[lang]; name,emoji,home,pettype,pet=person
    pet_memory=remembered_pet(world,lang,name)
    if pet_memory and any(x in lower for x in ('mi gato','mi gata','mi perro','my cat','my dog','mein hund','meine katze','mio gatto','mio cane','mi mascota','my pet','recuerdas','te acuerdas')):
        if lang=='es':return f'¡Claro que me acuerdo de {pet_memory}! 🐾 ¿Cómo está {pet_memory} hoy?'
        if lang=='en':return f'Of course I remember {pet_memory}! 🐾 How is {pet_memory} today?'
        if lang=='de':return f'Natürlich erinnere ich mich an {pet_memory}! 🐾 Wie geht es {pet_memory} heute?'
        if lang=='it':return f'Certo che mi ricordo di {pet_memory}! 🐾 Come sta {pet_memory} oggi?'
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


def persist_and_rerun(world):
    profile=st.session_state.get('v80_profile')
    if profile and v80.db_enabled():
        try:v80.save(profile,world)
        except Exception:st.warning('Sauvegarde distante momentanément indisponible.')
    st.rerun()


def page():
    """V68: three genuinely distinct social panels, no duplicate contact buttons."""
    world=store(); keys=list(CITIES)
    # Optional per-profile durable storage. Profile codes are not authentication.
    with st.expander('💾 Sauvegarde et IA · V80',expanded=False):
        st.caption('La sauvegarde durable nécessite SOCIAL_DATABASE_URL. Le code de profil est un identifiant, pas un mot de passe : ne l’utilise pas pour des données sensibles.')
        profile=st.text_input('Code de profil (6 à 64 caractères)',value=st.session_state.get('v80_profile',''),key='v80_profile_input',placeholder='ex. monaventure_2026')
        valid=v80.profile_id(profile)
        if st.button('📂 Charger mon profil',key='v80_load',disabled=not(valid and v80.db_enabled())):
            try:
                saved=v80.load(valid)
                if saved is not None:
                    st.session_state.v63_world=saved
                    st.session_state.v80_profile=valid
                    st.success('Monde social chargé.');st.session_state.v80_loaded_profile=valid;st.rerun()
                else:
                    st.session_state.v80_profile=valid
                    st.info('Nouveau profil : tes prochaines interactions pourront être sauvegardées.')
            except Exception as exc:st.error(f'Chargement impossible : {type(exc).__name__}')
        if st.button('💾 Enregistrer maintenant',key='v80_save',disabled=not(valid and v80.db_enabled())):
            try:
                v80.save(valid,world);st.session_state.v80_profile=valid;st.success('Sauvegarde effectuée.')
            except Exception as exc:st.error(f'Sauvegarde impossible : {type(exc).__name__}')
        st.caption(('🟢 IA connectée' if v80.ai_enabled() else '⚪ IA non configurée : dialogues scénarisés')+' · '+('🟢 Base connectée' if v80.db_enabled() else '⚪ Base non configurée : session uniquement'))
    if st.session_state.get('v80_profile') and v80.db_enabled():
        # Load at most once per profile in this Streamlit session.
        profile=st.session_state.v80_profile
        if st.session_state.get('v80_loaded_profile')!=profile:
            try:
                saved=v80.load(profile)
                if saved is not None:st.session_state.v63_world=saved;world=saved
                st.session_state.v80_loaded_profile=profile
            except Exception:pass
    default=next((i for i,k in enumerate(keys) if k==st.session_state.get('v57_lang')),0)
    st.markdown("""<style>
    .stApp{background:linear-gradient(160deg,#f4f8ff,#eaf2ff)!important}
    .block-container{max-width:1700px!important;padding-top:.4rem!important}
    .v68-head{background:linear-gradient(105deg,#0866ff,#6782f8);color:#fff;padding:13px 18px;border-radius:17px;margin:6px 0 12px}
    .v68-head strong{font-size:1.2rem}.v68-head small{display:block;margin-top:4px;color:#e9efff}
    .v68-title{color:#164c9e;font-weight:800;font-size:1.07rem;margin:5px 0 10px}
    .v68-contact{border-radius:12px;padding:6px 10px;background:#eef4ff;border:1px solid #d7e4ff;color:#15315c;font-size:.86rem}
    .v68-muted{color:#667c9f;font-size:.74rem}
    .v68-bubble{border-radius:16px;padding:10px 13px;margin:7px 0;max-width:91%;font-size:.9rem;line-height:1.45;overflow-wrap:anywhere}
    .v68-them{background:#e8edf5;color:#1c2b44;margin-right:auto}
    .v68-me{background:#0866ff;color:white;margin-left:auto}
    .v68-post{background:#fff;border:1px solid #dbe6fb;border-radius:15px;padding:13px;margin:8px 0;color:#1b315a}
    .v68-comment{background:#eef3fc;border-radius:12px;padding:8px 10px;margin:5px 0;font-size:.85rem;color:#203454}
    .v68-event{background:#fff;border:1px solid #dbe6fb;border-radius:14px;padding:11px;margin:8px 0;color:#1b315a}
    div[data-testid="stForm"]{border-radius:14px!important}
    div[data-testid="stButton"] button{min-height:36px!important}
    div[data-testid="stButton"] button[kind="primary"]{background:#0866ff!important;border-color:#0866ff!important;color:white!important}
    @media(max-width:900px){.v68-head{padding:12px}.v68-bubble{max-width:96%}}
    </style>""",unsafe_allow_html=True)
    language=st.selectbox('🌍 Langue de ton immersion',keys,index=default,format_func=lambda k:{'es':'🇪🇸 Espagnol','en':'🇬🇧 Anglais','de':'🇩🇪 Allemand','it':'🇮🇹 Italien'}.get(language_key(k),str(k)),key='v68_lang')
    lang=language_key(language);cities=CITIES[language];people=PEOPLE[lang]
    current=world['city'].setdefault(lang,st.session_state.get('v57_city',0) if language==st.session_state.get('v57_lang') else 0)
    current=max(0,min(current,len(cities)-1));city=cities[current][0]
    band,provisional=social_band(lang)
    st.markdown(f'<div class="v68-head"><strong>🌍 {html.escape(city)} · Ta vie sociale</strong><small>📅 {date.today().strftime("%d/%m/%Y")} · {html.escape(lang.upper())} · Niveau {band} {"(provisoire)" if provisional else "(indicatif)"}</small></div>',unsafe_allow_html=True)
    with st.expander('🚆 Voyager ou déménager'):
        dest=st.selectbox('Destination',range(len(cities)),index=current,format_func=lambda i:cities[i][0],key=f'v68_dest_{lang}')
        ca,cb=st.columns(2)
        for col,action in ((ca,'Voyager'),(cb,'Déménager')):
            with col:
                if st.button(('🧳 ' if action=='Voyager' else '🏡 ')+action,key=f'v68_{action}_{lang}',use_container_width=True):
                    world['city'][lang]=dest;st.session_state.v57_lang=language;st.session_state.v57_city=dest;st.session_state.pop('v57_place',None);persist_and_rerun(world)
    # Ensure initial greetings are created before daily simulation; no repeated greetings on reruns.
    for person in people:
        key=f'{lang}:{person[0]}'
        if not world['log'].get(key):record(world,lang,person[0],person[0],WORDS[lang]['hello'])
    events=daily_update(world,lang,people,cities)
    messages,feed,calendar=st.columns([1.05,1.08,.87],gap='medium')
    with messages:
        st.markdown('<div class="v68-title">💬 Messages</div>',unsafe_allow_html=True)
        selected=min(st.session_state.get(f'v65_selected_{lang}',0),len(people)-1)
        # Each contact is one tappable control; its label carries the last message.
        for i,person in enumerate(people):
            name,avatar,home,animal,pet=person
            log=world['log'][f'{lang}:{name}'];last=log[-1]['text'].replace('\n',' ')
            marker='🔵' if selected==i else avatar
            label=f'{marker} {name}  ·  {last[:48]}'+('…' if len(last)>48 else '')
            if st.button(label,key=f'v68_contact_{lang}_{i}',use_container_width=True,type='primary' if selected==i else 'secondary'):
                st.session_state[f'v65_selected_{lang}']=i;persist_and_rerun(world)
        person=people[selected];name=person[0];key=f'{lang}:{name}'
        st.markdown(f'<div class="v68-title">{person[1]} {html.escape(name)} <span class="v68-muted">· 🐾 {html.escape(person[4])}</span></div>',unsafe_allow_html=True)
        # No fixed-height empty scroll panel: chat grows naturally with content.
        for item in world['log'][key][-9:]:
            css='v68-me' if item['who']=='you' else 'v68-them'
            st.markdown(f'<div class="v68-bubble {css}">{html.escape(item["text"])}</div>',unsafe_allow_html=True)
        with st.form(key=f'v68_msg_{lang}_{selected}',clear_on_submit=True):
            msg=st.text_input('Ton message',placeholder='Écris dans la langue apprise…')
            send=st.form_submit_button('➤ Envoyer',type='primary',use_container_width=True)
        if send and msg.strip():
            history=list(world['log'][key]);response=None
            if v80.ai_enabled():
                try:response=v80.answer(lang,name,city,band,person[4],history,msg.strip(),world.get('memories',{}).get(key,[]))
                except Exception:st.toast('IA indisponible : réponse scénarisée utilisée.')
            if response is None:response=reply(lang,msg.strip(),person,world)
            record(world,lang,name,'you',msg.strip()[:500]);v80.remember(world,lang,name,msg.strip());record(world,lang,name,name,response)
            counts=st.session_state.setdefault('v65_free_messages',{});counts[lang]=counts.get(lang,0)+1;persist_and_rerun(world)
        with st.expander('💡 Traduction / réponses guidées'):
            for i,phrase in enumerate(GUIDES[lang]):
                if st.button(phrase,key=f'v68_guide_{lang}_{selected}_{i}',use_container_width=True):
                    record(world,lang,name,'you',phrase);record(world,lang,name,name,reply(lang,phrase,person,world));persist_and_rerun(world)
    with feed:
        st.markdown('<div class="v68-title">📸 Fil de vie</div>',unsafe_allow_html=True)
        st.caption('Tes amis publient et commentent, même si tu préfères observer.')
        for offset in range(3):
            day=date.today()-timedelta(days=offset)
            pid,person,topic,post=social_post(world,lang,people,city,day,band)
            topic_label=('☀️ Dans la ville','🎉 Sortie entre amis','🐾 Animaux')[topic]
            st.markdown(f'<div class="v68-post"><b>{person[1]} {html.escape(person[0])}</b> <span class="v68-muted">· {day.strftime("%d/%m")}</span><p>{html.escape(post)}</p><span class="v68-muted">{topic_label}</span></div>',unsafe_allow_html=True)
            likes=world.setdefault('post_likes',{})
            if st.button('💙 Aimé' if likes.get(pid) else '♡ J’aime',key=f'v68_like_{pid}'):
                likes[pid]=not likes.get(pid,False);persist_and_rerun(world)
            comments=world['post_comments'][pid]
            with st.expander(f'💬 {len(comments)} commentaires',expanded=(offset==0)):
                for j,item in enumerate(comments[-16:]):
                    st.markdown(f'<div class="v68-comment"><b>{html.escape(item["who"])}</b> · {html.escape(item["text"])}</div>',unsafe_allow_html=True)
                    if item['who']!='Toi' and st.button('↪ Répondre',key=f'v68_reply_{pid}_{j}'):
                        st.session_state[f'v68_target_{pid}']=item['who'];persist_and_rerun(world)
                target=st.session_state.get(f'v68_target_{pid}')
                if target:st.caption(f'↪ Réponse à {target}')
                with st.form(f'v68_comment_form_{pid}',clear_on_submit=True):
                    comment=st.text_input('Ton commentaire',placeholder='Écrire un commentaire…')
                    posted=st.form_submit_button('Publier',type='primary')
                if posted and comment.strip():
                    comments.append({'who':'Toi','text':(f'@{target} ' if target else '')+comment.strip()[:350]})
                    st.session_state.pop(f'v68_target_{pid}',None)
                    counts=st.session_state.setdefault('v65_free_messages',{});counts[lang]=counts.get(lang,0)+1;persist_and_rerun(world)
                with st.expander('💡 Idées de commentaires'):
                    for i,suggestion in enumerate(POST_LINES[lang][topic][1:]):
                        if st.button(suggestion,key=f'v68_suggest_{pid}_{i}'):
                            comments.append({'who':'Toi','text':suggestion});persist_and_rerun(world)
    with calendar:
        st.markdown('<div class="v68-title">🎉 Événements</div>',unsafe_allow_html=True)
        st.caption(f'À {city} · Selon la date et les habitants')
        if not events:st.info('🌤️ Rien de prévu pour le moment. Profite de la ville !')
        for e in events[:5]:
            day=e['date'];label='Aujourd’hui' if day==date.today() else 'Demain' if day==date.today()+timedelta(days=1) else day.strftime('%d/%m')
            done=e['id'] in world.setdefault('event_done',[])
            st.markdown(f'<div class="v68-event"><b>{html.escape(e["name"])}</b><div class="v68-muted">📅 {label} · {html.escape(e["friend"])}<br>📍 {html.escape(city)}</div></div>',unsafe_allow_html=True)
            if st.button('✓ Invitation ouverte' if done else '✨ Participer',key='v68_event_'+e['id'],use_container_width=True,disabled=done):
                friend=next(p for p in people if p[0]==e['friend']);idx=e['idx'];prompt=['invite','conflict','pet','family','trip'][idx];message=WORDS[lang][prompt]
                if idx==4:message=message.format(city=cities[(current+1)%len(cities)][0])
                if idx==2:message=message.format(pet=friend[4])
                record(world,lang,friend[0],friend[0],message);world['event_done'].append(e['id'])
                st.session_state[f'v65_selected_{lang}']=people.index(friend);persist_and_rerun(world)
    st.caption('ℹ️ V80 : IA facultative selon configuration ; sinon moteur scénarisé. Niveau CECRL indicatif. Sauvegarde durable uniquement avec base externe et profil chargé.')
    # Save the world after all widgets have been processed. Avoid database calls on every rerun
    # by using a digest of the serialized social state.
    if st.session_state.get('v80_profile') and v80.db_enabled():
        try:
            digest=hashlib.sha256(json.dumps(world,ensure_ascii=False,default=str,sort_keys=True).encode()).hexdigest()
            if digest!=st.session_state.get('v80_last_digest'):
                v80.save(st.session_state.v80_profile,world)
                st.session_state.v80_last_digest=digest
        except Exception:
            st.warning('La sauvegarde automatique n’a pas abouti. Réessaie depuis le panneau V80.')
