"""V63 : simulation sociale légère, locale, sans service IA externe."""
import json, os, re, uuid, hashlib, html, urllib.parse, urllib.request, urllib.request, urllib.parse
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

# Mémoire sociale V81 : 10 améliorations, sans API ni nouveau secret.
# Les souvenirs sont extraits uniquement des messages de l'utilisateur, par personnage.
MEMORY_RULES = {
 'pet': [r"(?:mi|my|mein(?:e)?|il mio|la mia|un|una|a|an)\s+(?:gato|gata|cat|katze|gatto|gatta|perro|dog|hund|cane)\s+(?:que\s+)?(?:se\s+llama|is called|named|heißt|heisst|si chiama)\s+([\wÀ-ÿ-]{2,25})"],
 'name': [r"(?:me llamo|mi nombre es|my name is|ich heiße|ich heisse|mi chiamo)\s+([\wÀ-ÿ-]{2,25})"],
 'city': [r"(?:vivo en|vivo a|i live in|ich wohne in|abito a|abito in)\s+([\wÀ-ÿ-]{2,30})"],
 'job': [r"(?:trabajo como|soy|i work as|i am a|ich bin|lavoro come|sono)\s+(?:un |una |a |an )?(profesor(?:a)?|maestr[oa]|médic[oa]|doctor|teacher|engineer|ingenier[oa]|student|estudiante|étudiant|studentessa|studente|developer|développeur|enfermer[oa]|nurse|chef|cocinero|koch|lehrer(?:in)?)\b"],
 'hobby': [r"(?:me gusta|me encanta|i like|i love|ich mag|ich liebe|mi piace|adoro)\s+(?:mucho\s+)?(?:el |la |los |las |the )?(leer|reading|read|lesen|leggere|bailar|dancing|dance|tanzen|ballare|cocinar|cooking|cook|kochen|cucinare|música|music|musik|musica|fútbol|football|fußball|calcio|viajar|travel|reisen|viaggiare)\b"],
 'birthday': [r"(?:mi cumpleaños es|my birthday is|mein geburtstag ist|il mio compleanno è)\s+(?:el |on |am |il )?([\wÀ-ÿ0-9 /-]{3,30})"],
 'friend': [r"(?:mi (?:mejor )?amig[oa]|my (?:best )?friend|mein(?:e)? freund(?:in)?|il mio amico|la mia amica)\s+(?:se llama|is called|heißt|heisst|si chiama)\s+([\wÀ-ÿ-]{2,25})"],
 'family': [r"(?:mi (?:herman[oa]|madre|padre)|my (?:brother|sister|mother|father)|mein(?:e)? (?:bruder|schwester|mutter|vater)|mi[oa] (?:fratello|sorella|madre|padre))\s+(?:se llama|is called|heißt|heisst|si chiama)\s+([\wÀ-ÿ-]{2,25})"],
}
MEMORY_LABELS={'pet':'🐾 Animal','name':'👋 Prénom','city':'🏙️ Ville','job':'💼 Métier','hobby':'❤️ Passion','birthday':'🎂 Anniversaire','friend':'🤝 Ami(e)','family':'👨‍👩‍👧 Famille'}
MEMORY_TRIGGERS={
 'pet':('gato','gata','perro','mascota','animal','cat','dog','pet','katze','hund','gatto','cane'),
 'name':('nombre','llamo','name','heiße','heisse','nome','chiamo'),
 'city':('vivo','ciudad','donde vivo','live','city','wohne','stadt','abito','città'),
 'job':('trabajo','profesión','oficio','work','job','beruf','arbeit','lavoro'),
 'hobby':('gusta','encanta','afición','hobby','like','love','mag','piace','passion'),
 'birthday':('cumpleaños','birthday','geburtstag','compleanno'),
 'friend':('amigo','amiga','friend','freund','amico','amica'),
 'family':('familia','hermano','hermana','madre','padre','family','brother','sister','familie','fratello','sorella'),
}
RECALL_WORDS=('recuerdas','acuerdas','recuerda','sabes','remember','recall','weißt','weisst','erinner','ricordi','ricorda','sai')

