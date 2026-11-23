"""Moteur autonome de conjugaison espagnole (modèles réguliers et irréguliers vérifiés)."""
from __future__ import annotations

PERSONS = ['yo', 'tú', 'él / ella / usted', 'nosotros/as', 'vosotros/as', 'ellos / ellas / ustedes']
IMP_PERSONS = ['tú', 'usted', 'nosotros/as', 'vosotros/as', 'ustedes']
AUX = {
    'presente': ['he','has','ha','hemos','habéis','han'],
    'imperfecto': ['había','habías','había','habíamos','habíais','habían'],
    'preterito': ['hube','hubiste','hubo','hubimos','hubisteis','hubieron'],
    'futuro': ['habré','habrás','habrá','habremos','habréis','habrán'],
    'condicional': ['habría','habrías','habría','habríamos','habríais','habrían'],
    'subj_presente': ['haya','hayas','haya','hayamos','hayáis','hayan'],
    'subj_imperfecto': ['hubiera','hubieras','hubiera','hubiéramos','hubierais','hubieran'],
    'subj_imperfecto_se': ['hubiese','hubieses','hubiese','hubiésemos','hubieseis','hubiesen'],
    'subj_futuro': ['hubiere','hubieres','hubiere','hubiéremos','hubiereis','hubieren'],
}
# Matrices des formes simples irrégulières les plus courantes, dans l'ordre des 6 personnes.
IRREG = {
 'ser': {'presente':'soy eres es somos sois son','preterito':'fui fuiste fue fuimos fuisteis fueron','imperfecto':'era eras era éramos erais eran','subj_presente':'sea seas sea seamos seáis sean','imperativo_tu':'sé','gerundio':'siendo'},
 'estar': {'presente':'estoy estás está estamos estáis están','preterito':'estuve estuviste estuvo estuvimos estuvisteis estuvieron','subj_presente':'esté estés esté estemos estéis estén','imperativo_tu':'está'},
 'tener': {'presente':'tengo tienes tiene tenemos tenéis tienen','preterito':'tuve tuviste tuvo tuvimos tuvisteis tuvieron','subj_presente':'tenga tengas tenga tengamos tengáis tengan','future_stem':'tendr','imperativo_tu':'ten'},
 'ir': {'presente':'voy vas va vamos vais van','preterito':'fui fuiste fue fuimos fuisteis fueron','imperfecto':'iba ibas iba íbamos ibais iban','subj_presente':'vaya vayas vaya vayamos vayáis vayan','imperativo_tu':'ve','imperativo_vosotros':'id','gerundio':'yendo'},
 'hacer': {'presente':'hago haces hace hacemos hacéis hacen','preterito':'hice hiciste hizo hicimos hicisteis hicieron','subj_presente':'haga hagas haga hagamos hagáis hagan','future_stem':'har','imperativo_tu':'haz','participio':'hecho'},
 'poder': {'presente':'puedo puedes puede podemos podéis pueden','preterito':'pude pudiste pudo pudimos pudisteis pudieron','subj_presente':'pueda puedas pueda podamos podáis puedan','future_stem':'podr','imperativo_tu':None,'gerundio':'pudiendo'},
 'querer': {'presente':'quiero quieres quiere queremos queréis quieren','preterito':'quise quisiste quiso quisimos quisisteis quisieron','subj_presente':'quiera quieras quiera queramos queráis quieran','future_stem':'querr','imperativo_tu':None},
 'decir': {'presente':'digo dices dice decimos decís dicen','preterito':'dije dijiste dijo dijimos dijisteis dijeron','subj_presente':'diga digas diga digamos digáis digan','future_stem':'dir','imperativo_tu':'di','participio':'dicho','gerundio':'diciendo'},
 'venir': {'presente':'vengo vienes viene venimos venís vienen','preterito':'vine viniste vino vinimos vinisteis vinieron','subj_presente':'venga vengas venga vengamos vengáis vengan','future_stem':'vendr','imperativo_tu':'ven','gerundio':'viniendo'},
 'saber': {'presente':'sé sabes sabe sabemos sabéis saben','preterito':'supe supiste supo supimos supisteis supieron','subj_presente':'sepa sepas sepa sepamos sepáis sepan','future_stem':'sabr','imperativo_tu':None},
 'poner': {'presente':'pongo pones pone ponemos ponéis ponen','preterito':'puse pusiste puso pusimos pusisteis pusieron','subj_presente':'ponga pongas ponga pongamos pongáis pongan','future_stem':'pondr','imperativo_tu':'pon','participio':'puesto'},
 'salir': {'presente':'salgo sales sale salimos salís salen','subj_presente':'salga salgas salga salgamos salgáis salgan','future_stem':'saldr','imperativo_tu':'sal'},
 'dormir': {'presente':'duermo duermes duerme dormimos dormís duermen','preterito':'dormí dormiste durmió dormimos dormisteis durmieron','subj_presente':'duerma duermas duerma durmamos durmáis duerman','imperativo_tu':'duerme','gerundio':'durmiendo'},
 'pedir': {'presente':'pido pides pide pedimos pedís piden','preterito':'pedí pediste pidió pedimos pedisteis pidieron','subj_presente':'pida pidas pida pidamos pidáis pidan','imperativo_tu':'pide','gerundio':'pidiendo'},
 'haber': {'presente':'he has ha hemos habéis han','preterito':'hube hubiste hubo hubimos hubisteis hubieron','imperfecto':'había habías había habíamos habíais habían','subj_presente':'haya hayas haya hayamos hayáis hayan','future_stem':'habr','imperativo_tu':None,'participio':'habido'},
}
VERBS = ['hablar','comer','vivir','ser','estar','tener','ir','hacer','poder','querer','decir','venir','saber','poner','salir','dormir','pedir','haber']
TENSES = {
 'presente': ('Indicatif · présent','A1–A2','Action actuelle ou habituelle : Hoy estudio.'),
 'imperfecto': ('Indicatif · imparfait','A2–B1','Description ou habitude passée : Antes jugaba.'),
 'preterito': ('Indicatif · passé simple (indefinido)','A2–B1','Événement passé et terminé : Ayer estudié.'),
 'perfecto': ('Indicatif · passé composé (perfecto compuesto)','A2–B1','Passé relié au présent dans de nombreux usages : Hoy he leído.'),
 'pluscuamperfecto': ('Indicatif · plus-que-parfait','B1','Action antérieure à une autre action passée : Ya había salido.'),
 'futuro': ('Indicatif · futur simple','A2–B1','Futur ou supposition : Mañana vendrá.'),
 'futuro_perfecto': ('Indicatif · futur antérieur','B2–C1','Action accomplie avant un repère futur : Ya habré terminado.'),
 'condicional': ('Indicatif · conditionnel simple','B1','Politesse ou hypothèse : Me gustaría viajar.'),
 'condicional_perfecto': ('Indicatif · conditionnel passé','B2','Hypothèse non réalisée : Habría venido.'),
 'preterito_anterior': ('Indicatif · passé antérieur (littéraire)','C2','Temps rare, surtout dans des textes anciens : Apenas hube llegado...'),
 'subj_presente': ('Subjonctif · présent','B1','Souhait, doute, émotion : Quiero que vengas.'),
 'subj_imperfecto': ('Subjonctif · imparfait en -ra','B2','Hypothèse ou concordance au passé : Si tuviera tiempo...'),
 'subj_imperfecto_se': ('Subjonctif · imparfait en -se','B2–C1','Autre forme de l’imparfait : Si tuviese tiempo...'),
 'subj_perfecto': ('Subjonctif · passé composé','B2','Doute ou jugement sur un fait accompli : Dudo que haya venido.'),
 'subj_pluscuamperfecto': ('Subjonctif · plus-que-parfait en -ra','B2–C1','Irréel passé : Si hubiera sabido...'),
 'subj_pluscuamperfecto_se': ('Subjonctif · plus-que-parfait en -se','C1','Variante : Si hubiese sabido...'),
 'subj_futuro': ('Subjonctif · futur (historique)','C2 · rare','Rencontré surtout en droit et en textes anciens : Cuando fuere...'),
 'subj_futuro_perfecto': ('Subjonctif · futur antérieur (historique)','C2 · rare','Construction littéraire / juridique : Cuando hubiere llegado...'),
 'imperativo_afirmativo': ('Impératif · affirmatif','A2–B1','Instruction : ¡Habla! ¡Venga usted!'),
 'imperativo_negativo': ('Impératif · négatif','B1','Défense : ¡No hables! ¡No vayáis!'),
}

