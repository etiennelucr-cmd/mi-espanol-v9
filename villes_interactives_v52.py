"""V52 - city exploration with branching tourist scenarios, four independent languages."""
import random
import sqlite3
from pathlib import Path
import streamlit as st
from aventure_multilingue_v50 import LANGS, WORLDS, INDEX
from suivi_langues_v48 import enregistrer, enregistrer_phrases, lire

CITIES={
'es':[('Madrid','🇪🇸','Puerta del Sol'),('Barcelone','🇪🇸','Quartier gothique'),('Valence','🇪🇸','Centre historique')],
'en':[('Londres','🇬🇧','Covent Garden'),('Édimbourg','🇬🇧','Royal Mile'),('Dublin','🇮🇪','Temple Bar')],
'de':[('Berlin','🇩🇪','Alexanderplatz'),('Munich','🇩🇪','Marienplatz'),('Hambourg','🇩🇪','Speicherstadt')],
'it':[('Rome','🇮🇹','Piazza Navona'),('Florence','🇮🇹','Piazza della Signoria'),('Venise','🇮🇹','Rialto')]
}
# All 12 worlds are accessible in every city; 4 featured places change by destination.
FEATURES={
'es':[[4,0,1,9],[7,5,8,9],[8,4,2,10]],
'en':[[0,5,9,1],[2,7,9,6],[6,5,1,4]],
'de':[[0,4,1,7],[5,8,9,2],[0,6,7,11]],
'it':[[4,5,9,1],[9,8,5,2],[0,4,1,7]]
}

# Progression par langue, ville et lieu, conservée entre les sessions locales.
_ADAPT_DB=Path(__file__).with_name('progression_situations_v53.sqlite3')
def _db():
    db=sqlite3.connect(str(_ADAPT_DB),timeout=5)
    db.execute("CREATE TABLE IF NOT EXISTS situations_v53 (lang TEXT, city INTEGER, world INTEGER, visit INTEGER, score INTEGER, total INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(lang,city,world,visit))")
    return db

def _history(lang,city,world):
    try:
        with _db() as db:
            return [r[0] for r in db.execute('SELECT score FROM situations_v53 WHERE lang=? AND city=? AND world=? ORDER BY visit DESC LIMIT 5',(lang,city,world)).fetchall()][::-1]
    except sqlite3.Error:
        return st.session_state.get(('v53_history',lang,city,world),[])

def _save_history(lang,city,world,score):
    try:
        with _db() as db:
            visit=db.execute('SELECT COALESCE(MAX(visit),0)+1 FROM situations_v53 WHERE lang=? AND city=? AND world=?',(lang,city,world)).fetchone()[0]
            db.execute('INSERT INTO situations_v53(lang,city,world,visit,score,total) VALUES(?,?,?,?,?,3)',(lang,city,world,visit,score))
    except sqlite3.Error:
        st.session_state.setdefault(('v53_history',lang,city,world),[]).append(score)

def _stage(scores):
    # Two strong recent independent visits unlock the next stage; poor results provide support.
    if len(scores)>=4 and sum(x>=2 for x in scores[-4:])>=3 and scores[-2:] == [3,3]:
        return 3
    if len(scores)>=2 and all(x>=2 for x in scores[-2:]):
        return 2
    return 1

def _state_key(lang,city,world):
    return f'v52_{lang}_{city}_{world}'

def _new_state():
    return {'step':0,'score':0,'choices':[],'path':[],'done':False,'variant':random.randrange(1000000)}

