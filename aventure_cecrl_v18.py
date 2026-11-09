"""Exploration CECRL ludique, complémentaire aux validations historiques."""
import random
import streamlit as st
import moteur as m
import conjugaison_parcours as cp

NIVEAUX=['A1','A2','B1','B2','C1','C2']

def _etat():
    return st.session_state.setdefault('cecrl_jeu_v18',{'niveau':'A1','theme':None,'question':None,'reponse':None,'xp':0,'pieces':0,'reussites':{},'historique':[]})

def _themes(niveau):
    # Les leçons historiques et le lexique constituent les deux sources de thèmes.
    cours=[('📘 '+str(x.get('titre','Leçon')),str(x.get('id','')),x) for x in m.COURS.get(niveau,[])]
    lex=sorted({str(x.get('theme','')).strip() for x in m.LEXIQUE if isinstance(x,dict) and x.get('niveau')==niveau and x.get('theme')})
    return cours,lex

def _question(niveau,theme,historique):
    mots=[x for x in m.LEXIQUE if isinstance(x,dict) and x.get('niveau')==niveau and x.get('theme')==theme and x.get('es') and x.get('fr')]
    if len({x['fr'] for x in mots})<4:return None
    eligibles=[x for x in mots if (niveau,theme,x['es']) not in historique] or mots
    bonne=random.choice(eligibles)
    autres=random.sample([x for x in mots if x['fr']!=bonne['fr']],3)
    choix=[bonne['fr']]+[x['fr'] for x in autres]
    random.shuffle(choix)
    return {'es':bonne['es'],'fr':bonne['fr'],'choix':choix,'exemple':bonne.get('exemple','')}

def page():
    s=_etat()
    st.title('🗺️ Mon aventure CECRL')
    st.caption('Explore librement A1 → C2. Les XP sont des récompenses de jeu, pas une certification CECRL.')
    cols=st.columns(3)
    cols[0].metric('⭐ XP aventure',s['xp']);cols[1].metric('🪙 Pièces',s['pieces']);cols[2].metric('🎯 Bonnes réponses',sum(s['reussites'].values()))
    niveau=st.select_slider('Choisis ton niveau à explorer',options=NIVEAUX,value=s['niveau'])
    if niveau!=s['niveau']:
        s.update(niveau=niveau,theme=None,question=None,reponse=None)
    cours,themes=_themes(niveau)
    st.subheader(f'📚 Thèmes et compétences {niveau}')
    st.caption(f'{len(cours)} leçons du parcours existant · {len(themes)} thèmes de vocabulaire disponibles')
    with st.expander('Voir toutes les leçons du niveau',expanded=False):
        for titre,ident,lecon in cours:
            st.markdown(f'**{titre}** — {lecon.get("objectif", "Objectif à découvrir")}')
    if themes:
        theme=st.selectbox('Choisis une mission de vocabulaire',themes,index=themes.index(s['theme']) if s['theme'] in themes else 0)
        if theme!=s['theme']:s.update(theme=theme,question=None,reponse=None)
        nb=sum(1 for x in m.LEXIQUE if isinstance(x,dict) and x.get('niveau')==niveau and x.get('theme')==theme)
        st.write(f'🎮 **Mission : {theme}** · {nb} mots du lexique')
        if s['question'] is None:
            if st.button('▶️ Jouer une question',type='primary'):
                s['question']=_question(niveau,theme,s['historique']);s['reponse']=None;st.rerun()
        else:
            q=s['question']
            st.markdown(f'### 🇪🇸 {q["es"]}')
            st.write('Quelle est la traduction ?')
            if s['reponse'] is None:
                for i,choix in enumerate(q['choix']):
                    if st.button(choix,key=f'cecrl_{i}',use_container_width=True):
                        s['reponse']=choix
                        s['historique']=(s['historique']+[(niveau,theme,q['es'])])[-250:]
                        if choix==q['fr']:
                            s['xp']+=10;s['pieces']+=2
                            k=f'{niveau}|{theme}';s['reussites'][k]=s['reussites'].get(k,0)+1
                        st.rerun()
            else:
                if s['reponse']==q['fr']:st.success('✨ ¡Excelente! +10 XP · +2 pièces')
                else:st.info(f'💡 La bonne réponse : **{q["fr"]}**. Tu peux réessayer sans pénalité.')
                if q['exemple']:st.caption('Exemple : '+q['exemple'])
                if st.button('➡️ Question suivante',type='primary'):
                    s['question']=_question(niveau,theme,s['historique']);s['reponse']=None;st.rerun()
            if st.button('⏹️ Terminer la mission'):
                s.update(question=None,reponse=None);st.rerun()
    else:st.info('Pas encore de thème de vocabulaire pour ce niveau dans le lexique.')
    st.divider()
    st.subheader('🔤 Progression des verbes et des temps')
    st.caption('Ordre indicatif progressif : les temps rares restent disponibles mais ne sont pas prioritaires.')
    for niv in NIVEAUX:
        with st.expander(('👉 ' if niv==niveau else '')+niv+' · '+str(len(cp.PARCOURS.get(niv,[])))+' temps'):
            for cle,libelle in cp.PARCOURS.get(niv,[]):
                exp=cp.EXPLICATIONS.get(cle,('',''))
                st.markdown(f'**{libelle}**')
                if exp[0]:st.caption(exp[0])
                if exp[1]:st.write(exp[1])
    st.info('Pour pratiquer et valider tes conjugaisons, ouvre « 📗 Verbes et conjugaisons » dans le menu. Le parcours CECRL classique reste inchangé.')
    st.caption('Les récompenses de cette page sont conservées pendant la session Streamlit seulement.')
