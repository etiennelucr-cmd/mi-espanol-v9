"""Pages supplémentaires Streamlit."""
import html, random
import streamlit as st
import streamlit.components.v1 as components
import moteur as m
import pedagogie as p
import coach_quotidien as cq
import parcours_v10 as pv

def parcours():
    st.title('🗺️ Attendus CECRL — A1 à C2')
    st.caption('Niveaux en haut, compétences en lignes. Chaque cellule affiche son texte sur plusieurs lignes, sans le couper.')
    import html as html_lib
    niveaux=[n for n in m.NIVEAUX if n in p.DESCRIPTEURS]
    entetes=''.join(f'<th scope="col">{html_lib.escape(n)}</th>' for n in niveaux)
    lignes=[]
    for i,dimension in enumerate(p.DIMENSIONS):
        cellules=''.join(f'<td>{html_lib.escape(p.DESCRIPTEURS[n][i])}</td>' for n in niveaux)
        lignes.append(f'<tr><th scope="row">{html_lib.escape(dimension)}</th>{cellules}</tr>')
    st.markdown('''<style>
    .cecrl-scroll {overflow-x:auto;max-width:100%;border:1px solid #ddd;border-radius:8px;}
    .cecrl-table {border-collapse:collapse;width:100%;min-width:1080px;table-layout:fixed;}
    .cecrl-table th,.cecrl-table td {border:1px solid #ddd;padding:14px 12px;
        white-space:normal!important;overflow-wrap:anywhere;word-break:normal;
        vertical-align:top;line-height:1.55;text-align:left;}
    .cecrl-table thead th {background:rgba(128,128,128,.16);font-weight:700;}
    .cecrl-table tbody th {background:rgba(128,128,128,.09);font-weight:600;width:165px;}
    .cecrl-table tbody tr {height:auto;}
    </style>''' + '<div class="cecrl-scroll"><table class="cecrl-table"><thead><tr><th scope="col">Compétence</th>'
        + entetes + '</tr></thead><tbody>' + ''.join(lignes) + '</tbody></table></div>',unsafe_allow_html=True)
    st.caption('Sur un petit écran, fais défiler horizontalement le tableau pour voir les niveaux C1 et C2.')
    st.subheader('⏱️ Repères indicatifs de pratique par niveau')
    from referentiel_heures import HEURES_PAR_NIVEAU, HEURES_CUMULEES
    st.dataframe({'Niveau':m.NIVEAUX,'Heures indicatives par niveau':[HEURES_PAR_NIVEAU[n] for n in m.NIVEAUX], 'Total cumulé depuis A1':[HEURES_CUMULEES[n] for n in m.NIVEAUX]},hide_index=True,use_container_width=True)
    st.caption('Objectifs pédagogiques internes, non imposés par le CECRL ; les heures seules ne valident pas un niveau.')
    st.subheader('📚 Objectifs indicatifs de vocabulaire par niveau')
    st.dataframe({'Niveau':m.NIVEAUX,'Objectif indicatif (mots)':[500,1000,2000,3500,5000,7000]},hide_index=True)
    st.caption('Repères pédagogiques internes, non imposés par le CECRL. Les objectifs peuvent être adaptés.')


