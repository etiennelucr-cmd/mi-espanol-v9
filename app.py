import json
"""Mi Español V6 — cours enrichis et contrôles /20 avec remédiation."""
import csv, io, json, random, time
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

st.set_page_config(page_title='Mi Español · Coach adaptatif',page_icon='🇪🇸',layout='wide')

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


def controle():
    title('🧪 Contrôle noté sur 20','20 phrases à traduire sur le thème prioritaire du planning hebdomadaire.')
    n=m.preference('niveau_suivi','A1')
    lecon=pv.theme(n)
    st.info(f'📅 Thème du planning : {lecon["titre"] if lecon else "Aucun thème"} · Temps : {pa.priorites(n)[1]}')
    phrases_traduction(n,lecon,20,f'controle_phrases_{n}_{lecon["id"] if lecon else "vide"}','Contrôle — phrases')
    st.caption('La note sur 20 est affichée lorsque 20 phrases sont disponibles. Cette évaluation écrite ne valide pas à elle seule un thème du Coach IA.')

def revisions():
    title('🧠 Révisions évolutives','20 phrases à traduire, en lien avec le planning hebdomadaire.')
    n=m.preference('niveau_suivi','A1')
    lecon=pv.theme(n)
    valides,total=pv.progression(n)
    st.progress(valides/max(1,total),text=f'Progression {n} : {valides}/{total} thèmes validés ({valides/max(1,total):.0%})')
    if not lecon:return
    st.info(f'📅 Thème prioritaire : {lecon["titre"]} · Temps : {pa.priorites(n)[1]}')
    import pedagogie as ped
    cle=f'revision_phrases_{n}_{lecon["id"]}'
    if cle not in st.session_state:st.session_state[cle]=ev.phrases(n,lecon,20,historique=_historique_phrases(cle+'_historique'))
    previous=st.session_state.pop(cle+'_correction',None)
    if previous:
        st.metric('Dernière révision',f'{previous[0]}/20')
        with st.expander('Voir les corrections',expanded=True):
            for fr,es,reponse,ok in previous[1]:st.write(('✅' if ok else '❌')+f' {fr} — {reponse or "(vide)"} → **{es}**')
    qs=st.session_state[cle]
    if len(qs)<20:
        st.warning(f'Seulement {len(qs)} phrases différentes disponibles pour ce thème : la note sur 20 est désactivée tant que le contenu n’est pas enrichi.')
    with st.form(cle+'_form'):
        reponses=[st.text_input(f'{i+1}. Traduis en {"espagnol" if i%2==0 else "français"} : {fr if i%2==0 else es}',key=f'{cle}_{st.session_state.get(cle+"_tour",0)}_{i}') for i,(fr,es) in enumerate(qs)]
        submit=st.form_submit_button('Corriger et enregistrer',type='primary')
    if submit:
        if len(qs)<20 or any(not x.strip() for x in reponses):st.warning('Il faut 20 phrases disponibles et toutes les réponses pour noter la révision.')
        else:
            details=[]
            for (fr,es),rep in zip(qs,reponses):
                consigne,attendu=(fr,es) if len(details)%2==0 else (es,fr)
                ok=ped.production(n,'Révision',consigne,rep,attendu)
                details.append((consigne,attendu,rep,ok))
            score=sum(x[3] for x in details)
            st.session_state[cle+'_correction']=(score,details)
            _memoriser_phrases(cle+'_historique',qs)
            st.session_state[cle]=ev.phrases(n,lecon,20,exclure=qs,historique=_historique_phrases(cle+'_historique'))
            st.session_state[cle+'_tour']=st.session_state.get(cle+'_tour',0)+1
            st.rerun()


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

pages={'📅 Planning de la semaine':pa.page,'🎯 Programme du jour':ext.programme,'🗺️ Parcours CECRL':ext.parcours,'✍️ Expression écrite':ext.expression,'🎧 Écoute et oral':ext.oral,'📚 Cours':cours,'🧪 Contrôles':controle,'🧠 Révisions':revisions,'🗂️ Historique':historique,'📖 Lexique':lexique,'📗 Verbes et conjugaisons':cp.page,'🤖 Coach IA':coach,'🏆 Défis':defis}
with st.sidebar:
    st.title('🇪🇸 Mi Español V8')
    niveau_suivi=st.selectbox('Niveau suivi',m.NIVEAUX,index=m.NIVEAUX.index(m.preference('niveau_suivi','A1')) if m.preference('niveau_suivi','A1') in m.NIVEAUX else 0,key='sidebar_niveau')
    if m.preference('niveau_suivi')!=niveau_suivi:m.definir_preference('niveau_suivi',niveau_suivi)
    valides,total=pv.progression(niveau_suivi)
    pourcentage=100*valides/total if total else 0
    st.metric('Progression totale du niveau',f'{pourcentage:.1f} %')
    st.progress(valides/total if total else 0)
    st.caption(f'{valides} thème(s) validé(s) sur {total} — validation Coach IA à 19/20 minimum')
    projection=m.projection_globale(niveau_suivi)
    prochain=m.NIVEAUX[m.NIVEAUX.index(niveau_suivi)+1] if niveau_suivi!=m.NIVEAUX[-1] else None
    if prochain:
        st.markdown(f'**Objectif : accéder à {prochain}**')
        if all(x['valide'] for x in m.themes_valides(niveau_suivi)):
            st.success('Tous les thèmes validés à 98 % : niveau suivant débloqué')
        else:
            st.caption('Niveau suivant verrouillé : termine chaque thème et réussis son quiz à 98 % minimum')
        if projection and projection.get('atteint'):
            st.success('Progression indicative atteinte (validation des thèmes : 98 %)')
        elif projection:
            st.info('Date estimée : '+projection['centre'])
        else:
            st.caption('Date estimée : en attente de 7 jours de progression mesurable')
    else:st.caption('C2 : dernier niveau du parcours')
    st.divider()
    page=st.radio('Navigation',list(pages))
    st.caption('Estimations internes, non certificatives · SQLite local')
pages[page]()
