"""Compléments pédagogiques CECRL, persistance et entraînement écrit."""
import random, re, unicodedata
from datetime import datetime, date
import moteur as m
DIMENSIONS=['Compréhension écrite','Compréhension orale','Expression écrite','Expression orale','Interaction']
DESCRIPTEURS={
'A1':['Lire des mots familiers et des phrases simples','Reconnaître des mots familiers prononcés lentement','Écrire de courtes phrases sur soi','Se présenter avec des expressions simples','Répondre à des questions personnelles simples'],
'A2':['Lire de courts textes usuels','Comprendre des expressions fréquentes','Écrire des messages simples','Décrire son environnement','Échanger dans des tâches routinières'],
'B1':['Comprendre des textes courants','Suivre les points principaux d’un discours clair','Écrire un texte suivi','Raconter des expériences','Faire face aux situations de voyage'],
'B2':['Comprendre des textes complexes','Suivre un discours développé','Rédiger des textes détaillés','Défendre une opinion','Interagir avec spontanéité'],
'C1':['Comprendre des textes longs exigeants','Suivre des discours longs implicites','Écrire des textes structurés complexes','S’exprimer avec fluidité','Adapter son langage au contexte'],
'C2':['Comprendre presque tous les textes','Comprendre presque tout discours','Rédiger avec nuance','S’exprimer avec finesse','Participer à des échanges complexes']}

def init():
    # Les tables pédagogiques ont été migrées vers Supabase.
    # Ne pas exécuter de DDL au démarrage de l'application.
    return None

def normaliser(texte):
    s=unicodedata.normalize('NFD',str(texte).casefold())
    return ' '.join(re.sub('[^a-z0-9 ]',' ',''.join(c for c in s if unicodedata.category(c)!='Mn')).split())

