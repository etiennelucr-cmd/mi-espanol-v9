"""Parcours professeur IA, contrôles déterministes et déblocage séquentiel."""
import random, time
from datetime import date, timedelta
import streamlit as st
import requests
import moteur as m

SEUIL=0.95

def valide(n, lecon):
    r=m.rows("SELECT MAX(CAST(score AS REAL)/NULLIF(total,0)) AS ratio FROM tentatives WHERE type='Coach IA' AND niveau=? AND lecon_id=? AND total>=20",(n,lecon['id']))
    return bool(r and r[0]['ratio'] is not None and r[0]['ratio']>=SEUIL)

def accessible(n):
    idx=m.NIVEAUX.index(n)
    return idx==0 or all(valide(m.NIVEAUX[idx-1], l) for l in m.COURS[m.NIVEAUX[idx-1]])

def selection(n,lecon_id,exclure=()):
    pool=m.banque(n,lecon_id,500,'aleatoire')
    historiques=m.rows("""SELECT r.question_id, SUM(CASE WHEN r.correct=0 THEN 1 ELSE 0 END) erreurs,
      SUM(CASE WHEN r.correct=1 THEN 1 ELSE 0 END) reussites
      FROM reponses r JOIN tentatives t ON t.id=r.tentative_id
      WHERE t.type='Coach IA' AND t.niveau=? AND t.lecon_id=? GROUP BY r.question_id""",(n,lecon_id))
    h={r['question_id']:r for r in historiques}
    random.shuffle(pool)
    pool.sort(key=lambda q:(q['id'] in exclure,-(h.get(q['id'],{}).get('erreurs',0)),h.get(q['id'],{}).get('reussites',0)))
    return pool[:20]

def lecon_page(l):
    st.subheader('📘 Leçon : '+l['titre'])
    st.write('**Objectif :** '+l.get('objectif',''))
    for titre,explication in l.get('grammaire',[]):
        st.markdown('**'+titre+'**')
        st.write(explication)
    st.markdown('**Exemples en contexte**')
    for exemple in l.get('exemples',[])[:10]:
        if isinstance(exemple,(list,tuple)):st.write('• **'+str(exemple[0])+'** — '+str(exemple[1]))
        else:st.write('• '+str(exemple))
    with st.expander('Vocabulaire et expressions',expanded=True):
        st.markdown('**Vocabulaire**')
        for a,b in l.get('vocabulaire',[])[:12]:st.write(f'• {a} — {b}')
        st.markdown('**Expressions**')
        for a,b in l.get('expressions',[])[:10]:st.write(f'• {a} — {b}')


def _revision_db():
    # coach_revisions_espacees a déjà été créée dans Supabase.
    return None


def _revision_statuts(n, valides):
    _revision_db()
    today = date.today()
    with m.connexion() as db:
        for lecon in valides:
            db.execute(
                """INSERT INTO coach_revisions_espacees
                   (niveau, lecon_id, etape, prochaine_date)
                   VALUES (?, ?, 0, ?)
                   ON CONFLICT (niveau, lecon_id) DO NOTHING""",
                (n, str(lecon['id']), (today + timedelta(days=1)).isoformat())
            )
    return {
        r['lecon_id']: r for r in m.rows(
            'SELECT * FROM coach_revisions_espacees WHERE niveau=?', (n,)
        )
    }


def _revision_enregistrer(n, lecon_id, score, total):
    today = date.today()
    rows = m.rows(
        'SELECT etape FROM coach_revisions_espacees WHERE niveau=? AND lecon_id=?',
        (n, str(lecon_id))
    )
    etape = rows[0]['etape'] if rows else 0
    if total == 20 and score / total >= SEUIL:
        etape = min(etape + 1, 6)
        jours = [1, 1, 3, 7, 14, 30, 60][etape]
    else:
        etape, jours = 0, 1
    prochaine = (today + timedelta(days=jours)).isoformat()
    score_ratio = score / total if total else 0
    with m.connexion() as db:
        db.execute(
            """INSERT INTO coach_revisions_espacees
               (niveau, lecon_id, etape, prochaine_date, dernier_score, derniere_date)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT (niveau, lecon_id) DO UPDATE SET
                 etape=EXCLUDED.etape,
                 prochaine_date=EXCLUDED.prochaine_date,
                 dernier_score=EXCLUDED.dernier_score,
                 derniere_date=EXCLUDED.derniere_date""",
            (n, str(lecon_id), etape, prochaine, score_ratio, today.isoformat())
        )