def social_memories(world,lang,name):
    """Reconstruit la mémoire à partir de l'historique sauvegardé (sans migration DB)."""
    facts={}; key=f'{lang}:{name}'
    for entry in world.get('log',{}).get(key,[]):
        if entry.get('who')!='you':continue
        msg=str(entry.get('text',''))[:500]
        # Permet de rectifier un souvenir : « olvida mi gato », etc.
        low=msg.casefold()
        if any(w in low for w in ('olvida ', 'forget ', 'vergiss ', 'dimentica ')):
            for kind,words in MEMORY_TRIGGERS.items():
                if any(w in low for w in words):facts.pop(kind,None)
            if any(w in low for w in ('todo','everything','alles','tutto')):facts.clear()
            continue
        for kind,patterns in MEMORY_RULES.items():
            for pattern in patterns:
                m=re.search(pattern,msg,re.IGNORECASE)
                if m:
                    value=m.group(1).strip(' .,!?;:')
                    if value and len(value)<=35:facts[kind]=value
                    break
    return facts

def memory_response(lang,kind,value):
    lines={
     'es':f'¡Claro que me acuerdo! 😊 {MEMORY_LABELS[kind].split(" ",1)[1]}: {value}. ¿Quieres contarme más?',
     'en':f'Of course I remember! 😊 {value}. Would you like to tell me more?',
     'de':f'Natürlich erinnere ich mich! 😊 {value}. Magst du mir mehr erzählen?',
     'it':f'Certo che mi ricordo! 😊 {value}. Vuoi raccontarmi di più?',
    }
    if kind=='pet':lines['es']=f'¡Claro que me acuerdo de {value}! 🐾 ¿Cómo está {value} hoy?'
    return lines[lang]

def reply(lang,text,person,world):
    lower=text.casefold(); d=WORDS[lang]; name,emoji,home,pettype,pet=person
    facts=social_memories(world,lang,name)
    # 1-8 : souvenirs personnels ; 9 : rappel ciblé ; 10 : correction/oubli.
    if any(x in lower for x in ('olvida ','forget ','vergiss ','dimentica ')):
        return {'es':'Entendido, no volveré a mencionar ese recuerdo. 💙','en':'Understood, I will not mention that memory again. 💙','de':'Verstanden, ich werde diese Erinnerung nicht mehr erwähnen. 💙','it':'Capito, non menzionerò più quel ricordo. 💙'}[lang]
    recall=any(x in lower for x in RECALL_WORDS)
    if recall:
        for kind,words in MEMORY_TRIGGERS.items():
            if any(x in lower for x in words) and kind in facts:return memory_response(lang,kind,facts[kind])
        if any(x in lower for x in ('de mí','sobre mí','about me','über mich','di me','sabes de','know about')):
            if facts:return {'es':'Recuerdo esto: ','en':'I remember: ','de':'Ich erinnere mich an: ','it':'Ricordo: '}[lang]+'; '.join(f'{MEMORY_LABELS[k]}: {v}' for k,v in facts.items())+'. 😊'
        return {'es':'Todavía no recuerdo ese dato. ¿Me lo cuentas?','en':'I do not remember that detail yet. Can you tell me?','de':'Daran erinnere ich mich noch nicht. Erzählst du es mir?','it':'Non ricordo ancora quel dettaglio. Me lo racconti?'}[lang]
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


