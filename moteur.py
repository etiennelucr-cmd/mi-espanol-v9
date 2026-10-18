"""Persistance SQLite et moteur pédagogique adaptatif, sans dépendance Streamlit."""
import json, math, random, sqlite3
from datetime import datetime, timedelta, date
from pathlib import Path

BASE = Path(__file__).resolve().parent / 'espagnol_v2.db'
DATA = json.loads((Path(__file__).resolve().parent / 'contenu.json').read_text(encoding='utf-8'))
COURS, LEXIQUE = DATA['cours'], DATA['lexique']
NIVEAUX = ['A1','A2','B1','B2','C1','C2']

def connexion():
    c=sqlite3.connect(BASE,timeout=20)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init():
    with connexion() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY, debut TEXT NOT NULL, date TEXT NOT NULL, type TEXT NOT NULL, niveau TEXT, lecon_id TEXT, minutes REAL NOT NULL DEFAULT 0, note TEXT);
        CREATE TABLE IF NOT EXISTS lecons(id TEXT PRIMARY KEY, niveau TEXT NOT NULL, titre TEXT NOT NULL, statut TEXT NOT NULL DEFAULT 'non commencé', debut TEXT, fin TEXT, visites INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS questions(id TEXT PRIMARY KEY, niveau TEXT NOT NULL, lecon_id TEXT, competence TEXT NOT NULL, type TEXT NOT NULL, enonce TEXT NOT NULL, options TEXT NOT NULL, bonne TEXT NOT NULL, explication TEXT, source TEXT NOT NULL DEFAULT 'catalogue');
        CREATE TABLE IF NOT EXISTS tentatives(id INTEGER PRIMARY KEY, date TEXT NOT NULL, type TEXT NOT NULL, niveau TEXT NOT NULL, lecon_id TEXT, score INTEGER NOT NULL, total INTEGER NOT NULL, secondes INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS reponses(id INTEGER PRIMARY KEY, tentative_id INTEGER NOT NULL REFERENCES tentatives(id), question_id TEXT NOT NULL, competence TEXT NOT NULL, choix TEXT, correct INTEGER NOT NULL, date TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS competences(code TEXT PRIMARY KEY, niveau TEXT NOT NULL, nom TEXT NOT NULL, maitrise REAL NOT NULL DEFAULT 0.3, essais INTEGER NOT NULL DEFAULT 0, succes INTEGER NOT NULL DEFAULT 0, intervalle INTEGER NOT NULL DEFAULT 1, prochaine_revision TEXT, derniere_revision TEXT);
        CREATE TABLE IF NOT EXISTS progression_jour(date TEXT NOT NULL, niveau TEXT NOT NULL, score REAL NOT NULL, confiance REAL NOT NULL, PRIMARY KEY(date,niveau));
        CREATE TABLE IF NOT EXISTS objectifs(cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS recompenses(code TEXT PRIMARY KEY, date TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS preferences(cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
        ''')
        for niveau, lecons in COURS.items():
            for lecon in lecons:
                c.execute('INSERT OR IGNORE INTO lecons(id,niveau,titre) VALUES(?,?,?)',(lecon['id'],niveau,lecon['titre']))
                for j,(titre,_) in enumerate(lecon['grammaire']):
                    code=f"{lecon['id']}-g{j}"
                    c.execute('INSERT OR IGNORE INTO competences(code,niveau,nom) VALUES(?,?,?)',(code,niveau,titre))
                code=f"{lecon['id']}-vocab"
                c.execute('INSERT OR IGNORE INTO competences(code,niveau,nom) VALUES(?,?,?)',(code,niveau,'Vocabulaire : '+lecon['titre']))
                for i,q in enumerate(lecon['questions']):
                    code=f"{lecon['id']}-g0"
                    c.execute('INSERT OR IGNORE INTO questions(id,niveau,lecon_id,competence,type,enonce,options,bonne,explication) VALUES(?,?,?,?,?,?,?,?,?)',
                        (f"{lecon['id']}-q{i}",niveau,lecon['id'],code,'qcm',q['question'],json.dumps(q['options'],ensure_ascii=False),q['options'][q['reponse']],q['explication']))
                # Questions de traduction du vocabulaire, réponses contrôlées et distracteurs du même cours
                vocab=lecon['vocabulaire']
                for i,(es,fr) in enumerate(vocab):
                    distracteurs=[x[1] for x in vocab if x[1]!=fr]
                    if len(distracteurs)<2: continue
                    opts=[fr]+random.Random(f'{lecon["id"]}-{i}').sample(distracteurs,2)
                    c.execute('INSERT OR IGNORE INTO questions(id,niveau,lecon_id,competence,type,enonce,options,bonne,explication) VALUES(?,?,?,?,?,?,?,?,?)',
                        (f"{lecon['id']}-v{i}",niveau,lecon['id'],f"{lecon['id']}-vocab",'qcm',f'Que signifie « {es} » ?',json.dumps(opts,ensure_ascii=False),fr,f'{es} = {fr}'))
                # Variantes de traduction inverse et de reconnaissance pour obtenir
                # 20 questions par leçon sans dépendre d'une API externe.
                for i,(es,fr) in enumerate(vocab):
                    autres=[x[0] for x in vocab if x[0]!=es]
                    if len(autres)<2:continue
                    opts=[es]+random.Random(f'inverse-{lecon["id"]}-{i}').sample(autres,2)
                    for suffixe,enonce in [('inv',f'Comment dit-on « {fr} » en espagnol ?'),
                                            ('reco',f'Choisis la traduction espagnole de « {fr} ».')]:
                        c.execute('INSERT OR IGNORE INTO questions(id,niveau,lecon_id,competence,type,enonce,options,bonne,explication) VALUES(?,?,?,?,?,?,?,?,?)',
                            (f"{lecon['id']}-{suffixe}{i}",niveau,lecon['id'],f"{lecon['id']}-vocab",'qcm',enonce,json.dumps(opts,ensure_ascii=False),es,f'{fr} = {es}'))
        c.execute("INSERT OR IGNORE INTO objectifs(cle,valeur) VALUES('minutes','30')")

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
        q['options']=json.loads(q['options']);random.shuffle(q['options'])
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
            score=.35*lesson+.20*ratio(['Exercice'])+.30*ratio(['Contrôle'])+.15*ratio(['Révision','Remédiation'])
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
    """Score interne 0-100 combinant achèvement, quiz, contrôles et révisions.
    Une activité absente vaut 0, pour éviter de valider un niveau sur une seule source.
    """
    le=rows("SELECT COUNT(*) n, SUM(CASE WHEN statut='terminé' THEN 1 ELSE 0 END) finis FROM lecons WHERE niveau=?",(niveau,))[0]
    total=max(1,le['n']);cours=(le['finis'] or 0)/total
    valeurs={}
    for typ,nom in [('Exercice','quiz'),('Contrôle','controle'),('Révision','revision'),('Remédiation','remediation')]:
        r=rows('SELECT COALESCE(SUM(score),0) points, COALESCE(SUM(total),0) total, COUNT(*) n FROM tentatives WHERE niveau=? AND type=?',(niveau,typ))[0]
        valeurs[nom]=(r['points']/r['total']) if r['total'] else 0
        valeurs[nom+'_n']=r['n']
    # Révisions et remédiations comptent ensemble.
    rr=rows("SELECT COALESCE(SUM(score),0) points,COALESCE(SUM(total),0) total FROM tentatives WHERE niveau=? AND type IN ('Révision','Remédiation')",(niveau,))[0]
    rev=rr['points']/rr['total'] if rr['total'] else 0
    score=100*(.35*cours+.20*valeurs['quiz']+.30*valeurs['controle']+.15*rev)
    return {'niveau':niveau,'pourcentage':round(score,1),'cours':round(100*cours,1),'quiz':round(100*valeurs['quiz'],1),'controles':round(100*valeurs['controle'],1),'revisions':round(100*rev,1),'lecons_terminees':le['finis'] or 0,'lecons_total':le['n'],'nb_quiz':valeurs['quiz_n'],'nb_controles':valeurs['controle_n'],'nb_revisions':valeurs['revision_n']+valeurs['remediation_n']}

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
    """Un thème est validé avec leçon terminée et dernière évaluation >=98%."""
    resultat=[]
    for lecon in COURS[niveau]:
        etat=rows('SELECT statut FROM lecons WHERE id=?',(lecon['id'],))
        essai=rows("""SELECT score,total FROM tentatives WHERE niveau=? AND lecon_id=?
            AND type='Exercice' ORDER BY id DESC LIMIT 1""",(niveau,lecon['id']))
        valide=bool(etat and etat[0]['statut']=='terminé' and essai and
            essai[0]['total']>=20 and essai[0]['score']/essai[0]['total']>=SEUIL_VALIDATION)
        resultat.append({'titre':lecon['titre'],'valide':valide})
    return resultat

def niveau_debloque(niveau):
    index=NIVEAUX.index(niveau)
    return index==0 or all(x['valide'] for x in themes_valides(NIVEAUX[index-1]))
