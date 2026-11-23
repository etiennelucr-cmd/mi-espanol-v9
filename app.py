"""Mi Español V6 — interface Streamlit ludique sur les modules de cours V5.
Nécessite programme.py, programmes_officiels.py, grammaire.py,
conjugaison.py et progression.py de la version V5 (conservés sans modification).
"""
from __future__ import annotations
import base64
import html
import json
import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from programme import CLASSES, EQUIVALENCES, SCOLAIRE, CECRL, SOURCES
from programmes_officiels import PROGRAMMES, LLCER, LLCER_EXERCICES
from grammaire import GRAMMAIRE
from conjugaison import PERSONS, IMP_PERSONS, VERBS, TENSES, conjugate, participle, gerund
from progression import available_indices, unlocked_groups, current_school_grade, score_passes

st.set_page_config(page_title='Mi Español · Mon école des langues',page_icon='🇪🇸',layout='wide',initial_sidebar_state='collapsed')
HERE=Path(__file__).resolve().parent
SAVE=HERE/'ma_progression_locale.json'
LOCAL_SAVE=os.environ.get('MI_ESPANOL_LOCAL_SAVE','0')=='1'

# La V6 ne modifie pas l'ordre des cours : les clés V5 restent compatibles.
TENSE_ORDER=['presente','imperfecto','preterito','perfecto','futuro','condicional',
 'imperativo_afirmativo','imperativo_negativo','pluscuamperfecto','subj_presente',
 'subj_imperfecto','subj_perfecto','condicional_perfecto','subj_pluscuamperfecto',
 'futuro_perfecto','subj_imperfecto_se','subj_pluscuamperfecto_se',
 'preterito_anterior','subj_futuro','subj_futuro_perfecto']
assert set(TENSE_ORDER)==set(TENSES)

MISSIONS=[
 ('Premiers contacts','Saluer et se présenter',('Bonjour','Guten Tag','Buongiorno'),('Merci','Danke','Grazie')),
 ('Nombres et prix','Comprendre un prix',('Combien ça coûte ?','Wie viel kostet das?','Quanto costa?'),('Dix','Zehn','Dieci')),
 ('Au restaurant','Commander à manger',('Je voudrais de l’eau','Ich hätte gern Wasser','Vorrei dell’acqua'),('L’addition, s’il vous plaît','Die Rechnung, bitte','Il conto, per favore')),
 ('À l’hôtel','Arriver à l’hôtel',('J’ai une réservation','Ich habe eine Reservierung','Ho una prenotazione'),('Une chambre','Ein Zimmer','Una camera')),
 ('Transports','Acheter un billet',('Un billet, s’il vous plaît','Eine Fahrkarte, bitte','Un biglietto, per favore'),('La gare','Der Bahnhof','La stazione')),
 ('Directions','Trouver son chemin',('Où est la gare ?','Wo ist der Bahnhof?','Dov’è la stazione?'),('À gauche','Links','A sinistra')),
 ('Achats','Faire des courses',('Je cherche…','Ich suche…','Cerco…'),('Trop cher','Zu teuer','Troppo caro')),
 ('Météo et loisirs','Parler simplement',('Il fait beau','Das Wetter ist schön','C’è bel tempo'),('Aujourd’hui','Heute','Oggi')),
 ('Santé et urgences','Demander de l’aide',('J’ai besoin d’aide','Ich brauche Hilfe','Ho bisogno di aiuto'),('Un médecin','Ein Arzt','Un medico')),
 ('Conversation','Échanger avec les habitants',('Je ne comprends pas','Ich verstehe nicht','Non capisco'),('Parlez plus lentement','Sprechen Sie langsamer','Parli più lentamente')),
]


def new_profile():
    return {'version':6,'name':'Élève','grade':0,'school':{},'school_exams':{},
            'cefr':{},'cefr_exams':{},'grammar':{},'grammar_exams':{},
            'verbs':{},'tenses':{},'conjugation':{},'german':{},'italian':{},
            'llcer':{},'notes':{},'stars':0,'legacy_spanish':{}}


def normalize(src):
    """Toujours normaliser, y compris un profil déjà dans session_state !"""
    default=new_profile()
    if isinstance(src,dict):
        for k,initial in list(default.items()):
            candidate=src.get(k)
            if type(candidate)==type(initial):
                default[k]=candidate
        if not default['legacy_spanish'] and isinstance(src.get('spanish'),dict):
            default['legacy_spanish']=src['spanish']
    try:requested=int(default['grade'])
    except (TypeError,ValueError):requested=0
    default['grade']=max(0,min(requested,current_school_grade(default['school_exams'],len(CLASSES)-1)))
    try:default['stars']=max(0,int(default['stars']))
    except (TypeError,ValueError):default['stars']=0
    default['version']=6
    return default


def load_profile():
    if LOCAL_SAVE:
        try:return normalize(json.loads(SAVE.read_text(encoding='utf-8')))
        except (ValueError,OSError,UnicodeError,TypeError):pass
    return new_profile()

if 'profile' not in st.session_state:
    st.session_state.profile=load_profile()
st.session_state.profile=normalize(st.session_state.profile)
p=st.session_state.profile


def persist():
    if LOCAL_SAVE:
        try:SAVE.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
        except OSError:st.warning('Impossible de sauvegarder automatiquement en local. Exporte ton profil JSON.')


def award(section,key,points=5):
    if p[section].get(key) is True:return False
    p[section][key]=True
    p['stars']+=points
    persist()
    return True


def done_count(section,keys):
    return sum(p[section].get(k) is True for k in keys)


