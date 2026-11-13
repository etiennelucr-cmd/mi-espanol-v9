"""V57 — carte ludique responsive, branchée sur les aventures V52–V54."""
import html
import streamlit as st
from villes_interactives_v52 import CITIES, FEATURES, _scene, _puzzle, _history, _stage
from aventure_multilingue_v50 import LANGS, WORLDS, INDEX

ICONS = ['🚆','🏙️','🌳','🏥','🍕','☕','🌙','🏨','🛒','🎭','👨‍👩‍👧','🆘']
CHARACTERS = {0:'👨‍✈️ Le contrôleur',1:'🧑‍🦱 Une habitante',2:'🥾 Un randonneur',3:'👩‍⚕️ Une soignante',4:'👨‍🍳 Le serveur',5:'👩‍🍳 La barista',6:'🎶 Une habituée',7:'🧑‍💼 La réceptionniste',8:'🛍️ Le commerçant',9:'🎟️ La billetterie',10:'🧑 Une personne du quartier',11:'🧑‍🚒 Une personne qui aide'}

def _illustrated_map(lang, ci, city, area, featured):
    """Accessible clickable illustrated town, with Streamlit-native fallback controls."""
    icons = {0:'🚉',1:'🏛️',2:'🌲',3:'🏥',4:'🍕',5:'☕',6:'🎶',7:'🏨',8:'🛍️',9:'🎭',10:'🏠',11:'🆘'}
    labels = {0:'Gare',1:'Centre-ville',2:'Parc',3:'Pharmacie',4:'Pizzeria',5:'Café',6:'Bar',7:'Hôtel',8:'Marché',9:'Théâtre',10:'Quartier',11:'Aide'}
    buildings={
      0:('🚆','🚉','🚪','🚉'),1:('🏙️','🏛️','🚪','🌳'),2:('🌳','🌲','🌿','🌳'),3:('🏥','🏥','🚪','➕'),
      4:('🍕','🍕','🚪','🍽️'),5:('☕','☕','🚪','🥐'),6:('🎶','🎵','🚪','🍹'),7:('🏨','🛎️','🚪','🛏️'),
      8:('🛍️','🛒','🚪','🍎'),9:('🎭','🎟️','🚪','🎭'),10:('🏠','🏡','🚪','🌻'),11:('🆘','🚑','🚪','❤️')}
    # Native Streamlit widgets preserve the websocket session. HTML href navigation
    # previously forced a full page load and could reset the user's progress.
    st.markdown(f'<div class="v58-map-heading">☀️ ☁️ 🕊️ {html.escape(city)} ☁️</div>',unsafe_allow_html=True)
    cols=st.columns(2)
    for position,idx in enumerate(featured):
        history=_history(lang,ci,idx)
        wins=sum(score>=2 for score in history)
        level=_stage(history)
        sign,window,door,detail=buildings[idx]
        with cols[position%2]:
            st.markdown(f'<div class="v62-facade" aria-hidden="true"><div class="v62-roof"></div><div class="v62-front"><span>{window}</span><span>{door}</span><span>{detail}</span></div></div>',unsafe_allow_html=True)
            if st.button(f'{sign} {labels[idx]}\n⭐ {wins} réussite(s) · niveau {level}',key=f'v62_building_{lang}_{ci}_{idx}',use_container_width=True):
                st.session_state.v57_place=idx
                st.rerun()
    st.markdown(f'<div class="v62-road">🚶 {html.escape(area)} 🚲</div>',unsafe_allow_html=True)
    st.caption('👆 Touche le nom du bâtiment pour entrer sans recharger la page.')

