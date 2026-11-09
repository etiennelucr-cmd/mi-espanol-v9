"""Parcours ludique CECRL : données du lexique existant, bilans non certifiants."""
import random
from datetime import date, datetime, timedelta
import streamlit as st
import moteur as m
import conjugaison_parcours as cp

LEVELS=['A1','A2','B1','B2','C1','C2']

def state():
    return st.session_state.setdefault('v18_arbre',{'completed':{},'attempts':[],'xp':0,'coins':0,'active':None,'answer':None,'seen':[]})

def words(level,theme):
    return [x for x in m.LEXIQUE if isinstance(x,dict) and x.get('niveau')==level and x.get('theme')==theme and x.get('es') and x.get('fr')]

def themes(level):
    return sorted({x.get('theme') for x in m.LEXIQUE if isinstance(x,dict) and x.get('niveau')==level and x.get('theme')})

def quiz(level,theme,s,stage_index):
    pool=words(level,theme)
    if len(pool)<2:
        st.info('Ce thème a besoin de davantage de mots pour proposer un quiz.');return
    key=(level,theme)
    if s['active'] is None or s['active'].get('key')!=key:
        candidates=[x for x in pool if (level,theme,x['es']) not in s['seen']] or pool
        target=random.choice(candidates)
        wrong=random.sample([x for x in pool if x['fr']!=target['fr']],min(3,len({x['fr'] for x in pool})-1))
        options=list(dict.fromkeys([target['fr']]+[x['fr'] for x in wrong]))
        random.shuffle(options)
        s['active']={'key':key,'target':target,'options':options};s['answer']=None
    q=s['active'];target=q['target']
    st.markdown('#### 🎮 Mini-défi : trouve la traduction')
    st.markdown('### '+target['es'])
    for i,opt in enumerate(q['options']):
        if st.button(opt,key=f'arbre_answer_{level}_{theme}_{stage_index}_{i}',use_container_width=True,disabled=s['answer'] is not None):
            correct=(opt==target['fr'])
            s['answer']=opt
            s['attempts'].append({'date':date.today().isoformat(),'level':level,'theme':theme,'correct':correct,'word':target['es']})
            s['seen']=(s['seen']+[(level,theme,target['es'])])[-100:]
            if correct:s['xp']+=10;s['coins']+=2
            st.rerun()
    if s['answer'] is not None:
        if s['answer']==target['fr']:st.success('¡Excelente! +10 XP et +2 pièces')
        else:st.info('À retenir : '+target['es']+' = '+target['fr'])
        if target.get('exemple'):st.caption('💬 '+target['exemple'])
        if st.button('➡️ Autre défi',type='primary',key=f'arbre_next_{level}_{theme}_{stage_index}'):
            s['active']=None;s['answer']=None;st.rerun()