def school_key(grade,i):return f'{grade}:{i}'
def cefr_key(level,i):return f'{level}:{i}'
def grammar_key(level,i):return f'{level}:{i}'
def s_keys(grade):return [school_key(grade,i) for i in range(len(SCOLAIRE[CLASSES[grade]]))]
def c_keys(level):return [cefr_key(level,i) for i in range(len(CECRL[level]))]
def g_keys(level):return [grammar_key(level,i) for i in range(len(GRAMMAIRE[level]))]
def permitted(section,keys):return available_indices(p[section],keys)


def b64_asset(name):
    file=HERE/'assets'/name
    return base64.b64encode(file.read_bytes()).decode('ascii') if file.exists() else ''

CSS=r'''<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap');
:root{--violet:#693694;--mauve:#8653b0;--lav:#f1e5fb;--ink:#302044;--peach:#ffebdf;--pink:#fbe9f2;--green:#ebf6df;--blue:#e5f3ff;--cream:#fff8ec}
html,body,[class*="css"],.stApp{font-family:'Nunito','Segoe UI',sans-serif!important}
.stApp{background:linear-gradient(135deg,#fffaf4 0%,#fff3ed 45%,#fbf6ff 100%);color:var(--ink)}
.block-container{max-width:1550px;padding:1.05rem 1.25rem 3rem!important}
[data-testid="stHeader"]{background:transparent}
[data-testid="stToolbar"]{right:1rem}
.stMarkdown p{line-height:1.54}
h1,h2,h3,h4{color:#513067!important;letter-spacing:-.02em}
h2{font-size:1.37rem!important}h3{font-size:1.18rem!important}
.hero-school{display:flex;justify-content:space-between;align-items:stretch;gap:14px;min-height:193px;padding:0 0 0 29px;overflow:hidden;border-radius:27px;background:linear-gradient(112deg,#743d9b 2%,#bb5f9d 47%,#ed9a74 100%);box-shadow:0 15px 35px #66326920}
.hero-copy{padding:24px 0 22px;color:#fff;flex:1;min-width:0;position:relative;z-index:2}
.hero-copy h1{color:#fff!important;font-size:clamp(1.7rem,2.5vw,2.55rem);font-weight:900;margin:0 0 4px;line-height:1.15}
.hero-copy .subtitle{font-weight:800;font-size:1.09rem}.hero-copy .tags{font-size:.88rem;margin-top:22px;display:flex;gap:16px;flex-wrap:wrap;color:white}
.hero-art{width:min(37%,530px);min-width:320px;object-fit:cover;object-position:center;clip-path:ellipse(87% 94% at 80% 45%)}
.lang-caption{margin:13px 0 4px;font-weight:900;color:#47215e;font-size:.95rem}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:12px 0 16px}
.kpi{min-height:117px;display:flex;align-items:center;gap:13px;border:1px solid #fff;box-shadow:0 4px 12px #734b7820;padding:16px 19px;border-radius:20px;overflow:hidden}
.kpi.rose{background:linear-gradient(132deg,#fff,#ffece5)}.kpi.blue{background:linear-gradient(132deg,#fff,#e1eeff)}.kpi.mint{background:linear-gradient(132deg,#fff,#def6ee)}.kpi.yellow{background:linear-gradient(132deg,#fff,#fff0cf)}
.kpi .emoji{font-size:3.2rem;line-height:1;filter:drop-shadow(0 3px 2px #8b669544)}.kpi .label{font-weight:800;color:#593660;font-size:.93rem}.kpi .big{font-size:2.35rem;font-weight:900;color:#2f1742;line-height:1.1;white-space:nowrap}
.title-row{display:flex;align-items:center;gap:9px;padding:9px 12px;color:#502670;font-size:1.19rem;font-weight:900}
.sofia-art{display:block;width:100%;max-height:244px;object-fit:cover;object-position:center;border-radius:18px 18px 12px 12px}
.teacher-box{background:linear-gradient(145deg,#fff,#fcecf5);border-radius:20px;padding:13px 13px 17px;box-shadow:0 8px 25px #54365a15}
.teacher-box .name{font-weight:900;font-size:1.42rem;color:#632b7e;padding-top:8px}.teacher-box .desc{font-size:.91rem;line-height:1.5;color:#5a4260}
.soft-card{padding:14px 17px;border-radius:17px;background:linear-gradient(125deg,#fff3f8,#f3eaff);margin-top:13px}
.soft-card strong{color:#62267b}.soft-card small{font-size:.85rem;color:#5a5262}
.lesson-header{border-radius:19px;padding:17px 21px;background:linear-gradient(115deg,#fff 55%,#ffebdb 100%);border:1px solid #f0e0ec;box-shadow:0 5px 13px #8a619417;margin:7px 0 16px}
.lesson-header .breadcrumb{font-size:.84rem;color:#7b6387;font-weight:700}.lesson-header .heading{font-weight:900;color:#562377;font-size:1.8rem;line-height:1.2;margin:8px 0}.lesson-header .chip{display:inline-block;background:#f1e1ff;border-radius:999px;padding:4px 10px;font-weight:800;color:#70429a;font-size:.79rem}
.lesson-panel{padding:16px 19px;border-radius:18px;margin:8px 0;min-height:133px;border:1px solid #ffffff90}
.lesson-panel .head{font-weight:900;font-size:1.09rem;margin-bottom:9px}
.lesson-panel.rule{background:linear-gradient(116deg,#ffe6ee,#fff1ea)}.lesson-panel.example{background:linear-gradient(116deg,#def1ff,#f0f8ff)}.lesson-panel.story{background:linear-gradient(110deg,#eaf7df,#f4fbea);min-height:105px}
.lesson-panel.story p{font-size:1.08rem;color:#385f4c;font-weight:700}.lesson-panel p{margin:0;color:#422d49;font-size:.96rem}
.mini-actions{display:flex;gap:10px;margin-top:11px;flex-wrap:wrap}
.mini-action{flex:1;min-width:140px;padding:13px 15px;border-radius:17px;background:linear-gradient(145deg,#f4e5ff,#fcf1ff);font-weight:800;color:#69438b;font-size:.86rem}
.mini-action.blue{background:linear-gradient(145deg,#dbf0ff,#eef7ff);color:#2865a3}.mini-action.gold{background:linear-gradient(145deg,#fff0cc,#fff8ec);color:#805317}
.progress-note{margin:8px 0;background:#f0e5ff;border-radius:9px;height:10px;overflow:hidden}.progress-note span{display:block;height:100%;background:linear-gradient(90deg,#a56ae2,#6946b4);border-radius:9px}
.section-note{background:#fffbff;border-left:4px solid #af7fde;border-radius:11px;padding:11px 14px;color:#5d4664;margin:11px 0;font-size:.92rem}
div[data-testid="stVerticalBlockBorderWrapper"]{border-color:#ebdce9!important;border-radius:21px!important;background:rgba(255,255,255,.76)!important;box-shadow:0 7px 20px #70497912}
.stButton button,.stFormSubmitButton button{border-radius:14px!important;font-weight:800!important;border:1px solid #dcbedc!important;transition:filter .2s ease, transform .2s ease}
.stButton button:hover,.stFormSubmitButton button:hover{transform:translateY(-1px);filter:brightness(1.03)}
button[kind="primary"]{background:linear-gradient(100deg,#7c4ac0,#b45bb5)!important;border:0!important;color:white!important}
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.88);border-radius:17px;gap:4px;padding:5px 7px;box-shadow:0 2px 10px #53275214;overflow-x:auto}
.stTabs [data-baseweb="tab"]{padding:8px 13px;border-radius:12px;font-size:.86rem;font-weight:800;white-space:nowrap;color:#654a7b}
.stTabs [aria-selected="true"]{background:#f0e0ff;color:#633091!important}
[data-baseweb="select"]>div{border-radius:12px!important}
[data-testid="stMetric"]{background:#fffaf7;border-radius:15px;padding:12px}
@media(max-width:1100px){.hero-art{min-width:260px;width:34%}.hero-copy .tags{margin-top:12px}.kpis{gap:8px}.kpi{padding:12px;gap:6px}.kpi .emoji{font-size:2.5rem}.kpi .big{font-size:1.8rem}}
@media(max-width:760px){.block-container{padding:.65rem .63rem 1.7rem!important}.hero-school{min-height:165px;padding-left:15px;border-radius:20px}.hero-copy{padding:17px 0}.hero-copy h1{font-size:1.52rem}.hero-copy .subtitle{font-size:.9rem}.hero-copy .tags{font-size:.72rem;gap:7px}.hero-art{min-width:105px;width:30%;clip-path:ellipse(100% 95% at 95% 50%)}.kpis{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.kpi{min-height:93px}.kpi .emoji{font-size:2.3rem}.kpi .big{font-size:1.8rem}.teacher-box .name{font-size:1.3rem}.lesson-header .heading{font-size:1.5rem}}
@media(max-width:390px){.hero-art{display:none}.kpi{padding:9px}.kpi .emoji{font-size:1.9rem}.kpi .label{font-size:.78rem}.kpi .big{font-size:1.48rem}}
</style>'''
st.markdown(CSS,unsafe_allow_html=True)

