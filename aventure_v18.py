"""Mi Español V18: mode aventure sans modification des tables historiques."""
import random
from pathlib import Path
import streamlit as st

MISSIONS = [
    {'titre':'Premier bonjour','lieu':'Madrid','icone':'👋','personnage':'Lucía','intro':'Tu arrives à Madrid. Lucía vient te saluer.','dialogue':[('¡Hola! ¿Cómo te llamas?','Me llamo Alex.',['Me llamo Alex.','Tengo hambre.','Son las tres.']),('¡Mucho gusto! ¿De dónde eres?','Soy de Francia.',['Estoy en casa.','Soy de Francia.','Buenas noches.'])]},
    {'titre':'Un café, por favor','lieu':'Madrid','icone':'☕','personnage':'Carlos','intro':'Carlos t’accueille dans son café.','dialogue':[('¿Qué quieres tomar?','Un café, por favor.',['Un café, por favor.','Soy estudiante.','Hasta luego.']),('¿Con leche o solo?','Con leche, gracias.',['La cuenta.','Con leche, gracias.','Tengo un perro.'])]},
    {'titre':'Trouver son chemin','lieu':'Madrid','icone':'🗺️','personnage':'Sofía','intro':'Tu cherches la gare. Sofía peut t’aider.','dialogue':[('¡Hola! ¿Qué buscas?','Busco la estación.',['Busco la estación.','Me gusta el queso.','Tengo sueño.']),('Está a la derecha. ¿Entiendes?','Sí, muchas gracias.',['No tengo dinero.','Buenos días.','Sí, muchas gracias.'])]},
    {'titre':'Au marché','lieu':'Valence','icone':'🍊','personnage':'Lucía','intro':'Tu achètes des fruits pour un pique-nique.','dialogue':[('¿Qué quieres comprar?','Quiero naranjas.',['Quiero naranjas.','Estoy perdido.','Me llamo Ana.']),('¿Cuántas naranjas?','Dos, por favor.',['Hasta mañana.','Dos, por favor.','Soy francés.'])]},
    {'titre':'La fête surprise','lieu':'Séville','icone':'🎉','personnage':'Sofía','intro':'Sofía organise une fête. Aide-la à inviter ses amis.','dialogue':[('¿Vienes a la fiesta?','¡Sí, claro!',['Tengo un libro.','¡Sí, claro!','¿Dónde está el banco?']),('¿A qué hora nos vemos?','A las ocho.',['A las ocho.','Con leche.','Me llamo Alex.'])]},
]

def _state():
    if 'aventura_v18' not in st.session_state:
        st.session_state.aventura_v18={'xp':0,'pieces':0,'terminees':[],'mission':None,'etape':0,'choix':None,'erreurs':0,'jeu':None,'serie':0}
    return st.session_state.aventura_v18

def _nouveau_jeu():
    import moteur as m
    mots=[]
    for item in m.LEXIQUE:
        if isinstance(item,dict):
            es=item.get('espagnol') or item.get('es') or item.get('mot')
            fr=item.get('francais') or item.get('fr') or item.get('traduction')
            if isinstance(es,str) and isinstance(fr,str) and es and fr:
                mots.append((es,fr))
    if len(mots)<4:
        mots=[('hola','bonjour'),('gracias','merci'),('agua','eau'),('casa','maison'),('libro','livre')]
    sample=random.sample(mots,min(4,len(mots)))
    bonne=sample[0]
    options=[x[1] for x in sample]
    random.shuffle(options)
    return {'mot':bonne[0],'bonne':bonne[1],'options':options}

