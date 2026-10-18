"""Moteur pédagogique adaptatif avec persistance PostgreSQL (Supabase)."""
import json, math, random
from datetime import datetime, timedelta, date
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parent / 'espagnol_v2.db'
DATA = json.loads((Path(__file__).resolve().parent / 'contenu.json').read_text(encoding='utf-8'))
COURS, LEXIQUE = DATA['cours'], DATA['lexique']
NIVEAUX = ['A1','A2','B1','B2','C1','C2']

# Adaptation cloud : les tables et leurs données existent déjà dans Supabase.
# Ne jamais recréer ni réimporter les données au démarrage.
from contextlib import contextmanager
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import streamlit as st

def _normaliser(valeur):
    """Restitue les types attendus par le moteur historique SQLite."""
    if isinstance(valeur, Decimal):
        return float(valeur)
    if isinstance(valeur, (datetime, date)):
        return valeur.isoformat()
    if isinstance(valeur, dict):
        return {cle: _normaliser(v) for cle, v in valeur.items()}
    if isinstance(valeur, list):
        return [_normaliser(v) for v in valeur]
    return valeur

class _Cursor:
    def __init__(self, cursor, inserted_id=None):
        self._cursor = cursor
        self.lastrowid = inserted_id
    def fetchone(self):
        return _normaliser(self._cursor.fetchone())
    def fetchall(self):
        return _normaliser(self._cursor.fetchall())

class _Connection:
    def __init__(self, conn):
        self._conn = conn
    def execute(self, query, params=()):
        # Les requêtes existantes de moteur.py utilisent des marqueurs SQLite '?'.
        # Elles ne contiennent pas de '?' littéral dans le SQL actuel.
        # Compatibilité PostgreSQL : ROUND(double precision, 1) nécessite numeric.
        query = query.replace('ROUND(SUM(minutes),1)', 'ROUND(SUM(minutes)::numeric,1)')
        query = query.replace('?', '%s')
        query = query.replace('substr(date,1,10)', 'substring(CAST(date AS TEXT) from 1 for 10)')
        ignore_insert = 'INSERT OR IGNORE INTO' in query.upper()
        query = query.replace('INSERT OR IGNORE INTO', 'INSERT INTO')
        # PostgreSQL requires an explicit conflict clause instead of SQLite OR IGNORE.
        if ignore_insert and 'ON CONFLICT' not in query.upper():
            query += ' ON CONFLICT DO NOTHING'
        # Legacy callers use lastrowid for these identity-backed tables.
        upper = query.lstrip().upper()
        identity_tables = ('INSERT INTO TENTATIVES(', 'INSERT INTO CONJUGAISON_TESTS(')
        if upper.startswith(identity_tables) and 'RETURNING' not in upper:
            query += ' RETURNING id'
            cur = self._conn.execute(query, params)
            row = cur.fetchone()
            return _Cursor(cur, row['id'] if row else None)
        return _Cursor(self._conn.execute(query, params))

    def executemany(self, query, seq_params):
        # Compatibilité PostgreSQL : ROUND(double precision, 1) nécessite numeric.
        query = query.replace('ROUND(SUM(minutes),1)', 'ROUND(SUM(minutes)::numeric,1)')
        query = query.replace('?', '%s')
        ignore_insert = 'INSERT OR IGNORE INTO' in query.upper()
        query = query.replace('INSERT OR IGNORE INTO', 'INSERT INTO')
        if ignore_insert and 'ON CONFLICT' not in query.upper():
            query += ' ON CONFLICT DO NOTHING'
        return _Cursor(self._conn.cursor().executemany(query, seq_params))

@st.cache_resource(show_spinner=False)
def _pool_postgres():
    """Pool partagé entre les relances Streamlit, sans partager une connexion active."""
    cfg = st.secrets['postgres']
    pool = ConnectionPool(
        conninfo='',
        kwargs={
            'host': cfg['host'],
            'port': int(cfg.get('port', 5432)),
            'dbname': cfg.get('dbname', 'postgres'),
            'user': cfg['user'],
            'password': cfg['password'],
            'sslmode': 'require',
            'connect_timeout': 15,
            'row_factory': dict_row,
        },
        min_size=1,
        max_size=4,
        timeout=20,
        open=True,
    )
    pool.wait(timeout=20)
    return pool

@contextmanager
def connexion():
    # pool.connection() rend la connexion au pool et gère commit/rollback.
    with _pool_postgres().connection() as raw:
        yield _Connection(raw)

def init():
    """Schéma et données importés précédemment dans Supabase : ne rien écraser."""
    return None

def rows(sql,args=()):
    with connexion() as c:return [dict(x) for x in c.execute(sql,args).fetchall()]

