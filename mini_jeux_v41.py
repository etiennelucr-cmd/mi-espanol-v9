"""Three mini-games based on the existing CECRL lexicon; results are non-certifying."""
import random
from datetime import datetime
import streamlit as st
import moteur as m
import progression_v40

MODES=['🎯 Quiz express','✍️ Traduction active','🧩 Phrase à reconstruire']
PHRASES=[('A1','Me llamo Ana.','Je m’appelle Ana.'),('A1','Quiero un café.','Je voudrais un café.'),
         ('A1','Mi casa es pequeña.','Ma maison est petite.'),('A2','Voy a la estación.','Je vais à la gare.'),
         ('B1','Ayer fui al mercado.','Hier, je suis allé au marché.'),
         ('B2','Si tuviera tiempo, viajaría más.','Si j’avais le temps, je voyagerais davantage.'),
         ('C1','Aunque llueva, saldremos.','Même s’il pleut, nous sortirons.'),
         ('C2','No bien hubo llegado, empezó la reunión.','À peine était-il arrivé que la réunion commença.')]

def state():
    return st.session_state.setdefault('v41_games',{'attempts':[],'xp':0,'coins':0,'question':None,'answer':None,'round':0})

def pool(level):
    data=[]
    for x in m.LEXIQUE:
        if not isinstance(x,dict) or x.get('niveau')!=level:continue
        es=x.get('es') or x.get('espagnol');fr=x.get('fr') or x.get('francais')
        if isinstance(es,str) and isinstance(fr,str) and 1<len(es)<80 and 1<len(fr)<100:
            data.append((es.strip(),fr.strip(),str(x.get('theme',''))))
    return list({(a,b,c) for a,b,c in data})

def new_question(mode,level):
    items=pool(level)
    if mode==MODES[2]:
        choices=[(es,fr) for lv,es,fr in PHRASES if lv==level]
        if not choices:return None
        es,fr=random.choice(choices)
        tokens=es.split();shuffled=tokens[:];random.shuffle(shuffled)
        return {'mode':mode,'level':level,'target':es,'hint':fr,'tokens':shuffled,'selection':[],'theme':'Phrases'}
    if len(items)<4:return None
    target=random.choice(items)
    if mode==MODES[0]:
        others=list({x[1] for x in items if x[1]!=target[1]})
        options=random.sample(others,min(3,len(others)))+[target[1]]
        random.shuffle(options)
        return {'mode':mode,'level':level,'target':target[1],'prompt':target[0],'options':options,'theme':target[2]}
    return {'mode':mode,'level':level,'target':target[0],'prompt':target[1],'theme':target[2]}

def _norm(text):
    return ' '.join(str(text).casefold().strip().strip('.!?¡¿').split())

def grade(s,answer):
    q=s['question'];correct=_norm(answer)==_norm(q['target'])
    s['attempts'].append({'date':datetime.now().isoformat(timespec='seconds'), 'mode':q['mode'],
                          'level':q['level'],'theme':q['theme'],'correct':correct})
    s['attempts']=s['attempts'][-2000:]
    if correct:s['xp']+=10;s['coins']+=2
    s['answer']={'correct':correct,'target':q['target']}

def page():
    st.title('🎲 Les mini-jeux de Lucía')
    st.caption('Jeux tirés du vocabulaire de ton niveau. Ces résultats servent au suivi des entraînements, pas au déblocage CECRL.')
    s=state()
    a,b,c=st.columns(3)
    a.metric('🎯 Parties jouées',len(s['attempts']))
    b.metric('⭐ XP mini-jeux',s['xp'])
    c.metric('🪙 Pièces mini-jeux',s['coins'])
    mode=st.selectbox('Choisis ton jeu',MODES,key='v41_mode')
    allowed=progression_v40.accessible_levels()
    level=st.selectbox('Niveau accessible',allowed,key='v41_level')
    if not s['question'] or s['question']['mode']!=mode or s['question']['level']!=level:
        s['question']=new_question(mode,level);s['answer']=None
    q=s['question']
    if q is None:
        st.info('Pas assez de mots ou de phrases disponibles pour ce jeu à ce niveau.')
        return
    st.progress(min(1,len(s['attempts'])%10/10))
    if mode==MODES[0]:
        st.subheader('🇪🇸 '+q['prompt'])
        st.write('Quelle est la traduction française ?')
        for i,option in enumerate(q['options']):
            if st.button(option,key=f'v41_q_{s["round"]}_{i}',disabled=s['answer'] is not None,use_container_width=True):
                grade(s,option);st.rerun()
    elif mode==MODES[1]:
        st.subheader('🇫🇷 '+q['prompt'])
        st.write('Écris la traduction espagnole.')
        with st.form('v41_translation',clear_on_submit=False):
            text=st.text_input('Ta réponse',key=f'v41_t_{s["round"]}',disabled=s['answer'] is not None)
            if st.form_submit_button('Vérifier',disabled=s['answer'] is not None) and text.strip():
                grade(s,text);st.rerun()
    else:
        st.subheader('🧩 '+q['hint'])
        st.write('Reconstruis la phrase espagnole dans le bon ordre.')
        st.markdown('**Ta phrase :** '+(' '.join(q['selection']) or '…'))
        remaining=list(enumerate(q['tokens']))
        used=set(q.get('used',[]))
        cols=st.columns(min(4,len(remaining)))
        for i,word in remaining:
            with cols[i%len(cols)]:
                if st.button(word,key=f'v41_word_{s["round"]}_{i}',disabled=i in used or s['answer'] is not None):
                    q['selection'].append(word);q.setdefault('used',[]).append(i);st.rerun()
        x,y=st.columns(2)
        if x.button('↶ Recommencer la phrase',disabled=s['answer'] is not None):
            q['selection']=[];q['used']=[];st.rerun()
        if y.button('Vérifier ma phrase',disabled=s['answer'] is not None or not q['selection']):
            grade(s,' '.join(q['selection']));st.rerun()
    if s['answer'] is not None:
        if s['answer']['correct']:st.success('¡Excelente! +10 XP et +2 pièces')
        else:st.info('À retenir : '+s['answer']['target'])
        if st.button('Question suivante →',type='primary',key='v41_next'):
            s['round']+=1;s['question']=new_question(mode,level);s['answer']=None;st.rerun()
    if s['attempts']:
        st.caption(f"Réussite aux mini-jeux : {sum(x['correct'] for x in s['attempts'])/len(s['attempts']):.0%} sur {len(s['attempts'])} réponses. Résultats conservés dans la session ou dans ta sauvegarde d'aventure.")
