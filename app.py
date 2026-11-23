"""Mi Español - école virtuelle, espagnol natif CP-Terminale + CECRL + langues de survie."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
import streamlit as st
from programme import CLASSES, EQUIVALENCES, SCOLAIRE, CECRL, SOURCES, validate
from conjugaison import PERSONS, IMP_PERSONS, VERBS, TENSES, conjugate, participle, gerund
from grammaire import GRAMMAIRE
from progression import available_indices, is_chapter_unlocked, unlocked_groups, current_school_grade, score_passes
from programmes_officiels import PROGRAMMES, LLCER, LLCER_EXERCICES

st.set_page_config(page_title='Mi Español · Mon école des langues',page_icon='🇪🇸',layout='wide',initial_sidebar_state='collapsed')

# Application sans base de données externe : mémoire dans la session utilisateur.
# Le JSON exporté est la méthode fiable pour conserver son profil entre deux sessions Cloud.
# En local privé, MI_ESPANOL_LOCAL_SAVE=1 autorise une sauvegarde automatique sur disque.
import os
LOCAL_SAVE = os.environ.get('MI_ESPANOL_LOCAL_SAVE','0')=='1'
SAVE_FILE = Path(__file__).with_name('ma_progression_locale.json')

MISSIONS = [
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
    return {'version':5,'name':'Élève','grade':0,'school':{},'school_exams':{},
            'cefr':{},'cefr_exams':{},'grammar':{},'grammar_exams':{},
            'verbs':{},'tenses':{},'conjugation':{},'german':{},'italian':{},
            'notes':{},'stars':0,'legacy_spanish':{},'llcer':{}}


def normalize(raw):
    default = new_profile()
    if not isinstance(raw,dict): return default
    for key in default:
        if key in raw and isinstance(raw[key],type(default[key])):
            default[key] = raw[key]
    # V2 : on conserve les deux langues de survie, les notes et les étoiles.
    if isinstance(raw.get('spanish'),dict) and not default['legacy_spanish']:
        default['legacy_spanish'] = raw['spanish']
    try: requested_grade = int(default['grade'])
    except (ValueError,TypeError): requested_grade=0
    default['grade'] = min(max(0,requested_grade), current_school_grade(default['school_exams'],len(CLASSES)-1))
    try: default['stars']=max(0,int(default['stars']))
    except (ValueError,TypeError):default['stars']=0
    default['version'] = 5
    return default


def load_profile():
    if LOCAL_SAVE:
        try:return normalize(json.loads(SAVE_FILE.read_text(encoding='utf-8')))
        except (OSError,ValueError,UnicodeError,TypeError):pass
    return new_profile()

if 'profile' not in st.session_state:
    st.session_state.profile = load_profile()
p = st.session_state.profile

def persist():
    if LOCAL_SAVE:
        try:SAVE_FILE.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
        except OSError:pass

def award(bucket,key,points=5):
    if not p[bucket].get(key):
        p[bucket][key] = True
        p['stars'] += points
        persist()
        return True
    return False


def school_key(i,j):return f'{i}:{j}'
def cefr_key(level,j):return f'{level}:{j}'
def grammar_key(level,j):return f'{level}:{j}'
def school_completed(i):return sum(p['school'].get(school_key(i,j)) is True for j in range(len(SCOLAIRE[CLASSES[i]])))
def cefr_completed(level):return sum(p['cefr'].get(cefr_key(level,j)) is True for j in range(len(CECRL[level])))
def grammar_completed(level):return sum(p['grammar'].get(grammar_key(level,j)) is True for j in range(len(GRAMMAIRE[level])))
def school_choices(i):
    return available_indices(p['school'],[school_key(i,j) for j in range(len(SCOLAIRE[CLASSES[i]]))])
def cefr_choices(level):
    return available_indices(p['cefr'],[cefr_key(level,j) for j in range(len(CECRL[level]))])
def grammar_choices(level):
    return available_indices(p['grammar'],[grammar_key(level,j) for j in range(len(GRAMMAIRE[level]))])

def check_lesson_access(bucket,key):
    if bucket=='school':
        i,j=map(int,key.split(':'))
        return i<=p['grade'] and j in school_choices(i)
    if bucket=='cefr':
        level,j=key.split(':')
        return level in unlocked_groups(p['cefr_exams'],list(CECRL)) and int(j) in cefr_choices(level)
    if bucket=='grammar':
        level,j=key.split(':')
        return level in unlocked_groups(p['grammar_exams'],list(GRAMMAIRE)) and int(j) in grammar_choices(level)
    return False

TENSE_ORDER = [
 'presente','imperfecto','preterito','perfecto','futuro','condicional',
 'imperativo_afirmativo','imperativo_negativo','pluscuamperfecto',
 'subj_presente','subj_imperfecto','subj_perfecto','condicional_perfecto',
 'subj_pluscuamperfecto','futuro_perfecto','subj_imperfecto_se',
 'subj_pluscuamperfecto_se','preterito_anterior','subj_futuro','subj_futuro_perfecto']
assert set(TENSE_ORDER)==set(TENSES)

def quiz_forms(verb,tense,unique_key):
    """Défi 3/3 requis pour maîtriser un verbe ou une nouvelle conjugaison."""
    forms=conjugate(verb,tense)
    persons=IMP_PERSONS if tense.startswith('imperativo_') else PERSONS
    ids=[i for i,f in enumerate(forms) if not f.startswith('—')]
    chosen_ids=[ids[0],ids[len(ids)//2],ids[-1]]
    with st.form('quiz_'+unique_key):
        answers=[]
        for number,idx in enumerate(chosen_ids):
            good=forms[idx]
            distractors=list(dict.fromkeys(f for f in forms if f!=good and not f.startswith('—')))
            choices=sorted(set([good]+distractors[:2]),key=str.casefold)
            answers.append(st.radio(f'{number+1}. {persons[idx]} → ?',choices,index=None,key=f'q_{unique_key}_{idx}'))
        submitted=st.form_submit_button('✅ Valider mes 3 réponses',type='primary',use_container_width=True)
    if not submitted:return False
    if any(a is None for a in answers):
        st.warning('Réponds aux trois questions pour valider les acquis.')
        return False
    score=sum(a==forms[idx] for a,idx in zip(answers,chosen_ids))
    if score==3:
        st.success('🎉 3/3 : acquis validés ! La prochaine étape est débloquée.')
        return True
    st.warning(f'{score}/3. Il faut 3/3 pour débloquer la suite. Tu peux réessayer immédiatement.')
    for a,idx in zip(answers,chosen_ids):
        if a!=forms[idx]:st.caption(f'Révision : {persons[idx]} → {forms[idx]}')
    return False

def lesson_panel(lesson,bucket,key,label):
    if not check_lesson_access(bucket,key):
        st.warning('🔒 Chapitre verrouillé. Valide d’abord les acquis des chapitres précédents.')
        return
    with st.container(border=True):
        st.caption(label)
        if lesson.get('axe'):
            st.caption('📋 '+lesson['axe']+' · '+lesson.get('competence','')+' · Atelier adossé au programme français LVE')
        st.subheader(lesson['titre'])
        st.markdown('#### 📌 La règle à retenir')
        st.write(lesson['notion'])
        st.markdown('#### 💬 Exemples espagnols')
        st.info(lesson['exemples'])
        st.markdown('#### 📖 Lis et comprends')
        st.markdown(f'> {lesson["texte"]}')
        st.markdown('#### ✍️ À toi de jouer')
        st.write(lesson['mission'])
        st.caption('Réussis le QCM (1/1) pour débloquer la suite. Les productions écrites et orales proposées sont des entraînements non corrigés automatiquement : le quiz seul ne certifie pas ces compétences.')
        if p[bucket].get(key):
            st.success('✅ Leçon acquise. Tu peux toujours la revoir.')
        with st.form('lesson_form_'+bucket+'_'+key):
            response = st.radio(lesson['question'],lesson['choix'],index=None,
                                key='answer_'+bucket+'_'+key)
            submit = st.form_submit_button('✅ Corriger mon exercice',type='primary',use_container_width=True)
        if submit:
            if response is None:
                st.warning('Choisis une réponse avant de valider.')
            elif response == lesson['reponse']:
                award(bucket,key)
                st.success('¡Excelente! Chapitre validé : le suivant est débloqué. Bonne réponse : '+lesson['reponse'])
                st.balloons() if bucket=='school' and school_completed(p['grade'])==len(SCOLAIRE[CLASSES[p['grade']]]) else None
            else:
                st.error('Pas encore : la bonne réponse est « '+lesson['reponse']+' ». Relis la règle et réessaie.')
        with st.expander('🔎 Réviser la notion et les exemples'):
            st.write(lesson['notion'])
            st.write('**Exemples :** '+lesson['exemples'])


def exam_form(lessons,bucket,group):
    """Bilan final à 80 %, accessible après tous les chapitres de ce niveau."""
    exam_bucket = {'school':'school_exams','cefr':'cefr_exams','grammar':'grammar_exams'}[bucket]
    exam_key = str(group)
    if bucket=='school' and int(group)>p['grade']:
        st.warning('🔒 Classe non débloquée.')
        return False
    if bucket!='school':
        names=list(CECRL) if bucket=='cefr' else list(GRAMMAIRE)
        if group not in unlocked_groups(p[exam_bucket],names):
            st.warning('🔒 Valide le bilan du niveau précédent pour accéder à celui-ci.')
            return False
    needed=len(lessons)
    done={'school':lambda:school_completed(int(group)),'cefr':lambda:cefr_completed(group),
          'grammar':lambda:grammar_completed(group)}[bucket]()
    if done<needed:
        st.info(f'🔒 Bilan verrouillé : valide les {needed} chapitres ({done}/{needed}).')
        if bucket=='school' and p[exam_bucket].get(exam_key) is True:
            st.caption('Ton ancien bilan V4 reste enregistré, mais les ateliers ajoutés en V5 doivent aussi être validés avant le passage à la classe supérieure.')
        return False
    if p[exam_bucket].get(exam_key) is True:
        st.success('🏅 Bilan déjà réussi ; tous les chapitres V5 sont également validés !')
        return True
    st.write(f'**Bilan final** · {needed} questions. Il faut **80 % de bonnes réponses** ; pas de limite de tentatives.')
    with st.form('exam_form_'+bucket+'_'+exam_key):
        answers=[]
        for i,l in enumerate(lessons):
            answers.append(st.radio(f'{i+1}. {l["question"]}',l['choix'],index=None,key=f'exam_answer_{bucket}_{exam_key}_{i}'))
        submit=st.form_submit_button('📝 Corriger et valider mon bilan',type='primary',use_container_width=True)
    if submit:
        if any(a is None for a in answers):
            st.warning('Réponds à toutes les questions avant de valider le bilan.')
            return False
        score=sum(a==l['reponse'] for a,l in zip(answers,lessons))
        threshold=(4*needed+4)//5  # ceil(0.8*n)
        st.write(f'**Résultat : {score}/{needed}** · seuil : {threshold}/{needed}')
        for i,(a,l) in enumerate(zip(answers,lessons)):
            if a!=l['reponse']:st.caption(f'Question {i+1} : bonne réponse « {l["reponse"]} ».')
        if score_passes(score,needed):
            award(exam_bucket,exam_key,20)
            st.success('🎉 Bilan validé ! Le niveau suivant est débloqué.')
            return True
        st.warning('Révise les réponses incorrectes et retente le bilan quand tu veux.')
    return False

st.markdown('''<style>
.stApp{background:linear-gradient(140deg,#fffaf0 0%,#fbece9 56%,#f5efff 100%);color:#362c3b}
.block-container{max-width:1400px;padding-top:1rem;padding-bottom:2rem}
.hero{background:linear-gradient(115deg,#633b99,#b65c93 55%,#efac79);color:#fff;
 padding:20px 24px;border-radius:24px;margin-bottom:15px;box-shadow:0 10px 24px #65417626}
.hero h1{color:#fff;font-size:clamp(1.5rem,3.3vw,2.25rem);margin:0 0 4px}
.hero p{margin:4px 0;color:#fff;opacity:.96}
h1,h2,h3{color:#633b7c}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#ffffffc8;border-radius:18px;border-color:#ecdfea}
.stButton button{border-radius:12px}.stButton button[kind="primary"]{background:#744fb0;color:#fff}
[data-testid="stMetric"]{background:#fffbf6;border-radius:13px;padding:10px}
@media(max-width:730px){.hero{padding:15px}.block-container{padding-left:.6rem;padding-right:.6rem}}
</style>''',unsafe_allow_html=True)
st.markdown(f'''<div class="hero"><h1>🇪🇸 Mi Español · Mon école des langues</h1>
<p>🏫 Espagnol du CP à la Terminale · 🌍 A1 → C2 · 🇩🇪 Allemand & 🇮🇹 Italien de survie</p>
<p>✨ À ton rythme, sans échéances · ⭐ {p['stars']} étoiles</p></div>''',unsafe_allow_html=True)

chosen = st.segmented_control('Choisis ta langue', ['🇪🇸 Espagnol','🇩🇪 Allemand','🇮🇹 Italien'],default='🇪🇸 Espagnol',key='chosen_lang')
chosen=chosen or '🇪🇸 Espagnol'
esp = chosen=='🇪🇸 Espagnol'
track = 'german' if chosen=='🇩🇪 Allemand' else 'italian'

if esp:
    a,b,c,d=st.columns(4)
    a.metric('🏫 Ma classe',CLASSES[p['grade']])
    b.metric('📘 Leçons du niveau',f'{school_completed(p["grade"])}/{len(SCOLAIRE[CLASSES[p["grade"]]])}')
    c.metric('🌍 Ateliers A1–C2',f'{sum(map(cefr_completed,CECRL))}/{sum(map(len,CECRL.values()))}')
    d.metric('⭐ Mes étoiles',p['stars'])
    st.caption(f'Équivalence scolaire indicative en Espagne : {CLASSES[p["grade"]]} ≈ {EQUIVALENCES[p["grade"]]} (la scolarité française et espagnole ne se superposent pas exactement).')
    tabs=st.tabs(['🏫 Mon école','🌍 Niveaux A1–C2','📐 Grammaire','🔤 Verbes & conjugaison','📖 Spécialité LLCER','📝 Évaluations','📈 Mon parcours','💾 Profil & sources'])
    with tabs[0]:
        left,right=st.columns([1,2.4],gap='medium')
        with left:
            with st.container(border=True):
                st.subheader('🎒 Ma classe avec Sofía')
                st.write('Tu progresses du **CP à la Terminale**, à ton rythme. Les leçons de langue maternelle sont complétées par les axes des programmes français d’espagnol LVE.')
                review_i=st.selectbox('Choisir une classe accessible',list(range(p['grade']+1)),
                                      format_func=lambda i:f'{CLASSES[i]} · {EQUIVALENCES[i]}',
                                      index=p['grade'],key=f'school_choice_{p["grade"]}')
                name=CLASSES[review_i]
                done=school_completed(review_i)
                st.progress(done/len(SCOLAIRE[name]))
                st.caption(f'{done}/{len(SCOLAIRE[name])} chapitres validés')
                st.write('**Méthode :** comprendre → observer la langue → lire et parler → réussir le QCM → produire un court écrit ou un dialogue.')
                phase, objective, info = PROGRAMMES[name]
                st.markdown(f'**📋 {phase}**')
                st.write(objective)
                st.caption(info)
                st.caption('Aucun cours bloqué par le calendrier. Les anciennes classes restent disponibles pour révision.')
        with right:
            chapters=SCOLAIRE[name]
            lesson_i=st.selectbox('📚 Chapitres accessibles',school_choices(review_i),
                                  format_func=lambda i:f'{i+1}. {chapters[i]["titre"]} '+('✓' if p['school'].get(school_key(review_i,i)) else ''),
                                  key=f'school_lesson_{review_i}')
            remaining=len(chapters)-len(school_choices(review_i))
            if remaining:st.caption(f'🔒 {remaining} chapitre(s) encore verrouillé(s) : réussite du précédent obligatoire.')
            lesson_panel(chapters[lesson_i],'school',school_key(review_i,lesson_i),
                         f'🇪🇸 {name} / {EQUIVALENCES[review_i]} · Leçon {lesson_i+1}/{len(chapters)}')
    with tabs[1]:
        st.subheader('🌍 Espagnol langue étrangère · A1 à C2')
        st.caption('Ces six niveaux sont des repères du CECRL indépendants de ta classe scolaire. Au lycée, les objectifs officiels diffèrent selon LVA/LVB/LVC et ne vont pas automatiquement jusqu’à C2. Ces ateliers ne valent pas certification.')
        col1,col2=st.columns([1,2.4],gap='medium')
        with col1:
            level=st.selectbox('Niveaux européens accessibles',unlocked_groups(p['cefr_exams'],list(CECRL)),key='cefr_level')
            st.caption(f'🔒 {len(CECRL)-len(unlocked_groups(p["cefr_exams"],list(CECRL)))} niveau(x) en attente d’un bilan réussi.')
            scope={'A1':'Débutant : comprendre et échanger très simplement','A2':'Élémentaire : situations courantes et récit simple',
                   'B1':'Intermédiaire : raconter, exprimer son opinion','B2':'Autonome : défendre ses idées et nuancer',
                   'C1':'Avancé : précision, implicite et style','C2':'Maîtrise approfondie : registre, littérature et argumentation'}
            st.info(scope[level])
            st.progress(cefr_completed(level)/len(CECRL[level]))
            st.caption(f'{cefr_completed(level)}/{len(CECRL[level])} ateliers validés')
        with col2:
            modules=CECRL[level]
            j=st.selectbox('Ateliers accessibles',cefr_choices(level),
                           format_func=lambda i:f'{i+1}. {modules[i]["titre"]} '+('✓' if p['cefr'].get(cefr_key(level,i)) else ''),
                           key=f'cefr_course_{level}')
            remaining=len(modules)-len(cefr_choices(level))
            if remaining:st.caption(f'🔒 {remaining} atelier(s) verrouillé(s) jusqu’à la validation du précédent.')
            lesson_panel(modules[j],'cefr',cefr_key(level,j),f'🌍 {level} · Atelier {j+1}/{len(modules)}')
    with tabs[2]:
        st.subheader('📐 Grammaire espagnole · A1 → C2')
        st.caption('24 règles en 6 niveaux. Chaque règle exige 1/1 ; le bilan (80 %) ouvre le niveau supérieur.')
        left,right=st.columns([1,2.4],gap='medium')
        with left:
            available=unlocked_groups(p['grammar_exams'],list(GRAMMAIRE))
            grammar_level=st.selectbox('Niveaux de grammaire accessibles',available,key='grammar_level')
            st.progress(grammar_completed(grammar_level)/len(GRAMMAIRE[grammar_level]))
            st.caption(f'{grammar_completed(grammar_level)}/{len(GRAMMAIRE[grammar_level])} règles validées')
            st.caption(f'🔒 {len(GRAMMAIRE)-len(available)} niveau(x) verrouillé(s)')
            with st.expander('📝 Bilan de grammaire · 80 %'):
                exam_form(GRAMMAIRE[grammar_level],'grammar',grammar_level)
        with right:
            grammar_modules=GRAMMAIRE[grammar_level]
            gi=st.selectbox('Règles accessibles',grammar_choices(grammar_level),
                            format_func=lambda i:f'{i+1}. {grammar_modules[i]["titre"]} '+('✓' if p['grammar'].get(grammar_key(grammar_level,i)) else ''),
                            key=f'grammar_course_{grammar_level}')
            locked=len(grammar_modules)-len(grammar_choices(grammar_level))
            if locked:st.caption(f'🔒 {locked} règle(s) bloquée(s) jusqu’à validation des précédentes.')
            lesson_panel(grammar_modules[gi],'grammar',grammar_key(grammar_level,gi),
                         f'📐 Grammaire {grammar_level} · Règle {gi+1}/{len(grammar_modules)}')
    with tabs[3]:
        st.subheader('🔤 Verbes & conjugaison · Apprendre, valider, débloquer')
        st.caption('18 verbes et 20 temps. **Pour débloquer la suite : 3/3 à chaque défi.** Aucun chronomètre et autant de tentatives que nécessaire.')
        part_verbs,part_tenses=st.tabs(['🗣️ Mes verbes','⏳ Mes temps de conjugaison'])
        with part_verbs:
            left,right=st.columns([1,2.4],gap='medium')
            with left:
                verb_indices=available_indices(p['verbs'],VERBS)
                selected_index=st.selectbox('Verbes accessibles',verb_indices,
                    format_func=lambda i:f'{i+1}. {VERBS[i]} '+('✓' if p['verbs'].get(VERBS[i]) else ''),key='verb_stage')
                verb=VERBS[selected_index]
                st.progress(sum(p['verbs'].get(v) is True for v in VERBS)/len(VERBS))
                st.caption(f'{sum(p["verbs"].get(v) is True for v in VERBS)}/{len(VERBS)} verbes maîtrisés')
                st.caption(f'🔒 {len(VERBS)-len(verb_indices)} verbe(s) à débloquer')
                st.info('Un verbe est acquis seulement après trois réponses correctes. Tu peux revoir tous ceux déjà maîtrisés.')
            with right:
                with st.container(border=True):
                    st.subheader(f'📖 {verb} · Indicatif présent')
                    st.table({'Pronom':PERSONS,'Forme':conjugate(verb,'presente')})
                    st.caption(f'Participe passé : {participle(verb)} · Gérondif : {gerund(verb)}')
                    if p['verbs'].get(verb):st.success('✅ Verbe validé. Tu peux le réviser.')
                    if quiz_forms(verb,'presente',f'verb_{verb}'):
                        award('verbs',verb,10)
                        award('conjugation',f'{verb}:presente',5)
        with part_tenses:
            mastered_verbs=[v for v in VERBS if p['verbs'].get(v) is True]
            if not mastered_verbs:
                st.info('🔒 Commence par réussir le défi du premier verbe « hablar » dans « Mes verbes » pour ouvrir la conjugaison.')
            else:
                left,right=st.columns([1,2.4],gap='medium')
                with left:
                    tense_keys=available_indices(p['tenses'],TENSE_ORDER)
                    ti=st.selectbox('Temps accessibles',tense_keys,
                        format_func=lambda i:f'{i+1}. {TENSES[TENSE_ORDER[i]][0]} '+('✓' if p['tenses'].get(TENSE_ORDER[i]) else ''),key='tense_stage')
                    tense=TENSE_ORDER[ti]
                    verb=st.selectbox('Verbes maîtrisés à utiliser',mastered_verbs,key='tense_verb')
                    st.progress(sum(p['tenses'].get(t) is True for t in TENSE_ORDER)/len(TENSE_ORDER))
                    st.caption(f'{sum(p["tenses"].get(t) is True for t in TENSE_ORDER)}/{len(TENSE_ORDER)} temps débloqués et validés')
                    st.caption(f'🔒 {len(TENSE_ORDER)-len(tense_keys)} temps encore verrouillé(s)')
                    st.info(f'**{TENSES[tense][0]}** · Repère {TENSES[tense][1]} : {TENSES[tense][2]}')
                with right:
                    with st.container(border=True):
                        st.subheader(f'⏳ {verb} · {TENSES[tense][0]}')
                        forms=conjugate(verb,tense)
                        persons=IMP_PERSONS if tense.startswith('imperativo_') else PERSONS
                        st.table({'Pronom':persons,'Conjugaison':forms})
                        if tense.startswith('subj_futuro') or tense=='preterito_anterior':
                            st.warning('Forme rare, historique, littéraire ou juridique : elle n’est pas courante dans la conversation.')
                        if p['tenses'].get(tense):st.success('✅ Temps déjà maîtrisé. Accessible pour révision.')
                        if quiz_forms(verb,tense,f'tense_{verb}_{tense}'):
                            award('tenses',tense,15)
                            award('conjugation',f'{verb}:{tense}',5)
    with tabs[4]:
        st.subheader('📖 Spécialité LLCER espagnol · Première et Terminale')
        st.caption('Parcours facultatif, distinct de l’espagnol du tronc commun. Références des listes officielles d’œuvres ; les questions portent sur des méthodes de lecture, pas sur le contenu intégral des œuvres.')
        phase = 'Première' if p['grade'] == CLASSES.index('Première') else 'Terminale'
        if p['grade'] < CLASSES.index('Première'):
            st.info('🔒 La bibliothèque de spécialité s’ouvre lorsque tu atteins la Première. Elle ne débloque pas les classes scolaires à elle seule.')
        else:
            choices = [x for x in LLCER if CLASSES.index(x) <= p['grade']]
            phase = st.selectbox('Année de spécialité accessible',choices,key='llcer_level')
            catalog = LLCER[phase]
            with st.container(border=True):
                st.caption('Œuvres du programme limitatif officiel · années scolaires '+catalog['periode'])
                st.write('Le programme prévoit un choix d’œuvres : cette bibliothèque **ne remplace pas leur lecture ou le visionnage des films**.')
                completed = [p['llcer'].get(phase+':'+str(i)) is True for i in range(len(catalog['oeuvres']))]
                indices = available_indices(p['llcer'],[phase+':'+str(i) for i in range(len(catalog['oeuvres']))])
                st.progress(sum(completed)/len(completed))
                st.caption(f'{sum(completed)}/{len(completed)} ateliers de méthode validés · les suivants sont verrouillés.')
                idx = st.selectbox('Œuvre à explorer',indices,
                    format_func=lambda i:('✓ ' if completed[i] else '🔓 ')+catalog['oeuvres'][i][1],key='llcer_work_'+phase)
                author,title,task = catalog['oeuvres'][idx]
                st.markdown(f'**{title}** — {author}')
                st.write('Mission guidée : '+task+'. Après lecture ou visionnage, relève un passage ou une scène significative et justifie ton interprétation.')
                with st.form('llcer_form_'+phase+'_'+str(idx)):
                    question_text, question_choices, expected = LLCER_EXERCICES[phase][idx]
                    answer = st.radio(question_text,question_choices,index=None,key='llcer_answer_'+phase+'_'+str(idx))
                    submit = st.form_submit_button('✅ Valider mon atelier de méthode')
                if submit:
                    if answer == expected:
                        award('llcer',phase+':'+str(idx),5)
                        st.success('Méthode validée : prochaine œuvre accessible. Cette validation ne certifie pas la lecture de l’œuvre.')
                    elif answer is None: st.warning('Choisis une réponse.')
                    else: st.warning('Révise la méthode : '+expected+'.')
    with tabs[5]:
        st.subheader('📝 Mes évaluations · Sans pression')
        st.caption('Ce sont des bilans de l’application, pas des examens ou certificats officiels. Recommencer est toujours possible tant que le seuil n’est pas atteint.')
        x,y=st.columns(2,gap='medium')
        with x:
            with st.container(border=True):
                st.markdown(f'#### 🎓 Passage en classe supérieure · {CLASSES[p["grade"]]}')
                current=p['grade']
                passed=exam_form(SCOLAIRE[CLASSES[current]],'school',str(current))
                if passed and current < len(CLASSES)-1:
                    if st.button(f'🎓 Passer en {CLASSES[current+1]}',type='primary',key=f'next_grade_{current}',use_container_width=True):
                        p['grade']+=1;persist();st.rerun()
                elif passed and current==len(CLASSES)-1:
                    st.success('🏆 Parcours scolaire achevé : Terminale !')
        with y:
            with st.container(border=True):
                st.markdown('#### 🌍 Bilan de niveau européen')
                exam_level=st.selectbox('Niveau à évaluer',unlocked_groups(p['cefr_exams'],list(CECRL)),key='cefr_exam_level')
                exam_form(CECRL[exam_level],'cefr',exam_level)
    with tabs[6]:
        st.subheader('📈 Ma progression scolaire')
        rows=[]
        for i,name in enumerate(CLASSES):
            done=school_completed(i)
            rows.append({'Classe':name,'Équivalent indicatif':EQUIVALENCES[i],
                         'Chapitres acquis':f'{done}/{len(SCOLAIRE[name])}',
                         'Bilan':'✓' if p['school_exams'].get(str(i)) else '—',
                         'Statut':'À venir' if i>p['grade'] else ('En cours' if i==p['grade'] else 'Révision')})
        st.dataframe(rows,use_container_width=True,hide_index=True)
        st.markdown('#### 🌍 CECRL · Parcours indépendant')
        c1,c2,c3=st.columns(3)
        for j,level in enumerate(CECRL):
            with [c1,c2,c3][j%3]:
                st.write(f'**{level}** · {cefr_completed(level)}/{len(CECRL[level])}')
                st.progress(cefr_completed(level)/len(CECRL[level]))
                st.caption('Bilan ✓' if p['cefr_exams'].get(level) else 'Bilan à valider')
        st.markdown('#### 📐 Grammaire, verbes & temps')
        st.write('Grammaire : '+str(sum(grammar_completed(level) for level in GRAMMAIRE))+'/24 chapitres ; '
                 +str(sum(p['grammar_exams'].get(level) is True for level in GRAMMAIRE))+'/6 bilans réussis')
        c4,c5=st.columns(2)
        c4.metric('Verbes maîtrisés',f'{sum(p["verbs"].get(v) is True for v in VERBS)}/18')
        c5.metric('Temps maîtrisés',f'{sum(p["tenses"].get(t) is True for t in TENSE_ORDER)}/20')
        st.metric('Défis verbe × temps réussis',len([v for v in p['conjugation'].values() if v is True]))
    with tabs[7]:
        st.subheader('💾 Ma sauvegarde et mon carnet')
        st.caption('Les progrès sont conservés automatiquement pendant la session. Sur Streamlit Cloud, exporte ton profil en JSON pour ne pas le perdre après un redémarrage.')
        note_name=f'school_{p["grade"]}'
        note=st.text_area('✏️ Mes phrases espagnoles',value=p['notes'].get(note_name,''),height=135,key='notes_'+note_name)
        if st.button('Enregistrer mes notes',key='save_note_school'):
            p['notes'][note_name]=note;persist();st.success('Notes enregistrées dans la session.')
        st.markdown('#### Sources pédagogiques de référence')
        st.info('📚 Double référence : programmes français **d’espagnol langue vivante** (BO 2025–2026) et progression de langue **maternelle espagnole** inspirée de la LOMLOE. Ces deux cursus ne sont pas identiques. Le parcours n’est pas un enseignement officiel ou diplômant.')
        st.caption('École primaire : nouveaux textes 2026 appliqués progressivement (CP/CM1 en 2026, CE1/CE2/CM2 en 2027). Collège : 6e 2025, 5e 2026, 4e 2027, 3e 2028. Lycée : seconde 2025 et première/terminale 2026.')
        for name,url in SOURCES:st.markdown(f'- [{name}]({url})')
else:
    teacher='Lena' if track=='german' else 'Giulia'
    language='allemand' if track=='german' else 'italien'
    ix=1 if track=='german' else 2
    complete=sum(bool(p[track].get(str(i))) for i in range(len(MISSIONS)))
    st.subheader(f'🌍 {language.capitalize()} · Survie A1++ avec {teacher}')
    st.caption('« A1++ » est notre nom pour un A1 renforcé, non un niveau officiel du CECRL. Ici, seuls les usages de voyage sont travaillés.')
    l,r=st.columns([1,2.5],gap='medium')
    with l:
        with st.container(border=True):
            st.metric('Missions réalisées',f'{complete}/{len(MISSIONS)}')
            st.progress(complete/len(MISSIONS))
            st.write(f'👩‍🏫 **{teacher}** t’accompagne dans dix situations réelles.')
            st.caption('Progression indépendante de l’espagnol. Aucun horaire ni date limite.')
    with r:
        i=st.selectbox('Missions accessibles',available_indices(p[track],[str(j) for j in range(len(MISSIONS))]),
                       format_func=lambda j:f'{j+1}. {MISSIONS[j][0]} '+('✓' if p[track].get(str(j)) else ''),key=f'mission_{track}')
        locked_missions=len(MISSIONS)-len(available_indices(p[track],[str(j) for j in range(len(MISSIONS))]))
        if locked_missions:st.caption(f'🔒 {locked_missions} mission(s) verrouillée(s) : réussis la mission précédente.')
        title,description,phrase1,phrase2=MISSIONS[i]
        with st.container(border=True):
            st.subheader(title)
            st.write(description)
            st.info(f'👩‍🏫 {teacher} : « Écoute intérieurement, répète puis retrouve la bonne expression. »')
            for words in (phrase1,phrase2):
                st.markdown(f'**{words[ix]}**')
                st.caption('🇫🇷 '+words[0])
            with st.form(f'mission_form_{track}_{i}'):
                ans=st.radio(f'Comment dire « {phrase1[0]} » ?', [phrase1[ix],phrase2[ix],'Je ne sais pas'],
                             index=None,key=f'mission_answer_{track}_{i}')
                submit=st.form_submit_button('Valider ma mission',type='primary')
            if submit:
                if ans==phrase1[ix]:award(track,str(i));st.success('🎉 Mission validée !')
                elif ans is None:st.warning('Choisis une réponse.')
                else:st.info(f'Bonne expression : {phrase1[ix]}. Réessaie !')
            if p[track].get(str(i)):st.success('✓ Mission acquise')
    if complete==len(MISSIONS):st.success('🏆 Toutes les missions de survie sont terminées ! Tu peux continuer à les réviser.')
    with st.expander('✏️ Mon carnet de voyage'):
        note=st.text_area('Mes expressions personnelles',value=p['notes'].get(track,''),key='notes_'+track)
        if st.button('Sauvegarder mes expressions',key='save_'+track):
            p['notes'][track]=note;persist();st.success('Carnet enregistré dans la session.')

st.divider()
with st.expander('💾 Exporter / importer mon profil · important pour Streamlit Cloud'):
    st.download_button('⬇️ Exporter ma progression en JSON',
        data=json.dumps(p,ensure_ascii=False,indent=2),
        file_name='mi_espanol_progression_v5.json',mime='application/json',
        use_container_width=True,key='download_profile')
    upload=st.file_uploader('Importer une sauvegarde V2, V3, V4 ou V5 (JSON)',type=['json'],key='upload_profile')
    if upload is not None and st.button('📂 Restaurer mon profil',key='restore_profile'):
        try:
            if upload.size>2_000_000:raise ValueError('Fichier supérieur à 2 Mo')
            raw=json.loads(upload.getvalue().decode('utf-8'))
            if not isinstance(raw,dict) or not any(k in raw for k in ('grade','spanish','school','cefr','grammar','verbs','tenses','german','italian','llcer')):
                raise ValueError('Format de sauvegarde non reconnu')
            st.session_state.profile=normalize(raw)
            p=st.session_state.profile
            persist()
            st.success('Profil restauré, y compris les missions d’allemand et d’italien de V2.')
            st.rerun()
        except (UnicodeError,ValueError,TypeError) as exc:st.error(f'Impossible de restaurer ce fichier : {exc}')
    st.caption('La sauvegarde JSON est personnelle. Ne la publie pas sur GitHub. En local privé, une sauvegarde automatique sur disque peut être activée via MI_ESPANOL_LOCAL_SAVE=1.')
st.caption('Mi Español · V5 · progression verrouillée · 104 leçons scolaires dont 56 ateliers liés aux programmes français · 30 ateliers CECRL · 24 règles de grammaire · 18 verbes · 20 temps · 20 missions de survie.')