def objectif():
    return int(rows("SELECT valeur FROM objectifs WHERE cle='minutes'")[0]['valeur'])

def definir_objectif(n):
    with connexion() as c:c.execute("UPDATE objectifs SET valeur=? WHERE cle='minutes'",(str(int(n)),))

def enregistrer_session(type_,minutes,niveau=None,lecon_id=None,note=''):
    minutes=max(0,min(float(minutes),240))
    now=datetime.now().isoformat(timespec='seconds')
    with connexion() as c:
        c.execute('INSERT INTO sessions(debut,date,type,niveau,lecon_id,minutes,note) VALUES(?,?,?,?,?,?,?)',(now,date.today().isoformat(),type_,niveau,lecon_id,minutes,note))
        if type_=='Cours' and lecon_id:
            c.execute("UPDATE lecons SET statut=CASE WHEN statut='terminé' THEN statut ELSE 'en cours' END, debut=COALESCE(debut,?), visites=visites+1 WHERE id=?",(now,lecon_id))
    snapshot()

def terminer_lecon(lecon_id):
    with connexion() as c:c.execute("UPDATE lecons SET statut='terminé', debut=COALESCE(debut,?),fin=? WHERE id=?",(datetime.now().isoformat(timespec='seconds'),datetime.now().isoformat(timespec='seconds'),lecon_id))
    snapshot()

def banque(niveau=None,lecon_id=None,limite=10,mode='adaptatif'):
    conditions=[];params=[]
    if niveau:conditions.append('q.niveau=?');params.append(niveau)
    if lecon_id:conditions.append('q.lecon_id=?');params.append(lecon_id)
    sql='''SELECT q.*,c.maitrise,c.prochaine_revision FROM questions q JOIN competences c ON c.code=q.competence'''
    if conditions:sql+=' WHERE '+' AND '.join(conditions)
    qs=rows(sql,params)
    if mode=='adaptatif':
        today=date.today().isoformat()
        qs.sort(key=lambda q:(q['maitrise']- (0.25 if q['prochaine_revision'] and q['prochaine_revision']<=today else 0),random.random()*0.25))
        # Diversity across skills, with emphasis on weak skills
        pool=qs[:max(limite*4,limite)]
        random.shuffle(pool)
        pool.sort(key=lambda q:q['maitrise']+random.random()*0.18)
        selected=[];used=set()
        for q in pool:
            if q['competence'] not in used:selected.append(q);used.add(q['competence'])
            if len(selected)>=limite:break
        for q in pool:
            if len(selected)>=limite:break
            if q['id'] not in {x['id'] for x in selected}:selected.append(q)
        qs=selected
    else:random.shuffle(qs)
    result=qs[:limite]
    for q in result:
        q['options']=json.loads(q['options']) if isinstance(q['options'], str) else list(q['options']);random.shuffle(q['options'])
    return result

def nom_competence(code):
    r=rows('SELECT nom FROM competences WHERE code=?',(code,))
    return r[0]['nom'] if r else code

def banque_ciblee(niveau,codes,limite=10,exclure=None):
    """Priorité aux notions échouées et aux questions non vues lors du contrôle."""
    exclure=set(exclure or [])
    base=banque(niveau,limite=10000,mode='aleatoire')
    # Si possible, choisir d'abord des questions inédites des compétences faibles.
    priorite=[q for q in base if q['competence'] in codes and q['id'] not in exclure]
    autres=[q for q in base if q['competence'] in codes and q['id'] in exclure]
    renfort=[q for q in base if q['competence'] not in codes and q['id'] not in exclure]
    random.shuffle(priorite);random.shuffle(autres);random.shuffle(renfort)
    return (priorite+renfort+autres)[:limite]

def enregistrer_test(type_,niveau,lecon_id,questions,reponses,secondes=0):
    if not questions:raise ValueError('Aucune question à corriger')
    now=datetime.now().isoformat(timespec='seconds');today=date.today()
    score=sum(reponses.get(q['id'])==q['bonne'] for q in questions)
    with connexion() as c:
        cur=c.execute('INSERT INTO tentatives(date,type,niveau,lecon_id,score,total,secondes) VALUES(?,?,?,?,?,?,?)',(now,type_,niveau,lecon_id,score,len(questions),max(0,int(secondes))))
        tid=cur.lastrowid
        for q in questions:
            choix=reponses.get(q['id']);correct=int(choix==q['bonne'])
            c.execute('INSERT INTO reponses(tentative_id,question_id,competence,choix,correct,date) VALUES(?,?,?,?,?,?)',(tid,q['id'],q['competence'],choix,correct,now))
            old=c.execute('SELECT * FROM competences WHERE code=?',(q['competence'],)).fetchone()
            if old is None:continue
            # Estimation heuristique lissée (non certification CECRL)
            mastery=max(0.05,min(0.99,float(old['maitrise'])*0.82+0.18*correct))
            interval=min(60,max(1,round(old['intervalle']*1.8))) if correct else 1
            if correct and old['intervalle'] == 1 and old['essais'] >= 1: interval = 2
            c.execute('''UPDATE competences SET maitrise=?, essais=essais+1, succes=succes+?, intervalle=?, derniere_revision=?, prochaine_revision=? WHERE code=?''',
                      (mastery,correct,interval,today.isoformat(),(today+timedelta(days=interval)).isoformat(),q['competence']))
    snapshot()
    return tid,score