DEF_ACCENT = str.maketrans('aeiou','áéíóú')

def _accent_last_vowel(stem):
    for i in range(len(stem)-1,-1,-1):
        if stem[i] in 'aeiou':
            return stem[:i]+stem[i].translate(DEF_ACCENT)+stem[i+1:]
    return stem

def _regular(verb,tense):
    stem,group=verb[:-2],verb[-2:]
    if tense=='presente':
        endings=['o','as','a','amos','áis','an'] if group=='ar' else (['o','es','e','emos','éis','en'] if group=='er' else ['o','es','e','imos','ís','en'])
    elif tense=='imperfecto':
        endings=['aba','abas','aba','ábamos','abais','aban'] if group=='ar' else ['ía','ías','ía','íamos','íais','ían']
    elif tense=='preterito':
        endings=['é','aste','ó','amos','asteis','aron'] if group=='ar' else ['í','iste','ió','imos','isteis','ieron']
    elif tense=='subj_presente':
        endings=['e','es','e','emos','éis','en'] if group=='ar' else ['a','as','a','amos','áis','an']
    elif tense in ('futuro','condicional'):
        stem=IRREG.get(verb,{}).get('future_stem',verb)
        endings=['é','ás','á','emos','éis','án'] if tense=='futuro' else ['ía','ías','ía','íamos','íais','ían']
    else: raise ValueError(tense)
    return [stem+end for end in endings]

