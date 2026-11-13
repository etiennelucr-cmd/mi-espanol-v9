import json
"""Mi Español V42 — édition España cumulée."""
import csv, io, json, random, time
import diagnostic_v16_2 as diagnostic
from datetime import date,datetime,timedelta
import pandas as pd
import requests
import streamlit as st
import moteur as m
import pedagogie as ped
import extension as ext
import conjugaison_parcours as cp
import coach_quotidien as cq
import planning_adaptatif as pa
import parcours_v10 as pv
import exercices_v11 as ev
import apprentissage_v16 as v16

st.set_page_config(page_title='Mi Español · Guide de survie',page_icon='🇪🇸',layout='wide')
st.markdown('''<style>
.stApp {background: linear-gradient(160deg,#fffaf0 0%,#fff4e4 100%);}
[data-testid="stSidebar"] {background: #fff0d5; border-right: 1px solid #edc76d;}
div.stButton > button[kind="primary"] {border-radius: 18px; font-weight: 750; background:#c61932; border-color:#c61932;}
div[data-testid="stMetric"] {background: white; border: 1px solid #efd6a5; border-radius: 16px; padding: 12px;}
[data-testid="stSidebar"] div[data-testid="stRadio"] label {padding: 5px 0;}
h1,h2,h3 {letter-spacing: -.025em;}
</style>''', unsafe_allow_html=True)