# Tous les visuels sont locaux, sans lien réseau et en définition nette (webp).
HERO_B64=b64_asset('classe_illustration.webp')
SOFIA_B64=b64_asset('sofia_illustration.webp')
hero_img=(f'<img class="hero-art" alt="Illustration 2D d’une salle de classe avec tableau ¡Hola!" src="data:image/webp;base64,{HERO_B64}"/>' if HERO_B64 else '')
st.markdown(f'''<div class="hero-school"><div class="hero-copy">
<h1>🇪🇸 Mi Español · Mon école des langues</h1>
<div class="subtitle">Progresse à ton rythme du CP à la Terminale !</div>
<div class="tags"><span>🎓 Espagnol scolaire</span><span>🌍 A1 → C2</span><span>🌱 Allemand et italien de survie</span><span>⭐ {int(p['stars'])} étoiles</span></div>
</div>{hero_img}</div>''',unsafe_allow_html=True)

st.markdown('<div class="lang-caption">🌍 Choisis ton parcours :</div>',unsafe_allow_html=True)
lang=st.segmented_control('Langue',['🇪🇸 Espagnol','🇩🇪 Allemand','🇮🇹 Italien'],default='🇪🇸 Espagnol',key='language_label',label_visibility='collapsed') or '🇪🇸 Espagnol'
esp=lang=='🇪🇸 Espagnol'
track='german' if lang=='🇩🇪 Allemand' else 'italian'
if esp:
    grade=int(p['grade'])
    s_done=done_count('school',s_keys(grade))
    c_done=sum(done_count('cefr',c_keys(level)) for level in CECRL)
    cards=[('🏫','Ma classe',CLASSES[grade],'rose'),('📖','Leçons du niveau',f'{s_done}/{len(s_keys(grade))}','blue'),('🎯','Ateliers A1–C2',f'{c_done}/{sum(map(len,CECRL.values()))}','mint'),('⭐','Mes étoiles',str(p['stars']),'yellow')]
else:
    m_done=done_count(track,[str(i) for i in range(len(MISSIONS))])
    cards=[('🌍','Mon parcours','A1++','rose'),('🗣️','Missions acquises',f'{m_done}/10','blue'),('🎯','Voyage pratique','10 missions','mint'),('⭐','Mes étoiles',str(p['stars']),'yellow')]
