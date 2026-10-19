"""Exercices basés sur les leçons et la fiche de conjugaison, sans IA externe."""
import random
import re
import unicodedata
from pathlib import Path
import json
import conjugaison_parcours as conj
import moteur as m

VERBES=json.loads((Path(__file__).parent/'verbes.json').read_text(encoding='utf-8'))

def _net(s):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(s).lower()) if unicodedata.category(c)!='Mn').split())

def _sources(lecon):
    result=[]
    for kind in ('exemples','expressions'):
        for es,fr in lecon.get(kind,[]):
            if es and fr and len(es.split())>=2 and len(fr.split())>=2:
                result.append((fr.strip(),es.strip(),kind))
    return list(dict.fromkeys(result))

def _temps(niveau):
    import planning_adaptatif as planning
    _,_,_,j=planning.priorites(niveau)
    temps=conj.PARCOURS[niveau]
    return temps[j if j is not None else 0]

def phrases(niveau,lecon,n=20,exclure=()):
    """Phrases authentiques puis combinaisons de deux propositions attestées.
    Ne crée pas de fausses conjugaisons : l'original reste inchangé.
    """
    base=_sources(lecon)
    code,_=_temps(niveau)
    exemple=conj.EXPLICATIONS.get(code,('', ''))[1]
    if ' — ' in exemple:
        es,fr=exemple.split(' — ',1)
        base.append((fr.strip(),es.strip(),'fiche de conjugaison'))
    if not base:return []
    rng=random.SystemRandom()
    pool=[(fr,es) for fr,es,_ in base]
    # Phrases plus longues et variées en combinant deux énoncés complets.
    if len(base)>1:
        for a in base:
            for b in base:
                if a==b:continue
                fr1,es1,_=a;fr2,es2,_=b
                pool.append((fr1.rstrip(' .!?')+'. '+fr2,es1.rstrip(' .!?')+'. '+es2))
    pool=list(dict.fromkeys(pool))
    previous={tuple(x) for x in exclure}
    rng.shuffle(pool)
    # Priorité aux traductions erronées de ce thème, puis aux énoncés inédits.
    try:
        erreurs=m.rows('SELECT consigne,attendu FROM productions WHERE niveau=? AND valide=0 ORDER BY id DESC LIMIT 200',(niveau,))
        fautes={(r['consigne'],r['attendu']) for r in erreurs}
    except Exception:
        fautes=set()
    pool.sort(key=lambda x:(x in previous,x not in fautes))
    return pool[:n]

def qcm(niveau,lecon,n=30):
    """30 QCM variés tirés du vocabulaire, des exemples et de la conjugaison."""
    rng=random.SystemRandom()
    result=[]
    vocab=[(es,fr) for es,fr in lecon.get('vocabulaire',[]) if es and fr]
    source=_sources(lecon)
    # Deux sens de traduction, avec des distracteurs issus de la même leçon.
    for category,pairs in [('Vocabulaire',vocab),('Exemples et expressions',[(es,fr) for fr,es,_ in source])]:
        for es,fr in pairs:
            for direct in (True,False):
                bonne=es if direct else fr
                autres=list(dict.fromkeys((e if direct else f) for e,f in pairs if (e if direct else f)!=bonne))
                if len(autres)<3:continue
                opts=rng.sample(autres,3)+[bonne];rng.shuffle(opts)
                result.append({'enonce':f'{category} — Traduis : « {fr if direct else es} »',
                               'options':opts,'bonne':bonne,'explication':f'{es} — {fr}',
                               'competence':lecon['id'],'type':category})
    # Fiche de conjugaison au temps du planning.
    code,temps_nom=_temps(niveau)
    personnes=['yo','tú','él/ella','nosotros','vosotros','ellos/ellas']
    for verbe,donnees in VERBES.items():
        formes=conj.formes(verbe,code,donnees)
        if not formes or len(formes)!=6:continue
        for i,personne in enumerate(personnes):
            bonne=formes[i]
            autres=list(dict.fromkeys(f for j,f in enumerate(formes) if j!=i and f!=bonne))
            if len(autres)<3:
                # Ajouter des formes du même temps provenant d'autres verbes.
                for v,d in VERBES.items():
                    if v==verbe:continue
                    fs=conj.formes(v,code,d)
                    if fs and len(fs)==6 and fs[i]!=bonne:autres.append(fs[i])
                    if len(set(autres))>=3:break
            autres=list(dict.fromkeys(autres))
            if len(autres)<3:continue
            opts=rng.sample(autres,3)+[bonne];rng.shuffle(opts)
            result.append({'enonce':f'Fiche de conjugaison — {verbe} ({temps_nom}) : {personne} …',
                           'options':opts,'bonne':bonne,'explication':f'{personne} {bonne} — {temps_nom} de {verbe}',
                           'competence':f'conj_{code}','type':'Conjugaison'})
    rng.shuffle(result)
    # Diversifier les catégories et éviter de répéter les mêmes énoncés.
    groupes={c:[q for q in result if q['type']==c] for c in ('Vocabulaire','Exemples et expressions','Conjugaison')}
    for group in groupes.values():rng.shuffle(group)
    selected=[]
    while len(selected)<n and any(groupes.values()):
        for group in groupes.values():
            if group and len(selected)<n:selected.append(group.pop())
    for i,q in enumerate(selected):q['id']=f"v11_{lecon['id']}_{code}_{i}_{rng.randrange(10**9)}"
    return selected
