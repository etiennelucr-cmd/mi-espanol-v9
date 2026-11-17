"""Academia Mi Español: microleçons quotidiennes locales, sans API payante."""
import hashlib
import html
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path
import streamlit as st

LEVELS=('A1','A2','B1','B2','C1','C2')
# Contenu de démonstration structuré : les niveaux supérieurs ne constituent pas une certification CECRL.
LESSONS={
'es':{
'A1':[
 ('Au café','Quiero un café, por favor.','Je voudrais un café, s’il vous plaît.', [('Comment demander un café ?','Quiero un café, por favor','quiero un cafe','un cafe por favor'),('Comment dire « merci » ?','Gracias','gracias','muchas gracias'),('Complète : ¿Cuánto ...? (Combien ça coûte ?)','cuesta','cuesta')]),
 ('Se présenter','Me llamo Alex. Soy de Francia.','Je m’appelle Alex. Je viens de France.', [('Comment dire « Je m’appelle » ?','Me llamo','me llamo'),('Complète : Soy ... Francia.','de','de'),('Comment demander le prénom ?','¿Cómo te llamas?','como te llamas')]),
 ('Se déplacer','¿Dónde está la estación?','Où est la gare ?', [('Comment demander où est la gare ?','¿Dónde está la estación?','donde esta la estacion'),('Comment dire « à droite » ?','A la derecha','a la derecha','derecha'),('Comment dire « à gauche » ?','A la izquierda','a la izquierda','izquierda')])],
'A2':[('Au restaurant','¿Me puede traer la carta?','Pouvez-vous m’apporter la carte ?', [('Demande la carte poliment.','¿Me puede traer la carta?','me puede traer la carta'),('Comment dire « sans oignon » ?','Sin cebolla','sin cebolla'),('Comment demander l’addition ?','La cuenta, por favor','la cuenta por favor')])],
'B1':[('Raconter hier','Ayer fui al museo y después cené con mis amigos.','Hier je suis allé au musée puis j’ai dîné avec mes amis.', [('Complète : Ayer ... al museo.','fui','fui'),('Comment dire « ensuite » ?','Después','despues'),('Complète : ... con mis amigos.','cené','cene')])],
'B2':[('Exprimer son avis','Aunque llovía, decidimos salir porque nos apetecía pasear.','Même s’il pleuvait, nous avons décidé de sortir car nous avions envie de nous promener.', [('Comment dire « bien que » ?','Aunque','aunque'),('Complète : nos ... pasear.','apetecía','apetecia'),('Comment dire « nous avons décidé » ?','Decidimos','decidimos')])],
'C1':[('Nuancer un argument','Si bien la propuesta resulta atractiva, convendría evaluar sus consecuencias.','Bien que la proposition soit attrayante, il conviendrait d’en évaluer les conséquences.', [('Comment dire « il conviendrait » ?','Convendría','convendria'),('Comment dire « conséquences » ?','Consecuencias','consecuencias'),('Complète : Si ... la propuesta...','bien','bien')])],
'C2':[('Précision stylistique','Lejos de ser una mera anécdota, el episodio pone de relieve una contradicción de fondo.','Loin d’être une simple anecdote, cet épisode révèle une contradiction profonde.', [('Comment dire « loin de » ?','Lejos de','lejos de'),('Complète : pone de ...','relieve','relieve'),('Comment dire « une simple anecdote » ?','Una mera anécdota','una mera anecdota')])]},
'en':{'A1':[('At the café','A coffee, please.','Un café, s’il vous plaît.', [('Ask for a coffee.','A coffee, please','a coffee please'),('Say thank you.','Thank you','thank you','thanks'),('Ask for the bill.','The bill, please','the bill please')])]},
'de':{'A1':[('Im Café','Einen Kaffee, bitte.','Un café, s’il vous plaît.', [('Demande un café.','Einen Kaffee, bitte','einen kaffee bitte'),('Dis merci.','Danke','danke'),('Demande l’addition.','Die Rechnung, bitte','die rechnung bitte')])]},
'it':{'A1':[('Al bar','Un caffè, per favore.','Un café, s’il vous plaît.', [('Demande un café.','Un caffè, per favore','un caffe per favore'),('Dis merci.','Grazie','grazie'),('Demande l’addition.','Il conto, per favore','il conto per favore')])]},
}