def snapshot():
    today=date.today().isoformat()
    with connexion() as c:
        for niveau in NIVEAUX:
            r=c.execute('SELECT AVG(maitrise) m,SUM(essais) n FROM competences WHERE niveau=?',(niveau,)).fetchone()
            n=int(r['n'] or 0)
            l=c.execute("SELECT COUNT(*) total, SUM(CASE WHEN statut='terminé' THEN 1 ELSE 0 END) finis FROM lecons WHERE niveau=?",(niveau,)).fetchone()
            lesson=(l['finis'] or 0)/max(1,l['total'])
            def ratio(types):
                marks=','.join('?' for _ in types)
                t=c.execute(f'SELECT COALESCE(SUM(score),0) a, COALESCE(SUM(total),0) b FROM tentatives WHERE niveau=? AND type IN ({marks})',(niveau,*types)).fetchone()
                return t['a']/t['b'] if t['b'] else 0
            score=.35*float(lesson)+.20*float(ratio(['Exercice']))+.30*float(ratio(['Contrôle']))+.15*float(ratio(['Révision','Remédiation']))
            confiance=min(1.0,n/40)
            c.execute('INSERT INTO progression_jour(date,niveau,score,confiance) VALUES(?,?,?,?) ON CONFLICT(date,niveau) DO UPDATE SET score=excluded.score,confiance=excluded.confiance',(today,niveau,score,confiance))

def niveau_estime():
    # Estimation prudente : un niveau doit avoir des observations suffisantes et maîtrise élevée.
    niveau='A1'
    for n in NIVEAUX:
        r=rows('SELECT AVG(maitrise) m,SUM(essais) essais FROM competences WHERE niveau=?',(n,))[0]
        if (r['essais'] or 0)>=20 and (r['m'] or 0)>=0.8:niveau=n
        else:break
    return niveau

def projection(niveau):
    hist=rows('SELECT date,score,confiance FROM progression_jour WHERE niveau=? ORDER BY date',(niveau,))
    if len(hist)<7:return None
    # 7+ dates distinctes, positive observed trend; avoids fabricated precision
    recent=hist[-14:];start=date.fromisoformat(recent[0]['date']);end=date.fromisoformat(recent[-1]['date']);span=(end-start).days
    if span<6:return None
    slope=(recent[-1]['score']-recent[0]['score'])/span
    if slope<=0.001 or recent[-1]['confiance']<0.5:return None
    days=(0.8-recent[-1]['score'])/slope
    if days<=0 or days>730:return None
    estimate=date.today()+timedelta(days=math.ceil(days))
    return {'debut':(date.today()+timedelta(days=max(1,int(days*.7)))).isoformat(),'fin':(date.today()+timedelta(days=int(days*1.5)+1)).isoformat(),'centre':estimate.isoformat()}

def statistiques():
    today=date.today().isoformat()
    s=rows('SELECT COALESCE(SUM(minutes),0) minutes,COUNT(*) activites FROM sessions WHERE date=?',(today,))[0]
    t=rows('SELECT COUNT(*) tests,COALESCE(SUM(score),0) bons,COALESCE(SUM(total),0) total FROM tentatives WHERE substr(date,1,10)=?', (today,))[0]
    return {**s,**t,'xp':int(rows('SELECT COALESCE(SUM(score),0)*10+COUNT(*)*5 xp FROM tentatives')[0]['xp'])}

def revisions(niveau=None):
    sql='SELECT * FROM competences WHERE essais>0';params=[]
    if niveau:sql+=' AND niveau=?';params.append(niveau)
    sql+=' ORDER BY CASE WHEN prochaine_revision IS NULL THEN 1 ELSE 0 END,prochaine_revision,maitrise'
    return rows(sql,params)

def erreurs(niveau=None):
    sql='''SELECT c.code,c.nom,c.niveau,COUNT(*) erreurs FROM reponses r JOIN competences c ON c.code=r.competence WHERE r.correct=0''';params=[]
    if niveau:sql+=' AND c.niveau=?';params.append(niveau)
    sql+=' GROUP BY c.code ORDER BY erreurs DESC LIMIT 12'
    return rows(sql,params)