card_html=''.join(f'<div class="kpi {kind}"><span class="emoji">{symbol}</span><div><div class="label">{html.escape(title)}</div><div class="big">{html.escape(value)}</div></div></div>' for symbol,title,value,kind in cards)
st.markdown('<div class="kpis">'+card_html+'</div>',unsafe_allow_html=True)


def decorate_title(text):
    st.markdown('<div class="title-row">'+html.escape(text)+'</div>',unsafe_allow_html=True)


def tts_button(sentence,code='es-ES',id_suffix='default'):
    # Web Speech est exécuté dans un composant HTML isolé, depuis un clic de l'utilisateur.
    phrase=json.dumps(str(sentence),ensure_ascii=False).replace('</','<\\/')
    lang_code=json.dumps(code)
    safe_id=html.escape(str(id_suffix),quote=True)
    components.html(f'''<!-- vocal-{safe_id} -->
<style>body{{margin:0;font-family:Arial,sans-serif}}button{{font-size:14px;background:linear-gradient(95deg,#7c50b5,#ab64c1);border:0;color:white;border-radius:13px;cursor:pointer;padding:11px 15px;font-weight:bold;max-width:100%}}button:hover{{filter:brightness(1.07)}}small{{color:#6e5974;font-size:11px;margin-left:10px}}</style>
<button aria-label="Écouter le texte en espagnol" onclick="speak()">🔊 Écouter et répéter</button><small id="status">Voix du navigateur</small>
<script>function speak(){{let text={phrase};let code={lang_code};let status=document.getElementById('status');if(!('speechSynthesis' in window)){{status.textContent='Audio non pris en charge';return;}}window.speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(text);u.lang=code;u.rate=0.84;u.onerror=()=>status.textContent='Voix indisponible';u.onend=()=>status.textContent='À toi de répéter !';window.speechSynthesis.speak(u);}}</script>''',height=58)


def colored_panel(kind,heading,content):
    return f'<div class="lesson-panel {kind}"><div class="head">{html.escape(heading)}</div><p>{html.escape(str(content))}</p></div>'


def lesson_available(bucket,key):
    if bucket=='school':
        grade,idx=map(int,key.split(':'))
        return grade<=p['grade'] and idx in permitted('school',s_keys(grade))
    if bucket=='cefr':
        level,idx=key.split(':')
        return level in unlocked_groups(p['cefr_exams'],list(CECRL)) and int(idx) in permitted('cefr',c_keys(level))
    if bucket=='grammar':
        level,idx=key.split(':')
        return level in unlocked_groups(p['grammar_exams'],list(GRAMMAIRE)) and int(idx) in permitted('grammar',g_keys(level))
    return False


def render_lesson(lesson,bucket,key,subtitle):
    if not lesson_available(bucket,key):
        st.warning('🔒 Ce chapitre n’est pas encore accessible : réussis les précédents.');return
    chapter_heading=html.escape(lesson['titre'])
    tag=f'{html.escape(subtitle)}'
    axe=html.escape(lesson.get('axe','Leçon interactive'))
    st.markdown(f'''<div class="lesson-header"><div class="breadcrumb">📚 {tag}</div><div class="heading">📖 {chapter_heading}</div><span class="chip">{axe}</span></div>''',unsafe_allow_html=True)
    a,b=st.columns(2,gap='small')
    with a:st.markdown(colored_panel('rule','📌 La règle à retenir',lesson['notion']),unsafe_allow_html=True)
    with b:st.markdown(colored_panel('example','💬 Exemples espagnols',lesson['exemples']),unsafe_allow_html=True)
    st.markdown(colored_panel('story','📖 Lis et comprends',lesson['texte']),unsafe_allow_html=True)
    tts_button(lesson['exemples']+' '+lesson['texte'],id_suffix=key)
    st.markdown('''<div class="mini-actions"><div class="mini-action">🎧 Écoute & répète<br><small>Travaille ta prononciation</small></div><div class="mini-action blue">✏️ À toi de jouer<br><small>Écris ou parle librement</small></div><div class="mini-action gold">🏅 Quiz<br><small>Valide tes acquis</small></div></div>''',unsafe_allow_html=True)
    with st.expander('🎨 Ma petite mission',expanded=False):
        st.write(lesson['mission'])
        st.caption('Production libre : elle n’est pas notée automatiquement. Une bonne réponse au QCM débloque le chapitre suivant.')
    if p[bucket].get(key) is True:st.success('✅ Chapitre déjà validé — tu peux le réviser quand tu veux.')
    with st.form('lesson_form_'+bucket+'_'+key):
        st.markdown('#### 🎯 Vérifie tes acquis')
        answer=st.radio(lesson['question'],lesson['choix'],index=None,key='answer_'+bucket+'_'+key)
        submit=st.form_submit_button('✅ Corriger mon quiz',type='primary',use_container_width=True)
    if submit:
        if answer is None:st.warning('Choisis une réponse.')
        elif answer==lesson['reponse']:
            award(bucket,key,5)
            st.success('🎉 ¡Muy bien! Tu as réussi et débloqué le chapitre suivant.')
        else:st.info('Réessaie à ton rythme. Pour t’aider : la bonne réponse est « '+lesson['reponse']+' ».')