def page(compact=False):
    from v18_style import apply
    apply()
    s=_state()
    st.markdown('''<style>
    .v18-hero{padding:1.4rem;border-radius:20px;background:linear-gradient(115deg,#aa1528,#ed7c2e);color:white;margin-bottom:1rem}
    .v18-hero h1,.v18-hero p{color:white!important;margin:.2rem 0}
    div.stButton>button[kind="primary"]{border-radius:14px;font-weight:750}
    </style>''',unsafe_allow_html=True)
    if not compact:
        st.markdown('<div class="v18-hero"><h1>🎮 ¡Vamos de aventura!</h1><p>Une mission, quelques minutes, zéro pression.</p></div>',unsafe_allow_html=True)
    if not compact:
        a,b,c=st.columns(3)
        a.metric('⭐ XP aventure (session)',s['xp']);b.metric('🪙 Pièces (session)',s['pieces']);c.metric('🏅 Missions',f"{len(s['terminees'])}/{len(MISSIONS)}")
    st.progress(len(s['terminees'])/len(MISSIONS))
    tab1,tab2,tab3=st.tabs(['🗺️ Aventure','🎲 Jeu éclair','🎁 Récompenses'])
    with tab1:
        if s['mission'] is None:
            st.subheader('🗺️ Choisis ta prochaine mission')
            st.caption('Les missions sont des histoires courtes. Les personnages t’accompagnent à ton rythme.')
            for i,mission in enumerate(MISSIONS):
                ok=i==0 or i-1 in s['terminees']
                fini=i in s['terminees']
                personnage_emoji={'Lucía':'👩🏽','Carlos':'👨🏻‍🍳','Sofía':'👩🏻‍🎓'}.get(mission['personnage'],'🧑')
                col,btn=st.columns([4,1],vertical_alignment='center')
                with col:
                    st.markdown(f"""<div class="mission-card {'mission-done' if fini else 'mission-locked' if not ok else 'mission-ready'}">
                    <div class="mission-avatar">{personnage_emoji}</div><div class="mission-info">
                    <div class="mission-label">{'🏆 TERMINÉE' if fini else '🔒 À DÉBLOQUER' if not ok else '✨ MISSION DISPONIBLE'}</div>
                    <div class="mission-title">{mission['icone']} {mission['titre']}</div>
                    <div class="mission-sub">📍 {mission['lieu']} · {mission['personnage']} · +30 XP</div></div></div>""",unsafe_allow_html=True)
                with btn:
                    if st.button('↻ Rejouer' if fini else '▶ Jouer',key=f'v18_m_{i}',disabled=not ok,use_container_width=True):
                        s.update(mission=i,etape=0,choix=None,erreurs=0)
                        st.rerun()
        else:
            mission=MISSIONS[s['mission']]
            st.subheader(f"{mission['icone']} {mission['titre']}")
            st.caption(f"📍 {mission['lieu']} · {mission['personnage']}")
            avatar={'Lucía':'👩🏽','Carlos':'👨🏻‍🍳','Sofía':'👩🏻‍🎓'}.get(mission['personnage'],'🧑')
            photo={'Lucía':'lucia.png','Carlos':'carlos.png','Sofía':'sofia.png'}.get(mission['personnage'])
            cphoto,ctext=st.columns([1,4],vertical_alignment='center')
            with cphoto:
                if photo:st.image(str(Path(__file__).parent/'assets'/photo),width=105)
            with ctext:
                st.markdown(f'<div class="dialogue-card"><strong>{mission["personnage"]}</strong><p>{mission["intro"]}</p></div>',unsafe_allow_html=True)
            if s['etape']>=len(mission['dialogue']):
                st.success('🎉 ¡Misión cumplida! Tu aventure continue !')
                if st.button('Récupérer ma récompense',type='primary'):
                    if s['mission'] not in s['terminees']:
                        s['terminees'].append(s['mission']);s['xp']+=30;s['pieces']+=10
                    s.update(mission=None,etape=0,choix=None)
                    st.rerun()
            else:
                phrase,bonne,options=mission['dialogue'][s['etape']]
                st.progress(s['etape']/len(mission['dialogue']))
                st.markdown(f"### 💬 {mission['personnage']} : « {phrase} »")
                st.write('Que réponds-tu ?')
                if s['choix'] is None:
                    for j,option in enumerate(options):
                        if st.button(option,key=f"v18_c_{s['mission']}_{s['etape']}_{j}",use_container_width=True):
                            s['choix']=option
                            if option!=bonne:s['erreurs']+=1
                            st.rerun()
                else:
                    if s['choix']==bonne:st.success('✨ ¡Excelente! Bonne réponse !')
                    else:st.warning(f"Bien essayé ! La réponse naturelle ici : **{bonne}**")
                    if st.button('Continuer ➜',type='primary'):
                        s['etape']+=1;s['choix']=None;st.rerun()
            if st.button('← Retour à la carte'):
                s.update(mission=None,etape=0,choix=None);st.rerun()
    with tab2:
        st.subheader('⚡ Un mot, une victoire')
        st.caption('Une question à la fois. Les mots viennent de ton lexique quand il est disponible.')
        if s['jeu'] is None:s['jeu']=_nouveau_jeu()
        jeu=s['jeu']
        st.markdown(f"### 🇪🇸 {jeu['mot']}")
        st.write('Quelle est la traduction ?')
        for j,option in enumerate(jeu['options']):
            if st.button(option,key=f'v18_jeu_{s["serie"]}_{j}',use_container_width=True):
                if option==jeu['bonne']:
                    s['xp']+=5;s['pieces']+=2;st.toast('🎉 +5 XP · +2 pièces')
                else:st.toast(f"💡 À retenir : {jeu['mot']} = {jeu['bonne']}")
                s['serie']+=1;s['jeu']=_nouveau_jeu();st.rerun()
    with tab3:
        st.subheader('🏆 Ton carnet de voyage')
        st.write(f"⭐ **{s['xp']} XP** gagnés · 🪙 **{s['pieces']} pièces** collectées")
        st.write('🎖️ Badge explorateur :', 'débloqué !' if len(s['terminees'])>=1 else 'termine ta première mission')
        st.write('🌟 Badge aventurier :', 'débloqué !' if len(s['terminees'])>=3 else 'termine trois missions')
        st.caption('Les récompenses sont ludiques et n’affectent pas les validations CECRL. Elles sont conservées durant la session Streamlit uniquement.')
