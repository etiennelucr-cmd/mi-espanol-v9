"""Suivi factuel des acquis par langue, sans attribuer de CECRL sur de simples QCM."""
import sqlite3
import re
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from pathlib import Path
import streamlit as st

DB = Path(__file__).with_name('suivi_langues_v48.sqlite3')
LANGUES = [('🇪🇸', 'Espagnol', 'es', 'A2'), ('🇬🇧', 'Anglais', 'en', 'B1 (entretien)'), ('🇩🇪', 'Allemand', 'de', 'A1 survie'), ('🇮🇹', 'Italien', 'it', 'A1 survie')]

def _connect():
    db = sqlite3.connect(str(DB), timeout=5)
    db.execute('CREATE TABLE IF NOT EXISTS resultats (langue TEXT NOT NULL, activite TEXT NOT NULL, meilleur_score INTEGER NOT NULL, total INTEGER NOT NULL, tentatives INTEGER NOT NULL DEFAULT 1, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(langue, activite))')
    db.execute('CREATE TABLE IF NOT EXISTS phrase_acquis (langue TEXT NOT NULL, identifiant TEXT NOT NULL, texte TEXT NOT NULL, meilleur_resultat INTEGER NOT NULL DEFAULT 0, tentatives INTEGER NOT NULL DEFAULT 0, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(langue, identifiant))')
    db.execute('CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY AUTOINCREMENT, langue TEXT NOT NULL, activite TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    return db

def enregistrer_phrases(langue, activite, phrases, reponses):
    """Suivi de reconnaissance par phrase ; une phrase correcte n'est pas une production maîtrisée."""
    if langue not in ('es','en','de','it'):
        return
    try:
        with _connect() as db:
            for i, ((texte, traduction), reponse) in enumerate(zip(phrases, reponses)):
                db.execute("""INSERT INTO phrase_acquis(langue,identifiant,texte,meilleur_resultat,tentatives)
                    VALUES(?,?,?,?,1) ON CONFLICT(langue,identifiant) DO UPDATE SET
                    meilleur_resultat=max(meilleur_resultat,excluded.meilleur_resultat),
                    tentatives=tentatives+1,updated_at=CURRENT_TIMESTAMP""",
                    (langue, f'{activite}:{i}', texte, int(reponse == traduction)))
    except (OSError, sqlite3.Error):
        st.session_state.setdefault('phrases_fallback', []).append((langue, activite, phrases, reponses))

def enregistrer(langue, activite, score, total):
    """Ne conserve que le meilleur score pour éviter de gonfler la maîtrise par répétition."""
    if langue not in ('es','en','de','it') or not 0 <= score <= total or total <= 0:
        return
    try:
        with _connect() as db:
            db.execute('INSERT INTO journal(langue,activite,score,total) VALUES(?,?,?,?)', (langue,activite,score,total))
            db.execute('''INSERT INTO resultats(langue,activite,meilleur_score,total) VALUES(?,?,?,?)
                ON CONFLICT(langue,activite) DO UPDATE SET meilleur_score=max(meilleur_score,excluded.meilleur_score), tentatives=tentatives+1,updated_at=CURRENT_TIMESTAMP''', (langue,activite,score,total))
    except (OSError,sqlite3.Error):
        state=st.session_state.setdefault('suivi_v48_fallback',{})
        old=state.get((langue,activite),(0,total,0))
        state[(langue,activite)]=(max(score,old[0]),total,old[2]+1)

def lire(langue):
    try:
        with _connect() as db:
            return db.execute('SELECT activite,meilleur_score,total,tentatives,updated_at FROM resultats WHERE langue=? ORDER BY activite',(langue,)).fetchall()
    except (OSError,sqlite3.Error):
        return [(a,s,t,n,'Session en cours') for (l,a),(s,t,n) in st.session_state.get('suivi_v48_fallback',{}).items() if l==langue]

def _bilan(langue):
    try:
        with _connect() as db:
            phrases=db.execute('SELECT texte,meilleur_resultat,tentatives FROM phrase_acquis WHERE langue=?',(langue,)).fetchall()
            events=db.execute('SELECT activite,score,total,created_at FROM journal WHERE langue=? ORDER BY created_at',(langue,)).fetchall()
    except (OSError,sqlite3.Error):
        phrases=[]; events=[]
    # Le vocabulaire est un inventaire de mots rencontrés dans les phrases évaluées,
    # PAS une mesure de mots maîtrisés. Les apostrophes et accents sont conservés.
    mots=set()
    for texte,_,_ in phrases:
        mots.update(re.findall(r"[\wÀ-ÿ]+(?:['’][\wÀ-ÿ]+)?",texte.lower(),flags=re.UNICODE))
    return phrases,events,mots

def _prevision(events, total_objectif):
    """Fourchette empirique seulement après >= 7 jours et 5 activités distinctes."""
    if len(events)<8 or len({x[0] for x in events})<5:
        return None
    dates=[]
    for _,_,_,date in events:
        try: dates.append(datetime.fromisoformat(date).date())
        except ValueError: pass
    if not dates or (max(dates)-min(dates)).days<7:
        return None
    best={}
    for activity,score,total,_ in events:
        best[activity]=max(best.get(activity,0), int(score==total))
    achieved=sum(best.values())
    remaining=max(0,total_objectif-achieved)
    weeks=max(1,(max(dates)-min(dates)).days/7)
    rate=achieved/weeks
    if rate<=0 or remaining==0: return None
    low=max(1,int(remaining/rate*0.8))
    high=max(low+1,int(remaining/rate*1.5+0.99))
    return low,high

def page():
    st.title('🌍 Mes langues & ma progression')
    st.caption('Progression issue des exercices, sans sélection manuelle du niveau. Les résultats sont des indices de compréhension écrite, pas une certification CECRL.')
    for drapeau,nom,code,but in LANGUES:
        rows=lire(code)
        phrases,events,mots=_bilan(code)
        valides=sum(score==maximum for _,score,maximum,*_ in rows)
        reconnues=sum(bool(resultat) for _,resultat,_ in phrases)
        with st.container(border=True):
            st.subheader(f'{drapeau} {nom} · 🎯 {but}')
            if not rows:
                st.info('À évaluer : aucune activité enregistrée dans cette langue.')
                st.caption('Le suivi sera activé quand des exercices de cette langue seront disponibles.')
                continue
            a,b,c=st.columns(3)
            a.metric('🧩 Activités réussies',f'{valides}/{len(rows)}')
            b.metric('💬 Phrases reconnues',f'{reconnues}/{len(phrases)}')
            c.metric('📖 Mots rencontrés',len(mots))
            st.progress(valides/21 if code=='es' else valides/max(1,len(rows)),text='Progression des leçons évaluées (pas du niveau CECRL)')
            st.caption('Les mots sont dédupliqués à partir des phrases travaillées. « Rencontré » ne signifie pas « maîtrisé ». Les phrases sont reconnues en QCM, pas encore produites librement.')
            st.write('**Niveau CECRL détecté :** données insuffisantes pour une estimation fiable (production, compréhension orale et dialogues à évaluer).')
            forecast=_prevision(events,21 if code=='es' else max(1,len(rows)))
            if forecast:
                lo,hi=forecast
                d1=(datetime.now().date()+timedelta(weeks=lo)).strftime('%d/%m/%Y')
                d2=(datetime.now().date()+timedelta(weeks=hi)).strftime('%d/%m/%Y')
                st.write(f'📅 **Projection des leçons restantes :** environ {lo} à {hi} semaines ({d1} – {d2}), si ton rythme se maintient.')
                st.caption('Projection indicative des leçons, et non une date d’obtention du niveau CECRL.')
            else:
                st.write('📅 **Prévision :** en attente de 7 jours de recul et d’au moins 5 activités différentes.')
            with st.expander('📚 Carnet des phrases et activités'):
                for texte,ok,n in phrases:
                    st.write(('✅ ' if ok else '🔁 ')+texte+f' · {n} essai(s)')
                if not phrases: st.caption('Aucune phrase suivie pour le moment.')
                st.divider()
                for activite,score,maximum,tentatives,date in rows:
                    st.write(f'{activite} : {score}/{maximum} · {tentatives} tentative(s) · {date}')
    st.caption('Stockage SQLite local : non individualisé par compte, et potentiellement temporaire sur Streamlit Cloud. Ne pas utiliser comme suivi multi-utilisateurs sans authentification et stockage persistant.')