def participle(verb):
    return IRREG.get(verb,{}).get('participio',verb[:-2]+('ado' if verb.endswith('ar') else 'ido'))

def gerund(verb):
    return IRREG.get(verb,{}).get('gerundio',verb[:-2]+('ando' if verb.endswith('ar') else 'iendo'))

def _preterite_stem(verb):
    # Hablaron -> habla-, comieron -> comie-, fueron -> fue-.
    return conjugate(verb,'preterito')[-1][:-3]

def conjugate(verb, tense):
    if verb not in VERBS or tense not in TENSES: raise ValueError('Verbe ou temps inconnu')
    data=IRREG.get(verb,{})
    if tense in ('presente','preterito','imperfecto','subj_presente','futuro','condicional'):
        if tense in data and isinstance(data[tense],str):return data[tense].split()
        return _regular(verb,tense)
    if tense in ('subj_imperfecto','subj_imperfecto_se','subj_futuro'):
        stem=_preterite_stem(verb); accent=_accent_last_vowel(stem)
        endings={
            'subj_imperfecto':['ra','ras','ra','ramos','rais','ran'],
            'subj_imperfecto_se':['se','ses','se','semos','seis','sen'],
            'subj_futuro':['re','res','re','remos','reis','ren'],
        }[tense]
        return [(accent if i==3 else stem)+ending for i,ending in enumerate(endings)]
    compound={
        'perfecto':'presente','pluscuamperfecto':'imperfecto',
        'preterito_anterior':'preterito','futuro_perfecto':'futuro',
        'condicional_perfecto':'condicional','subj_perfecto':'subj_presente',
        'subj_pluscuamperfecto':'subj_imperfecto',
        'subj_pluscuamperfecto_se':'subj_imperfecto_se',
        'subj_futuro_perfecto':'subj_futuro',
    }
    if tense in compound:
        return [form+' '+participle(verb) for form in AUX[compound[tense]]]
    subj=conjugate(verb,'subj_presente')
    if tense=='imperativo_negativo':return ['no '+subj[i] for i in (1,2,3,4,5)]
    if tense=='imperativo_afirmativo':
        tu=data.get('imperativo_tu',conjugate(verb,'presente')[2]); vos=data.get('imperativo_vosotros',verb[:-1]+'d')
        return [tu or '— (inusité)',subj[2],subj[3],vos,subj[5]]
    raise ValueError(tense)
