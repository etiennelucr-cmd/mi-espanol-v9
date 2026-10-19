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

# Variations bilingues prudentes : une seule proposition par exercice.
# Les substitutions de noms propres et les compléments contextuels
# conservent le sens et le temps du texte pédagogique de départ.
_NOMS = [
    (('Ana', 'Ana'), ('Lucía', 'Lucía')),
    (('Pablo', 'Pablo'), ('Carlos', 'Carlos')),
    (('María', 'María'), ('Elena', 'Elena')),
    (('Madrid', 'Madrid'), ('Sevilla', 'Séville')),
    (('París', 'Paris'), ('Lyon', 'Lyon')),
    (('Barcelona', 'Barcelone'), ('Valencia', 'Valence')),
]
_CONTEXTES = [
    ('Hoy', "Aujourd’hui"),
    ('Normalmente', "D’habitude"),
    ('En general', "En général"),
    ('A veces', "Parfois"),
    ('Esta semana', "Cette semaine"),
]

def _variantes(fr, es):
    """Retourne des paires de traductions autonomes, sans collage de phrases."""
    fr, es = fr.strip(), es.strip()
    yield (fr, es)
    # Variation d'entités nommées attestées dans les deux langues.
    for (es_old, fr_old), (es_new, fr_new) in _NOMS:
        if re.search(r'(?<!\\w)' + re.escape(es_old) + r'(?!\\w)', es) and re.search(r'(?<!\\w)' + re.escape(fr_old) + r'(?!\\w)', fr):
            yield (re.sub(r'(?<!\\w)' + re.escape(fr_old) + r'(?!\\w)', fr_new, fr),
                   re.sub(r'(?<!\\w)' + re.escape(es_old) + r'(?!\\w)', es_new, es))
    # Les adverbes s'ajoutent seulement aux affirmations simples au présent.
    # Ne pas les ajouter aux questions, ordres, souhaits ou phrases au passé/futur.
    if (es.endswith('.') and fr.endswith('.') and not any(c in es+fr for c in '¿?¡!')
            and not re.search(r'\\b(ayer|mañana|hier|demain|fui|fue|estuve|hablé|seré|fut|étais|étaient)\\b',
                              es+' '+fr, flags=re.I)):
        for es_adv, fr_adv in _CONTEXTES:
            # Une phrase déjà introduite par un marqueur temporel ne reçoit pas
            # de second marqueur.
            if re.match(r'(?i)^(hoy|ayer|mañana|normalmente|a veces|esta semana|en general|aujourd|hier|demain|parfois)',es+' '+fr):
                break
            yield (fr_adv + ', ' + fr[0].lower() + fr[1:],
                   es_adv + ', ' + es[0].lower() + es[1:])

def phrases(niveau, lecon, n=20, exclure=(), historique=()):
    """Sélectionne au plus n traductions différentes, sans fusion d'exemples.

    Priorité à la couverture du thème et aux formulations inédites.
    Ne fabrique pas de fausses traductions pour atteindre artificiellement n.
    """
    rng=random.SystemRandom()
    sources=_phrases_sources(lecon,niveau)
    rng.shuffle(sources)
    pools=[]
    used=set()
    for idx,(fr,es,kind) in enumerate(sources):
        group=[]
        for fr_v,es_v in _variantes(fr,es):
            key=_net_pair(fr_v,es_v)
            if key not in used:
                used.add(key)
                group.append((fr_v,es_v))
        rng.shuffle(group)
        if group:pools.append(group)
    # Tour de rôle : couvrir tous les exemples avant de répéter une structure.
    previous={_net_pair(fr,es) for fr,es in list(exclure)+list(historique)}
    for group in pools:
        group.sort(key=lambda p:_net_pair(*p) in previous)
    result=[]
    while len(result)<n and any(pools):
        rng.shuffle(pools)
        for group in pools:
            if group and len(result)<n:
                result.append(group.pop(0))
        pools=[g for g in pools if g]
    return result

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