def expression():
    st.title('✍️ Expression écrite — entraînement adaptatif')
    n=m.preference('niveau_suivi','A1')
    l=pv.theme(n)
    st.info(f'📅 Planning hebdomadaire : {n} — {l["titre"] if l else "Aucun thème"}')
    key='write_exercises_'+n+'_'+(l['id'] if l else '')
    if key not in st.session_state:st.session_state[key]=p.exercices(n,20,lecon=l)
    if st.button('🔀 Nouveau lot',key='write_new_'+n):
        st.session_state[key]=p.exercices(n,20,exclure=st.session_state[key],lecon=l);st.rerun()
    resultat=st.session_state.pop(key+'_result',None)
    if resultat:
        with st.expander('Correction du lot précédent',expanded=True):
            for fr,es,reponse,valide in resultat:
                st.write(('✅' if valide else '❌')+f' **{fr}** — ta réponse : {reponse or "(vide)"} — attendu : **{es}**')
            st.caption('Les traductions alternatives correctes peuvent être rejetées par la comparaison stricte.')
    taux,nb=p.statistiques_ecriture(n)
    st.metric('Réussite évolutive (100 dernières réponses)',f'{taux} %',f'{nb} réponses évaluées')
    st.progress(taux/100)
    tasks=st.session_state[key]
    if not tasks:st.warning('Aucun exercice disponible pour ce niveau.');return
    st.caption('Les erreurs passées sont prioritaires ; le lot change après chaque correction.')
    with st.form('write_form_'+n):
        answers=[st.text_input(f'{i+1}. Traduis en espagnol : {fr}',key=f'write_{n}_{st.session_state.get(key+"_tour",0)}_{i}') for i,(fr,es) in enumerate(tasks)]
        duree=st.number_input('Temps consacré à ce lot (minutes)',min_value=1,max_value=120,value=10,key='write_duree_'+n)
        submitted=st.form_submit_button('Corriger et sauvegarder')
    if submitted:
        outcomes=[]
        for (fr,es),answer in zip(tasks,answers):
            valid=p.production(n,'Expression écrite',fr,answer,es)
            outcomes.append((fr,es,answer,valid))
        m.enregistrer_session('Expression écrite',duree,n)
        st.session_state[key+'_result']=outcomes
        st.session_state[key]=p.exercices(n,20,exclure=tasks,lecon=l)
        st.session_state[key+'_tour']=st.session_state.get(key+'_tour',0)+1
        st.rerun()


def oral():
    st.title('🎧 Écoute, compréhension et expression orale')
    choix=st.radio('Choisis ton entraînement',['🎧 Écoute et oral','👂 Compréhension orale — questions','🎙️ Expression orale — prise de parole'],horizontal=True,key='oral_choix_v17')
    if choix.startswith('👂'):
        import entrainement_oral_v17 as entrainement
        entrainement.comprehension();return
    if choix.startswith('🎙️'):
        import entrainement_oral_v17 as entrainement
        entrainement.expression();return
    st.divider()
    st.subheader('Écoute et compréhension orale — parcours progressif')
    st.caption('Jusqu’à 500 énoncés par niveau, construits à partir des exemples des cours. Les énoncés longs peuvent associer deux phrases.')
    disponibles=[n for n in m.NIVEAUX if p.oral_debloque(n)]
    n=m.preference('niveau_suivi','A1')
    if n not in disponibles:
        st.warning('Ce niveau oral est encore verrouillé.');return
    l=pv.theme(n)
    st.info(f'📅 Planning hebdomadaire : {l["titre"] if l else "Aucun thème"}')
    score,total=p.progression_orale(n)
    st.metric('Compréhension — 20 dernières réponses',f'{score} %',f'{total}/20 évaluations récentes')
    st.progress(score/100)
    if total>=20 and score>=95:
        st.success('Niveau validé à 95 % : le niveau suivant est débloqué, si disponible.')
    else:
        st.info('Pour débloquer le niveau suivant : au moins 19 réponses exactes sur les 20 dernières évaluations.')
    banque=p.banque_orale(n,lecon=l)
    st.caption(f'Banque disponible : {len(banque)} énoncés · Correction automatique stricte : une paraphrase correcte peut être refusée.')
    if not banque:st.warning('Aucun énoncé disponible.');return
    cle='oral_tirage_'+n+'_'+(l['id'] if l else '')
    if cle not in st.session_state:st.session_state[cle]=p.tirage_oral(n,lecon=l)
    es,fr=st.session_state[cle]
    phrase=html.escape(es,quote=True)
    components.html(f'''<div style="font:16px sans-serif"><button onclick="let u=new SpeechSynthesisUtterance(document.getElementById('phrase').textContent);u.lang='es-ES';u.rate=.82;speechSynthesis.cancel();speechSynthesis.speak(u)">▶ Écouter en espagnol</button><span id="phrase" style="display:none">{phrase}</span></div>''',height=55)
    resultat=st.session_state.pop('oral_feedback_'+n,None)
    if resultat:
        with st.expander('Correction de la phrase précédente',expanded=True):
            st.write(('✅' if resultat[3] else '❌')+' '+resultat[0])
            st.write('**Traduction attendue :**',resultat[1])
            st.write('**Ta réponse :**',resultat[2])
    with st.form('oral_form_'+n):
        compris=st.text_area('Écris en français exactement ce que tu as compris',key='oral_rep_'+n+'_'+str(st.session_state.get('oral_tour_'+n,0)))
        duree=st.number_input('Temps de pratique (minutes)',min_value=1,max_value=60,value=5,key='oral_duree_'+n)
        submitted=st.form_submit_button('Corriger, enregistrer et changer de phrase')
    if submitted:
        if not compris.strip():st.warning('Écris ta réponse avant de valider.')
        else:
            valide=p.enregistrer_comprehension(n,es,fr,compris)
            p.audio(n,es,'compréhension orale',compris)
            m.enregistrer_session('Écoute / oral',duree,n)
            st.session_state['oral_feedback_'+n]=(es,fr,compris,valide)
            st.session_state[cle]=p.tirage_oral(n,exclure=[es],lecon=l)
            st.session_state['oral_tour_'+n]=st.session_state.get('oral_tour_'+n,0)+1
            st.rerun()
    if hasattr(st,'audio_input'):
        with st.expander('🎙️ Écouter ta propre prononciation'):
            recorded=st.audio_input('Enregistre ta voix')
            if recorded:st.audio(recorded)
            st.caption('Prononciation non évaluée automatiquement.')