def normalize(s):
    s=''.join(c for c in unicodedata.normalize('NFKD',str(s).casefold()) if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9 ]+',' ',s).strip()


# V90 : missions supplémentaires, scénarios de survie et grammaire contextualisée.
SURVIVAL = {
 'A1': [('Urgence','¡Ayuda! Necesito un médico.','À l’aide ! J’ai besoin d’un médecin.', [('Comment demander de l’aide ?','Ayuda','ayuda'),('Complète : Necesito un ...','médico','medico'),('Comment dire « pharmacie » ?','Farmacia','farmacia')]),('À l’hôtel','Tengo una reserva a nombre de Alex.','J’ai une réservation au nom d’Alex.', [('Comment dire « réservation » ?','Reserva','reserva'),('Complète : Tengo una ...','reserva','reserva'),('Comment dire « chambre » ?','Habitación','habitacion')]),('Faire des courses','¿Cuánto cuesta esta botella de agua?','Combien coûte cette bouteille d’eau ?', [('Comment dire « combien » ?','Cuánto','cuanto'),('Comment dire « eau » ?','Agua','agua'),('Complète : ¿Cuánto ...?','cuesta','cuesta')]),('Prendre le bus','¿Qué autobús va al centro?','Quel bus va au centre ?', [('Comment dire « bus » ?','Autobús','autobus'),('Comment dire « centre » ?','Centro','centro'),('Complète : ¿Qué autobús ... al centro?','va','va')])],
 'A2': [('À la pharmacie','Me duele la cabeza desde ayer.','J’ai mal à la tête depuis hier.', [('Comment dire « j’ai mal » ?','Me duele','me duele'),('Comment dire « tête » ?','Cabeza','cabeza'),('Comment dire « depuis hier » ?','Desde ayer','desde ayer')]),('Rendez-vous','¿Podría darme una cita para mañana?','Pourriez-vous me donner rendez-vous demain ?', [('Comment dire « rendez-vous » ?','Cita','cita'),('Comment dire « demain » ?','Mañana','manana'),('Complète : ¿Podría ... una cita?','darme','darme')]),('Perdre son chemin','Me he perdido. ¿Puede ayudarme?','Je me suis perdu. Pouvez-vous m’aider ?', [('Comment dire « je me suis perdu » ?','Me he perdido','me he perdido'),('Comment dire « aider » ?','Ayudar','ayudar'),('Complète : ¿Puede ...?','ayudarme','ayudarme')])],
 'B1': [('Train annulé','Han cancelado mi tren. ¿Qué alternativas tengo?','Mon train a été annulé. Quelles alternatives ai-je ?', [('Comment dire « annulé » ?','Cancelado','cancelado'),('Comment dire « alternatives » ?','Alternativas','alternativas'),('Complète : ¿Qué alternativas ...?','tengo','tengo')]),('Appartement','Quisiera visitar el piso antes de alquilarlo.','Je voudrais visiter l’appartement avant de le louer.', [('Comment dire « louer » ?','Alquilar','alquilar'),('Comment dire « avant » ?','Antes','antes'),('Complète : ... visitar el piso.','Quisiera','quisiera')])],
 'B2': [('Réclamation à l’hôtel','La habitación no coincide con la reserva. Quisiera una solución.','La chambre ne correspond pas à la réservation. Je voudrais une solution.', [('Comment dire « ne correspond pas » ?','No coincide','no coincide'),('Comment dire « solution » ?','Solución','solucion'),('Complète : ... una solución.','Quisiera','quisiera')]),('Problème médical','Aunque he seguido el tratamiento, los síntomas persisten.','Bien que j’aie suivi le traitement, les symptômes persistent.', [('Comment dire « symptômes » ?','Síntomas','sintomas'),('Comment dire « traitement » ?','Tratamiento','tratamiento'),('Complète : Aunque ... seguido.','he','he')])],
 'C1': [('Négocier un bail','Si se redujera la fianza, estaría dispuesto a firmar.','Si la caution était réduite, je serais prêt à signer.', [('Comment dire « caution » ?','Fianza','fianza'),('Comment dire « signer » ?','Firmar','firmar'),('Complète : Si se ... la fianza.','redujera','redujera')]),('Démarches administratives','Le agradecería que me indicara los documentos necesarios.','Je vous serais reconnaissant de m’indiquer les documents nécessaires.', [('Comment dire « documents » ?','Documentos','documentos'),('Complète : Le ... que...','agradecería','agradeceria'),('Complète : que me ...','indicara','indicara')])],
 'C2': [('Malentendu délicat','Lamento que mis palabras se hayan interpretado de ese modo.','Je regrette que mes paroles aient été interprétées ainsi.', [('Comment dire « je regrette » ?','Lamento','lamento'),('Comment dire « paroles » ?','Palabras','palabras'),('Complète : se hayan ...','interpretado','interpretado')]),('Situation de crise','Conviene actuar con cautela sin restar importancia a lo ocurrido.','Il convient d’agir avec prudence sans minimiser ce qui s’est passé.', [('Comment dire « prudence » ?','Cautela','cautela'),('Comment dire « ce qui s’est passé » ?','Lo ocurrido','lo ocurrido'),('Complète : Conviene ...','actuar','actuar')])]
}
for _lvl,_items in SURVIVAL.items():
    LESSONS['es'][_lvl].extend(_items)