def page():
    st.markdown("""<style>
    .v52-hero{background:linear-gradient(125deg,#eaa25c,#d98371,#8bb3a1);border-radius:25px;padding:24px;text-align:center;color:#402326}
    .v52-hero h1{margin:0;font-size:2rem}.v52-hero p{margin:5px 0}
    .v52-scene{border:2px solid #c98655;background:#ffe8c7;border-radius:20px;padding:20px;color:#513926;font-size:1.1rem;margin:10px 0}
    .v52-scene strong{font-size:1.3rem}.v52-note{background:#e7f6ed;border-radius:14px;padding:12px;color:#245a3d}
    </style><div class="v52-hero"><h1>🧭 Voyage autour du monde</h1><p>Choisis une ville, explore ses lieux et vis de petites aventures !</p></div>""",unsafe_allow_html=True)
    lang=st.selectbox('🌍 Langue de mon voyage',list(CITIES),format_func=lambda x:' '.join(LANGS[x]),key='v52_lang')
    st.caption('Une seule langue à la fois · les progrès sont séparés · tous les lieux sont libres d’accès')
    st.subheader('🏙️ Choisis ta ville')
    st.caption('Choisis ta destination : chaque ville est une porte vers tes aventures.')
    cities=CITIES[lang]
    cols=st.columns(3)
    for i,(name,flag,area) in enumerate(cities):
        with cols[i]:
            if st.button(f'{flag} {name}\n📍 {area}',key=f'v52_city_{lang}_{i}',use_container_width=True):
                st.session_state.v52_city=i
                st.session_state.pop('v52_world',None)
                st.rerun()
    ci=st.session_state.get('v52_city',0)
    city,flag,area=cities[ci]
    st.info(f'📍 Tu explores **{city}** — {area}. Les situations sont des simulations touristiques, pas des itinéraires géographiques réels.')
    st.subheader('🗺️ Où veux-tu aller ?')
    featured=FEATURES[lang][ci]
    st.caption('⭐ Lieux conseillés dans cette ville')
    _place_buttons(lang,ci,featured,'featured')
    with st.expander('🧳 Voir les 12 lieux et situations disponibles'):
        _place_buttons(lang,ci,list(range(len(WORLDS))),'all')
    world=st.session_state.get('v52_world')
    if world is None:
        st.write('👆 Choisis un lieu pour commencer ton aventure.')
        return
    emoji,name,phrases=WORLDS[world]
    st.divider()
    st.subheader(f'{emoji} {name} · {city}')
    tabs=st.tabs(['🎭 Jouer la scène','🧩 Puzzle de phrases','📖 Mes phrases utiles','🆘 Mode voyage'])
    with tabs[0]: _scene(lang,ci,world,phrases,city)
    with tabs[1]: _puzzle(lang,ci,world,phrases)
    with tabs[2]:
        st.caption('Des phrases à découvrir avant de jouer. Les traductions restent en français.')
        for row in phrases:
            with st.container(border=True):
                st.markdown('**'+row[INDEX[lang]]+'**')
                st.caption('🇫🇷 '+row[0])
    with tabs[3]:
        st.caption('Accès immédiat sans test ni déblocage.')
        for row in phrases:
            st.markdown(f'**{row[INDEX[lang]]}** — {row[0]}')
    st.caption('Les résultats de ces choix évaluent la compréhension et la sélection de phrases, pas la prononciation ni le niveau CECRL global.')

def _place_buttons(lang,ci,indices,group):
    cols=st.columns(4)
    for j,idx in enumerate(indices):
        emoji,name,_=WORLDS[idx]
        with cols[j%4]:
            if st.button(f'{emoji} {name}',key=f'v52_{group}_{lang}_{ci}_{idx}',use_container_width=True):
                st.session_state.v52_world=idx
                st.rerun()