# Données météo publiques Open-Meteo ; aucune clé ni dépendance supplémentaire.
CITY_COORDS = {
 'Madrid':(40.4168,-3.7038),'Barcelona':(41.3874,2.1686),'Valencia':(39.4699,-0.3763),'London':(51.5072,-0.1276),'Edinburgh':(55.9533,-3.1883),'München':(48.1351,11.5820),'Münich':(48.1351,11.5820),'München':(48.1351,11.5820),'Roma':(41.9028,12.4964),'Firenze':(43.7696,11.2558),'Venezia':(45.4408,12.3155),'Venice':(45.4408,12.3155),'Barcelone':(41.3874,2.1686),'Valence':(39.4699,-0.3763),
 'Londres':(51.5072,-0.1276),'Édimbourg':(55.9533,-3.1883),'Dublin':(53.3498,-6.2603),
 'Berlin':(52.5200,13.4050),'Munich':(48.1351,11.5820),'Hambourg':(53.5511,9.9937),
 'Rome':(41.9028,12.4964),'Florence':(43.7696,11.2558),'Venise':(45.4408,12.3155)
}

def weather_label(code):
    if code in (0,):return '☀️','Ensoleillé'
    if code in (1,2):return '🌤️','Éclaircies'
    if code in (3,):return '☁️','Nuageux'
    if code in (45,48):return '🌫️','Brouillard'
    if code in (51,53,55,56,57):return '🌦️','Bruine'
    if code in (61,63,65,66,67,80,81,82):return '🌧️','Pluie'
    if code in (71,73,75,77,85,86):return '❄️','Neige'
    if code in (95,96,99):return '⛈️','Orage'
    return '🌡️','Météo variable'

@st.cache_data(ttl=1200,show_spinner=False)
def city_weather(city):
    coords=CITY_COORDS.get(city)
    if not coords:return None
    lat,lon=coords
    url='https://api.open-meteo.com/v1/forecast?'+urllib.parse.urlencode({
        'latitude':lat,'longitude':lon,'current':'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
        'timezone':'auto'})
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MiEspanol/1.0'}),timeout=3) as response:
            data=json.load(response)['current']
        icon,label=weather_label(int(data['weather_code']))
        return {'temp':round(float(data['temperature_2m'])),'icon':icon,'label':label,
                'humidity':round(float(data['relative_humidity_2m'])),
                'wind':round(float(data['wind_speed_10m']))}
    except (OSError,ValueError,KeyError,TypeError):return None

def weather_reply(lang,city,weather):
    if not weather:return None
    t=weather['temp'];label=weather['label'].lower()
    templates={
      'es':f'¡En {city} tenemos {t} °C y tiempo {label}! {"¿Prefieres un paseo o un café calentito?" if t<17 else "¿Salimos a dar un paseo?"}',
      'en':f'It is {t} °C in {city} right now ({label}). Shall we go for a walk?',
      'de':f'In {city} sind es gerade {t} °C ({label}). Wollen wir spazieren gehen?',
      'it':f'A {city} ci sono {t} °C ({label}). Facciamo una passeggiata?'
    }
    return templates.get(lang,templates['es'])

def asks_weather(text):
    return bool(re.search(r'\b(?:tiempo|clima|temperatura|grados|llueve|sol|weather|temperature|rain|sunny|wetter|temperatur|regen|sonne|meteo|tempo|piove|caldo|frío|frio)\b',text.lower()))

# V82 : micro-activités sociales locales, déterministes et sans API.
SOCIAL_PROMPTS={
 'es':['¿Cómo estás hoy?','¿Qué haces esta tarde?','¿Te gusta esta ciudad?','¿Vamos a tomar un café?','¿Cómo está tu mascota?','¿Qué música te gusta?'],
 'en':['How are you today?','What are you doing?','Do you like this city?','Shall we get coffee?','How is your pet?','What music do you like?'],
 'de':['Wie geht es dir?','Was machst du heute?','Magst du die Stadt?','Gehen wir ins Café?','Wie geht es deinem Tier?','Welche Musik magst du?'],
 'it':['Come stai oggi?','Che fai oggi?','Ti piace la città?','Prendiamo un caffè?','Come sta il tuo animale?','Che musica ti piace?']}