def tree():
    from v18_style import apply
    apply()
    s=state();st.title('🌳 Mon arbre de compétences')
    st.caption('Parcours progressif : ton niveau suivi et les niveaux précédents sont accessibles. Les niveaux supérieurs restent verrouillés.')
    current=m.preference('niveau_suivi','A1')
    if current not in LEVELS:current='A1'
    unlocked=LEVELS[:LEVELS.index(current)+1]
    st.markdown('<div class="cecrl-road">'+''.join(f'<span class="cecrl-pill {"cecrl-open" if lv in unlocked else "cecrl-locked"}">{"🔓" if lv in unlocked else "🔒"} {lv}</span>' for lv in LEVELS)+'</div>',unsafe_allow_html=True)
    level=st.selectbox('Niveau à explorer (niveaux accessibles)',options=unlocked,index=len(unlocked)-1,key='arbre_niveau_accessible')
    if current!='C2':st.info(f'🔒 {LEVELS[LEVELS.index(current)+1]} et les niveaux suivants sont verrouillés. Ils seront accessibles lorsque ton niveau suivi évoluera après validation dans le parcours CECRL.')
    st.caption('⚠️ Le niveau suivi est modifiable dans la barre latérale : ce verrouillage n’est pas encore une certification automatique. Les XP ne valident pas un niveau.')
    st.metric('⭐ XP aventure',s['xp']);st.caption(f'🪙 {s["coins"]} pièces · récompenses de session')
    t=themes(level)
    if not t:st.warning('Aucun thème disponible pour ce niveau.');return
    selected=st.selectbox('Thème de compétences',t,key='arbre_theme')
    key=level+'|'+selected
    pool=words(level,selected)
    stages=['📖 Découvrir','🎮 Jouer','💬 Pratiquer','🧠 Réviser','🏆 Maîtriser']
    st.subheader(f'{level} · {selected}')
    st.progress(min(1,s['completed'].get(key,0)/len(stages)))
    for i,stage in enumerate(stages):
        progress_step=s['completed'].get(key,0)
        node_class='done' if progress_step>i else 'current' if progress_step==i else 'locked'
        if i:st.markdown('<div class="skill-connector"></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="skill-node {node_class}"><span class="skill-emoji">{stage.split()[0]}</span><div><div class="skill-name">{stage.split(" ",1)[1]}</div><div class="skill-status">{"✓ Terminée" if progress_step>i else "▶ Étape actuelle" if progress_step==i else "🔒 À venir"}</div></div></div>',unsafe_allow_html=True)
        status='✅' if s['completed'].get(key,0)>i else ('🟢' if s['completed'].get(key,0)==i else '🔒')
        with st.expander(f'{status} {stage}',expanded=s['completed'].get(key,0)==i):
            if i==0:
                st.write('Mots essentiels du thème :')
                for w in pool[:12]:st.write('**'+w['es']+'** — '+w['fr']+' · '+w.get('exemple',''))
            elif i in (1,2,3):
                if s['completed'].get(key,0)==i:
                    quiz(level,selected,s,i)
                elif s['completed'].get(key,0)>i:
                    st.success('Étape terminée')
                else:
                    st.info('Termine les étapes précédentes pour débloquer ce défi.')
            else:
                st.info('Maîtrise durable : utilise les contrôles et révisions du parcours historique pour valider réellement la compétence.')
            if i<4 and s['completed'].get(key,0)==i and st.button('Étape découverte / pratiquée ✓',key=f'complete_{i}'):
                s['completed'][key]=i+1;st.rerun()
    st.divider();st.subheader('🔤 Verbes et conjugaisons progressives')
    for lv in LEVELS:
        with st.expander(lv+' · Temps à travailler'+(' 👈' if lv==level else '')):
            for _,label in cp.PARCOURS.get(lv,[]):st.write('• '+str(label))
    st.caption('La pratique complète des verbes reste disponible dans « Verbes et conjugaisons ».')

def progress():
    s=state();st.title('📊 Mes progrès')
    st.caption('Bilans issus des mini-défis joués dans cette session ; ils ne certifient pas ton niveau CECRL.')
    mode=st.radio('Période',['Jour','Semaine','Mois'],horizontal=True)
    days={'Jour':1,'Semaine':7,'Mois':30}[mode]
    cutoff=date.today()-timedelta(days=days-1)
    recent=[a for a in s['attempts'] if date.fromisoformat(a['date'])>=cutoff]
    previous=[a for a in s['attempts'] if cutoff-timedelta(days=days)<=date.fromisoformat(a['date'])<cutoff]
    success=sum(a['correct'] for a in recent)
    c1,c2,c3=st.columns(3)
    c1.metric('Questions jouées',len(recent));c2.metric('Réussite',f'{100*success/len(recent):.0f}%' if recent else '—');c3.metric('Thèmes travaillés',len({(a['level'],a['theme']) for a in recent}))
    if previous and recent:st.caption(f'Période précédente : {100*sum(a["correct"] for a in previous)/len(previous):.0f}% de réussite')
    if recent:
        st.subheader('Par thème')
        for level,theme in sorted({(a['level'],a['theme']) for a in recent}):
            vals=[a for a in recent if (a['level'],a['theme'])==(level,theme)]
            rate=sum(a['correct'] for a in vals)/len(vals)
            st.write(f'{level} · {theme} — {len(vals)} réponses · {rate:.0%} réussies')
            st.progress(rate)
    else:st.info('Joue quelques mini-défis dans ton arbre de compétences pour afficher ton premier bilan.')
    st.info('Pour une véritable évaluation CECRL, il faudra intégrer les résultats des contrôles, de la compréhension et de l’expression orale/écrite, avec stockage durable en base.')