def _scene(lang,ci,world,phrases,city):
    key=_state_key(lang,ci,world)
    if key not in st.session_state: st.session_state[key]=_new_state()
    state=st.session_state[key]
    history=_history(lang,ci,world)
    stage=_stage(history)
    labels={1:'🌱 Découverte',2:'🧭 Autonomie',3:'🎲 Imprévu'}
    st.info(f'**{labels[stage]}** · {len(history)} visite(s) terminée(s) dans ce lieu · progression selon tes dernières réussites')
    if stage==1: st.caption('Reconnais des phrases utiles. Deux aventures réussies débloquent l’autonomie.')
    elif stage==2: st.caption('Les situations changent : tu dois sélectionner la bonne réponse à une demande concrète.')
    else: st.caption('Défi surprise : demandes plus variées, avec moins d’indices.')
    if st.button('🔀 Recommencer avec une variante',key=key+'_reset'):
        st.session_state[key]=_new_state()
        st.rerun()
    if state['done']:
        st.success(f"🏆 Aventure terminée à {city} ! {state['score']}/3 bonnes décisions.")
        if state['score']==3: st.balloons()
        st.write('Tu peux visiter un autre lieu ou essayer une nouvelle variante. Chaque visite complète compte une fois dans la progression locale.')
        return
    step=state['step']
    # Paths vary by answer: a mistaken decision leads to a recovery scene, while a correct
    # decision opens the next planned tourist interaction. No fake generative dialogue.
    offset=(state['variant']+ci+world+len(history)*2)%len(phrases)
    if step==0: phrase_idx=offset
    elif step==1: phrase_idx=(offset+(1 if state['path'][0] else 2))%len(phrases)
    else: phrase_idx=(offset+(2 if state['path'][-1] else 3))%len(phrases)
    row=phrases[phrase_idx]
    target=row[INDEX[lang]]
    st.progress(step/3,text=f'🎬 Scène {step+1} sur 3')
    roles=['🧳 Tu arrives dans ce lieu','🧑 Une personne te répond' if state['path'] and state['path'][-1] else '💡 Tu dois reformuler ta demande','🎯 Dernier défi avant de repartir' if state['path'] and state['path'][-1] else '🛟 Tu demandes une précision']
    if stage==1:
        instruction=f'Tu veux dire : « {row[0]} »'
    elif stage==2:
        instruction=f'Ton objectif : {row[0]}. Choisis ce que tu dirais au personnage.'
    else:
        surprises=['Le personnage te demande de préciser.','La situation vient de changer !','Tu dois réagir rapidement.']
        instruction=f'{surprises[step]} Ta mission : {row[0]}'
    st.markdown(f'<div class="v52-scene"><small>{roles[step]}</small><p>{instruction}</p></div>',unsafe_allow_html=True)
    st.write('**Quelle phrase peux-tu utiliser ?**')
    others=[r[INDEX[lang]] for i,r in enumerate(phrases) if i!=phrase_idx]
    rng=random.Random(f'{lang}:{ci}:{world}:{state["variant"]}:{step}:{stage}')
    options=[target]+rng.sample(others,min(len(others),3 if stage==3 else 2))
    rng.shuffle(options)
    choice_key=f'{key}_choice_{state["variant"]}_{step}'
    selection=st.radio('Choisis ta réponse',options,index=None,key=choice_key)
    feedback_key=f'{key}_feedback_{step}'
    if feedback_key not in st.session_state:
        if st.button('💬 Parler au personnage',disabled=selection is None,key=f'{key}_check_{step}',type='primary'):
            correct=selection==target
            state['choices'].append((target,row[0],selection,correct))
            state['path'].append(correct)
            state['score']+=int(correct)
            st.session_state[feedback_key]=correct
            st.rerun()
    else:
        if st.session_state[feedback_key]:
            st.success('🌟 Bravo ! Le personnage a compris ta demande.')
        else:
            st.warning('🧩 Le personnage hésite. Voici la phrase utile :')
            st.markdown('**'+target+'**')
            st.caption('🇫🇷 '+row[0])
        st.markdown('<div class="v52-note">'+('✨ La conversation continue !' if state['path'][-1] else '🤝 Pas grave : tu peux te rattraper à la prochaine scène.')+'</div>',unsafe_allow_html=True)
        if st.button('➡️ Continuer' if step<2 else '🏁 Terminer',key=f'{key}_next_{step}',type='primary'):
            st.session_state.pop(feedback_key,None)
            if step==2:
                state['done']=True
                activity=f'v52:ville:{lang}:{ci}:lieu:{world}'
                enregistrer(lang,activity,state['score'],3)
                _save_history(lang,ci,world,state['score'])
                pairs=[(x[0],x[1]) for x in state['choices']]
                responses=[x[2] for x in state['choices']]
                # Tracking records selected target-language phrases, not oral production.
                enregistrer_phrases(lang,activity,pairs,responses)
            else: state['step']+=1
            st.rerun()


def _puzzle(lang, ci, world, phrases):
    """Reconstruction active d'une phrase, avec validation explicite et suivi distinct."""
    key=f'v54_puzzle_{lang}_{ci}_{world}'
    if key not in st.session_state:
        st.session_state[key]={'phrase':random.randrange(len(phrases)), 'picked':[], 'checked':False}
    state=st.session_state[key]
    row=phrases[state['phrase']]
    target=row[INDEX[lang]]
    words=target.split()
    st.caption('Construis la phrase dans la langue étudiée, mot après mot. Les mots peuvent être répétés.')
    st.info('🇫🇷 '+row[0])
    rng=random.Random(f'{key}:{state["phrase"]}')
    shuffled=list(enumerate(words))
    rng.shuffle(shuffled)
    st.write('**Ta phrase :** '+' '.join(words[i] for i in state['picked']) if state['picked'] else '**Ta phrase :** …')
    if not state['checked']:
        remaining=[(i,w) for i,w in shuffled if i not in state['picked']]
        cols=st.columns(3)
        for j,(i,w) in enumerate(remaining):
            with cols[j%3]:
                if st.button(w,key=f'{key}_word_{i}',use_container_width=True):
                    state['picked'].append(i)
                    st.rerun()
        if st.button('↩️ Effacer le dernier mot',key=key+'_undo',disabled=not state['picked']):
            state['picked'].pop();st.rerun()
        if st.button('✅ Vérifier ma phrase',key=key+'_check',disabled=len(state['picked'])!=len(words),type='primary'):
            state['checked']=True
            state['correct']=[words[i] for i in state['picked']]==words
            activity=f'v54:puzzle:{lang}:{ci}:{world}'
            enregistrer(lang,activity,int(state['correct']),1)
            enregistrer_phrases(lang,activity,[(target,row[0])],[' '.join(words[i] for i in state['picked'])])
            st.rerun()
    else:
        if state['correct']:st.success('🌟 Bravo ! Tu as reconstruit la phrase.')
        else:st.warning('La bonne phrase est : '+target)
        if st.button('🎲 Une autre phrase',key=key+'_next',type='primary'):
            next_idx=(state['phrase']+random.randrange(1,len(phrases)))%len(phrases) if len(phrases)>1 else 0
            st.session_state[key]={'phrase':next_idx,'picked':[],'checked':False}
            st.rerun()
