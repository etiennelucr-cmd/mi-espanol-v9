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

def _net_pair(fr, es):
    return (_net(fr).strip(" .!?¿¡"), _net(es).strip(" .!?¿¡"))

def _phrases_sources(lecon, niveau):
    """Uniquement des traductions attestées dans le contenu pédagogique."""
    base = _sources(lecon)
    try:
        code, _ = _temps(niveau)
        exemple = conj.EXPLICATIONS.get(code, ('', ''))[1]
        if ' — ' in exemple:
            es, fr = exemple.split(' — ', 1)
            if es.strip() and fr.strip():
                base.append((fr.strip(), es.strip(), 'conjugaison'))
    except (KeyError, IndexError, TypeError):
        pass
    seen = set()
    distinct = []
    for fr, es, kind in base:
        key = _net_pair(fr, es)
        if key not in seen:
            seen.add(key)
            distinct.append((fr.strip(), es.strip(), kind))
    return distinct

def phrases(niveau, lecon, n=20, exclure=(), historique=()):
    """20 énoncés distincts et équilibrés, issus de la leçon et du temps étudié.

    Les énoncés à deux phrases préservent exactement les traductions attestées.
    Les paires inversées ne comptent pas comme de nouveaux exercices.
    """
    sources = _phrases_sources(lecon, niveau)
    if not sources:
        return []
    rng = random.SystemRandom()
    rng.shuffle(sources)
    pool = []
    # Chaque exemple peut être interrogé individuellement.
    for i, (fr, es, _) in enumerate(sources):
        pool.append((fr, es, (i,)))
    # Combinaisons de DEUX exemples différents : pas de répétition interne.
    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            fr1, es1, _ = sources[i]
            fr2, es2, _ = sources[j]
            pool.append((fr1.rstrip(' .!?') + '. ' + fr2,
                         es1.rstrip(' .!?') + '. ' + es2, (i, j)))
    rng.shuffle(pool)
    previous = {_net_pair(fr, es) for fr, es in list(exclure) + list(historique)}
    counts = {i: 0 for i in range(len(sources))}
    selected = []
    used = set()
    # On privilégie les énoncés nouveaux et une couverture équilibrée des exemples.
    for _ in range(min(n, len(pool))):
        candidates = [x for x in pool if _net_pair(x[0], x[1]) not in used]
        if not candidates:
            break
        best = min(
            candidates,
            key=lambda x: (
                _net_pair(x[0], x[1]) in previous,
                max(counts[i] for i in x[2]),
                sum(counts[i] for i in x[2]),
                rng.random(),
            ),
        )
        selected.append((best[0], best[1]))
        used.add(_net_pair(best[0], best[1]))
        for i in best[2]:
            counts[i] += 1
    return selected

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