def consolidation(n):
    """Bilans transversaux et contrôle de maintien des acquis, sans déblocage artificiel."""
    import pedagogie as ped
    from datetime import date
    st.divider()
    st.header('🔁 Le professeur vérifie aussi tes acquis')
    st.caption('Révision espacée après validation : J+1, J+3, J+7, J+14, J+30, puis J+60. En cas de difficulté, retour à J+1. Les contrôles de consolidation ne débloquent pas les thèmes.')
    valides=[l for l in m.COURS[n] if valide(n,l)]
    ecrit=m.rows("SELECT valide FROM productions WHERE niveau=? AND dimension='Expression écrite' ORDER BY id DESC LIMIT 100",(n,))
    oral=m.rows('SELECT valide FROM comprehension_orale WHERE niveau=? ORDER BY id DESC LIMIT 20',(n,))
    tests=m.rows("SELECT type,score,total,date FROM tentatives WHERE niveau=? ORDER BY id DESC LIMIT 30",(n,))
    minutes=m.rows('SELECT COALESCE(SUM(minutes),0) AS minutes FROM sessions WHERE date=? AND niveau=?',(date.today().isoformat(),n))
    revisions=m.rows('SELECT COUNT(*) AS nb FROM competences WHERE niveau=? AND prochaine_revision<=?',(n,date.today().isoformat()))
    c=st.columns(3)
    c[0].metric('Thèmes du professeur validés',f'{len(valides)}/{len(m.COURS[n])}')
    c[1].metric('Expression écrite (100 dernières)',f'{sum(x["valide"] for x in ecrit)/len(ecrit):.0%}' if ecrit else 'Non évaluée')
    c[2].metric('Oral (20 dernières)',f'{sum(x["valide"] for x in oral)/len(oral):.0%}' if oral else 'Non évalué')
    st.write(f'**Programme quotidien :** {minutes[0]["minutes"]:.0f} min enregistrées aujourd’hui pour {n}.')
    st.write(f'**Révisions évolutives :** {revisions[0]["nb"]} compétence(s) à réviser. **Défis et récompenses :** les badges continuent de dépendre des activités réellement enregistrées.')
    if tests:
        st.write('**Contrôles et quiz récents :** '+', '.join(f'{x["type"]} {x["score"]}/{x["total"]}' for x in tests[:5]))
    st.subheader('🎯 Contrôle de maintien des acquis')
    st.caption('20 questions si la banque le permet, provenant des thèmes déjà validés. Le professeur cible les réponses ratées dans les évaluations précédentes.')
    if not valides:
        st.info('Valide d’abord un thème du professeur à 95 % pour lancer une évaluation de consolidation de tes acquis.')
        return
    statuts=_revision_statuts(n,valides)
    aujourd_hui=date.today().isoformat()
    echeances=[l for l in valides if statuts[str(l['id'])]['prochaine_date']<=aujourd_hui]
    st.write(f'**Révisions dues aujourd’hui : {len(echeances)} / {len(valides)} thèmes acquis.**')
    for l in valides:
        statut=statuts[str(l['id'])]
        st.caption(f'• {l["titre"]} — prochaine révision : {statut["prochaine_date"]} · palier {statut["etape"]}/6')
    if not echeances:
        st.success('Aucune révision échue aujourd’hui. Les acquis restent programmés pour les prochains jours.')
        return
    ids={l['id'] for l in echeances}
    historique=m.rows("""SELECT r.question_id,SUM(CASE WHEN r.correct=0 THEN 1 ELSE 0 END) erreurs,
       SUM(CASE WHEN r.correct=1 THEN 1 ELSE 0 END) reussites
       FROM reponses r JOIN tentatives t ON t.id=r.tentative_id
       WHERE t.niveau=? GROUP BY r.question_id""",(n,))
    h={x['question_id']:x for x in historique}
    prefix='coach_consolidation_'+n
    def tirer(exclure=()):
        pool=[q for q in m.banque(n,limite=10000,mode='aleatoire') if q.get('lecon_id') in ids]
        random.shuffle(pool)
        pool.sort(key=lambda q:(q['id'] in exclure, -(h.get(q['id'],{}).get('erreurs',0)), h.get(q['id'],{}).get('reussites',0)))
        return pool[:20]
    if st.session_state.get(prefix+'_ids')!=tuple(sorted(ids)):
        st.session_state[prefix+'_ids']=tuple(sorted(ids))
        st.session_state[prefix+'_qs']=tirer()
        st.session_state[prefix+'_start']=time.monotonic()
    previous=st.session_state.get(prefix+'_previous')
    if previous:
        st.success(f'Dernière consolidation : {previous["score"]}/{previous["total"]} ({previous["score"]/previous["total"]:.0%})')
        with st.expander('Correction détaillée du contrôle précédent',expanded=previous['score']<previous['total']):
            for q,rep in previous['details']:
                if rep!=q['bonne']:
                    st.error(q['enonce'])
                    st.write('Ta réponse :',rep or 'Aucune','— Réponse attendue :',q['bonne'])
                    st.write('**Explication :**',q.get('explication') or 'Révise les exemples du cours associé à cette question.')
    qs=st.session_state[prefix+'_qs']
    if not qs:
        st.info('Aucune question disponible pour les thèmes déjà validés.')
        return
    if len(qs)<20:st.warning(f'{len(qs)} questions disponibles : cette séance ne constitue pas un contrôle sur 20.')
    with st.form(prefix+'_form'):
        reponses={q['id']:st.radio(f'{i+1}. {q["enonce"]}',q['options'],index=None,key=prefix+'_rep_'+q['id']) for i,q in enumerate(qs)}
        submitted=st.form_submit_button('Corriger et préparer une nouvelle consolidation')
    if submitted:
        _,score=m.enregistrer_test('Consolidation Coach IA',n,None,qs,reponses,int(time.monotonic()-st.session_state[prefix+'_start']))
        # One review session per due theme, with a separate score and schedule.
        for lecon in echeances:
            sous_questions=[q for q in qs if q.get('lecon_id')==lecon['id']]
            if sous_questions:
                bons=sum(reponses.get(q['id'])==q['bonne'] for q in sous_questions)
                # A partial theme sample cannot certify 95% mastery; reschedule for tomorrow.
                _revision_enregistrer(n,lecon['id'],bons,len(sous_questions))
        st.session_state[prefix+'_previous']={'score':score,'total':len(qs),'details':[(q,reponses.get(q['id'])) for q in qs]}
        for q in qs:st.session_state.pop(prefix+'_rep_'+q['id'],None)
        st.session_state[prefix+'_ids']=None
        st.session_state[prefix+'_qs']=tirer({q['id'] for q in qs})
        st.session_state[prefix+'_start']=time.monotonic()
        st.rerun()