def exercices(niveau,n=20,exclure=None,lecon=None):
    """Réactive les traductions ratées et renouvelle le reste du lot."""
    lecons=[lecon] if lecon else m.COURS.get(niveau,[])
    pool=list(dict.fromkeys((fr,es) for lesson in lecons
        for es,fr in (lesson['expressions']+lesson['exemples']) if 3<=len(es.split()) and len(es)<180 and len(fr)<180))
    if not pool:return []
    exclure=set(tuple(x) for x in (exclure or []))
    erreurs=m.rows("""SELECT consigne,attendu FROM productions WHERE niveau=? AND valide=0
        ORDER BY id DESC LIMIT 100""",(niveau,))
    priorites=list(dict.fromkeys((r['consigne'],r['attendu']) for r in erreurs if
        (r['consigne'],r['attendu']) in pool))
    random.shuffle(priorites)
    # Au moins la moitié du nouveau lot varie lorsque le catalogue le permet.
    quota=min(len(priorites),max(1,n//2))
    choisis=priorites[:quota]
    reste=[x for x in pool if x not in choisis and x not in exclure]
    random.shuffle(reste)
    choisis+=reste[:max(0,n-len(choisis))]
    if len(choisis)<n:
        autres=[x for x in pool if x not in choisis]
        random.shuffle(autres);choisis+=autres[:n-len(choisis)]
    random.shuffle(choisis)
    return choisis

def production(niveau,dimension,consigne,reponse,attendu=None):
    valide=None if attendu is None else int(normaliser(reponse)==normaliser(attendu))
    with m.connexion() as c:
        c.execute('INSERT INTO productions(date,niveau,dimension,consigne,reponse,attendu,valide,methode) VALUES(?,?,?,?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),niveau,dimension,consigne,reponse,attendu,valide,'correction stricte' if attendu else 'non évaluée'))
    return valide

def evaluer(niveau,dimension,score,commentaire):
    with m.connexion() as c:
        c.execute('INSERT INTO evaluations_cecrl(date,niveau,dimension,score,commentaire) VALUES(?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),niveau,dimension,int(score),commentaire[:1000]))

def profil(niveau):
    result={}
    for dim in DIMENSIONS:
        data=m.rows('SELECT score FROM evaluations_cecrl WHERE niveau=? AND dimension=? ORDER BY id DESC LIMIT 5',(niveau,dim))
        result[dim]=round(sum(r['score'] for r in data)/len(data),1) if data else None
    return result

def plan(niveau,minutes):
    due=[x for x in m.revisions(niveau) if x['prochaine_revision'] and x['prochaine_revision']<=date.today().isoformat()]
    faibles=m.rows('SELECT nom,maitrise FROM competences WHERE niveau=? AND essais>0 ORDER BY maitrise LIMIT 4',(niveau,))
    weights=[('Cours',.25),('Révisions',.25 if due else .15),('Écoute / oral',.25 if due else .35),('Expression écrite',.15),('Coach IA',.10)]
    return [(label,round(minutes*weight)) for label,weight in weights],due,faibles

def audio(niveau,phrase,activite,note=''):
    with m.connexion() as c:c.execute('INSERT INTO pratiques_audio(date,niveau,phrase,activite,note) VALUES(?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),niveau,phrase,activite,note[:500]))


def statistiques_ecriture(niveau):
    rows=m.rows("SELECT valide FROM productions WHERE niveau=? AND dimension='Expression écrite' ORDER BY id DESC LIMIT 100",(niveau,))
    return (round(100*sum(int(r['valide'] or 0) for r in rows)/len(rows),1),len(rows)) if rows else (0,0)

def init_oral():
    # La table comprehension_orale existe déjà dans Supabase.
    return None

def enregistrer_comprehension(niveau,phrase,attendu,reponse):
    init_oral()
    valide=int(normaliser(attendu)==normaliser(reponse))
    with m.connexion() as c:
        c.execute('INSERT INTO comprehension_orale(date,niveau,phrase,attendu,reponse,valide) VALUES(?,?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),niveau,phrase,attendu,reponse,valide))
    return valide

def progression_orale(niveau):
    init_oral()
    rows=m.rows('SELECT valide FROM comprehension_orale WHERE niveau=? ORDER BY id DESC LIMIT 20',(niveau,))
    return (round(100*sum(r['valide'] for r in rows)/len(rows),1),len(rows)) if rows else (0,0)

def oral_debloque(niveau):
    if niveau==m.NIVEAUX[0]:return True
    precedent=m.NIVEAUX[m.NIVEAUX.index(niveau)-1]
    score,total=progression_orale(precedent)
    return total>=20 and score>=95 and oral_debloque(precedent)

def banque_orale(niveau,maximum=500,lecon=None):
    # Énoncés réels du cours, complétés par des combinaisons de deux phrases distinctes.
    base=list(dict.fromkeys((es.strip().rstrip('.!?')+'.',fr.strip().rstrip('.!?')+'.')
        for lesson in ([lecon] if lecon else m.COURS[niveau]) for es,fr in lesson['exemples']
        if len(es.split())>=3 and len(fr.split())>=3))
    banque=list(base)
    if len(banque)<maximum:
        for i,(es,fr) in enumerate(base):
            for j,(es2,fr2) in enumerate(base):
                if i!=j:
                    banque.append((es+' '+es2,fr+' '+fr2))
                    if len(banque)>=maximum:break
            if len(banque)>=maximum:break
    return banque[:maximum]

def tirage_oral(niveau,exclure=None,lecon=None):
    init_oral()
    pool=banque_orale(niveau,lecon=lecon)
    if not pool:return None
    derniers=m.rows('SELECT phrase,valide FROM comprehension_orale WHERE niveau=? ORDER BY id DESC LIMIT 120',(niveau,))
    poids={}
    for r in reversed(derniers):poids[r['phrase']]=5 if not r['valide'] else 0.3
    exclure=set(exclure or [])
    candidats=[pair for pair in pool if pair[0] not in exclure] or pool
    return random.choices(candidats,weights=[poids.get(es,1.5) for es,fr in candidats],k=1)[0]