def page():
    st.markdown("""<style>
    .v57-header{background:linear-gradient(125deg,#76223c,#b44c42);padding:22px 20px;border-radius:22px;color:#fff;text-align:center;margin-bottom:16px}
    .v57-header h2{color:white!important;margin:0;font-size:clamp(1.45rem,4vw,2.15rem)}
    .v57-header p{color:#fff2df;margin:7px 0 0}
    .v57-town{background:linear-gradient(180deg,#83bec5 0%,#c9e2d6 43%,#e7bd85 44%,#f3d4a6 100%);border:3px solid #9e5947;border-radius:23px;padding:14px 12px 18px;margin:14px 0 10px;box-shadow:0 5px 0 #a95f47}
    .v57-sky{text-align:center;font-size:clamp(1.1rem,3vw,1.65rem);color:#3b3b42;font-weight:800;text-shadow:0 1px #fff}
    .v57-street{text-align:center;color:#54332d;font-size:.92rem;font-weight:700;margin:8px 0 3px}
    .v57-card{background:#fff0d8;border:2px solid #c9885d;border-radius:15px;padding:12px;color:#512d31;margin:5px 0 10px}
    .v57-card b{color:#76223c}
    .v58-map{background:linear-gradient(#8cc9d4 0%,#cbe9e4 29%,#a3bd8c 30%,#a8c38b 82%,#b88a64 83%);border:3px solid #9c574b;border-radius:24px;overflow:hidden;padding:16px 12px 0;margin:14px 0;box-shadow:0 6px 0 #9e614e}
    .v58-sky{text-align:center;color:#452d38;font-size:clamp(1.2rem,3vw,1.8rem);font-weight:800;margin-bottom:12px;text-shadow:0 1px #fff}
    .v58-buildings{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;align-items:end;min-height:210px}
    .v58-building{position:relative;min-height:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;background:linear-gradient(145deg,#fff2d9,#f3be8a);border:3px solid #a45948;border-bottom:9px solid #8c5149;border-radius:15px 15px 5px 5px;color:#63263d!important;text-decoration:none!important;box-shadow:0 7px 0 #7f956d;transition:transform .15s ease,filter .15s ease;text-align:center;padding:10px 5px}
    .v58-building:nth-child(2){background:linear-gradient(145deg,#fff4d9,#dfb6b0)}
    .v58-building:nth-child(3){background:linear-gradient(145deg,#e7edc6,#c8d49e)}
    .v58-building:nth-child(4){background:linear-gradient(145deg,#fce9c6,#d8bdc9)}
    .v58-building:hover,.v58-building:focus-visible{transform:translateY(-5px);filter:saturate(1.2);outline:3px solid #7b2544;outline-offset:2px}
    .v60-roof{width:94%;height:24px;background:#933c49;clip-path:polygon(50% 0,100% 100%,0 100%);margin-bottom:-7px}
    .v60-facade{display:flex;justify-content:space-evenly;align-items:flex-end;width:94%;height:75px;background:repeating-linear-gradient(90deg,#eebc87 0 20px,#f5c99a 20px 40px);border:2px solid #9e624d;border-radius:3px 3px 0 0;padding:7px 3px 0}
    .v60-window{background:#8ac9d5;border:2px solid #8d5e57;border-radius:5px 5px 0 0;width:27%;height:44px;display:grid;place-items:center;font-size:1.15rem}
    .v60-door{background:#8c4c55;border:2px solid #613840;border-radius:7px 7px 0 0;width:29%;height:59px;display:grid;place-items:center;font-size:1.2rem}
    .v60-sign{background:#fff5da;border:1px solid #aa6c53;border-radius:12px;padding:1px 10px;font-size:1.05rem}
    .v60-interior{background:linear-gradient(180deg,#f7d6a9 0%,#f7d6a9 74%,#ad7967 74%);border:3px solid #995f53;border-radius:20px;padding:18px;text-align:center;color:#572d3d;margin:12px 0;min-height:185px}
    .v60-character{display:inline-grid;place-items:center;background:#fff0d6;border:3px solid #ae6754;border-radius:50%;width:100px;height:100px;font-size:3rem;margin:10px auto}
    .v60-bubble{background:#fff9ed;border:2px solid #c58b68;border-radius:18px;padding:12px;margin:10px auto;max-width:440px;font-weight:650}
    .v60-street{display:flex;justify-content:space-around;font-size:1.6rem;margin-bottom:-8px}
    .v58-roof{font-size:clamp(2.1rem,5vw,3.6rem);line-height:1.2}
    .v58-building strong{font-size:clamp(.9rem,2vw,1.1rem)}
    .v58-status{font-size:.72rem;font-weight:700;color:#653b3b}
    .v58-road{text-align:center;background:repeating-linear-gradient(90deg,#a57b60 0 30px,#ba9174 30px 60px);color:#fff6e8;font-weight:800;margin:14px -12px 0;padding:13px;text-shadow:0 1px 2px #5b3935}
    @media(max-width:640px){.v58-buildings{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.v58-building{min-height:128px}.v58-status{font-size:.67rem}.v58-map{padding:10px 8px 0}.v58-road{margin-left:-8px;margin-right:-8px}}
    @media(max-width:640px){.v57-town{padding:10px 7px}.v57-header{padding:16px 10px}.v57-card{padding:9px}}
    .v58-map-heading{text-align:center;background:#a1d2d7;border:2px solid #a45948;border-radius:18px 18px 0 0;padding:12px;font-size:clamp(1.1rem,3vw,1.6rem);font-weight:800;color:#5b2a3d}
    .v62-facade{background:#f7d8ae;border:2px solid #a45948;border-bottom:0;border-radius:10px 10px 0 0;padding:7px 5px 0;margin-top:8px;min-height:100px}
    .v62-roof{height:20px;background:#923d4b;clip-path:polygon(50% 0,100% 100%,0 100%)}
    .v62-front{display:flex;align-items:end;justify-content:space-around;background:#efbd8e;height:60px;padding:5px 2px 0}
    .v62-front span{display:grid;place-items:center;background:#8bc8d5;border:1px solid #a45948;width:30%;height:42px;font-size:1.1rem}
    .v62-front span:nth-child(2){background:#8e5057;height:54px}
    .v62-road{text-align:center;background:repeating-linear-gradient(90deg,#a57b60 0 30px,#ba9174 30px 60px);color:white;border-radius:0 0 16px 16px;padding:12px;font-weight:800}
    div[data-testid="stButton"] button[kind="secondary"]{white-space:pre-line}
    @media(max-width:640px){.v62-facade{min-height:74px;padding:4px 2px 0}.v62-front{height:43px}.v62-front span{height:31px;font-size:.8rem}.v62-front span:nth-child(2){height:39px}.v62-roof{height:14px}}
    </style>""",unsafe_allow_html=True)
    st.markdown('<div class="v57-header"><h2>🗺️ Ma ville, mon aventure</h2><p>Choisis une destination, touche un bâtiment et parle aux habitants !</p></div>',unsafe_allow_html=True)
    lang=st.selectbox('🌍 Langue du voyage',list(CITIES),format_func=lambda x:' '.join(LANGS[x]),key='v57_lang')
    if st.session_state.get('v57_previous_lang')!=lang:
        st.session_state.v57_previous_lang=lang
        st.session_state.v57_city=0
        st.session_state.pop('v57_place',None)
    cities=CITIES[lang]
    st.markdown('**🚩 Choisis ta destination**')
    cols=st.columns(3)
    for i,(name,flag,area) in enumerate(cities):
        with cols[i]:
            if st.button(f'{flag} {name}',key=f'v57_city_{lang}_{i}',use_container_width=True,type='primary' if st.session_state.get('v57_city',0)==i else 'secondary'):
                st.session_state.v57_city=i
                st.session_state.pop('v57_place',None)
                st.rerun()
    ci=st.session_state.get('v57_city',0)
    city,flag,area=cities[ci]
    featured=FEATURES[lang][ci]
    if st.session_state.get("v57_place") is None:
        _illustrated_map(lang,ci,city,area,featured)
    with st.expander('♿ Autres accès aux bâtiments', expanded=False):
        # Streamlit-native controls: unlike static HTML image maps, these work with touch and keyboard.
        cols=st.columns(2)
        for i,idx in enumerate(featured):
            emoji,name,_=WORLDS[idx]
            history=_history(lang,ci,idx)
            stage=_stage(history)
            level=['','🌱 Découverte','🧭 Autonomie','🎲 Imprévu'][stage]
            with cols[i%2]:
                st.caption(f'{emoji} {name} · {level} · {sum(x>=2 for x in history)} mission(s) réussie(s)')
                if st.button(f'🚪 Entrer · {name}',key=f'v57_enter_{lang}_{ci}_{idx}',use_container_width=True,type='primary' if st.session_state.get('v57_place')==idx else 'secondary'):
                    st.session_state.v57_place=idx
                    st.rerun()
    with st.expander('🧳 Explorer les 8 autres lieux de la ville', expanded=False):
        others=[i for i in range(len(WORLDS)) if i not in featured]
        for offset in range(0,len(others),2):
            cols=st.columns(2)
            for col,idx in zip(cols,others[offset:offset+2]):
                emoji,name,_=WORLDS[idx]
                with col:
                    if st.button(f'{emoji} {name}',key=f'v57_extra_{lang}_{ci}_{idx}',use_container_width=True):
                        st.session_state.v57_place=idx
                        st.rerun()
    world=st.session_state.get('v57_place')
    if world is None:
        st.info('👆 Entre dans un bâtiment pour rencontrer un personnage et commencer une mission.')
        return
    emoji,name,phrases=WORLDS[world]
    st.divider()
    a,b=st.columns([3,1])
    with a: st.subheader(f'{emoji} {name} · {city}')
    with b:
        if st.button('↩️ Carte',key='v57_back_map',use_container_width=True):
            st.session_state.pop('v57_place',None)
            st.rerun()
    persona=CHARACTERS.get(world,'🧑 Une personne du quartier')
    avatar={0:'👨‍✈️',1:'🧑‍🦱',2:'🥾',3:'👩‍⚕️',4:'👨‍🍳',5:'👩‍🍳',6:'🎶',7:'🧑‍💼',8:'🛍️',9:'🎟️',10:'🧑',11:'🧑‍🚒'}.get(world,'🧑')
    greetings={0:'Bienvenue à la gare !',1:'Bonjour ! Tu cherches quelque chose ?',2:'Prêt pour la promenade ?',3:'Bonjour, comment puis-je t’aider ?',4:'Bienvenue ! Tu as choisi ?',5:'Bonjour ! Qu’est-ce qui te ferait plaisir ?',6:'Bonsoir ! Que souhaites-tu ?',7:'Bienvenue à la réception !',8:'Bonjour ! Je peux te renseigner ?',9:'Bienvenue ! Tu as un billet ?',10:'Salut ! Bienvenue dans le quartier.',11:'Je suis là pour t’aider.'}
    from dialogues_v59 import ASK
    greeting=ASK[lang][0]
    st.markdown(f'<div class="v60-interior"><div style="font-size:1.2rem;font-weight:800">{html.escape(city)} · {html.escape(name)}</div><div class="v60-character" role="img" aria-label="Personnage : {html.escape(persona)}">{avatar}</div><div><strong>{html.escape(persona)}</strong></div><div class="v60-bubble">💬 {html.escape(greeting)}</div></div>',unsafe_allow_html=True)
    st.caption('🎭 Rencontre dans la ville : poursuis la conversation ci-dessous.')
    tabs=st.tabs(['🎭 Histoire interactive','🎯 Défi classique','🧩 Puzzle','📖 Carnet','🆘 SOS voyage'])
    from dialogues_v59 import play
    with tabs[0]: play(lang,ci,world,phrases,city)
    with tabs[1]: _scene(lang,ci,world,phrases,city)
    with tabs[2]: _puzzle(lang,ci,world,phrases)
    with tabs[3]:
        for row in phrases:
            with st.container(border=True):
                st.write('**'+row[INDEX[lang]]+'**')
                st.caption('🇫🇷 '+row[0])
    with tabs[4]:
        st.caption('Disponible immédiatement, sans exercice à réussir.')
        for row in phrases: st.write('**'+row[INDEX[lang]]+'** — '+row[0])
    st.caption('Les personnages et lieux sont des simulations pédagogiques. Les résultats mesurent des réponses écrites, pas la parole spontanée.')
