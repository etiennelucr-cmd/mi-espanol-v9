"""Mi Español - école virtuelle, espagnol natif CP-Terminale + CECRL + langues de survie."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
import streamlit as st
from programme import CLASSES, EQUIVALENCES, SCOLAIRE, CECRL, SOURCES, validate
from conjugaison import PERSONS, IMP_PERSONS, VERBS, TENSES, conjugate, participle, gerund

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
    return {'version':3,'name':'Élève','grade':0,'school':{},'school_exams':{},
            'cefr':{},'cefr_exams':{},'conjugation':{},'german':{},'italian':{},
            'notes':{},'stars':0,'legacy_spanish':{}}


def normalize(raw):
    default = new_profile()
    if not isinstance(raw,dict): return default
    for key in default:
        if key in raw and isinstance(raw[key],type(default[key])):
            default[key] = raw[key]
    # V2 : on conserve les deux langues de survie, les notes et les étoiles.
    if isinstance(raw.get('spanish'),dict) and not default['legacy_spanish']:
        default['legacy_spanish'] = raw['spanish']
    default['grade'] = max(0,min(len(CLASSES)-1,default['grade']))
    default['stars'] = max(0,default['stars'])
    default['version'] = 3
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
def school_completed(i):return sum(bool(p['school'].get(school_key(i,j))) for j in range(len(SCOLAIRE[CLASSES[i]])))
def cefr_completed(level):return sum(bool(p['cefr'].get(cefr_key(level,j))) for j in range(len(CECRL[level])))

def lesson_panel(lesson,bucket,key,label):
    with st.container(border=True):
        st.caption(label)
        st.subheader(lesson['titre'])
        st.markdown('#### 📌 La règle à retenir')
        st.write(lesson['notion'])
        st.markdown('#### 💬 Exemples espagnols')
        st.info(lesson['exemples'])
        st.markdown('#### 📖 Lis et comprends')
        st.markdown(f'> {lesson["texte"]}')
        st.markdown('#### ✍️ À toi de jouer')
        st.write(lesson['mission'])
        st.caption('L’activité d’écriture est libre : le QCM ci-dessous est le seul exercice corrigé automatiquement.')
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
                st.success('¡Excelente! Bonne réponse : '+lesson['reponse'])
                st.balloons() if bucket=='school' and school_completed(p['grade'])==len(SCOLAIRE[CLASSES[p['grade']]]) else None
            else:
                st.error('Pas encore : la bonne réponse est « '+lesson['reponse']+' ». Relis la règle et réessaie.')
        with st.expander('🔎 Réviser la notion et les exemples'):
            st.write(lesson['notion'])
            st.write('**Exemples :** '+lesson['exemples'])


def exam_form(lessons,bucket,group):
    """QCM récapitulatif avec nouvelles réponses à soumettre en une fois."""
    exam_bucket = 'school_exams' if bucket=='school' else 'cefr_exams'
    exam_key = str(group)
    if p[exam_bucket].get(exam_key):
        st.success('🏅 Évaluation de ce niveau déjà validée !')
        return True
    needed = len(lessons)
    done = school_completed(int(group)) if bucket=='school' else cefr_completed(group)
    if done < needed:
        st.info(f'Commence par valider les {needed} leçons de ce niveau ({done}/{needed}). Tu peux les refaire autant de fois que tu veux.')
        return False
    st.write('**Évaluation finale** · 4 ou 5 questions, sans chronomètre. Il faut au moins 75 % de bonnes réponses pour valider.')
    with st.form('exam_form_'+bucket+'_'+exam_key):
        answers=[]
        for i,l in enumerate(lessons):
            answers.append(st.radio(f'{i+1}. {l["question"]}',l['choix'],index=None,key=f'exam_answer_{bucket}_{exam_key}_{i}'))
        submit=st.form_submit_button('📝 Corriger mon évaluation',type='primary',use_container_width=True)
    if submit:
        score=sum(a==l['reponse'] for a,l in zip(answers,lessons))
        threshold=(3*needed+3)//4  # ceil(0.75*n)
        st.write(f'**Résultat : {score}/{needed}** · seuil : {threshold}/{needed}')
        for i,(a,l) in enumerate(zip(answers,lessons)):
            if a!=l['reponse']:
                st.caption(f'Question {i+1} : bonne réponse « {l["reponse"]} ».')
        if score>=threshold:
            award(exam_bucket,exam_key,20)
            st.success('🎉 Évaluation validée ! Tu peux poursuivre ton parcours.')
            return True
        st.warning('Révise les points manqués et retente l’évaluation quand tu veux.')
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
    tabs=st.tabs(['🏫 Mon école','🌍 Niveaux A1–C2','🔤 Conjugaison','📝 Évaluations','📈 Mon parcours','💾 Profil & sources'])
    with tabs[0]:
        left,right=st.columns([1,2.4],gap='medium')
        with left:
            with st.container(border=True):
                st.subheader('🎒 Ma classe avec Sofía')
                st.write('Tu progresses du **CP à la Terminale**, à ton rythme, en travaillant la langue comme dans une classe en Espagne.')
                review_i=st.selectbox('Choisir une classe accessible',list(range(p['grade']+1)),
                                      format_func=lambda i:f'{CLASSES[i]} · {EQUIVALENCES[i]}',
                                      index=p['grade'],key=f'school_choice_{p["grade"]}')
                name=CLASSES[review_i]
                done=school_completed(review_i)
                st.progress(done/len(SCOLAIRE[name]))
                st.caption(f'{done}/{len(SCOLAIRE[name])} chapitres validés')
                st.write('**Méthode :** lire la règle → observer les exemples → comprendre le texte → répondre au QCM → produire un court écrit.')
                st.caption('Aucun cours bloqué par le calendrier. Les anciennes classes restent disponibles pour révision.')
        with right:
            chapters=SCOLAIRE[name]
            lesson_i=st.selectbox('📚 Choisis ton chapitre',range(len(chapters)),
                                  format_func=lambda i:f'{i+1}. {chapters[i]["titre"]} '+('✓' if p['school'].get(school_key(review_i,i)) else ''),
                                  key=f'school_lesson_{review_i}')
            lesson_panel(chapters[lesson_i],'school',school_key(review_i,lesson_i),
                         f'🇪🇸 {name} / {EQUIVALENCES[review_i]} · Leçon {lesson_i+1}/{len(chapters)}')
    with tabs[1]:
        st.subheader('🌍 Espagnol langue étrangère · A1 à C2')
        st.caption('Ces six niveaux sont des repères du CECRL. Ils sont indépendants de ta classe scolaire et ne valent pas certification officielle.')
        col1,col2=st.columns([1,2.4],gap='medium')
        with col1:
            level=st.selectbox('Niveau européen',list(CECRL),key='cefr_level')
            scope={'A1':'Débutant : comprendre et échanger très simplement','A2':'Élémentaire : situations courantes et récit simple',
                   'B1':'Intermédiaire : raconter, exprimer son opinion','B2':'Autonome : défendre ses idées et nuancer',
                   'C1':'Avancé : précision, implicite et style','C2':'Maîtrise approfondie : registre, littérature et argumentation'}
            st.info(scope[level])
            st.progress(cefr_completed(level)/len(CECRL[level]))
            st.caption(f'{cefr_completed(level)}/{len(CECRL[level])} ateliers validés')
        with col2:
            modules=CECRL[level]
            j=st.selectbox('Choisir un atelier',range(len(modules)),
                           format_func=lambda i:f'{i+1}. {modules[i]["titre"]} '+('✓' if p['cefr'].get(cefr_key(level,i)) else ''),
                           key=f'cefr_course_{level}')
            lesson_panel(modules[j],'cefr',cefr_key(level,j),f'🌍 {level} · Atelier {j+1}/{len(modules)}')
    with tabs[2]:
        st.subheader('🔤 Atelier de conjugaison espagnole')
        st.write('18 verbes, **20 temps et formes**, tous les modes : indicatif, subjonctif, impératif. Les constructions archaïques sont signalées.')
        c1,c2=st.columns(2)
        with c1:verb=st.selectbox('Choisir un verbe',VERBS,key='verb')
        with c2:tense=st.selectbox('Choisir un temps / mode',list(TENSES),format_func=lambda t:TENSES[t][0],key='tense')
        label,cefr_hint,usage=TENSES[tense]
        st.info(f'**{label}** · Repère pédagogique {cefr_hint}. {usage}')
        forms=conjugate(verb,tense)
        persons=IMP_PERSONS if tense.startswith('imperativo_') else PERSONS
        tleft,tright=st.columns([1.25,1])
        with tleft:
            st.markdown(f'#### 📖 {verb} · {label}')
            st.table({'Pronom':persons,'Conjugaison':forms})
            st.caption(f'Participe passé : {participle(verb)} · Gérondif : {gerund(verb)}')
            if tense.startswith('subj_futuro') or tense=='preterito_anterior':
                st.warning('Cette forme est rare en espagnol contemporain et principalement historique, littéraire ou juridique.')
            if verb=='haber':st.caption('« Haber » a aussi un emploi impersonnel : hay, había, hubo, habrá…')
            if tense=='imperativo_afirmativo':st.caption('Impératif : pas de première personne du singulier. Certaines formes sont très peu employées.')
        with tright:
            with st.container(border=True):
                st.subheader('🎯 Défi de conjugaison')
                st.caption('Trois questions, sans chronomètre et sans pénalité.')
                ids=[0,2,5] if len(forms)==6 else ([1,2,4] if forms[0].startswith('—') else [0,2,4])
                with st.form(f'conj_quiz_{verb}_{tense}'):
                    answers=[]
                    for idx in ids:
                        good=forms[idx]
                        alternatives=[f for f in forms if f!=good and not f.startswith('—')]
                        # Mélange déterministe des options, sans dépendance externe.
                        alternatives=list(dict.fromkeys(alternatives))
                        choices=sorted(set([good]+alternatives[:2]),key=lambda s:s.casefold())
                        answers.append(st.radio(f'{persons[idx]} → ?',choices,index=None,key=f'conj_ans_{verb}_{tense}_{idx}'))
                    submitted=st.form_submit_button('Corriger le défi',type='primary',use_container_width=True)
                if submitted:
                    score=sum(got==forms[idx] for got,idx in zip(answers,ids))
                    if score==3:
                        award('conjugation',f'{verb}:{tense}',10)
                        st.success('🎉 3/3 ! Défi maîtrisé (+10 étoiles la première fois).')
                    else:
                        st.info(f'{score}/3. Réessaie : tes erreurs ne retirent aucune étoile.')
                        for got,idx in zip(answers,ids):
                            if got!=forms[idx]:st.caption(f'{persons[idx]} : {forms[idx]}')
                if p['conjugation'].get(f'{verb}:{tense}'):
                    st.success('✓ Défi déjà validé')
                st.caption('Les tableaux correspondent au modèle de conjugaison choisi. Les usages régionaux sont parfois différents.')
    with tabs[3]:
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
                exam_level=st.selectbox('Niveau à évaluer',list(CECRL),key='cefr_exam_level')
                exam_form(CECRL[exam_level],'cefr',exam_level)
    with tabs[4]:
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
        st.metric('Défis de conjugaison maîtrisés',len([v for v in p['conjugation'].values() if v is True]))
    with tabs[5]:
        st.subheader('💾 Ma sauvegarde et mon carnet')
        st.caption('Les progrès sont conservés automatiquement pendant la session. Sur Streamlit Cloud, exporte ton profil en JSON pour ne pas le perdre après un redémarrage.')
        note_name=f'school_{p["grade"]}'
        note=st.text_area('✏️ Mes phrases espagnoles',value=p['notes'].get(note_name,''),height=135,key='notes_'+note_name)
        if st.button('Enregistrer mes notes',key='save_note_school'):
            p['notes'][note_name]=note;persist();st.success('Notes enregistrées dans la session.')
        st.markdown('#### Sources pédagogiques de référence')
        st.caption('Leçons originales inspirées des domaines de travail du PCIC et du curriculum espagnol LOMLOE ; ni reproduction de manuels officiels ni validation du niveau CECRL.')
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
        i=st.selectbox('Choisir une mission de survie',range(len(MISSIONS)),
                       format_func=lambda j:f'{j+1}. {MISSIONS[j][0]} '+('✓' if p[track].get(str(j)) else ''),key=f'mission_{track}')
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
        file_name='mi_espanol_progression_v3.json',mime='application/json',
        use_container_width=True,key='download_profile')
    upload=st.file_uploader('Importer une sauvegarde V2 ou V3 (JSON)',type=['json'],key='upload_profile')
    if upload is not None and st.button('📂 Restaurer mon profil',key='restore_profile'):
        try:
            if upload.size>2_000_000:raise ValueError('Fichier supérieur à 2 Mo')
            raw=json.loads(upload.getvalue().decode('utf-8'))
            if not isinstance(raw,dict) or not any(k in raw for k in ('grade','spanish','school','cefr','german','italian')):
                raise ValueError('Format de sauvegarde non reconnu')
            st.session_state.profile=normalize(raw)
            p=st.session_state.profile
            persist()
            st.success('Profil restauré, y compris les missions d’allemand et d’italien de V2.')
            st.rerun()
        except (UnicodeError,ValueError,TypeError) as exc:st.error(f'Impossible de restaurer ce fichier : {exc}')
    st.caption('La sauvegarde JSON est personnelle. Ne la publie pas sur GitHub. En local privé, une sauvegarde automatique sur disque peut être activée via MI_ESPANOL_LOCAL_SAVE=1.')
st.caption('Mi Español · V3 · 48 leçons scolaires · 30 ateliers CECRL · 18 verbes / 20 temps · 20 missions de survie · contenus pédagogiques d’initiation, sans certification officielle.')