def programme():
    st.markdown('## 🇪🇸 ¡Hola! Bienvenido a Mi Español')
    stats=m.statistiques()
    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric('Niveau estimé',m.niveau_estime())
    c2.metric('Étude aujourd’hui',f"{stats['minutes']:.0f} min")
    c3.metric('Quiz du jour',stats['tests'])
    c4.metric('XP total',stats['xp'])
    niveau_actuel=m.preference('niveau_suivi','A1')
    c5.metric(f'Mots acquis estimés — {niveau_actuel}',pv.mots_acquis(niveau_actuel))
    import suivi_temps_v17 as suivi
    heures=suivi.heures_niveau(niveau_actuel)
    c6.metric(f'Heures apprises — {niveau_actuel}',f'{heures:.1f} h')
    st.caption(f'Objectif indicatif {niveau_actuel} : {suivi.OBJECTIFS[niveau_actuel]} h de pratique. Les heures ne valident pas à elles seules un niveau CECRL.')
    st.caption('Estimation basée sur les mots du lexique utilisés dans au moins deux traductions enregistrées correctes ; les QCM ne sont pas encore pris en compte.')
    obj=m.objectif()
    st.progress(min(1,stats['minutes']/obj),text=f"Objectif quotidien : {stats['minutes']:.0f} / {obj} minutes")
    st.divider()
    st.title('🎯 Programme quotidien personnalisé')
    n=st.selectbox('Niveau de travail',m.NIVEAUX,index=m.NIVEAUX.index(m.preference('niveau_suivi','A1')),key='plan_level')
    from datetime import date
    import pandas as pd
    jour=date.today().isoformat()
    cle=f'programme_minutes_{jour}'
    # Une fois validé, le temps du jour reste verrouillé dans SQLite.
    # Une nouvelle date ouvre automatiquement un nouveau choix.
    memorise=m.preference(cle)
    widget_cle=f'programme_minutes_choix_{jour}'
    if memorise is None:
        st.info('Choisis ton temps disponible puis clique sur « Valider mon temps pour aujourd’hui ». Ce choix sera bloqué jusqu’à demain.')
        with st.form(f'programme_minutes_validation_{jour}'):
            minutes_choisies=st.slider('Temps disponible aujourd’hui',15,120,40,5,key=widget_cle)
            validation=st.form_submit_button('🔒 Valider mon temps pour aujourd’hui',type='primary')
        if validation:
            # Ne pas écraser une valeur déjà validée dans une autre session.
            if m.preference(cle) is None:
                m.definir_preference(cle,int(minutes_choisies))
            st.rerun()
        st.caption('La répartition des activités apparaîtra après validation du temps.')
        return
    try:
        minutes=int(memorise)
    except (TypeError,ValueError):
        st.error('Le temps enregistré pour cette journée est invalide. Vérifie la préférence du jour dans SQLite.')
        return
    st.success(f'🔒 Temps validé pour aujourd’hui : {minutes} minutes. Modification possible demain.')
    activites,due,faibles=p.plan(n,minutes)
    lecon=pv.theme(n)
    if lecon:st.info(f'📅 Thème du planning hebdomadaire : **{lecon["titre"]}**')
    st.subheader('📊 Répartition de ton temps aujourd’hui')
    st.caption('Temps des cours, productions écrites et pratiques orales sauvegardés, ainsi que durée des quiz et contrôles enregistrés. Les durées des quiz sont indicatives (temps écoulé entre ouverture et correction).')
    # Les séances existantes sont comptées automatiquement. Pour les autres activités,
    # l'utilisateur peut déclarer son temps, sans fabriquer une durée à partir des clics.
    types={
        'Cours':('Cours',),
        'Révisions':('Révision','Révisions','Remédiation'),
        'Écoute / oral':('Écoute / oral','Oral','Écoute'),
        'Expression écrite':('Expression écrite',),
        'Coach IA':('Coach IA','Conversation'),
        'Verbes et conjugaisons':('Verbes et conjugaisons',),
    }
    enregistre=m.rows('SELECT type,COALESCE(SUM(minutes),0) minutes FROM sessions WHERE date=? AND niveau=? GROUP BY type',(jour,n))
    par_type={r['type']:float(r['minutes']) for r in enregistre}
    # Les quiz et contrôles enregistrent leur durée dans tentatives.secondes, pas dans sessions.
    tentatives=m.rows('''SELECT type,COALESCE(SUM(CASE WHEN secondes BETWEEN 1 AND 7200 THEN secondes ELSE 0 END),0) secondes
        FROM tentatives WHERE substr(date,1,10)=? AND niveau=? GROUP BY type''',(jour,n))
    durees_tests={r['type']:float(r['secondes'])/60 for r in tentatives}
    par_type['Révision']=par_type.get('Révision',0)+sum(durees_tests.get(t,0) for t in ('Révision','Remédiation'))
    par_type['Cours']=par_type.get('Cours',0)+durees_tests.get('Exercice',0)
    # Les contrôles sont affichés séparément, sans les confondre avec les révisions.
    controle_minutes=durees_tests.get('Contrôle',0)
    tableau=[]
    # Catégorie dédiée, indépendante des cours et des révisions classiques.
    activites=list(activites)
    if not any(nom=='Verbes et conjugaisons' for nom,_ in activites):
        activites.append(('Verbes et conjugaisons',0))
    for categorie,prevision in activites:
        fait=sum(par_type.get(t,0) for t in types.get(categorie,(categorie,)))
        tableau.append({'Activité':categorie,'Prévu (min)':prevision,
                        'Réalisé (min)':round(fait,1),
                        '% du temps quotidien':round(100*fait/minutes,1),
                        '% de la catégorie':round(100*fait/prevision,1) if prevision else 0})
    total=sum(par_type.get(t,0) for ts in types.values() for t in ts)+controle_minutes
    if controle_minutes:
        tableau.append({'Activité':'Contrôles /20','Prévu (min)':0,'Réalisé (min)':round(controle_minutes,1),
                        '% du temps quotidien':round(100*controle_minutes/minutes,1),'% de la catégorie':0})
    st.dataframe(pd.DataFrame(tableau),hide_index=True,use_container_width=True,
                 column_config={'% du temps quotidien':st.column_config.ProgressColumn('% du temps quotidien',min_value=0,max_value=100,format='%.1f %%'),
                                '% de la catégorie':st.column_config.ProgressColumn('% de la catégorie',min_value=0,max_value=100,format='%.1f %%')})
    st.progress(min(1,total/minutes),text=f'Temps enregistré pour {n} : {total:g} / {minutes} min ({100*total/minutes:.1f} %)')
    with st.expander('➕ Enregistrer le temps passé dans une activité'):
        with st.form('temps_programme_'+n):
            categorie=st.selectbox('Activité',list(types),key='temps_categorie_'+n)
            duree=st.number_input('Minutes réellement effectuées',min_value=1,max_value=240,value=10,step=1)
            if st.form_submit_button('Enregistrer le temps'):
                # Utiliser le même type que les séances existantes pour le regroupement.
                m.enregistrer_session(types[categorie][0],duree,n)
                st.rerun()
    st.caption('Les QCM et contrôles de conjugaison sont comptabilisés automatiquement après validation. Les leçons et fiches peuvent être saisies manuellement. Cours, expression écrite, oral et quiz déjà sauvegardés sont comptés automatiquement : ne les saisis pas une seconde fois. Les activités simplement consultées ne peuvent pas être chronométrées rétroactivement.')
    if due:
        st.subheader('Révisions prioritaires')
        for item in due[:8]:st.write(f"• {item['nom']} — {item['maitrise']:.0%}")
    # Les points faibles suivent le niveau actuel défini dans la barre latérale,
    # indépendamment du niveau choisi pour le programme du jour.
    niveau_actuel=st.session_state.get('sidebar_niveau',m.preference('niveau_suivi','A1'))
    if niveau_actuel not in m.NIVEAUX:
        niveau_actuel='A1'
    cq.points_faibles(niveau_actuel)
    st.caption('Synthèse de toutes les activités enregistrées. Les exercices écrits ont une correction stricte ; les auto-évaluations et l’oral sont déclaratifs.')