def exam_form(lessons,bucket,group):
    exams={'school':'school_exams','cefr':'cefr_exams','grammar':'grammar_exams'}[bucket]
    group=str(group)
    if bucket=='school':
        if int(group)>p['grade']:st.warning('Classe verrouillée.');return False
        lesson_keys=s_keys(int(group))
    elif bucket=='cefr':
        if group not in unlocked_groups(p['cefr_exams'],list(CECRL)):st.warning('Niveau verrouillé.');return False
        lesson_keys=c_keys(group)
    else:
        if group not in unlocked_groups(p['grammar_exams'],list(GRAMMAIRE)):st.warning('Niveau verrouillé.');return False
        lesson_keys=g_keys(group)
    count=done_count(bucket,lesson_keys)
    if count<len(lesson_keys):
        st.info(f'🔒 Valide d’abord les chapitres de ce niveau : {count}/{len(lesson_keys)} acquis.')
        return False
    if p[exams].get(group) is True:
        st.success('🏆 Bilan déjà réussi. Le niveau suivant est accessible.')
        return True
    with st.form(f'exam_{bucket}_{group}'):
        st.write('Réponds à toutes les questions. **80 % de réussite** sont nécessaires ; tu peux recommencer sans pénalité.')
        answers=[st.radio(f'{i+1}. {lesson["question"]}',lesson['choix'],index=None,key=f'exam_{bucket}_{group}_{i}') for i,lesson in enumerate(lessons)]
        submit=st.form_submit_button('📝 Corriger mon bilan',type='primary',use_container_width=True)
    if submit:
        if any(a is None for a in answers):st.warning('Réponds à toutes les questions.');return False
        score=sum(ans==lesson['reponse'] for ans,lesson in zip(answers,lessons))
        st.write(f'**Résultat : {score}/{len(lessons)}**')
        if score_passes(score,len(lessons)):
            award(exams,group,20)
            st.success('🏅 Bravo, niveau validé ! Le suivant est maintenant débloqué.')
            st.balloons()
            return True
        st.warning('Continue à t’entraîner : il faut atteindre 80 %.')
        for i,(a,lesson) in enumerate(zip(answers,lessons)):
            if a!=lesson['reponse']:st.caption(f'Question {i+1} : {lesson["reponse"]}')
    return False


