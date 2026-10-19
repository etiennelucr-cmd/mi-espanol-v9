"""Indicateurs et thème central du planning, sans migration de schéma."""
import re
from collections import defaultdict
import moteur as m
import coach_parcours as coach

def theme(niveau):
    lecons=m.COURS.get(niveau,[])
    return next((l for l in lecons if not coach.valide(niveau,l)),lecons[-1] if lecons else None)

def progression(niveau):
    lecons=m.COURS.get(niveau,[])
    valides=sum(coach.valide(niveau,l) for l in lecons)
    return valides,len(lecons)

def phrases(niveau,lecon=None):
    lecon=lecon or theme(niveau)
    if not lecon:return []
    return list(dict.fromkeys((fr,es) for es,fr in (lecon.get('exemples',[])+lecon.get('expressions',[])) if len(es.split())>=3 and len(fr.split())>=3))

def mots_acquis(niveau):
    """Estimation conservatrice: mots du vocabulaire du niveau vus dans >=2 productions exactes.
    Pas un décompte certifié de mots connus; n'inclut pas les QCM faute de preuve lexicale.
    """
    lexique={}
    for l in m.COURS.get(niveau,[]):
        for es,fr in l.get('vocabulaire',[]):
            for mot in re.findall(r"[a-záéíóúüñ]+",es.lower()):
                if len(mot)>2:lexique[mot]=1
    if not lexique:return 0
    lignes=m.rows("SELECT attendu FROM productions WHERE niveau=? AND valide=1",(niveau,))
    occurrences=defaultdict(int)
    for r in lignes:
        mots=set(re.findall(r"[a-záéíóúüñ]+",(r['attendu'] or '').lower()))
        for mot in mots & lexique.keys():occurrences[mot]+=1
    return sum(v>=2 for v in occurrences.values())