SOCIAL_STORIES={
 'es':['☕ Un café con amigos','🐾 Paseo con mi mascota','🎵 Escuchando música','🌇 Una tarde preciosa','📚 Aprendiendo algo nuevo','🍕 ¡Qué hambre!'],
 'en':['☕ Coffee with friends','🐾 Walking my pet','🎵 Listening to music','🌇 Lovely afternoon','📚 Learning something new','🍕 So hungry!'],
 'de':['☕ Kaffee mit Freunden','🐾 Mit meinem Tier spazieren','🎵 Musik hören','🌇 Schöner Nachmittag','📚 Etwas Neues lernen','🍕 Ich habe Hunger!'],
 'it':['☕ Caffè con amici','🐾 A passeggio','🎵 Ascolto musica','🌇 Bel pomeriggio','📚 Imparo qualcosa','🍕 Che fame!']}
SOCIAL_POLL={
 'es':('¿Qué prefieres hoy?','☕ Café','🌳 Parque'),
 'en':('What do you prefer today?','☕ Coffee','🌳 Park'),
 'de':('Was magst du heute?','☕ Kaffee','🌳 Park'),
 'it':('Cosa preferisci oggi?','☕ Caffè','🌳 Parco')}
SOCIAL_REACTIONS=['❤️','😂','👏','😮']

def social_score(world,lang,name):
    return max(0,min(100,int(world.setdefault('social_affinity',{}).get(f'{lang}:{name}',20))))

def social_bond(world,lang,name,points=2):
    key=f'{lang}:{name}'; scores=world.setdefault('social_affinity',{})
    scores[key]=max(0,min(100,int(scores.get(key,20))+points))

def social_day(world,lang,people):
    # At most one ambient message per character and day, generated on return.
    today=date.today().isoformat(); stamps=world.setdefault('social_ambient_days',{})
    for person in people:
        name=person[0];key=f'{lang}:{name}'
        if stamps.get(key)==today:continue
        stamps[key]=today
        log=world.get('log',{}).get(key,[])
        if log and stable_number(today,lang,name,'ambient')%3==0:
            prompt=SOCIAL_PROMPTS[lang][stable_number(today,name,'topic')%len(SOCIAL_PROMPTS[lang])]
            record(world,lang,name,name,prompt)

def social_metrics(world,lang):
    logs=world.get('log',{})
    count=sum(sum(1 for m in items if m.get('who')=='you') for key,items in logs.items() if key.startswith(lang+':'))
    days=set(m.get('day') for key,items in logs.items() if key.startswith(lang+':') for m in items if m.get('who')=='you' and m.get('day'))
    streak=0;d=date.today()
    if d.isoformat() not in days:d-=timedelta(days=1)
    while d.isoformat() in days:
        streak+=1;d-=timedelta(days=1)
    return count,streak