def quiz_forms(verb,tense,key):
    forms=conjugate(verb,tense)
    persons=IMP_PERSONS if tense.startswith('imperativo_') else PERSONS
    indices=[i for i,f in enumerate(forms) if not f.startswith('—')]
    picked=[indices[0],indices[len(indices)//2],indices[-1]]
    with st.form(f'conj_form_{key}'):
        answers=[]
        for n,idx in enumerate(picked,1):
            good=forms[idx]
            other=list(dict.fromkeys(f for f in forms if f!=good and not f.startswith('—')))
            options=sorted(set([good]+other[:2]),key=str.casefold)
            answers.append(st.radio(f'{n}. {persons[idx]}',options,index=None,key=f'conj_{key}_{idx}'))
        submit=st.form_submit_button('🎯 Valider mon défi',type='primary',use_container_width=True)
    if not submit:return False
    if any(a is None for a in answers):st.warning('Réponds aux trois questions.');return False
    correct=sum(a==forms[i] for a,i in zip(answers,picked))
    if correct==3:st.success('🎉 3/3 ! La prochaine étape se débloque.');return True
    st.info(f'{correct}/3. Réessaie pour obtenir 3/3, sans pénalité.')
    for a,i in zip(answers,picked):
        if a!=forms[i]:st.caption(f'{persons[i]} → {forms[i]}')
    return False

# ─────────────────────────────────────────────────────────────────────────────
# ESPAGNOL : école, CECRL, grammaire, conjugaison, LLCER, bilans, progression
# ─────────────────────────────────────────────────────────────────────────────
if esp:
    st.caption(f'🎓 {CLASSES[p["grade"]]} · équivalence indicative en Espagne : {EQUIVALENCES[p["grade"]]}. Les cursus français et espagnol diffèrent.')
    tabs=st.tabs(['🏠 Mon école','🌍 A1–C2','📐 Grammaire','🔤 Verbes & temps','🎭 LLCER','📝 Évaluations','📈 Mon parcours','💾 Profil & sources'])
    with tabs[0]:
        left,right=st.columns([0.95,2.15],gap='medium')
        with left:
            art=(f'<img class="sofia-art" alt="Illustration 2D de Sofía et des élèves dans leur classe" src="data:image/webp;base64,{SOFIA_B64}"/>' if SOFIA_B64 else '<div style="font-size:5rem;text-align:center">👩‍🏫</div>')
            st.markdown(f'''<div class="teacher-box">{art}<div class="name">👩‍🏫 Ma classe avec Sofía</div>
            <p class="desc">Avance du <b>CP à la Terminale</b> avec des textes, des règles, des exercices et des découvertes culturelles. Les chapitres deviennent accessibles après validation.</p></div>''',unsafe_allow_html=True)
            grade_idx=st.selectbox('🎒 Choisir ma classe',list(range(p['grade']+1)),index=p['grade'],
                                 format_func=lambda i:f'{CLASSES[i]} · {EQUIVALENCES[i]}',key='school_grade')
            levels=SCOLAIRE[CLASSES[grade_idx]]
            ids=s_keys(grade_idx)
            complete=done_count('school',ids)
            st.progress(complete/len(ids))
            st.caption(f'✨ {complete}/{len(ids)} chapitres validés')
            phase,objective,extra=PROGRAMMES[CLASSES[grade_idx]]
            st.markdown(f'''<div class="soft-card"><strong>🎯 {html.escape(phase)}</strong><br>
            <small>{html.escape(objective)}</small><hr style="border:0;border-top:1px solid #e8ccec;margin:10px 0">
            <strong>📚 Ma méthode</strong><br><small>Observer → écouter → comprendre → pratiquer → valider</small></div>''',unsafe_allow_html=True)
            st.caption(extra)
        with right:
            decorate_title('📚 Mes chapitres accessibles')
            keys=s_keys(grade_idx)
            accessible=permitted('school',keys)
            j=st.selectbox('Choisir un chapitre',accessible,
                           format_func=lambda i:f'{i+1}. {levels[i]["titre"]}'+(' · ✓' if p['school'].get(keys[i]) else ''),
                           key=f'school_chapter_{grade_idx}',label_visibility='collapsed')
            locked=len(keys)-len(accessible)
            if locked:st.caption(f'🔒 {locked} chapitre(s) à débloquer : valide le précédent pour continuer.')
            render_lesson(levels[j],'school',keys[j],f'🇪🇸 {CLASSES[grade_idx]} · {EQUIVALENCES[grade_idx]} · Leçon {j+1}/{len(levels)}')
    with tabs[1]:
        col1,col2=st.columns([0.9,2.25],gap='medium')
        with col1:
            with st.container(border=True):
                st.subheader('🌍 A1 → C2')
                available=unlocked_groups(p['cefr_exams'],list(CECRL))
                level=st.selectbox('Niveau accessible',available,key='cefr_level')
                n=done_count('cefr',c_keys(level));total=len(c_keys(level))
                st.progress(n/total)
                st.caption(f'🎯 {n}/{total} ateliers réussis')
                st.info('Un niveau se débloque après ses leçons et son bilan final à 80 %. Les niveaux scolaires sont un parcours distinct.')
                st.caption(f'🔒 {len(CECRL)-len(available)} niveau(x) encore verrouillé(s).')
        with col2:
            items=CECRL[level];keys=c_keys(level)
            selected=st.selectbox('Ateliers accessibles',permitted('cefr',keys),
                                  format_func=lambda i:f'{i+1}. {items[i]["titre"]}'+(' ✓' if p['cefr'].get(keys[i]) else ''),key=f'cefr_chapter_{level}')
            render_lesson(items[selected],'cefr',keys[selected],f'🌍 Niveau {level} · Atelier {selected+1}/{len(items)}')
    with tabs[2]:
        col1,col2=st.columns([0.9,2.25],gap='medium')
        with col1:
            with st.container(border=True):
                st.subheader('📐 Grammaire')
                levels=unlocked_groups(p['grammar_exams'],list(GRAMMAIRE))
                g_level=st.selectbox('Niveaux accessibles',levels,key='grammar_level')
                keys=g_keys(g_level);n=done_count('grammar',keys)
                st.progress(n/len(keys))
                st.caption(f'📚 {n}/{len(keys)} règles réussies')
                st.caption(f'🔒 {len(GRAMMAIRE)-len(levels)} niveau(x) à débloquer')
                with st.expander('🏆 Bilan de grammaire · 80 %'):
                    exam_form(GRAMMAIRE[g_level],'grammar',g_level)
        with col2:
            rules=GRAMMAIRE[g_level];keys=g_keys(g_level)
            j=st.selectbox('Règles disponibles',permitted('grammar',keys),
                           format_func=lambda i:f'{i+1}. {rules[i]["titre"]}'+(' ✓' if p['grammar'].get(keys[i]) else ''),key=f'grammar_chapter_{g_level}')
            render_lesson(rules[j],'grammar',keys[j],f'📐 Niveau {g_level} · Grammaire {j+1}/{len(rules)}')
    with tabs[3]:
        st.subheader('🔤 Mon laboratoire des verbes')
        st.caption('18 verbes, 20 temps et modes. Un défi de **3/3** débloque chaque nouvel élément. Les formes déjà réussies restent consultables.')
        verb_tab,tense_tab=st.tabs(['🗣️ Apprendre les verbes','⏰ Apprendre les temps'])
        with verb_tab:
            a,b=st.columns([0.9,2.25],gap='medium')
            with a:
                with st.container(border=True):
                    st.markdown('### 📖 Mes verbes')
                    v_indices=permitted('verbs',VERBS)
                    i=st.selectbox('Verbes disponibles',v_indices,
                         format_func=lambda idx:f'{idx+1}. {VERBS[idx]}'+(' ✓' if p['verbs'].get(VERBS[idx]) else ''),key='verb_choice')
                    verb=VERBS[i]
                    learned=done_count('verbs',VERBS)
                    st.progress(learned/len(VERBS))
                    st.caption(f'{learned}/{len(VERBS)} verbes maîtrisés')
                    st.caption('🔒 Les autres verbes se débloquent dans l’ordre.')
            with b:
                with st.container(border=True):
                    st.markdown(f'### 🗣️ {verb} · Indicatif présent')
                    st.table({'Personne':PERSONS,'Forme espagnole':conjugate(verb,'presente')})
                    st.caption(f'Participe passé : {participle(verb)} · Gérondif : {gerund(verb)}')
                    if p['verbs'].get(verb) is True:st.success('✅ Verbe maîtrisé !')
                    if quiz_forms(verb,'presente','verb_'+verb):
                        award('verbs',verb,10)
                        award('conjugation',verb+':presente',5)
        with tense_tab:
            verified=[v for v in VERBS if p['verbs'].get(v) is True]
            if not verified:st.info('🔒 Commence par maîtriser le premier verbe « hablar » pour ouvrir les temps de conjugaison.')
            else:
                a,b=st.columns([0.9,2.25],gap='medium')
                with a:
                    with st.container(border=True):
                        indices=permitted('tenses',TENSE_ORDER)
                        i=st.selectbox('Temps accessibles',indices,
                            format_func=lambda j:f'{j+1}. {TENSES[TENSE_ORDER[j]][0]}'+(' ✓' if p['tenses'].get(TENSE_ORDER[j]) else ''),key='tense_choice')
                        tense=TENSE_ORDER[i]
                        verb=st.selectbox('Verbe déjà maîtrisé',verified,key='tense_verb')
                        n=done_count('tenses',TENSE_ORDER)
                        st.progress(n/len(TENSE_ORDER))
                        st.caption(f'⏰ {n}/{len(TENSE_ORDER)} temps maîtrisés')
                        st.caption(f'🔒 {len(TENSE_ORDER)-len(indices)} temps encore verrouillé(s)')
                with b:
                    with st.container(border=True):
                        title,cefr_hint,usage=TENSES[tense]
                        st.markdown(f'### ⏰ {verb} · {title}')
                        st.info(f'**Repère pédagogique : {cefr_hint}** · {usage}')
                        forms=conjugate(verb,tense)
                        persons=IMP_PERSONS if tense.startswith('imperativo_') else PERSONS
                        st.table({'Personne':persons,'Conjugaison':forms})
                        if tense=='preterito_anterior' or tense.startswith('subj_futuro'):
                            st.warning('Forme surtout historique, littéraire ou juridique, rarement utilisée à l’oral.')
                        if p['tenses'].get(tense) is True:st.success('✅ Temps maîtrisé !')
                        if quiz_forms(verb,tense,'tense_'+verb+'_'+tense):
                            award('tenses',tense,15)
                            award('conjugation',verb+':'+tense,5)
    with tabs[4]:
        st.subheader('🎭 Bibliothèque LLCER · Première & Terminale')
        if p['grade']<CLASSES.index('Première'):
            st.info('🔒 Cette spécialité se débloque à partir de la Première. Elle reste facultative.')
        else:
            choices=[level for level in LLCER if CLASSES.index(level)<=p['grade']]
            phase=st.selectbox('Année LLCER accessible',choices,key='llcer_level')
            works=LLCER[phase]['oeuvres']
            keys=[f'{phase}:{i}' for i in range(len(works))]
            j=st.selectbox('Œuvres à découvrir',permitted('llcer',keys),
                format_func=lambda i:works[i][1]+(' ✓' if p['llcer'].get(keys[i]) else ''),key=f'llcer_work_{phase}')
            author,title,mission=works[j]
            with st.container(border=True):
                st.markdown('### 📖 '+title)
                st.write('**Auteur / réalisation :** '+author)
                st.write('**Mission :** '+mission)
                st.caption('Cet atelier de méthode ne remplace pas la lecture du livre ou le visionnage du film.')
                q,choices,correct=LLCER_EXERCICES[phase][j]
                with st.form(f'llcer_form_{phase}_{j}'):
                    response=st.radio(q,choices,index=None,key=f'llcer_answer_{phase}_{j}')
                    submitted=st.form_submit_button('✅ Valider la méthode')
                if submitted:
                    if response==correct:award('llcer',keys[j]);st.success('Méthode validée, prochaine œuvre disponible !')
                    elif response is None:st.warning('Choisis une réponse.')
                    else:st.warning('Révise la méthode : '+correct)
    with tabs[5]:
        st.subheader('📝 Mes évaluations · Sans pression')
        st.markdown('<div class="section-note">🎯 Les bilans se débloquent après les chapitres du niveau. Il faut <b>80 % de réussite</b> pour avancer. Aucune limite de tentatives.</div>',unsafe_allow_html=True)
        c1,c2=st.columns(2,gap='medium')
        with c1:
            with st.container(border=True):
                st.markdown('### 🎓 Passage en classe supérieure')
                g=p['grade']
                st.write('**Classe actuelle :** '+CLASSES[g])
                passed=exam_form(SCOLAIRE[CLASSES[g]],'school',str(g))
                if passed:
                    if g<len(CLASSES)-1:
                        if st.button(f'🎓 Passer en {CLASSES[g+1]}',key=f'next_grade_{g}',type='primary',use_container_width=True):
                            p['grade']+=1;persist();st.rerun()
                    else:st.success('🏆 Parcours scolaire terminé !')
        with c2:
            with st.container(border=True):
                st.markdown('### 🌍 Bilan A1–C2')
                eligible=unlocked_groups(p['cefr_exams'],list(CECRL))
                g=st.selectbox('Niveau CECRL à évaluer',eligible,key='exam_cefr')
                exam_form(CECRL[g],'cefr',g)
    with tabs[6]:
        st.subheader('📈 Ma progression')
        st.markdown('<div class="section-note">🏫 Tu peux toujours réviser les classes et les niveaux déjà validés. Ton parcours avance étape par étape.</div>',unsafe_allow_html=True)
        rows=[]
        for i,name in enumerate(CLASSES):
            count=done_count('school',s_keys(i))
            rows.append({'Classe':name,'Équivalent espagnol':EQUIVALENCES[i],
                         'Chapitres':f'{count}/{len(s_keys(i))}','Bilan':'✅' if p['school_exams'].get(str(i)) else '—',
                         'Statut':'🔒 À venir' if i>p['grade'] else '📘 En cours' if i==p['grade'] else '✓ Révision'})
        st.dataframe(rows,use_container_width=True,hide_index=True)
        st.markdown('#### 🌍 Ateliers CECRL')
        cols=st.columns(3)
        for i,level in enumerate(CECRL):
            with cols[i%3]:
                st.write(f'**{level}** · {done_count("cefr",c_keys(level))}/{len(c_keys(level))}')
                st.progress(done_count('cefr',c_keys(level))/len(c_keys(level)))
                st.caption('Bilan ✓' if p['cefr_exams'].get(level) else 'Bilan à valider')
        st.divider()
        c1,c2,c3=st.columns(3)
        c1.metric('Règles de grammaire',f'{sum(done_count("grammar",g_keys(level)) for level in GRAMMAIRE)}/24')
        c2.metric('Verbes maîtrisés',f'{done_count("verbs",VERBS)}/18')
        c3.metric('Temps maîtrisés',f'{done_count("tenses",TENSE_ORDER)}/20')
    with tabs[7]:
        st.subheader('💾 Mon profil, mon carnet et les références')
        name_key='school_'+str(p['grade'])
        text=st.text_area('✏️ Mes phrases en espagnol',value=p['notes'].get(name_key,''),height=145,key='notes_'+name_key)
        if st.button('💾 Enregistrer mes phrases',key='save_notes'):
            p['notes'][name_key]=text;persist();st.success('Notes enregistrées dans la session.')
        st.markdown('#### 📚 Sources pédagogiques')
        st.info('Les ateliers sont inspirés des programmes français LVE, et les cours de langue maternelle s’inspirent aussi des attendus de l’Espagne. Aucune certification officielle n’est délivrée.')
        for title,url in SOURCES:st.markdown(f'- [{title}]({url})')
else:
    teacher='Lena' if track=='german' else 'Giulia'
    ix=1 if track=='german' else 2
    st.markdown(f'<div class="section-note">👩‍🏫 <b>{teacher}</b> t’accompagne dans 10 missions de survie. Le niveau A1++ est une appellation interne (A1 renforcé), pas une certification CECRL.</div>',unsafe_allow_html=True)
    l,r=st.columns([0.94,2.15],gap='medium')
    with l:
        with st.container(border=True):
            st.markdown('### 🎒 Mon voyage')
            count=done_count(track,[str(i) for i in range(len(MISSIONS))])
            st.progress(count/len(MISSIONS))
            st.caption(f'🧭 {count}/{len(MISSIONS)} missions réussies')
            st.info('🌱 À ton rythme : relis, écoute, répète et réussis chaque mission pour avancer.')
    with r:
        indices=permitted(track,[str(i) for i in range(len(MISSIONS))])
        j=st.selectbox('🧭 Missions accessibles',indices,
                       format_func=lambda i:f'{i+1}. {MISSIONS[i][0]}'+(' ✓' if p[track].get(str(i)) else ''),key=f'{track}_mission')
        title,description,first,second=MISSIONS[j]
        st.markdown(f'<div class="lesson-header"><div class="breadcrumb">{html.escape(lang)} · Mission {j+1}/10</div><div class="heading">🧭 {html.escape(title)}</div><span class="chip">{html.escape(description)}</span></div>',unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:st.markdown(colored_panel('rule','🗣️ Phrase essentielle',first[ix]+' · '+first[0]),unsafe_allow_html=True)
        with col2:st.markdown(colored_panel('example','💬 Autre expression',second[ix]+' · '+second[0]),unsafe_allow_html=True)
        tts_button(first[ix]+'. '+second[ix],code='de-DE' if track=='german' else 'it-IT',id_suffix=track+str(j))
        with st.form(f'survival_form_{track}_{j}'):
            response=st.radio(f'Comment dire « {first[0]} » ?', [first[ix],second[ix],'Je ne sais pas'],index=None,key=f'survival_{track}_{j}')
            submit=st.form_submit_button('✅ Corriger et débloquer la suite',type='primary',use_container_width=True)
        if submit:
            if response==first[ix]:award(track,str(j),5);st.success('🎉 Mission validée, la prochaine est accessible !')
            elif response is None:st.warning('Choisis une réponse.')
            else:st.info('Réessaie : la bonne expression est « '+first[ix]+' ».')
        if p[track].get(str(j)) is True:st.success('✓ Mission déjà validée')
    if done_count(track,[str(i) for i in range(len(MISSIONS))])==len(MISSIONS):st.success('🏆 Bravo ! Toutes les missions de voyage sont acquises.')
    with st.expander('✏️ Mon carnet de voyage'):
        note=st.text_area('Mes phrases utiles',value=p['notes'].get(track,''),key='travel_notes_'+track)
        if st.button('💾 Sauvegarder mon carnet',key='save_travel_'+track):
            p['notes'][track]=note;persist();st.success('Carnet enregistré dans la session.')

st.divider()
with st.expander('💾 Exporter / importer ma progression · Important sur Streamlit Cloud'):
    st.download_button('⬇️ Télécharger ma sauvegarde JSON',json.dumps(p,ensure_ascii=False,indent=2),
                       file_name='mi_espanol_progression_v6.json',mime='application/json',use_container_width=True,key='export_profile')
    uploaded=st.file_uploader('Importer un profil V2 à V6',type=['json'],key='import_profile')
    if uploaded is not None and st.button('📂 Restaurer le profil',key='restore_profile'):
        try:
            if uploaded.size>2_000_000:raise ValueError('Le fichier dépasse 2 Mo.')
            incoming=json.loads(uploaded.getvalue().decode('utf-8'))
            if not isinstance(incoming,dict) or not any(k in incoming for k in ('grade','school','cefr','grammar','german','italian','spanish')):
                raise ValueError('Ce fichier ne ressemble pas à une sauvegarde Mi Español.')
            st.session_state.profile=normalize(incoming)
            p=st.session_state.profile
            persist()
            st.success('Progression restaurée : la page va se mettre à jour.')
            st.rerun()
        except (UnicodeError,ValueError,TypeError) as error:st.error(str(error))
    st.caption('Sur Streamlit Cloud, les sauvegardes locales peuvent disparaître. Conserve ce fichier JSON pour retrouver tes résultats. Ne publie jamais ton fichier personnel sur GitHub.')
st.caption('🇪🇸 Mi Español V6 · Interface 2D responsive · Cours V5 préservés · Déblocage par validation des acquis · Aucun diplôme officiel.')
