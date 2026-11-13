"""V57 — carte ludique responsive, branchée sur les aventures V52–V54."""
import html
import streamlit as st
from villes_interactives_v52 import CITIES, FEATURES, _scene, _puzzle, _history, _stage
from aventure_multilingue_v50 import LANGS, WORLDS, INDEX

ICONS = ['🚆','🏙️','🌳','🏥','🍕','☕','🌙','🏨','🛒','🎭','👨‍👩‍👧','🆘']
CHARACTERS = {0:'👨‍✈️ Le contrôleur',1:'🧑‍🦱 Une habitante',2:'🥾 Un randonneur',3:'👩‍⚕️ Une soignante',4:'👨‍🍳 Le serveur',5:'👩‍🍳 La barista',6:'🎶 Une habituée',7:'🧑‍💼 La réceptionniste',8:'🛍️ Le commerçant',9:'🎟️ La billetterie',10:'🧑 Une personne du quartier',11:'🧑‍🚒 Une personne qui aide'}

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
    @media(max-width:640px){.v57-town{padding:10px 7px}.v57-header{padding:16px 10px}.v57-card{padding:9px}}
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
    st.markdown(f'<div class="v57-town"><div class="v57-sky">☀️ ☁️ &nbsp; {html.escape(city)} &nbsp; 🕊️</div><div class="v57-street">🏘️ {html.escape(area)} · Choisis un lieu ci-dessous ↓</div></div>',unsafe_allow_html=True)
    # Streamlit-native controls: unlike static HTML image maps, these work with touch and keyboard.
    cols=st.columns(2)
    for i,idx in enumerate(featured):
        emoji,name,_=WORLDS[idx]
        history=_history(lang,ci,idx)
        stage=_stage(history)
        level=['','🌱 Découverte','🧭 Autonomie','🎲 Imprévu'][stage]
        with cols[i%2]:
            st.markdown(f'<div class="v57-card"><b>{emoji} {html.escape(name)}</b><div>{html.escape(CHARACTERS.get(idx,"🧑 Un habitant"))}</div><small>{level} · {len(history)} visite(s)</small></div>',unsafe_allow_html=True)
            if st.button(f'🚪 Entrer · {name}',key=f'v57_enter_{lang}_{ci}_{idx}',use_container_width=True,type='primary' if st.session_state.get('v57_place')==idx else 'secondary'):
                st.session_state.v57_place=idx
                st.rerun()
    with st.expander('🧳 Explorer les 8 autres lieux de la ville'):
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
    st.markdown(f'<div class="v57-card">🎭 <b>{html.escape(CHARACTERS.get(world,"Un habitant"))}</b> t’accueille. À toi de jouer !</div>',unsafe_allow_html=True)
    tabs=st.tabs(['🎭 Mission interactive','🧩 Puzzle de mots','📖 Carnet de phrases','🆘 SOS voyage'])
    with tabs[0]: _scene(lang,ci,world,phrases,city)
    with tabs[1]: _puzzle(lang,ci,world,phrases)
    with tabs[2]:
        for row in phrases:
            with st.container(border=True):
                st.write('**'+row[INDEX[lang]]+'**')
                st.caption('🇫🇷 '+row[0])
    with tabs[3]:
        st.caption('Disponible immédiatement, sans exercice à réussir.')
        for row in phrases: st.write('**'+row[INDEX[lang]]+'** — '+row[0])
    st.caption('Les personnages et lieux sont des simulations pédagogiques. Les résultats mesurent des réponses écrites, pas la parole spontanée.')