def page():
    st.title('🤖 Coach IA — professeur par niveau')
    st.caption('Leçon → exemples → entraînement → contrôle /20. Validation à 95 % (19/20) par thème, dans l’ordre.')
    niveaux=[n for n in m.NIVEAUX if accessible(n)]
    n=st.selectbox('Niveau accessible',niveaux,key='coach_prof_niveau')
    lecons=m.COURS[n]
    acquis=[valide(n,l) for l in lecons]
    actuel=next((i for i,v in enumerate(acquis) if not v),len(lecons)-1)
    st.progress(sum(acquis)/len(lecons),text=f'{sum(acquis)}/{len(lecons)} thèmes validés ({sum(acquis)/len(lecons):.0%})')
    st.info('📌 Thème prioritaire : **'+lecons[actuel]['titre']+'**. Il reste au programme jusqu’à un contrôle à 19/20. Les thèmes suivants restent verrouillés.')
    with st.expander('Afficher tous les thèmes du niveau',expanded=False):
        for i,l in enumerate(lecons):
            statut='✅' if acquis[i] else ('📖' if i==actuel else '🔒')
            st.caption(f'{statut} {i+1}. {l["titre"]}')
    if all(acquis):st.success('Tous les thèmes de ce niveau sont validés. Le niveau suivant est débloqué !')
    l=lecons[actuel]
    st.divider()
    with st.expander("📘 Leçon : "+l["titre"],expanded=False):
        lecon_page(l)
    st.divider()
    st.subheader('🧠 Entraînement avec le professeur')
    st.write('Pose une question sur la leçon ou demande des explications supplémentaires. La conversation ne remplace pas le contrôle noté.')
    ident=f'{n}:{l["id"]}'
    if st.session_state.get('coach_ident')!=ident:
        st.session_state.coach_ident=ident
        st.session_state.coach_messages=[]
        st.session_state.pop('coach_questions',None)
        st.session_state.pop('coach_feedback',None)
    for message in st.session_state.coach_messages:
        with st.chat_message(message['role']):st.markdown(message['content'])
    prompt=st.chat_input('Pose une question sur ce thème…',key='coach_prof_chat')
    if prompt:
        st.session_state.coach_messages.append({'role':'user','content':prompt})
        consigne=(f'Tu es professeur particulier d’espagnol. Enseigne uniquement le thème {l["titre"]} '
                  f'au niveau {n}. Objectif : {l.get("objectif", "")}. '
                  'Procède pas à pas, avec exemples en espagnol et explications en français. '
                  'Corrige les erreurs avec bienveillance, pose une question à la fois. '
                  'Ne prétends jamais valider le thème : seul le contrôle intégré décide du déblocage.')
        try:
            rep=requests.post('http://localhost:11434/api/chat',json={'model':'llama3.2','messages':[{'role':'system','content':consigne}]+st.session_state.coach_messages[-12:],'stream':False},timeout=90)
            rep.raise_for_status();reponse=rep.json()['message']['content']
        except (requests.RequestException,ValueError,KeyError) as e:
            reponse=f'Professeur conversationnel indisponible (Ollama) : {e}. Les leçons et contrôles restent accessibles.'
        st.session_state.coach_messages.append({'role':'assistant','content':reponse})
        st.rerun()
    st.divider()
    consolidation(n)
    st.divider()
    st.subheader('📝 Contrôle de validation du thème')
    st.write('Objectif : **19 bonnes réponses sur 20**. Les questions privilégient les erreurs précédentes.')
    if 'coach_feedback' in st.session_state:
        resultat=st.session_state.coach_feedback
        st.info(f'Dernier contrôle : {resultat["score"]}/{resultat["total"]}. '+('Thème validé !' if resultat['score']>=19 else 'Révise les erreurs puis réessaie.'))
        with st.expander('📖 Explications du professeur et exemples',expanded=resultat['score']<19):
            for q,reponse in resultat['details']:
                if reponse!=q['bonne']:
                    st.error(f'❌ {q["enonce"]} — Ta réponse : {reponse or "aucune"} — Réponse attendue : {q["bonne"]}')
                    st.write('**Pourquoi ?**',q.get('explication') or 'Reprends la règle de la leçon, puis compare avec la bonne réponse.')
                    st.write('**Exemple de la leçon :**',str(l.get('exemples', [''])[0]))
            st.caption('Illustration pédagogique : les exemples sont issus du cours ; ils ne constituent pas une correction humaine.')
    if 'coach_questions' not in st.session_state:
        st.session_state.coach_questions=selection(n,l['id'])
        st.session_state.coach_start=time.monotonic()
    qs=st.session_state.coach_questions
    if len(qs)<20:
        consolidation(n)
        st.warning(f'Il n’y a que {len(qs)} questions pour ce thème. Impossible de certifier 95 % sur un contrôle de 20 questions.')
        return
    with st.form('coach_controle_form'):
        reponses={}
        for i,q in enumerate(qs):
            reponses[q['id']]=st.radio(f'{i+1}. {q["enonce"]}',q['options'],index=None,key='coach_answer_'+q['id'])
        envoyer=st.form_submit_button('Corriger le contrôle et générer un nouveau tirage',type='primary')
    if envoyer:
        _,score=m.enregistrer_test('Coach IA',n,l['id'],qs,reponses,int(time.monotonic()-st.session_state.coach_start))
        st.session_state.coach_feedback={'score':score,'total':len(qs),'details':[(q,reponses.get(q['id'])) for q in qs]}
        for q in qs:st.session_state.pop('coach_answer_'+q['id'],None)
        st.session_state.coach_questions=selection(n,l['id'],{q['id'] for q in qs})
        st.session_state.coach_start=time.monotonic()
        st.rerun()

