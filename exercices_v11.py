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

# Phrases bilingues rédigées pour pratiquer le temps du planning.
# Chaque entrée est (espagnol, français), et non une forme isolée.
PHRASES_TEMPS = {
 'presente': [
  ('Yo como en casa todos los días.', 'Je mange à la maison tous les jours.'),
  ('Nosotros estudiamos español por la tarde.', "Nous étudions l’espagnol l’après-midi."),
  ('Ella vive cerca de la escuela.', "Elle habite près de l’école."),
  ('¿Tú trabajas los lunes?', 'Est-ce que tu travailles le lundi ?'),
  ('Mis amigos hablan español.', 'Mes amis parlent espagnol.'),
  ('Yo escribo una carta a mi hermana.', 'J’écris une lettre à ma sœur.')],
 'perfecto': [
  ('Yo he comido con mi familia.', "J’ai mangé avec ma famille."),
  ('Esta semana hemos estudiado mucho.', 'Cette semaine, nous avons beaucoup étudié.'),
  ('Ella ha visitado a sus abuelos.', 'Elle a rendu visite à ses grands-parents.'),
  ('¿Has terminado tus deberes?', 'As-tu terminé tes devoirs ?'),
  ('Mis amigos han comprado un libro.', 'Mes amis ont acheté un livre.'),
  ('Hoy he hablado con mi profesor.', "Aujourd’hui, j’ai parlé avec mon professeur.")],
 'indefinido': [
  ('Ayer compré un libro.', "Hier, j’ai acheté un livre."),
  ('El sábado visitamos el museo.', 'Samedi, nous avons visité le musée.'),
  ('Ella habló con su hermano anoche.', 'Elle a parlé avec son frère hier soir.'),
  ('¿Terminaste el trabajo ayer?', 'As-tu terminé le travail hier ?'),
  ('Mis amigos llegaron el lunes.', 'Mes amis sont arrivés lundi.'),
  ('El año pasado viví en Madrid.', "L’année dernière, j’ai habité à Madrid.")],
 'imperfecto': [
  ('Cuando era niño, jugaba en el parque.', 'Quand j’étais enfant, je jouais au parc.'),
  ('Antes vivíamos cerca del mar.', 'Avant, nous habitions près de la mer.'),
  ('Ella leía todas las noches.', 'Elle lisait tous les soirs.'),
  ('¿Estudiabas español en la escuela?', "Étudiais-tu l’espagnol à l’école ?"),
  ('Los domingos comíamos juntos.', 'Le dimanche, nous mangions ensemble.'),
  ('Mi abuelo trabajaba en una tienda.', 'Mon grand-père travaillait dans un magasin.')],
 'futuro': [
  ('Mañana estudiaré español.', "Demain, j’étudierai l’espagnol."),
  ('Nosotros visitaremos el museo.', 'Nous visiterons le musée.'),
  ('Ella comprará una casa.', 'Elle achètera une maison.'),
  ('¿Trabajarás el sábado?', 'Travailleras-tu samedi ?'),
  ('Mis amigos llegarán mañana.', 'Mes amis arriveront demain.'),
  ('Escribiré una carta esta noche.', "J’écrirai une lettre ce soir.")],
 'condicional': [
  ('Yo compraría una casa más grande.', "J’achèterais une maison plus grande."),
  ('Nosotros viajaríamos en tren.', 'Nous voyagerions en train.'),
  ('Ella estudiaría más con tiempo.', 'Elle étudierait davantage si elle avait le temps.'),
  ('¿Hablarías con el profesor?', 'Parlerais-tu avec le professeur ?'),
  ('Mis amigos vivirían aquí.', 'Mes amis habiteraient ici.'),
  ('Yo comería contigo.', 'Je mangerais avec toi.')],
 'subj_pres': [
  ('Quiero que estudies español.', "Je veux que tu étudies l’espagnol."),
  ('Es importante que lleguemos temprano.', 'Il est important que nous arrivions tôt.'),
  ('Espero que ella coma con nosotros.', "J’espère qu’elle mangera avec nous."),
  ('Dudo que ellos vivan aquí.', "Je doute qu’ils habitent ici."),
  ('Prefiero que hables despacio.', 'Je préfère que tu parles lentement.'),
  ('Es necesario que trabajemos juntos.', 'Il faut que nous travaillions ensemble.')],
 'imperativo': [
  ('¡Habla más despacio!', 'Parle plus lentement !'),
  ('¡Estudia esta lección!', 'Étudie cette leçon !'),
  ('¡Comed con nosotros!', 'Mangez avec nous !'),
  ('¡Escriba su nombre aquí!', 'Écrivez votre nom ici !'),
  ('¡Escuchad al profesor!', 'Écoutez le professeur !'),
  ('¡Trabajemos juntos!', 'Travaillons ensemble !')],
 'pluscuamperfecto': [
  ('Yo ya había comido.', "J’avais déjà mangé."),
  ('Nosotros habíamos terminado antes.', 'Nous avions terminé auparavant.'),
  ('Ella había estudiado la lección.', 'Elle avait étudié la leçon.'),
  ('¿Habías hablado con Ana?', 'Avais-tu parlé avec Ana ?'),
  ('Ellos habían visitado la ciudad.', 'Ils avaient visité la ville.'),
  ('Yo había trabajado allí.', "J’avais travaillé là-bas.")],
 'subj_imp': [
  ('Quería que estudiaras español.', "Je voulais que tu étudies l’espagnol."),
  ('Era importante que llegáramos pronto.', 'Il était important que nous arrivions vite.'),
  ('Esperaba que ella comiera con nosotros.', "J’espérais qu’elle mange avec nous."),
  ('Dudaba que ellos vivieran aquí.', "Je doutais qu’ils habitent ici."),
  ('Prefería que hablaras despacio.', 'Je préférais que tu parles lentement.'),
  ('Era necesario que trabajáramos juntos.', 'Il fallait que nous travaillions ensemble.')],
 'futuro_perfecto': [
  ('Mañana ya habré terminado.', "Demain, j’aurai déjà terminé."),
  ('Para entonces habremos llegado.', "D’ici là, nous serons arrivés."),
  ('Ella habrá estudiado todo.', 'Elle aura tout étudié.'),
  ('¿Habrás comido antes de salir?', 'Auras-tu mangé avant de partir ?'),
  ('Ellos habrán visitado el museo.', 'Ils auront visité le musée.'),
  ('Yo habré escrito la carta.', "J’aurai écrit la lettre.")],
 'condicional_compuesto': [
  ('Yo habría estudiado más.', "J’aurais étudié davantage."),
  ('Nosotros habríamos llegado antes.', 'Nous serions arrivés plus tôt.'),
  ('Ella habría comprado el libro.', 'Elle aurait acheté le livre.'),
  ('¿Habrías hablado con él?', 'Aurais-tu parlé avec lui ?'),
  ('Ellos habrían visitado el museo.', 'Ils auraient visité le musée.'),
  ('Yo habría terminado a tiempo.', "J’aurais terminé à temps.")],
 'subj_perfecto': [
  ('Espero que hayas comido.', "J’espère que tu as mangé."),
  ('Me alegra que hayamos llegado.', 'Je suis heureux que nous soyons arrivés.'),
  ('Dudo que ella haya terminado.', "Je doute qu’elle ait terminé."),
  ('Es posible que hayan estudiado.', 'Il est possible qu’ils aient étudié.'),
  ('Me sorprende que hayas escrito.', 'Je suis surpris que tu aies écrit.'),
  ('Espero que él haya trabajado.', "J’espère qu’il a travaillé.")],
 'subj_pluscuam': [
  ('Ojalá hubieras estudiado más.', 'Si seulement tu avais étudié davantage.'),
  ('Si hubiéramos salido antes, habríamos llegado.', 'Si nous étions partis plus tôt, nous serions arrivés.'),
  ('Quería que ella hubiera terminado.', "Je voulais qu’elle ait terminé."),
  ('Dudaba que ellos hubieran llegado.', "Je doutais qu’ils soient arrivés."),
  ('Me habría gustado que hubieras venido.', "J’aurais aimé que tu sois venu."),
  ('Era imposible que hubieran sabido eso.', "Il était impossible qu’ils aient su cela.")],
 'preterito_anterior': [
  ('Apenas hube terminado, salí.', 'À peine eus-je terminé que je sortis.'),
  ('Cuando hubo comido, se marchó.', "Lorsqu’il eut mangé, il partit."),
  ('En cuanto hubimos llegado, empezó la reunión.', 'Dès que nous fûmes arrivés, la réunion commença.'),
  ('Apenas hubo hablado, calló.', "À peine eut-il parlé qu’il se tut."),
  ('Cuando hubieron terminado, salieron.', "Lorsqu’ils eurent terminé, ils sortirent."),
  ('Tan pronto como hube leído la carta, respondí.', "Dès que j’eus lu la lettre, je répondis.")],
 'futuro_subj': [
  ('Quien llegare tarde deberá esperar.', 'Quiconque arrivera en retard devra attendre.'),
  ('Si alguien incumpliere la norma, será sancionado.', 'Si quelqu’un enfreint la règle, il sera sanctionné.'),
  ('Donde fueres, haz lo que vieres.', 'À Rome, fais comme les Romains.'),
  ('Quien tuviere dudas podrá preguntar.', 'Quiconque aura des doutes pourra poser des questions.'),
  ('Si el solicitante presentare pruebas, serán examinadas.', 'Si le demandeur présente des preuves, elles seront examinées.'),
  ('Quien así lo deseare podrá participar.', 'Quiconque le souhaitera pourra participer.')],
 'futuro_subj_perfecto': [
  ('Quien hubiere terminado podrá salir.', 'Quiconque aura terminé pourra sortir.'),
  ('Si alguien hubiere incumplido la norma, será sancionado.', 'Si quelqu’un a enfreint la règle, il sera sanctionné.'),
  ('Quien hubiere presentado la solicitud recibirá respuesta.', 'Quiconque aura déposé la demande recevra une réponse.'),
  ('Si el juez hubiere dictado sentencia, se notificará.', 'Si le juge a rendu son jugement, celui-ci sera notifié.'),
  ('Quien hubiere pagado quedará inscrito.', 'Quiconque aura payé sera inscrit.'),
  ('Si hubieren llegado los documentos, los revisaremos.', 'Si les documents sont arrivés, nous les examinerons.')],
}