def preference(cle, defaut=None):
    r=rows('SELECT valeur FROM preferences WHERE cle=?',(cle,))
    return r[0]['valeur'] if r else defaut

def definir_preference(cle,valeur):
    with connexion() as c:
        c.execute('INSERT INTO preferences(cle,valeur) VALUES(?,?) ON CONFLICT(cle) DO UPDATE SET valeur=excluded.valeur',(cle,str(valeur)))

def progression_globale(niveau):
    """Progression identique, avec 2 requêtes au lieu de 6."""
    le = rows(
        "SELECT COUNT(*) n, SUM(CASE WHEN statut='terminé' THEN 1 ELSE 0 END) finis "
        "FROM lecons WHERE niveau=?", (niveau,)
    )[0]
    cours = (le['finis'] or 0) / max(1, le['n'])
    bilans = rows(
        "SELECT type, COALESCE(SUM(score),0) points, "
        "COALESCE(SUM(total),0) total, COUNT(*) n "
        "FROM tentatives WHERE niveau=? "
        "AND type IN ('Exercice','Contrôle','Révision','Remédiation') "
        "GROUP BY type", (niveau,)
    )
    par_type = {r['type']: r for r in bilans}
    def ratio(typ):
        r = par_type.get(typ)
        return float(r['points']) / float(r['total']) if r and r['total'] else 0.0
    quiz = ratio('Exercice')
    controle = ratio('Contrôle')
    revisions = [par_type[t] for t in ('Révision','Remédiation') if t in par_type]
    points_rev = sum(float(r['points']) for r in revisions)
    total_rev = sum(float(r['total']) for r in revisions)
    rev = points_rev / total_rev if total_rev else 0.0
    score = 100 * (.35*cours + .20*quiz + .30*controle + .15*rev)
    def nb(typ):
        return par_type[typ]['n'] if typ in par_type else 0
    return {
        'niveau': niveau, 'pourcentage': round(score,1),
        'cours': round(100*cours,1), 'quiz': round(100*quiz,1),
        'controles': round(100*controle,1), 'revisions': round(100*rev,1),
        'lecons_terminees': le['finis'] or 0, 'lecons_total': le['n'],
        'nb_quiz': nb('Exercice'), 'nb_controles': nb('Contrôle'),
        'nb_revisions': nb('Révision') + nb('Remédiation')
    }

def projection_globale(niveau):
    """Projection indicative à 98% du score combiné."""
    hist=rows('SELECT date,score,confiance FROM progression_jour WHERE niveau=? ORDER BY date',(niveau,))
    if len(hist)<7:return None
    recent=hist[-14:]
    start=date.fromisoformat(recent[0]['date']);end=date.fromisoformat(recent[-1]['date']);jours=(end-start).days
    if jours<6:return None
    courant=progression_globale(niveau)['pourcentage']/100
    if courant>=.98:return {'atteint':True,'centre':date.today().isoformat()}
    pente=(recent[-1]['score']-recent[0]['score'])/jours
    if pente<=0.0005 or recent[-1]['confiance']<.35:return None
    attente=(.98-courant)/pente
    if attente<=0 or attente>730:return None
    return {'atteint':False,'centre':(date.today()+timedelta(days=math.ceil(attente))).isoformat(), 'debut':(date.today()+timedelta(days=max(1,int(attente*.7)))).isoformat(),'fin':(date.today()+timedelta(days=int(attente*1.5)+1)).isoformat()}


SEUIL_VALIDATION = 0.98

def themes_valides(niveau):
    """Validation inchangée ; lecture groupée de toutes les leçons et tentatives."""
    etats = rows('SELECT id, statut FROM lecons WHERE niveau=?', (niveau,))
    statuts = {r['id']: r['statut'] for r in etats}
    derniers = rows(
        "SELECT DISTINCT ON (lecon_id) lecon_id, score, total "
        "FROM tentatives WHERE niveau=? AND type='Exercice' "
        "AND lecon_id IS NOT NULL ORDER BY lecon_id, id DESC", (niveau,)
    )
    essais = {r['lecon_id']: r for r in derniers}
    resultat = []
    for lecon in COURS[niveau]:
        essai = essais.get(lecon['id'])
        valide = bool(
            statuts.get(lecon['id']) == 'terminé'
            and essai and essai['total'] >= 20
            and float(essai['score']) / float(essai['total']) >= SEUIL_VALIDATION
        )
        resultat.append({'titre': lecon['titre'], 'valide': valide})
    return resultat

def niveau_debloque(niveau):
    index=NIVEAUX.index(niveau)
    return index==0 or all(x['valide'] for x in themes_valides(NIVEAUX[index-1]))