def social_quick_response(lang,txt,person):
    t=txt.casefold()
    if any(w in t for w in ('hola','hello','hallo','ciao','salut')):
        return {'es':'¡Hola! 😊 ¡Qué alegría verte!','en':'Hi! 😊 Great to see you!','de':'Hallo! 😊 Schön, dich zu sehen!','it':'Ciao! 😊 Che bello vederti!'}[lang]
    if any(w in t for w in ('gracias','thank','danke','grazie')):
        return {'es':'¡De nada! 💙','en':'You are welcome! 💙','de':'Gern geschehen! 💙','it':'Prego! 💙'}[lang]
    if any(w in t for w in ('café','cafe','coffee','kaffee','caffè')):
        return {'es':'¡Sí! ☕ ¿A qué hora?','en':'Yes! ☕ What time?','de':'Ja! ☕ Um wie viel Uhr?','it':'Sì! ☕ A che ora?'}[lang]
    return None

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
    /* 1. Fond doux et profondeur */
    .stApp{background:radial-gradient(circle at 12% 8%,#f8e7ff 0,transparent 34%),linear-gradient(155deg,#f8fbff,#eaf2ff)!important}
    /* 2. En-tête premium */
    .v68-head{background:linear-gradient(115deg,#1746b9,#477cff 68%,#8d77f2);color:#fff;padding:18px 22px;border-radius:22px;margin:6px 0 12px;box-shadow:0 12px 28px rgba(35,75,165,.19)}
    /* 3. Bulles plus lisibles */
    .v68-bubble{box-shadow:0 3px 12px rgba(28,64,130,.08);border:1px solid rgba(110,150,210,.10)}
    /* 4. Cartes du fil et événements */
    .v68-post,.v68-event{box-shadow:0 5px 18px rgba(40,72,125,.07);transition:transform .16s,box-shadow .16s}
    .v68-post:hover,.v68-event:hover{transform:translateY(-2px);box-shadow:0 9px 22px rgba(40,72,125,.12)}
    /* 5. Boutons et champs harmonisés */
    div[data-testid="stButton"] button{border-radius:12px!important;transition:filter .15s,transform .15s}
    div[data-testid="stButton"] button:hover:not(:disabled){filter:brightness(1.04);transform:translateY(-1px)}
    div[data-testid="stTextInput"] input{border-radius:12px!important}
    .v81-weather{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:rgba(255,255,255,.88);border:1px solid #dce7ff;border-radius:17px;padding:13px 17px;margin:0 0 14px;box-shadow:0 5px 16px rgba(40,72,125,.07);color:#20395d}
    .v81-weather .temp{font-size:1.8rem;font-weight:800;color:#1b4fbb}
    .v81-weather .muted{font-size:.78rem;color:#61738e}
    
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
    .v82-stats{background:#fff;border:1px solid #dce7ff;border-radius:14px;padding:11px 16px;margin:9px 0;color:#254477;font-weight:700;box-shadow:0 3px 12px rgba(30,70,120,.05)}
    .v82-story{background:linear-gradient(145deg,#fff,#f2f5ff);border:1px solid #e3d6ff;border-radius:16px;padding:10px;min-height:105px;box-shadow:0 3px 10px rgba(42,58,130,.07);color:#243f75}
    .v82-story small{display:block;color:#8b68ba;font-size:.7rem}.v82-story p{font-size:.84rem;margin:8px 0 0}
    .v68-post,.v68-event{box-shadow:0 5px 18px rgba(48,65,105,.07)}
    .v68-bubble{box-shadow:0 2px 8px rgba(30,58,110,.06)}
    @media(max-width:900px){.v82-story{min-height:110px;padding:6px}.v82-story p{font-size:.75rem}}
    </style>""",unsafe_allow_html=True)
    language=st.selectbox('🌍 Langue de ton immersion',keys,index=default,format_func=lambda k:{'es':'🇪🇸 Espagnol','en':'🇬🇧 Anglais','de':'🇩🇪 Allemand','it':'🇮🇹 Italien'}.get(language_key(k),str(k)),key='v68_lang')
    lang=language_key(language);cities=CITIES[language];people=PEOPLE[lang]
    current=world['city'].setdefault(lang,st.session_state.get('v57_city',0) if language==st.session_state.get('v57_lang') else 0)
    current=max(0,min(current,len(cities)-1));city=cities[current][0]
    band,provisional=social_band(lang)
    st.markdown(f'<div class="v68-head"><strong>🌍 {html.escape(city)} · Ta vie sociale</strong><small>📅 {date.today().strftime("%d/%m/%Y")} · {html.escape(lang.upper())} · Niveau {band} {"(provisoire)" if provisional else "(indicatif)"}</small></div>',unsafe_allow_html=True)
    weather=city_weather(city)
    if weather:
        st.markdown(f'<div class="v81-weather"><div><strong>📍 {html.escape(city)} · Météo en direct</strong><div class="muted">{weather["icon"]} {html.escape(weather["label"])} · 💧 {weather["humidity"]}% humidité · 💨 {weather["wind"]} km/h</div></div><div class="temp">{weather["temp"]} °C</div></div>',unsafe_allow_html=True)
        st.caption('💬 Idée de conversation : « ¿Qué tiempo hace hoy? » · Source : Open-Meteo (actualisation toutes les 20 min)')
    else:
        st.caption(f'🌤️ Météo de {city} momentanément indisponible · La conversation reste accessible.')
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
    social_day(world,lang,people)
    count,streak=social_metrics(world,lang)
    st.markdown(f'<div class="v82-stats">📨 {count} messages · 🔥 {streak} jour(s) de suite · 🎯 Niveau {html.escape(band)} · 🟢 {len(people)} contacts</div>',unsafe_allow_html=True)
    with st.expander('🔔 Activité du réseau · Stories et défis',expanded=True):
        storycols=st.columns(min(4,len(people)))
        for i,person in enumerate(people[:4]):
            name=person[0];story=SOCIAL_STORIES[lang][stable_number(date.today(),lang,name)%len(SOCIAL_STORIES[lang])]
            with storycols[i]:
                st.markdown(f'<div class="v82-story"><b>{person[1]} {html.escape(name)}</b><small>● Story du jour</small><p>{html.escape(story)}</p></div>',unsafe_allow_html=True)
                if st.button('👀 Voir',key=f'v82_story_{lang}_{i}'):
                    st.session_state[f'v65_selected_{lang}']=i
                    social_bond(world,lang,name,1)
                    persist_and_rerun(world)
        st.caption('🗓️ Les stories changent chaque jour · 📩 Les messages spontanés apparaissent lors de tes visites.')
    with st.expander('🎯 Défi du jour · niveau adapté'):
        challenge=SOCIAL_PROMPTS[lang][stable_number(date.today(),lang,'challenge')%len(SOCIAL_PROMPTS[lang])]
        st.write('💬 '+challenge)
        st.caption('Essaie cette phrase dans une conversation. Aucune pénalité si tu fais une erreur.')
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
        st.markdown(f'<div class="v68-title">{person[1]} {html.escape(name)} <span class="v68-muted">· 🐾 {html.escape(person[4])} · 💙 Amitié {social_score(world,lang,name)}/100 · 🟢 Actif dans le jeu</span></div>',unsafe_allow_html=True)
        with st.expander('⚡ Actions rapides avec ce contact'):
            actioncols=st.columns(3)
            for i,(emoji,topic) in enumerate([('👋',SOCIAL_PROMPTS[lang][0]),('☕',SOCIAL_PROMPTS[lang][3]),('🐾',SOCIAL_PROMPTS[lang][4])]):
                with actioncols[i]:
                    if st.button(emoji+' '+('Saluer','Inviter','Animal')[i],key=f'v82_action_{lang}_{selected}_{i}',use_container_width=True):
                        record(world,lang,name,'you',topic)
                        record(world,lang,name,name,social_quick_response(lang,topic,person) or reply(lang,topic,person,world))
                        social_bond(world,lang,name,2)
                        persist_and_rerun(world)
        with st.expander('🎁 Petit cadeau virtuel'):
            gifts=['🌷 Fleur','🍫 Chocolat','📚 Livre']
            gift=st.radio('Choisir un cadeau',gifts,horizontal=True,key=f'v82_gift_{lang}_{selected}')
            if st.button('🎁 Offrir',key=f'v82_sendgift_{lang}_{selected}'):
                record(world,lang,name,'you','🎁 '+gift)
                record(world,lang,name,name,{'es':'¡Muchas gracias! 💝','en':'Thank you so much! 💝','de':'Vielen Dank! 💝','it':'Grazie mille! 💝'}[lang])
                social_bond(world,lang,name,4)
                persist_and_rerun(world)
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
            if response is None and asks_weather(msg):response=weather_reply(lang,city,weather)
            if response is None and not any(w in msg.casefold() for w in RECALL_WORDS):response=social_quick_response(lang,msg,person)
            if response is None:response=reply(lang,msg.strip(),person,world)
            social_bond(world,lang,name,3);record(world,lang,name,'you',msg.strip()[:500]);v80.remember(world,lang,name,msg.strip());record(world,lang,name,name,response)
            counts=st.session_state.setdefault('v65_free_messages',{});counts[lang]=counts.get(lang,0)+1;persist_and_rerun(world)
        # Panneau consultable : 8 types de souvenirs, propres à ce contact.
        with st.expander('🧠 Ce que ce personnage retient de moi'):
            known=social_memories(world,lang,name)
            if known:
                for kind,value in known.items():st.caption(f'{MEMORY_LABELS[kind]} : {value}')
            else:st.caption('Aucun souvenir personnel reconnu pour ce personnage.')
            st.caption('Pour corriger : redonne une information. Pour oublier : « olvida mi gato » (ou « olvida todo »).')
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
            # Reactions distinctes des likes, conservées dans le profil.
            reactions=world.setdefault('social_reactions',{})
            rc=st.columns(4)
            for j,emoji in enumerate(SOCIAL_REACTIONS):
                with rc[j]:
                    if st.button(emoji,key=f'v82_react_{pid}_{j}',use_container_width=True):
                        reactions[pid]=emoji;persist_and_rerun(world)
            if reactions.get(pid):st.caption('Ta réaction : '+reactions[pid])
            saved_posts=world.setdefault('social_bookmarks',[])
            if st.button('🔖 Enregistré' if pid in saved_posts else '🔖 Garder ce post',key=f'v82_bookmark_{pid}'):
                if pid in saved_posts:saved_posts.remove(pid)
                else:saved_posts.append(pid)
                persist_and_rerun(world)
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
        with st.expander('📊 Sondage du jour',expanded=True):
            question,opt1,opt2=SOCIAL_POLL[lang]
            st.write(question)
            pollid=f'{lang}:{city}:{date.today().isoformat()}'
            votes=world.setdefault('social_polls',{})
            chosen=votes.get(pollid)
            if chosen:
                st.success('🗳️ '+chosen)
                seed=stable_number(pollid,'poll')
                first=2+seed%9;second=2+(seed//7)%9
                if chosen==opt1:first+=1
                else:second+=1
                st.progress(first/(first+second),text=f'{opt1} · {round(first/(first+second)*100)} %')
                st.caption('Résultats simulés pour les personnages, plus ton vote.')
            else:
                for i,opt in enumerate((opt1,opt2)):
                    if st.button(opt,key=f'v82_poll_{pollid}_{i}',use_container_width=True):
                        votes[pollid]=opt;persist_and_rerun(world)
        with st.expander('📅 Agenda social · 7 jours'):
            for offset in range(7):
                day=date.today()+timedelta(days=offset)
                seed=stable_number(lang,city,day,'agenda')
                name=EVENT_NAMES[seed%len(EVENT_NAMES)]
                st.caption(f'{day.strftime("%d/%m")} · {name} · {people[(seed//5)%len(people)][0]}')
        with st.expander('🏆 Mon activité'):
            st.metric('Messages envoyés',count)
            st.metric('Série de jours',streak)
            st.caption('💙 Les amitiés progressent avec les messages, les stories et les cadeaux.')
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
                social_bond(world,lang,friend[0],5);st.session_state[f'v65_selected_{lang}']=people.index(friend);persist_and_rerun(world)
    st.caption('ℹ️ V82 : simulation locale, activités datées et météo Open-Meteo. Pas de simulation en arrière-plan · V80 : IA facultative selon configuration ; sinon moteur scénarisé. Niveau CECRL indicatif. Sauvegarde durable uniquement avec base externe et profil chargé.')
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