def _phrases_sources(lecon, niveau):
    """Uniquement des traductions attestées dans le contenu pédagogique."""
    base = _sources(lecon)
    try:
        code, _ = _temps(niveau)
        base.extend((fr, es, 'temps du planning') for es, fr in PHRASES_TEMPS.get(code, []))
    except (KeyError, IndexError, TypeError):
        pass
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
    """Paires authentiques, sans collage ni variation artificielle.

    La direction est choisie à l'affichage : une phrase sur deux sera
    espagnol vers français. Si la leçon contient moins de 20 paires,
    des paires seront revues dans l'autre sens.
    """
    rng=random.SystemRandom()
    sources=_phrases_sources(lecon,niveau)
    previous={_net_pair(fr,es) for fr,es in list(exclure)+list(historique)}
    rng.shuffle(sources)
    sources.sort(key=lambda x:(_net_pair(x[0],x[1]) in previous, x[2]!='temps du planning'))
    pairs=[(fr,es) for fr,es,_ in sources]
    if not pairs:return []
    # Ne jamais répéter une paire dans la même direction.
    if len(pairs)>=n:return pairs[:n]
    # Le lot a deux directions : 10 de chaque pour un lot de 20.
    # Chaque paire peut apparaître une fois dans chaque direction.
    k=min(n,len(pairs)*2)
    return (pairs+list(reversed(pairs)))[:k]

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