CONJUGATION = {
 'A1': ('Présent · tener', 'yo tengo · tú tienes · él tiene · nosotros tenemos', 'Yo ___ una reserva.', 'tengo'),
 'A2': ('Passé composé · haber', 'he ido · has ido · ha ido · hemos ido', 'Hoy ___ ido a la farmacia.', 'he'),
 'B1': ('Passé simple · ir', 'fui · fuiste · fue · fuimos', 'Ayer ___ a la estación.', 'fui'),
 'B2': ('Subjonctif présent · poder', 'pueda · puedas · pueda · podamos', 'Espero que usted ___ ayudarme.', 'pueda'),
 'C1': ('Imparfait du subjonctif · reducir', 'redujera · redujeras · redujera · redujéramos', 'Si se ___ la fianza...', 'redujera'),
 'C2': ('Subjonctif composé · interpretar', 'haya interpretado · hayas interpretado · haya interpretado', 'Lamento que se ___ interpretado así.', 'haya')
}

SCENE = {'A1':'👩‍🎓 Emma : Je suis nouvelle en ville. Peux-tu m’aider ?', 'A2':'🧑‍🎓 Diego : Je dois régler ce problème aujourd’hui.', 'B1':'👨‍🎓 Pablo : Il y a un imprévu, quelle solution proposes-tu ?', 'B2':'👩‍🎓 Lucía : Peux-tu expliquer calmement ce qui ne va pas ?', 'C1':'👩‍🏫 Sofía : Négocie poliment en utilisant une hypothèse.', 'C2':'👩‍🏫 Sofía : Reformule avec précision et diplomatie.'}

def _answer_ok(response, options):
    candidate=normalize(response)
    return bool(candidate) and candidate in {normalize(x) for x in options}

def _streak(completed):
    days={k.split(':')[0] for k,v in completed.items() if v}
    today=date.today(); count=0
    if today.isoformat() not in days:today-=timedelta(days=1)
    while today.isoformat() in days:count+=1;today-=timedelta(days=1)
    return count

