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

def render(world,lang):
    today=date.today()
    all_lessons=LESSONS.get(lang,LESSONS['es'])
    academy=world.setdefault('academy_v84',{})
    langdata=academy.setdefault(lang,{'level':'A1','completed':{},'attempts':{},'xp':0})
    st.markdown('''<style>
    .academy-classmates{background:linear-gradient(120deg,#fff9ed,#f0f4ff);border:1px solid #e9dff2;border-radius:17px;padding:15px 19px;margin:12px 0;color:#46376d;box-shadow:0 4px 14px #4a367015}
    .academy-classmates b{font-size:1.08rem}.academy-classmates p{font-size:1.07rem;margin:10px 0}.academy-classmates small{color:#726a87}
    .academy-hero{background:linear-gradient(110deg,#273b9d,#7156d9,#ad78de);color:white;padding:18px 22px;border-radius:19px;margin:10px 0;box-shadow:0 8px 22px #35276b25}
    .academy-hero b{font-size:1.25rem}.academy-hero p{margin:5px 0 0;color:#f1eaff}
    .academy-board{background:#fff9e9;border:2px solid #e7d9b0;border-radius:15px;padding:15px;color:#49351b;animation:academyIn .35s ease-out}
    @keyframes academyIn{from{opacity:.5;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
    .academy-meter{height:9px;border-radius:20px;background:#ddd8f3;overflow:hidden;margin:8px 0}.academy-meter span{display:block;height:100%;background:linear-gradient(90deg,#40bb9c,#7565e7);transition:width .3s}
    </style>''',unsafe_allow_html=True)
    with st.expander('🏫 Academia · Mon école de langues · Cours du jour',expanded=False):
        st.markdown('<div class="academy-hero"><b>👩‍🏫 ¡Bienvenido a clase!</b><p>Une petite leçon par jour, puis pratique en ville 🌍</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="academy-classmates"><b>👩‍🏫 Sofía · Ta classe virtuelle</b><p>👩🏻 Lucía &nbsp; 🧑🏽 Diego &nbsp; 👩🏼 Emma &nbsp; 👨🏾 Pablo</p><small>Des camarades fictifs pour apprendre ensemble, à ton rythme.</small></div>',unsafe_allow_html=True)
        opts=[l for l in LEVELS if l in all_lessons]
        level=st.selectbox('📚 Niveau des exercices (choix libre, sans certification)',opts,index=opts.index(langdata.get('level','A1')) if langdata.get('level','A1') in opts else 0,key=f'acad_level_{lang}')
        langdata['level']=level
        lessons=all_lessons[level]
        idx=int(hashlib.sha256(f'{today.isoformat()}|{lang}|{level}'.encode()).hexdigest()[:8],16)%len(lessons)
        title,phrase,translation,questions=lessons[idx]
        lesson_id=f'{today.isoformat()}:{level}:{idx}'
        done=langdata['completed'].get(lesson_id,False)
        total=sum(1 for k,v in langdata['completed'].items() if v)
        dates={k.split(':')[0] for k,v in langdata['completed'].items() if v}
        streak=0;day=today
        if day.isoformat() not in dates:day-=timedelta(days=1)
        while day.isoformat() in dates:streak+=1;day-=timedelta(days=1)
        st.caption(f'⭐ {langdata.get("xp",0)} XP · 🔥 {streak} jour(s) de suite · 🏅 {total} leçon(s) terminée(s)')
        st.markdown(f'**📖 Leçon du jour : {html.escape(title)}**')
        video=Path(__file__).parent/'academia_v85_videos'/f'{lang}_{level}.mp4'
        with st.expander('🎬 Classe animée · Regarder le mini-cours',expanded=True):
            st.caption('Vidéo courte pré-générée : Sofía et trois camarades illustrent une situation de survie. Sous-titres intégrés, sans API ni coût.')
            if video.is_file(): st.video(str(video))
            else: st.info('Vidéo absente : ajoute le dossier academia_v85_videos à côté de ce fichier.')
            st.caption('Après la vidéo, réponds aux exercices pour vérifier ce que tu as compris.')
        grammar={
          'es':{'A1':'Présent : ser, estar, tener, querer ; demander et commander.', 'A2':'Passé : perfecto, indefinido et imperfecto ; pharmacie et rendez-vous.', 'B1':'Futur, conditionnel et introduction au subjonctif ; imprévus de transport.', 'B2':'Subjonctif présent et passé ; réclamations et négociations.', 'C1':'Imparfait du subjonctif et hypothèses ; logement et démarches.', 'C2':'Concordance, nuances et registres ; malentendus et situations complexes.'},
          'en':{'A1':'Present simple ; café, présentation et directions.'},
          'de':{'A1':'Präsens ; café, présentation et transports.'},
          'it':{'A1':'Presente ; café, présentation et orientation.'}}
        st.caption('📘 Grammaire / survie : '+grammar.get(lang,{}).get(level,'Situations pratiques et grammaire adaptées au niveau.'))
        st.markdown(f'<div class="academy-board">👩‍🏫 <b>La professeure explique :</b><p style="font-size:1.15rem">{html.escape(phrase)}</p><small>🇫🇷 {html.escape(translation)}</small></div>',unsafe_allow_html=True)
        st.caption('💡 Lis la phrase à voix haute, puis réponds aux trois questions.')
        key=f'{lang}:{lesson_id}'
        attempts=langdata['attempts'].setdefault(key,{})
        if done:st.success('🎉 Leçon du jour terminée ! Reviens demain pour une nouvelle mission.')
        else:
            for i,(prompt,example,*accepted) in enumerate(questions):
                st.markdown(f'**{i+1}/3 · {prompt}**')
                response=st.text_input('Ta réponse',key=f'acad_{lang}_{lesson_id}_{i}',placeholder='Écris dans la langue étudiée…',label_visibility='collapsed')
                c1,c2=st.columns([1,2])
                with c1:
                    if st.button('✓ Vérifier',key=f'acad_check_{lang}_{lesson_id}_{i}',disabled=not response.strip()):
                        good=normalize(response) in {normalize(x) for x in accepted+[example]}
                        attempts[str(i)]=good
                        if good:st.toast('¡Muy bien! ⭐')
                        else:st.toast('Presque ! Essaie avec l’indice 💙')
                with c2:
                    with st.popover('💡 Indice / solution'):
                        st.write(f'Exemple : **{example}**')
                if attempts.get(str(i)):st.caption('✅ Bonne réponse !')
            correct=sum(bool(attempts.get(str(i))) for i in range(len(questions)))
            st.markdown(f'<div class="academy-meter"><span style="width:{int(100*correct/len(questions))}%"></span></div>',unsafe_allow_html=True)
            st.caption(f'{correct}/{len(questions)} réponses validées')
            if correct==len(questions):
                if st.button('🏆 Terminer la leçon · +30 XP',key=f'acad_finish_{lang}_{lesson_id}'):
                    langdata['completed'][lesson_id]=True;langdata['xp']=int(langdata.get('xp',0))+30
                    st.balloons();st.rerun()
        st.info('🎮 Mission en ville : utilise la phrase du jour avec un personnage ou dans une situation de voyage. Les niveaux avancés sont des aperçus. Les vidéos sont pré-générées, sans voix ni génération à la demande. Ce n’est pas une certification.')