def conjugaisons():
    """Tableaux scolaires à six personnes et exemples de formes verbales."""
    import json
    from pathlib import Path
    import pandas as pd
    verbes=json.loads((Path(__file__).resolve().parent/'verbes.json').read_text(encoding='utf-8'))
    st.title('📗 Verbes essentiels et conjugaisons')
    st.caption('18 verbes fréquents, regroupés par thème. Tableaux à six personnes : présent, passé simple (pretérito indefinido), imparfait et futur.')
    themes=sorted({v[0] for v in verbes.values()})
    theme=st.selectbox('Thème',['Tous']+themes,key='verbes_theme')
    choix=[k for k,v in verbes.items() if theme=='Tous' or v[0]==theme]
    verbe=st.selectbox('Verbe',choix,format_func=lambda x:f'{x} — {verbes[x][1]}',key='verbes_verbe')
    donnees=verbes[verbe]
    personnes=['yo','tú','él / ella / usted','nosotros/as','vosotros/as','ellos / ellas / ustedes']
    temps=['Présent de l’indicatif','Passé simple (indefinido)','Imparfait','Futur simple']
    st.subheader(f'{verbe} — {donnees[1]}')
    tableau={'Personne':personnes}
    for titre,formes in zip(temps,donnees[2:]):tableau[titre]=formes
    st.dataframe(pd.DataFrame(tableau),hide_index=True,use_container_width=True)
    st.subheader('Exemples de conjugaison — 10 minimum')
    exemples=[]
    for temps,formes in zip(temps,donnees[2:]):
        for pronom,forme in zip(personnes,formes):
            exemples.append({'Temps':temps,'Exemple':f'{pronom} {forme}','Traduction / aide':f'{donnees[1]} — {temps.lower()}'})
    st.dataframe(pd.DataFrame(exemples),hide_index=True,use_container_width=True)
    st.caption('Les exemples présentent des formes conjuguées isolées avec leur sujet, pas des phrases contextualisées.')