def _topic_emoji(title):
    low=normalize(title)
    for word,emoji in [('cafe','☕'),('restaurant','🍽️'),('farmacia','💊'),('pharmacie','💊'),('hotel','🏨'),('urgence','🚑'),('train','🚆'),('bus','🚌'),('deplacer','🧭'),('courses','🛒'),('logement','🏠'),('bail','🏠'),('medical','🏥')]:
        if word in low:return emoji
    return '🌍'

def render(world,lang):
    today=date.today()
    lessons_by_level=LESSONS.get(lang,LESSONS['es'])
    academy=world.setdefault('academy_v84',{})
    data=academy.setdefault(lang,{'level':'A1','completed':{},'attempts':{},'xp':0})
    data.setdefault('completed',{});data.setdefault('attempts',{});data.setdefault('xp',0)
    data.setdefault('notes',{});data.setdefault('stars',{});data.setdefault('review',{})
    st.markdown("""<style>
    .ac90-hero{background:linear-gradient(115deg,#4e49ae,#8661d9,#c68ee6);border-radius:20px;padding:20px 24px;color:white;box-shadow:0 8px 25px #5344a52e;margin:10px 0 14px}
    .ac90-hero strong{font-size:1.4rem;color:white}.ac90-hero p{color:#f8efff;margin:6px 0 0}
    .ac90-card{border-radius:18px;background:linear-gradient(130deg,#fff9ed,#f2f5ff);border:1px solid #e7def4;padding:17px 19px;margin:12px 0;color:#40345d}
    .ac90-card strong{color:#47349d}.ac90-board{background:#fff7df;border-left:5px solid #efb653;border-radius:13px;padding:16px 18px;margin:10px 0;color:#44341e}
    .ac90-steps{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.ac90-step{border-radius:99px;padding:6px 12px;background:#eae6ff;color:#463c93;font-weight:600;font-size:.85rem}
    .ac90-chips{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.ac90-chip{padding:6px 12px;border-radius:99px;background:#e8f7f2;color:#226c57;font-size:.85rem}
    div[data-testid='stVideo']{max-width:580px;margin:auto}
    @keyframes ac90pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
    .ac90-card,.ac90-board{animation:ac90pop .28s ease-out}
    </style>""",unsafe_allow_html=True)
    with st.expander('🏫 Academia · École interactive · V90',expanded=False):
        st.markdown('<div class="ac90-hero"><strong>🎓 Academia Mi Español</strong><p>Apprendre pour vivre, voyager et se débrouiller · Des missions, pas seulement des fiches !</p></div>',unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.metric('⭐ XP',int(data.get('xp',0)))
        c2.metric('🔥 Série',str(_streak(data['completed']))+' j')
        c3.metric('🏅 Leçons',sum(bool(v) for v in data['completed'].values()))
        st.markdown('<div class="ac90-card"><strong>👩‍🏫 Sofía et ta classe</strong><div class="ac90-chips"><span class="ac90-chip">👩🏻 Lucía · curieuse</span><span class="ac90-chip">🧑🏽 Diego · aventurier</span><span class="ac90-chip">👩🏼 Emma · débutante</span><span class="ac90-chip">👨🏾 Pablo · sociable</span></div><small>Des camarades fictifs : ils t’accompagnent dans les situations du quotidien.</small></div>',unsafe_allow_html=True)
        levels=[x for x in LEVELS if x in lessons_by_level]
        level=st.selectbox('📚 Niveau de pratique',levels,index=levels.index(data.get('level','A1')) if data.get('level','A1') in levels else 0,key=f'ac95_academia_level_{lang}',help='Libre choix pour s’entraîner ; ce n’est pas une certification.')
        data['level']=level
        lesson_list=lessons_by_level[level]
        daily_idx=int(hashlib.sha256(f'{today}|{lang}|{level}'.encode()).hexdigest()[:8],16)%len(lesson_list)
        st.caption('🎯 Programme de survie : '+str(len(lesson_list))+' situations disponibles à ce niveau.')
        mode=st.radio('Ton parcours',['📅 Mission du jour','🗺️ Choisir une situation','🔁 Révisions','📖 Cahier de conjugaison'],horizontal=True,key=f'ac90_mode_{lang}')
        if mode=='📖 Cahier de conjugaison':
            if lang=='es':
                for lv in LEVELS:
                    name,forms,example,answer=CONJUGATION[lv]
                    with st.expander(f'{lv} · {name}',expanded=lv==level):
                        st.write(forms)
                        st.caption(example.replace('___','_____'))
                        st.caption('Réponse : '+answer)
            else:st.info('Le cahier détaillé des temps est disponible en espagnol ; les autres langues conservent leurs leçons existantes.')
            return
        if mode=='🔁 Révisions':
            misses=[k for k,v in data['review'].items() if v and k.startswith(f'{lang}:')]
            st.markdown('### 🔁 Mes notions à revoir')
            if misses:
                for k in misses[-12:]:st.write('📌 '+data['review'][k])
                if st.button('🧹 Marquer mes révisions comme relues',key=f'ac90_clear_{lang}'):
                    for k in misses:data['review'].pop(k,None)
                    st.rerun()
            else:st.success('Aucune erreur enregistrée à revoir pour le moment. 🌟')
            st.caption('Les erreurs restent dans ton cahier jusqu’à ce que tu les relises. Tu peux refaire les missions librement.')
            return
        if mode=='🗺️ Choisir une situation':
            idx=st.selectbox('🧳 Quelle situation veux-tu pratiquer ?',list(range(len(lesson_list))),index=daily_idx,format_func=lambda i:_topic_emoji(lesson_list[i][0])+' '+lesson_list[i][0],key=f'ac90_topic_{lang}_{level}')
        else:idx=daily_idx
        title,phrase,translation,questions=lesson_list[idx]
        lesson_id=f'{today}:{level}:{idx}' if mode=='📅 Mission du jour' else f'libre:{level}:{idx}'
        key=f'{lang}:{lesson_id}'
        attempts=data['attempts'].setdefault(key,{})
        st.markdown(f'<div class="ac90-steps"><span class="ac90-step">1 · Observer</span><span class="ac90-step">2 · Comprendre</span><span class="ac90-step">3 · Pratiquer</span><span class="ac90-step">4 · Valider</span></div>',unsafe_allow_html=True)
        st.markdown(f'### {_topic_emoji(title)} {title} <small>· {level}</small>',unsafe_allow_html=True)
        st.progress(sum(bool(attempts.get(str(i))) for i in range(len(questions)))/len(questions),text='🎯 Avancement de ta mission')
        st.markdown('<div class="ac90-card"><strong>🎭 Mission de survie</strong><p>'+html.escape(SCENE.get(level,'À toi de jouer !'))+'</p><small>Objectif : réussir une conversation utile dans la vraie vie.</small></div>',unsafe_allow_html=True)
        video_topics={'es':{'A1':'Au café','A2':'Pharmacie','B1':'Transport','B2':'Réclamation','C1':'Logement','C2':'Malentendu'},'en':{'A1':'At the café'},'de':{'A1':'Im Café'},'it':{'A1':'Al bar'}}
        video=Path(__file__).parent/'academia_v85_videos'/f'{lang}_{level}.mp4'
        matches=video_topics.get(lang,{}).get(level)==title
        with st.expander('🎬 Regarder la mini-leçon',expanded=False):
            if matches and video.is_file():
                st.video(str(video));st.caption('Mini-vidéo illustrée pré-générée, silencieuse et sous-titrée.')
            else:
                st.info('Cette situation n’a pas encore de vidéo correspondante. Voici une scène guidée à la place.')
                st.write('👩‍🏫 Sofía : '+phrase)
                if st.button('👩🏼 Emma : répète la phrase',key=f'ac90_scene_{lang}_{lesson_id}'):
                    st.success('👩🏼 Emma : '+phrase)
        st.markdown('<div class="ac90-board"><b>👩‍🏫 Sofía explique</b><p style="font-size:1.2rem">'+html.escape(phrase)+'</p><small>🇫🇷 '+html.escape(translation)+'</small></div>',unsafe_allow_html=True)
        if lang=='es':
            name,forms,ex,ans=CONJUGATION[level]
            with st.expander('🧠 Point conjugaison · '+name):
                st.write('**À retenir :** '+forms)
                st.write('**Exemple :** '+ex)
                with st.popover('🔎 Voir la correction'):st.write(ans)
        st.caption('🔊 Prononce la phrase à voix haute, puis réponds. Les accents et la ponctuation ne sont pas pénalisés.')
        st.markdown('### ✍️ À toi de jouer')
        for i,(prompt,example,*accepted) in enumerate(questions):
            st.markdown(f'**{i+1}/{len(questions)} · {prompt}**')
            response=st.text_input('Ta réponse',key=f'ac90_ans_{lang}_{lesson_id}_{i}',placeholder='Écris dans la langue étudiée…',label_visibility='collapsed')
            a,b=st.columns([1,2])
            with a:
                if st.button('✅ Vérifier',key=f'ac90_check_{lang}_{lesson_id}_{i}',disabled=not response.strip()):
                    correct=_answer_ok(response,[example]+accepted)
                    attempts[str(i)]=correct
                    if correct:
                        data['review'].pop(f'{key}:{i}',None)
                        st.toast('¡Excelente! ⭐')
                    else:
                        data['review'][f'{key}:{i}']=f'{title} — {prompt} → {example}'
                        st.toast('Encore un essai ! Tu peux consulter l’indice. 💙')
            with b:
                with st.popover('💡 Indice'):
                    st.write('Premier mot : **'+example.split()[0]+'**')
                    st.caption('Essaie d’abord sans regarder toute la solution.')
                    if st.checkbox('Afficher la solution',key=f'ac90_hint_{lang}_{lesson_id}_{i}'):st.write('**'+example+'**')
            if attempts.get(str(i)):st.success('⭐ Réponse validée !')
            elif str(i) in attempts:st.warning('À revoir : tu peux réessayer sans pénalité.')
        correct=sum(bool(attempts.get(str(i))) for i in range(len(questions)))
        st.markdown(f'**🎯 Résultat : {correct}/{len(questions)}**')
        done=bool(data['completed'].get(lesson_id))
        if done:st.success('🏆 Mission réussie ! Tu peux la refaire pour t’entraîner.')
        elif correct==len(questions):
            if st.button('🏆 Valider ma mission · +30 XP',key=f'ac90_finish_{lang}_{lesson_id}',type='primary'):
                data['completed'][lesson_id]=True
                data['xp']=int(data.get('xp',0))+30
                st.balloons();st.rerun()
        else:st.caption('💪 Réussis les trois questions pour valider. Les erreurs ne retirent aucun XP.')
        with st.expander('📓 Mon carnet de mission'):
            note=st.text_area('Écris ta propre phrase ou ce que tu as appris',value=data['notes'].get(key,''),key=f'ac90_note_{lang}_{lesson_id}',height=90)
            if st.button('💾 Garder ma note',key=f'ac90_note_save_{lang}_{lesson_id}'):
                data['notes'][key]=note[:1000];st.toast('Note enregistrée dans ta progression de session.')
        st.info('🌍 Défi réel : réutilise cette phrase dans « Ma ville », « Mon voyage » ou avec un ami fictif. Les cours A1–C2 sont des exercices de pratique, pas une certification officielle.')