def verifier_acces():
    if st.session_state.get("acces_autorise", False):
        return

    st.title("🇪🇸 Mi Español")
    st.subheader("Accès privé")

    mot_de_passe = st.text_input(
        "Mot de passe",
        type="password"
    )

    if st.button("Se connecter"):
        if mot_de_passe == st.secrets["APP_PASSWORD"]:
            st.session_state["acces_autorise"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")

    st.stop()


verifier_acces()

import espana_theme_v24
espana_theme_v24.apply()
m.init()
ped.init()
st.markdown('''<style>.block-container{max-width:1280px;padding-top:1.3rem}.hero{padding:1.5rem;border-radius:18px;background:linear-gradient(120deg,#84212c,#df5c45);color:white}.hero h1,.hero p{color:white}.small{opacity:.8}</style>''',unsafe_allow_html=True)

def title(t,sub=None):
    st.title(t)
    if sub:st.caption(sub)

def question_session(prefix,questions,typ,niveau,lecon_id=None):
    key=f'{prefix}_questions'
    if key not in st.session_state:st.session_state[key]=questions;st.session_state[prefix+'_start']=time.monotonic()
    qs=st.session_state[key]
    if not qs:st.info('Pas encore assez de questions pour cette sélection.');return
    if typ=='Exercice' and len(qs)<20:st.warning(f'Seulement {len(qs)} questions disponibles : 20 sont nécessaires pour valider ce thème.')
    # En révision, conserver la correction précédente pendant que le nouveau lot apparaît.
    if typ=='Révision' and prefix+'_previous' in st.session_state:
        previous=st.session_state[prefix+'_previous']
        st.success(f"Révision précédente : {previous['score']} / {len(previous['qs'])} — enregistrée")
        with st.expander('Voir la correction du tirage précédent',expanded=previous['score']<len(previous['qs'])):
            for old_q in previous['qs']:
                correct=previous['answers'].get(old_q['id'])==old_q['bonne']
                st.write(('✅ ' if correct else '❌ ')+old_q['enonce'])
                st.write('Ta réponse :',previous['answers'].get(old_q['id']) or 'Aucune')
                st.write('Bonne réponse :',old_q['bonne'])
                if old_q.get('explication'):st.caption(old_q['explication'])
    with st.form(prefix+'_form'):
        answers={}
        for i,q in enumerate(qs):
            answers[q['id']]=st.radio(f"{i+1}. {q['enonce']}",q['options'],index=None,key=prefix+'_'+q['id'])
        submitted=st.form_submit_button('Corriger et enregistrer',type='primary')
    if submitted and st.session_state.get(prefix+'_result',{}).get('qs')!=qs:
        elapsed=int(time.monotonic()-st.session_state[prefix+'_start'])
        tid,score=m.enregistrer_test(typ,niveau,lecon_id,qs,answers,elapsed)
        st.session_state[prefix+'_result']={'id':tid,'score':score,'qs':qs,'answers':answers}
        if typ=='Révision':
            st.session_state[prefix+'_previous']=st.session_state.pop(prefix+'_result')
            # Favoriser les notions ratées, puis des questions différentes du lot précédent.
            erreurs=list(dict.fromkeys(q['competence'] for q in qs if answers.get(q['id'])!=q['bonne']))
            anciens={q['id'] for q in qs}
            pool=m.banque(niveau,limite=10000,mode='aleatoire')
            if erreurs:
                nouveaux=m.banque_ciblee(niveau,erreurs,len(qs),anciens)
            else:
                nouveaux=[q for q in pool if q['id'] not in anciens][:len(qs)]
            # Compléter si le catalogue ne contient pas assez de questions inédites.
            deja={q['id'] for q in nouveaux}
            nouveaux += [q for q in pool if q['id'] not in deja][:max(0,len(qs)-len(nouveaux))]
            for q in qs:st.session_state.pop(prefix+'_'+q['id'],None)
            st.session_state[key]=nouveaux[:len(qs)]
            st.session_state[prefix+'_start']=time.monotonic()
            st.rerun()
    result=st.session_state.get(prefix+'_result')
    if result and result['qs']==qs:
        st.success(f"Résultat : {result['score']} / {len(qs)} — enregistré dans le suivi")
        for q in qs:
            with st.expander(('✅ ' if result['answers'].get(q['id'])==q['bonne'] else '❌ ')+q['enonce']):
                st.write('Ta réponse :',result['answers'].get(q['id']) or 'Aucune')
                st.write('Bonne réponse :',q['bonne']);st.caption(q.get('explication') or '')
    if typ!='Révision' and not prefix.startswith('cours_qcm_v11_') and st.button('🔄 Nouveau tirage de questions',key=prefix+'_new'):
        for q in qs:st.session_state.pop(prefix+'_'+q['id'],None)
        st.session_state.pop(prefix+'_result',None)
        st.session_state[key]=m.banque(niveau,lecon_id,len(qs))
        st.session_state[prefix+'_start']=time.monotonic();st.rerun()

def accueil():
    st.markdown('<div class="hero"><h1>🇪🇸 ¡Hola! Mi Español</h1><p>Ton parcours personnalisé : apprendre, pratiquer, réviser et mesurer tes progrès.</p></div>',unsafe_allow_html=True)
    stats=m.statistiques();lvl=m.niveau_estime();a,b,c,d=st.columns(4)
    a.metric('Niveau estimé',lvl);b.metric('Étude aujourd’hui',f"{stats['minutes']:.0f} min");c.metric('Quiz du jour',stats['tests']);d.metric('XP total',stats['xp'])
    objectif=m.objectif();st.progress(min(1,stats['minutes']/objectif),text=f"Objectif quotidien : {stats['minutes']:.0f} / {objectif} minutes")
    st.subheader('🎯 Ton programme du jour')
    due=[x for x in m.revisions() if x['prochaine_revision'] and x['prochaine_revision']<=date.today().isoformat()]
    if due:
        st.warning(f'{len(due)} compétence(s) à revoir aujourd’hui')
        for r in due[:5]:st.write(f"• **{r['nom']}** ({r['niveau']}) — maîtrise estimée {r['maitrise']:.0%}")
    else:st.info('Aucune révision échue. Découvre une leçon ou lance un contrôle diagnostique.')
    st.write('📘 15 min de cours · 🧠 10 min de révision · 📝 10 min de contrôle · 💬 5 min de conversation')
    st.caption('Les durées proposées sont indicatives. Enregistre ton temps actif dans chaque activité.')
    st.subheader('📅 Activité des 14 derniers jours')
    df=pd.DataFrame(m.rows('SELECT date,ROUND(SUM(minutes),1) minutes FROM sessions GROUP BY date ORDER BY date DESC LIMIT 14'))
    if not df.empty:st.bar_chart(df.sort_values('date').set_index('date')['minutes'])
    else:st.info('Ton activité apparaîtra après la première session.')

def cours():
    title('📚 Cours structurés','Cours organisés par niveau A1 à C2 et par thème, avec révisions et évaluations.')
    n=st.selectbox('Niveau',m.NIVEAUX,key='cours_n')
    lecons=m.COURS[n];ids=[x['id'] for x in lecons]
    cle='cours_dernier_'+n
    # La sélection de leçon est stockée dans SQLite : changer de page,
    # rafraîchir le navigateur ou redémarrer ne fait pas perdre la position.
    if st.session_state.get('cours_n_precedent')!=n:
        st.session_state['cours_n_precedent']=n
    selection_sauvee=m.preference(cle)
    if selection_sauvee not in ids:
        en_cours=m.rows("SELECT id FROM lecons WHERE niveau=? AND statut='en cours' ORDER BY debut DESC LIMIT 1",(n,))
        selection_sauvee=en_cours[0]['id'] if en_cours else next((i for i in ids if not any(r['id']==i for r in m.rows("SELECT id FROM lecons WHERE niveau=? AND statut='terminé'",(n,)))),ids[0])
        m.definir_preference(cle,selection_sauvee)
    widget_cle='cours_select_'+n
    # Appliquer la navigation différée avant l'instanciation du selectbox.
    attente_cle='cours_selection_attente_'+n
    if attente_cle in st.session_state:
        selection_attente=st.session_state.pop(attente_cle)
        if selection_attente in ids:
            st.session_state[widget_cle]=selection_attente
    if widget_cle not in st.session_state or st.session_state[widget_cle] not in ids:
        st.session_state[widget_cle]=selection_sauvee
    # Si la page a été quittée puis rechargée, Streamlit peut supprimer
    # la clé du widget ; la préférence SQLite reste la source de vérité.
    def sauver_choix():
        m.definir_preference(cle,st.session_state[widget_cle])
    selection=st.selectbox('Leçon',ids,format_func=lambda i:next(x['titre'] for x in lecons if x['id']==i),key=widget_cle,on_change=sauver_choix)
    st.caption('La leçon sélectionnée est mémorisée automatiquement, même sans enregistrer ta séance.')
    l=lecons[ids.index(selection)]
    st.caption(f'Leçon {ids.index(selection)+1} sur {len(ids)} · Niveau {n}')
    st.header(l['titre']);st.info(l['objectif'])
    for titre_g,ex in l['grammaire']:
        with st.expander(titre_g,expanded=True):st.write(ex)
    st.subheader('Vocabulaire');st.dataframe(pd.DataFrame(l['vocabulaire'],columns=['Espagnol','Français']),hide_index=True)
    st.subheader('Expressions');st.dataframe(pd.DataFrame(l['expressions'],columns=['Espagnol','Français']),hide_index=True)
    st.subheader('Exemples')
    for es,fr in l['exemples']:st.write(f'**{es}** — {fr}')
    with st.form('etude_'+l['id']):
        mins=st.number_input('Temps actif consacré à cette leçon (minutes)',min_value=1,max_value=240,value=15)
        done=st.checkbox('J’ai terminé la leçon')
        if st.form_submit_button('💾 Enregistrer ma séance'):
            m.enregistrer_session('Cours',mins,n,l['id'])
            if done:m.terminer_lecon(l['id'])
            st.session_state['cours_message']=f'Séance enregistrée : {l["titre"]}.'
            if done:
                pos=ids.index(l['id'])
                if pos+1<len(ids):
                    m.definir_preference(cle,ids[pos+1])
                    st.session_state['cours_selection_attente_'+n]=ids[pos+1]
                    st.session_state['cours_message']+=' Passage automatique à la leçon suivante.'
                else:
                    st.session_state['cours_message']+=' Toutes les leçons de ce niveau ont été parcourues.'
            st.rerun()
    if st.session_state.pop('cours_message',None):
        st.success('Séance enregistrée. Continue avec la leçon affichée.')
    st.subheader('📝 QCM de la leçon — 30 questions variées')
    st.caption('Vocabulaire, expressions, exemples et fiche de conjugaison au temps du planning hebdomadaire.')
    cle_qcm=f'cours_qcm_v11_{n}_{l["id"]}'
    if cle_qcm not in st.session_state:
        st.session_state[cle_qcm]=ev.qcm(n,l,30)
    question_session(cle_qcm,st.session_state[cle_qcm],'Exercice',n,l['id'])
    if st.button('🔄 Renouveler les 30 questions',key=cle_qcm+'_refresh'):
        for q in st.session_state[cle_qcm]:st.session_state.pop(cle_qcm+'_'+q['id'],None)
        st.session_state.pop(cle_qcm+'_result',None)
        st.session_state[cle_qcm]=ev.qcm(n,l,30)
        st.session_state[cle_qcm+'_questions']=st.session_state[cle_qcm]
        st.rerun()

def _historique_phrases(cle):
    try:
        valeur=m.preference(cle, '[]')
        data=json.loads(valeur) if isinstance(valeur,str) else []
        return [tuple(x) for x in data if isinstance(x,list) and len(x)==2]
    except (ValueError,TypeError):
        return []

def _memoriser_phrases(cle, phrases):
    anciens=_historique_phrases(cle)
    ensemble={tuple(x) for x in anciens}
    for paire in phrases:
        if tuple(paire) not in ensemble:
            anciens.append(tuple(paire))
            ensemble.add(tuple(paire))
    m.definir_preference(cle,json.dumps(anciens[-300:],ensure_ascii=False))

def phrases_traduction(n, lecon, nombre, prefix, dimension):
    """Phrases contextualisées ; aucune écriture avant validation explicite."""
    if not lecon:
        st.info('Aucun thème disponible dans le planning.')
        return
    key=prefix+'_lot'
    if key not in st.session_state:
        st.session_state[key]=ev.phrases(n,lecon,nombre,historique=_historique_phrases(prefix+'_historique'))
    lot=st.session_state[key]
    if len(lot)<nombre:
        st.warning(f'{len(lot)} phrase(s) disponibles pour ce thème : {nombre} demandées. Aucun contenu inventé.')
    if not lot:return
    precedent=st.session_state.get(prefix+'_correction')
    if precedent:
        st.success(f'Dernier résultat : {precedent["score"]}/{precedent["total"]} — sauvegardé')
        with st.expander('Voir les corrections précédentes',expanded=True):
            for consigne,attendu,reponse,ok in precedent['items']:
                st.write(('✅ ' if ok else '❌ ')+consigne)
                st.write('Ta réponse :',reponse or '(vide)')
                st.write('Réponse de référence :',attendu)
        st.caption('Correction indicative par comparaison normalisée : une autre traduction correcte peut être refusée.')
    tour=st.session_state.get(prefix+'_tour',0)
    with st.form(prefix+'_form'):
        reponses=[st.text_input(f'{i+1}. Traduis en {"espagnol" if i%2==0 else "français"} : {fr if i%2==0 else es}',key=f'{prefix}_{tour}_{i}') for i,(fr,es) in enumerate(lot)]
        soumis=st.form_submit_button('Corriger et sauvegarder',type='primary')
    if soumis:
        if any(not r.strip() for r in reponses):
            st.warning('Réponds à toutes les phrases avant de valider.')
            return
        items=[]
        for (fr,es),rep in zip(lot,reponses):
            consigne,attendu=(fr,es) if len(items)%2==0 else (es,fr)
            ok=ped.production(n,dimension,consigne,rep,attendu)
            items.append((consigne,attendu,rep,ok))
        score=sum(bool(x[3]) for x in items)
        st.session_state[prefix+'_correction']={'score':score,'total':len(lot),'items':items}
        _memoriser_phrases(prefix+'_historique',lot)
        st.session_state[key]=ev.phrases(n,lecon,nombre,exclure=lot,historique=_historique_phrases(prefix+'_historique'))
        st.session_state[prefix+'_tour']=tour+1
        st.rerun()


def _themes_mixte(niveau):
    """Thèmes validés par le Coach IA et premier thème encore en cours."""
    import coach_parcours as coach
    lecons=m.COURS.get(niveau,[])
    scores=m.scores_coach_par_niveau(niveau)
    valides=[l for l in lecons if scores.get(str(l['id']),0)>=coach.SEUIL]
    en_cours=next((l for l in lecons if scores.get(str(l['id']),0)<coach.SEUIL),None)
    return valides+([en_cours] if en_cours else [])


def _temps_mixte(niveau):
    """Tous les temps validés + premier temps non validé des niveaux accessibles."""
    niveaux=m.NIVEAUX[:m.NIVEAUX.index(niveau)+1]
    result=[]
    for n in niveaux:
        scores=m.scores_conjugaison_par_niveau(n)
        en_cours=False
        for code,libelle in cp.PARCOURS[n]:
            acquis=scores.get(code,(0,0))[0]>=.95
            if acquis or not en_cours:
                result.append((n,code,libelle))
            if not acquis:
                en_cours=True
                break
    return result


def _tirage_mixte(niveau,nombre=20,exclure=(),historique=()):
    """12 traductions multi-thèmes + 8 conjugaisons multi-temps, réparties équitablement."""
    themes=_themes_mixte(niveau)
    anciens={ev._net_pair(fr,es) for fr,es in list(exclure)+list(historique)
             if isinstance(fr,str) and isinstance(es,str)}
    groupes=[]
    for lecon in themes:
        phrases=list(dict.fromkeys((fr,es) for fr,es,_ in ev._sources(lecon)))
        random.shuffle(phrases)
        phrases.sort(key=lambda x:ev._net_pair(*x) in anciens)
        if phrases:groupes.append(phrases)
    traductions=[];vus=set()
    while len(traductions)<12 and any(groupes):
        ordre=list(range(len(groupes)));random.shuffle(ordre)
        for idx in ordre:
            if len(traductions)>=12:break
            while groupes[idx]:
                fr,es=groupes[idx].pop(0);cle=ev._net_pair(fr,es)
                if cle not in vus:
                    vus.add(cle);traductions.append(('traduction',fr,es));break
    temps=_temps_mixte(niveau)
    banque_verbes=ev.VERBES
    conj_groupes=[]
    for _,code,libelle in temps:
        candidats=[]
        for verbe,donnees in banque_verbes.items():
            valeurs=cp.formes(verbe,code,donnees)
            if valeurs:
                for i,forme in enumerate(valeurs):
                    if forme and forme!='—':
                        candidats.append(('conjugaison',f'{verbe} — {libelle} — {cp.PERSONNES[i]}',forme))
        random.shuffle(candidats)
        if candidats:conj_groupes.append(candidats)
    conj=[]
    while len(conj)<8 and any(conj_groupes):
        ordre=list(range(len(conj_groupes)));random.shuffle(ordre)
        for idx in ordre:
            if len(conj)>=8:break
            if conj_groupes[idx]:conj.append(conj_groupes[idx].pop())
    lot=traductions+conj
    random.shuffle(lot)
    return lot[:nombre]


def _exercice_mixte(niveau,mode):
    prefix=f'mixte_{mode}_{niveau}_v173';cle=prefix+'_lot';nombre=20
    themes=_themes_mixte(niveau);temps=_temps_mixte(niveau)
    if not themes:
        st.info('Aucun thème disponible.');return
    st.info(f'{len(themes)} thèmes : '+', '.join(l['titre'] for l in themes))
    st.info(f'{len(temps)} temps de conjugaison : '+', '.join(libelle for _,_,libelle in temps))
    st.caption('12 traductions et 8 conjugaisons : acquis et notions en cours mélangés. '
               'Les traductions alternent français → espagnol et espagnol → français.')
    if cle not in st.session_state:
        st.session_state[cle]=_tirage_mixte(niveau,nombre,historique=_historique_phrases(prefix+'_historique'))
    lot=st.session_state[cle];tour=st.session_state.get(prefix+'_tour',0)
    precedent=st.session_state.get(prefix+'_correction')
    if precedent:
        st.success(f'Dernier résultat : {precedent["score"]}/{precedent["total"]} — sauvegardé')
        with st.expander('Voir les corrections',expanded=True):
            for consigne,attendu,reponse,ok in precedent['items']:
                st.write(('✅ ' if ok else '❌ ')+consigne)
                st.write('Ta réponse :',reponse or '(vide)')
                st.write('Réponse de référence :',attendu)
    if len(lot)<nombre:
        st.warning(f'{len(lot)} questions disponibles. 20 sont nécessaires pour une note sur 20.')
    if not lot:return
    with st.form(prefix+'_form'):
        reponses=[];traduction_index=0
        for i,(genre,source,cible) in enumerate(lot):
            if genre=='traduction':
                vers_es=traduction_index%2==0;traduction_index+=1
                consigne=(f'Traduis en {"espagnol" if vers_es else "français"} : '
                          f'{source if vers_es else cible}')
            else:
                consigne=f'Conjugue : {source}'
            reponses.append(st.text_input(f'{i+1}. {consigne}',key=f'{prefix}_{tour}_{i}'))
        soumis=st.form_submit_button('Corriger et enregistrer',type='primary')
    if soumis:
        if len(lot)<nombre or any(not x.strip() for x in reponses):
            st.warning('Il faut 20 questions et toutes les réponses pour valider.');return
        dimension='Contrôle — thèmes et temps' if mode=='controle' else 'Révision — thèmes et temps'
        items=[];traduction_index=0
        for (genre,source,cible),rep in zip(lot,reponses):
            if genre=='traduction':
                vers_es=traduction_index%2==0;traduction_index+=1
                consigne,attendu=(source,cible) if vers_es else (cible,source)
            else:
                consigne,attendu=source,cible
            ok=ped.production(niveau,dimension,consigne,rep,attendu)
            items.append((consigne,attendu,rep,ok))
        score=sum(bool(x[3]) for x in items)
        st.session_state[prefix+'_correction']={'score':score,'total':len(lot),'items':items}
        paires=[(fr,es) for genre,fr,es in lot if genre=='traduction']
        _memoriser_phrases(prefix+'_historique',paires)
        st.session_state[cle]=_tirage_mixte(niveau,nombre,exclure=paires,
                              historique=_historique_phrases(prefix+'_historique'))
        st.session_state[prefix+'_tour']=tour+1
        st.rerun()


def controle():
    title('🧪 Contrôle noté sur 20','20 phrases tirées de tous les thèmes validés et en cours.')
    _exercice_mixte(m.preference('niveau_suivi','A1'),'controle')
    st.caption('Cette évaluation écrite ne valide pas à elle seule un thème du Coach IA.')


def revisions():
    title('🧠 Révisions évolutives','20 phrases tirées de tous les thèmes validés et en cours.')
    n=m.preference('niveau_suivi','A1')
    valides,total=pv.progression(n)
    st.progress(valides/max(1,total),text=f'Progression {n} : {valides}/{total} thèmes validés')
    _exercice_mixte(n,'revision')


def dashboard():
    title('📊 Tableau de bord quotidien')
    v=st.number_input('Objectif quotidien (minutes)',min_value=5,max_value=240,value=m.objectif(),step=5)
    if st.button('Enregistrer objectif'):m.definir_objectif(v);st.success('Objectif enregistré')
    ss=pd.DataFrame(m.rows('SELECT date,type,ROUND(SUM(minutes),1) minutes,COUNT(*) sessions FROM sessions GROUP BY date,type ORDER BY date'))
    tests=pd.DataFrame(m.rows('SELECT substr(date,1,10) jour,type,COUNT(*) tentatives,SUM(score) bonnes,SUM(total) questions FROM tentatives GROUP BY substr(date,1,10),type ORDER BY jour'))
    if not ss.empty:
        st.subheader('Temps par jour et activité');st.bar_chart(ss.pivot_table(index='date',columns='type',values='minutes',aggfunc='sum',fill_value=0))
        st.dataframe(ss.sort_values('date',ascending=False),hide_index=True)
    else:st.info('Aucune séance enregistrée.')
    if not tests.empty:
        tests['réussite (%)']=(100*tests['bonnes']/tests['questions']).round(1)
        st.subheader('Contrôles et exercices par jour');st.dataframe(tests.sort_values('jour',ascending=False),hide_index=True)
    st.subheader('Cours suivis');lecons=pd.DataFrame(m.rows('SELECT niveau,titre,statut,visites,debut,fin FROM lecons ORDER BY niveau,id'))
    st.dataframe(lecons,hide_index=True)
    st.subheader('Points faibles');weak=pd.DataFrame(m.erreurs(st.session_state.get('sidebar_niveau', 'A1')))
    if not weak.empty:st.dataframe(weak,hide_index=True)
    st.subheader('Progression par niveau')
    hist=pd.DataFrame(m.rows('SELECT * FROM progression_jour ORDER BY date'))
    if not hist.empty:st.line_chart(hist.pivot(index='date',columns='niveau',values='score'))
    st.caption('Maîtrise : estimation heuristique issue des réponses, non équivalente à une certification CECRL.')

def axe():
    title('📈 Axe de progression — cours, contrôles, quiz et révisions')
    n=st.selectbox('Niveau à analyser',m.NIVEAUX,key='axe_n')
    p=m.progression_globale(n)
    st.metric('Progression globale du niveau',f"{p['pourcentage']:.1f} %")
    st.progress(min(1,p['pourcentage']/100))
    cols=st.columns(4)
    for col,label,cle in zip(cols,['Leçons terminées','Quiz','Contrôles /20','Révisions'],['cours','quiz','controles','revisions']):
        col.metric(label,f"{p[cle]:.0f} %")
    st.caption(f"{p['lecons_terminees']} leçons terminées sur {p['lecons_total']} · {p['nb_quiz']} quiz · {p['nb_controles']} contrôles · {p['nb_revisions']} révisions")
    st.info('Calcul : 35 % leçons terminées + 20 % quiz + 30 % contrôles + 15 % révisions/remédiations. Une activité non pratiquée compte pour 0 %.')
    hist=pd.DataFrame(m.rows('SELECT date,score,confiance FROM progression_jour WHERE niveau=? ORDER BY date',(n,)))
    if not hist.empty:
        st.subheader('Évolution du score global')
        st.line_chart(hist.set_index('date')['score']*100)
    proj=m.projection_globale(n)
    if proj and proj.get('atteint'):st.success('Objectif interne de 80 % déjà atteint pour ce niveau.')
    elif proj:st.info(f"Date estimée pour 80 % : {proj['centre']} (fourchette indicative : {proj['debut']} à {proj['fin']}).")
    else:st.info('Date non calculable pour le moment : il faut au moins 7 jours de suivi, des données suffisantes et une progression positive.')
    st.warning('Pourcentage et projection internes : ils ne constituent pas une évaluation ou certification officielle CECRL.')

def historique():
    title('🗂️ Historique et export')
    t=pd.DataFrame(m.rows('SELECT * FROM tentatives ORDER BY date DESC'))
    s=pd.DataFrame(m.rows('SELECT * FROM sessions ORDER BY debut DESC'))
    st.subheader('Contrôles et quiz');st.dataframe(t,hide_index=True)
    st.subheader('Séances');st.dataframe(s,hide_index=True)
    if not t.empty:st.download_button('⬇️ Exporter les quiz CSV',t.to_csv(index=False).encode('utf-8-sig'),'quiz.csv','text/csv')
    if not s.empty:st.download_button('⬇️ Exporter les séances CSV',s.to_csv(index=False).encode('utf-8-sig'),'sessions.csv','text/csv')

def lexique():
    title('📖 Lexique thématique')
    df=pd.DataFrame(m.LEXIQUE);n=st.selectbox('Niveau',['Tous']+m.NIVEAUX);themes=['Tous']+sorted(df.theme.unique());theme=st.selectbox('Thème',themes);search=st.text_input('Rechercher en espagnol ou français')
    if n!='Tous':df=df[df.niveau==n]
    if theme!='Tous':df=df[df.theme==theme]
    if search:df=df[df.apply(lambda r:search.casefold() in ' '.join(map(str,r.values)).casefold(),axis=1)]
    st.dataframe(df,hide_index=True)

def coach():
    import coach_parcours
    coach_parcours.page()

def defis():
    title('🏆 Défis et récompenses', 'Des badges progressifs qui évoluent avec ta pratique, jour après jour.')
    from datetime import timedelta
    from math import ceil
    aujourd_hui=date.today()
    jours=m.rows("""SELECT date, ROUND(SUM(minutes),1) minutes FROM sessions
        GROUP BY date ORDER BY date""")
    tests=m.rows("""SELECT substr(date,1,10) jour, COUNT(*) n,
        SUM(score) reussites, SUM(total) questions FROM tentatives
        GROUP BY substr(date,1,10) ORDER BY jour""")
    activites={r['date']:float(r['minutes']) for r in jours}
    quiz_par_jour={r['jour']:int(r['n']) for r in tests}
    toutes_dates=sorted(set(activites)|set(quiz_par_jour))
    jours_actifs={d for d in toutes_dates if activites.get(d,0)>0 or quiz_par_jour.get(d,0)>0}
    total_minutes=sum(activites.values())
    total_quiz=sum(quiz_par_jour.values())
    xp=m.statistiques()['xp']
    serie=0
    courant=aujourd_hui
    if courant.isoformat() not in jours_actifs:courant-=timedelta(days=1)
    while courant.isoformat() in jours_actifs:
        serie+=1
        courant-=timedelta(days=1)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('XP total',xp)
    c2.metric('Jours actifs',len(jours_actifs))
    c3.metric('Série actuelle',f'{serie} jour(s)')
    c4.metric('Minutes cumulées',f'{total_minutes:.0f}')

    st.subheader('📈 Axe de progression quotidien')
    if toutes_dates:
        cumul_minutes=0.0
        cumul_quiz=0
        cumul_jours=0
        evolution=[]
        for jour in toutes_dates:
            cumul_minutes+=activites.get(jour,0)
            cumul_quiz+=quiz_par_jour.get(jour,0)
            if jour in jours_actifs:cumul_jours+=1
            evolution.append({'Date':jour,'Minutes cumulées':round(cumul_minutes,1),
                              'Quiz cumulés':cumul_quiz,'Jours actifs cumulés':cumul_jours})
        graphique=pd.DataFrame(evolution).set_index('Date')
        mesure=st.selectbox('Afficher la progression de',graphique.columns.tolist(),key='badges_axe_mesure')
        st.line_chart(graphique[[mesure]])
    else:
        st.info('Ton axe apparaîtra après ta première activité enregistrée.')

    st.subheader('🎖️ Badges à paliers')
    categories=[
        ('📅 Régularité','jours',len(jours_actifs),[1,3,7,14,30,60,100],'jours actifs'),
        ('📚 Temps étudié','minutes',total_minutes,[15,60,180,600,1200,3000,6000],'minutes'),
        ('🧠 Quiz et contrôles','quiz',total_quiz,[1,5,10,25,50,100,200],'évaluations'),
        ('⭐ Expérience','xp',xp,[100,500,1000,2500,5000,10000,25000],'XP'),
        ('🔥 Série quotidienne','serie',serie,[2,3,7,14,30,60,100],'jours consécutifs'),
    ]
    for titre,code,valeur,paliers,unite in categories:
        atteints=[v for v in paliers if valeur>=v]
        prochain=next((v for v in paliers if valeur<v),None)
        if prochain is None:
            st.write(f'**{titre} — tous les paliers atteints !**')
            st.progress(1.0)
        else:
            precedent=atteints[-1] if atteints else 0
            st.write(f'**{titre}** · {valeur:g} {unite} · prochain badge : {prochain:g}')
            st.progress(min(1.0,max(0.0,(valeur-precedent)/(prochain-precedent))))
            st.caption(f'Encore {max(0,ceil(prochain-valeur))} {unite} pour le prochain palier.')
        if atteints:
            st.caption('Paliers obtenus : '+', '.join(str(v) for v in atteints))
        # La date du premier franchissement est enregistrée une seule fois.
        for palier in atteints:
            cle=f'badge_{code}_{palier}'
            with m.connexion() as conn:
                conn.execute('INSERT OR IGNORE INTO recompenses(code,date) VALUES (?,?)',
                             (cle,aujourd_hui.isoformat()))
    st.caption('Les dates des badges déjà acquis sont enregistrées à partir de cette mise à jour ; '
               'les anciennes dates de déblocage ne peuvent pas être reconstituées avec certitude. '
               'Les badges récompensent la régularité, sans certifier un niveau CECRL.')

def controles_et_revisions():
    title('🧪 Contrôles et révisions évolutives',
          'Deux entraînements complémentaires, liés au même planning hebdomadaire.')
    choix=st.radio('Choisis ton activité',
                   ['🧪 Contrôle noté sur 20','🧠 Révisions évolutives'],
                   horizontal=True,key='controle_revision_choix')
    st.divider()
    if choix.startswith('🧪'):
        controle()
    else:
        revisions()

import voyage_survie_v43
import aventure_v18 as aventure
import accueil_v19
import accueil_v20
import aventure_cecrl_v18 as aventure_cecrl
import arbre_competences_v18 as arbre_v18
import progression_v40
import mini_jeux_v41
import bilan_unifie_v41
import v40_theme
import projection_cecrl_v25
pages={'🧳 Espagnol de survie · 7 jours':voyage_survie_v43.page,'🇪🇸 Mon aventure V42':accueil_v19.page,'🏡 Mon aventure V19':accueil_v19.page,'📅 Ma progression et mes objectifs':projection_cecrl_v25.page,'🗺️ Carte de progression CECRL':progression_v40.page,'🌳 Arbre de compétences':arbre_v18.tree,'📊 Bilans jour/semaine/mois':arbre_v18.progress,'🎲 Mini-jeux V42':mini_jeux_v41.page,'📊 Tableau de bord V42':bilan_unifie_v41.page,'🎮 Jouer et apprendre':aventure.page,'🌍 Aventure CECRL A1–C2':aventure_cecrl.page,'📅 Planning de la semaine':pa.page,'🎯 Programme du jour':ext.programme,'🗺️ Parcours CECRL':ext.parcours,'✍️ Expression écrite':ext.expression,'🎧 Écoute et expression orale':ext.oral,'📚 Cours':cours,'🧪 Contrôles et révisions':controles_et_revisions,'🎓 Examens blancs':lambda:__import__('examens_v17').page(),'📖 Lexique':lexique,'📗 Verbes et conjugaisons':cp.page,'🤖 Coach IA':coach,'🏆 Défis':defis,'🧠 Répétition espacée':lambda:v16.repetition(m.preference('niveau_suivi','A1')),'📈 Maîtrise durable':lambda:v16.maitrise(m.preference('niveau_suivi','A1'))}
# Le thème V26 est optionnel : ne jamais bloquer le démarrage si
# Streamlit Cloud possède un ancien v18_style.py dans son déploiement.
try:
    from v18_style import apply_v26_global
except ImportError:
    def apply_v26_global():
        st.markdown("""<style>
        .block-container {max-width:1150px; padding-top:2rem}
        h1,h2,h3 {color:#94152a!important}
        div[data-testid="stMetric"] {background:#fffdf8;border:1px solid #efcd8d;border-radius:16px;padding:13px 16px}
        </style>""", unsafe_allow_html=True)
apply_v26_global()
v40_theme.apply()
import v42_theme
v42_theme.apply()
# V47: navigation centrale, guide prioritaire. Les anciennes pages restent accessibles.
st.markdown("""<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"] {display:none!important;}
.block-container {max-width:1080px!important;margin:auto!important;padding-top:1.5rem!important;}
.v47-hero{text-align:center;padding:18px 10px 10px}
.v47-hero h1{font-size:2.3rem;margin-bottom:0.2rem}
.v47-hero p{color:#856a57;font-size:1.05rem}
div.stButton>button {min-height:58px;border-radius:16px;border:1px solid #e9c58f;background:#fffaf2;white-space:normal;}
</style>""",unsafe_allow_html=True)
# V55 : identité visuelle plus contrastée, responsive téléphone / ordinateur.
st.markdown("""<style>
:root {color-scheme:light;}
html, body, .stApp, [data-testid="stAppViewContainer"] {
 background:linear-gradient(145deg,#f3d8ae 0%,#ebc6a0 46%,#dfb6a0 100%)!important;
 color:#33211e!important;
}
.block-container {max-width:1040px!important;padding:1.2rem 1.2rem 5rem!important;}
.v47-hero {background:linear-gradient(115deg,#77233d,#a92c45 60%,#c45440)!important;
 border-radius:26px!important;padding:30px 18px!important;margin:0 0 22px!important;
 box-shadow:0 12px 30px #642d3040!important;}
.v47-hero h1 {color:#fff9eb!important;font-size:clamp(1.9rem,5vw,2.7rem)!important;}
.v47-hero p {color:#ffe8d5!important;font-size:clamp(.94rem,2.6vw,1.1rem)!important;}
h1,h2,h3 {color:#70253a!important;}
[data-testid="stMarkdownContainer"] p {line-height:1.55;}
.stButton>button, div.stButton>button {background:#fff0d9!important;color:#502938!important;
 border:2px solid #c99162!important;border-radius:17px!important;
 min-height:58px!important;box-shadow:0 3px 0 #a8674438!important;
 font-weight:700!important;white-space:normal!important;transition:transform .12s,box-shadow .12s;}
.stButton>button:hover {background:#ffe0b7!important;border-color:#9f3d49!important;transform:translateY(-1px);}
.stButton>button[kind="primary"],div.stButton>button[kind="primary"] {
 background:#9c2543!important;color:white!important;border-color:#9c2543!important;}
.stButton>button[kind="primary"]:hover {background:#7c1935!important;}
[data-testid="stExpander"], [data-testid="stForm"],div[data-testid="stMetric"],
[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:17px!important;}
[data-testid="stForm"], [data-testid="stMetric"] {background:#fff1dd!important;border:1px solid #d6a477!important;}
[data-testid="stAlert"] {border-radius:16px!important;}
[data-testid="stRadio"] label, [data-testid="stSelectbox"] label {color:#43242b!important;}
[data-testid="stTabs"] button {font-weight:700!important;}
@media(max-width:720px) {
 .block-container {padding:.6rem .75rem 5rem!important;max-width:100%!important;}
 .v47-hero {padding:22px 12px!important;border-radius:20px!important;margin-bottom:14px!important;}
 /* Streamlit columns become large touch-friendly cards in a single column. */
 div[data-testid="stHorizontalBlock"] {flex-wrap:wrap!important;gap:.55rem!important;}
 div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  flex:1 1 100%!important;min-width:0!important;width:100%!important;}
 div.stButton>button {min-height:54px!important;font-size:1rem!important;}
 [data-testid="stTabs"] [data-baseweb="tab-list"] {overflow-x:auto!important;flex-wrap:nowrap!important;}
 [data-testid="stTabs"] [data-baseweb="tab"] {white-space:nowrap!important;flex-shrink:0!important;}
 .v52-hero {padding:18px 12px!important;}
 .v52-scene {padding:15px!important;font-size:1rem!important;}
}
@media(min-width:721px) and (max-width:1000px) {
 .block-container {padding:1rem 1.2rem 4rem!important;}
 div[data-testid="stHorizontalBlock"] {gap:.65rem!important;}
}
</style>""",unsafe_allow_html=True)
# V56 : navigation immersive, quatre entrées, contenu affiché uniquement à la demande.
st.markdown("""<style>
.v56-banner{background:linear-gradient(115deg,#702139,#a83348 62%,#bb5942);border-radius:25px;
 padding:26px 18px;text-align:center;box-shadow:0 10px 24px #632b3033;margin-bottom:12px}
.v56-banner h1{color:#fff9eb!important;font-size:clamp(1.65rem,4vw,2.5rem);margin:0}
.v56-banner p{color:#ffe8d5!important;margin:8px 0 0}
.v56-subtitle{font-size:1.15rem;font-weight:800;color:#70253a;margin:12px 0 8px}
.v56-tip{padding:12px 16px;border-radius:15px;background:#fce6c9;border:1px solid #cb976e;color:#5d3440}
@media(max-width:720px){.v56-banner{padding:18px 12px}.v56-banner h1{font-size:1.65rem}
 .v56-menu div[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important}}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="v56-banner"><h1>🌍 Mon aventure linguistique</h1><p>Explore les villes, parle aux habitants et progresse à ton rythme !</p></div>',unsafe_allow_html=True)
if 'v47_page' not in st.session_state:
    st.session_state.v47_page='🏙️ Visiter les villes'
# Choix du mode : les quatre cartes restent identiques sur mobile et ordinateur.
menu=[('🗺️ Explorer les villes','🏙️ Visiter les villes'),('🎮 Mes défis','🎮 Aventure multilingue'),
      ('💬 Mes rencontres','💬 Mes rencontres'),('📖 Apprendre','📖 Apprendre'),('🏆 Ma progression','🌍 Mes langues & mes capacités')]
cols=st.columns(2,gap='small')
for i,(label,target) in enumerate(menu):
    with cols[i%2]:
        if st.button(label,key=f'v56_main_{i}',use_container_width=True,type='primary' if st.session_state.v47_page==target else 'secondary'):
            st.session_state.v47_page=target
            st.rerun()
legacy={'🇪🇸 Mon aventure V42':'🇪🇸 Mon aventure V42','🎲 Mini-jeux':'🎲 Mini-jeux V42',
 '📖 Lexique complet':'📖 Lexique','🗺️ Parcours CECRL':'🗺️ Carte de progression CECRL',
 '📊 Bilans':'📊 Tableau de bord V42','🤖 Coach IA':'🤖 Coach IA',
 '📚 Cours classiques':'📚 Cours','✍️ Expression écrite':'✍️ Expression écrite',
 '🎧 Écoute et oral':'🎧 Écoute et expression orale','💾 Révisions':'🧪 Contrôles et révisions'}
if st.session_state.v47_page=='📖 Apprendre':
    st.markdown('<div class="v56-subtitle">📖 Que veux-tu apprendre aujourd’hui ?</div>',unsafe_allow_html=True)
    nav_items=[('🧳 Programme 7 jours','📅 Mon itinéraire · 7 jours'),
     ('💬 Phrases utiles','🧰 Expressions de survie'),('📚 Vocabulaire','🧰 Expressions de survie'),
     ('✏️ Exercices','📅 Mon itinéraire · 7 jours'),('🗺️ Situations réelles','🧰 Expressions de survie'),
     ('🏡 Vie quotidienne','🧰 Expressions de survie')]
    for start in (0,3):
        cs=st.columns(3,gap='small')
        for c,(label,section) in zip(cs,nav_items[start:start+3]):
            with c:
                if st.button(label,key='v56_learn_'+label,use_container_width=True):
                    st.session_state.v47_page=label
                    st.session_state.voyage_section=section
                    st.rerun()
if st.session_state.v47_page not in ('🏙️ Visiter les villes','🎮 Aventure multilingue','🌍 Mes langues & mes capacités','💬 Mes rencontres'):
    with st.expander('⚙️ Autres activités et outils classiques (facultatif)'):
        selected_legacy=st.selectbox('Choisir une activité',list(legacy),key='v56_legacy_choice')
        if st.button('Ouvrir cette activité',key='v56_open_legacy'):
            st.session_state.v47_page=selected_legacy
            st.rerun()
if st.session_state.v47_page=='📖 Apprendre':
    st.markdown('<div class="v56-tip">👆 Choisis une activité ci-dessus. Les leçons et les exercices s’ouvriront ici, sans encombrer l’accueil.</div>',unsafe_allow_html=True)
page=legacy.get(st.session_state.v47_page,'🧳 Espagnol de survie · 7 jours')
page_start=time.perf_counter()
try:
    if st.session_state.v47_page=='🏙️ Visiter les villes':
        import carte_v57
        carte_v57.page()
    elif st.session_state.v47_page=='💬 Mes rencontres':
        import rencontres_v63
        rencontres_v63.page()
    elif st.session_state.v47_page=='🎮 Aventure multilingue':
        import aventure_multilingue_v50
        aventure_multilingue_v50.page()
    elif st.session_state.v47_page=='🌍 Mes langues & mes capacités':
        import suivi_langues_v48
        suivi_langues_v48.page()
    elif st.session_state.v47_page!='📖 Apprendre':
        pages[page]()
finally:
    diagnostic.record("Page sélectionnée",time.perf_counter()-page_start)
    diagnostic.report()
    try:
        import sync_aventure_v29
        sync_aventure_v29.autosave()
    except Exception:
        pass
