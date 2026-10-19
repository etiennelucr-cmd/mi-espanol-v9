"""Entraînement durable V16 : préférences Supabase, aucune table nouvelle."""
import json,random,re,unicodedata,html
from datetime import date,timedelta,datetime
from zoneinfo import ZoneInfo
import streamlit as st
import streamlit.components.v1 as components
import moteur as m
import exercices_v11 as ev
import planning_adaptatif as planning

SAINTS={(10,18):"Saint Luc",(10,19):"Saint René",(10,20):"Sainte Adeline",
(1,1):"Sainte Marie",(2,14):"Saint Valentin",(3,19):"Saint Joseph",
(4,23):"Saint Georges",(5,1):"Saint Joseph travailleur",(6,24):"Saint Jean-Baptiste",
(7,14):"Saint Camille",(8,15):"Sainte Marie",(9,29):"Saint Michel",
(11,1):"Toussaint",(12,25):"Noël"}
MOIS=['','janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
JOURS=['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']

def entete():
    now=datetime.now(ZoneInfo('Europe/Paris'))
    saint=SAINTS.get((now.month,now.day),'Saint du jour non renseigné')
    st.markdown("""<style>
    .v16brand{background:linear-gradient(115deg,#ffffff,#fff2dc);border:1px solid #f2dfc7;border-radius:14px;padding:13px 11px;margin-bottom:8px}
    .v16brand .v16name{font-size:1.35rem;font-weight:800;color:#13264b}
    .v16brand .v16flag{font-size:2rem;vertical-align:middle;margin-right:7px}
    .v16brand .v16saint{color:#a36d12;font-size:.88rem;margin-top:4px}
    </style>""",unsafe_allow_html=True)
    st.markdown('<div class="v16brand"><span class="v16flag">🇪🇸</span><span class="v16name">Mi Español V16</span><div class="v16saint">📅 '
                +html.escape(f'{JOURS[now.weekday()]} {now.day} {MOIS[now.month]} {now.year}')
                +' · '+html.escape(saint)+'</div></div>',unsafe_allow_html=True)
    # Horloge locale mise à jour sans relancer l'application.
    components.html("""<div id="h" style="font:600 18px system-ui;color:#bc2941;padding:0 2px">--:--</div>
    <script>function tick(){document.getElementById('h').textContent='🕒 '+new Intl.DateTimeFormat('fr-FR',{timeZone:'Europe/Paris',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date());}tick();setInterval(tick,1000);</script>""",height=33)

def _key(n):return 'v16_srs_'+n
def _load(n):
    try:return json.loads(m.preference(_key(n),'{}'))
    except (ValueError,TypeError):return {}
def _save(n,data):m.definir_preference(_key(n),json.dumps(data,ensure_ascii=False))
def _norm(s):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(s).lower()) if (unicodedata.category(c)!='Mn' and c.isalnum()) or c.isspace()).split())
def _items(n):
    theme,temps,i,j=planning.priorites(n)
    lessons=m.COURS.get(n,[])
    if not lessons:return []
    lesson=lessons[i if i is not None else 0]
    pairs=ev._phrases_sources(lesson,n)
    return [{'id':f"{lesson['id']}:{k}",'fr':fr,'es':es,'theme':lesson['titre']} for k,(fr,es,kind) in enumerate(pairs)]
def _due(item,state,today):
    return state.get(item['id'],{}).get('due','0000-01-01')<=today
def _record(n,item,correct):
    data=_load(n); old=data.get(item['id'],{})
    streak=(old.get('streak',0)+1) if correct else 0
    interval=min(60,[1,3,7,14,30,60][min(streak-1,5)]) if correct else 1
    data[item['id']]={'streak':streak,'interval':interval,'due':(date.today()+timedelta(days=interval)).isoformat(),
                      'attempts':old.get('attempts',0)+1,'correct':old.get('correct',0)+int(correct),
                      'last':date.today().isoformat(),'theme':item['theme']}
    _save(n,data)

def repetition(n):
    st.title('🧠 Répétition espacée')
    st.caption('Les phrases reviennent après 1, 3, 7, 14, 30 puis 60 jours de réussites consécutives. Une erreur réinitialise le cycle.')
    items=_items(n); data=_load(n); today=date.today().isoformat()
    due=[x for x in items if _due(x,data,today)]
    st.metric('Phrases à revoir aujourd’hui',len(due))
    if not due:st.success('Aucune phrase à revoir aujourd’hui pour le thème prioritaire.');return
    key='v16_review_'+n
    if key not in st.session_state or st.session_state[key] not in [x['id'] for x in due]:
        st.session_state[key]=random.choice(due)['id']
    item=next(x for x in due if x['id']==st.session_state[key])
    st.info('Traduis en espagnol : '+item['fr'])
    with st.form('v16_srs_form_'+n):
        response=st.text_input('Ta traduction',key='v16_srs_answer_'+item['id'])
        submit=st.form_submit_button('Corriger et enregistrer')
    if submit:
        correct=_norm(response)==_norm(item['es'])
        _record(n,item,correct)
        if correct:st.success('Bonne réponse !')
        else:st.warning('Réponse attendue : '+item['es'])
        st.caption('Correction automatique stricte : une traduction équivalente peut être refusée.')
        st.session_state.pop(key,None)
        st.button('Phrase suivante',on_click=st.rerun)

DIALOGUES={
 'Restaurant':[('Hola, ¿tiene una mesa para dos?', 'Demande une table pour deux personnes.'),
               ('¿Qué desea beber?', 'Commande une boisson en espagnol.'),
               ('¿Qué desea comer?', 'Commande un plat en espagnol.'),
               ('¿Desea algo más?', 'Réponds poliment à cette question.')],
 'Hôtel':[('Buenas tardes, ¿tiene una reserva?', 'Indique que tu as une réservation.'),
          ('¿A nombre de quién?', 'Donne un nom pour la réservation.'),
          ('¿Cuántas noches se queda?', 'Précise la durée du séjour.'),
          ('Aquí tiene su llave.', 'Remercie la réception.')],
 'Se présenter':[('¡Hola! ¿Cómo te llamas?', 'Présente-toi.'),
                 ('¿De dónde eres?', 'Dis ton pays d’origine.'),
                 ('¿Dónde vives?', 'Indique où tu habites.'),
                 ('¿Qué te gusta hacer?', 'Parle de tes loisirs.')]}
def conversation(n):
    st.title('💬 Conversations guidées')
    st.caption('Dialogue écrit avec mises en situation et conseils. Ce module ne prétend pas être une conversation IA libre.')
    scene=st.selectbox('Situation',list(DIALOGUES))
    questions=DIALOGUES[scene]
    key='v16_conv_'+n+'_'+scene
    if key not in st.session_state:st.session_state[key]=[]
    history=st.session_state[key]
    for idx,answer in enumerate(history):
        st.chat_message('assistant').write(questions[idx][0])
        st.chat_message('user').write(answer)
    if len(history)<len(questions):
        prompt,tip=questions[len(history)]
        st.chat_message('assistant').write(prompt)
        with st.form('v16_conv_form'):
            answer=st.text_input('Ta réponse en espagnol')
            submitted=st.form_submit_button('Envoyer')
        if submitted and answer.strip():
            st.session_state[key]=history+[answer.strip()]
            st.rerun()
        with st.expander('Aide pour répondre'):st.write(tip)
    else:
        st.success('Dialogue terminé !')
        st.caption('Relis tes réponses : cette version ne vérifie pas automatiquement la grammaire.')
        if st.button('Recommencer'):st.session_state[key]=[];st.rerun()

def maitrise(n):
    st.title('📈 Maîtrise durable')
    st.caption('Indicateur distinct de la progression officielle des thèmes. Une phrase est considérée durablement maîtrisée après au moins 3 réussites consécutives espacées.')
    items=_items(n); data=_load(n)
    mastered=sum(data.get(x['id'],{}).get('streak',0)>=3 for x in items)
    total=len(items)
    st.metric('Phrases maîtrisées durablement',f'{mastered} / {total}')
    st.progress(mastered/total if total else 0)
    st.caption('Ne modifie pas le pourcentage de thèmes validés affiché dans la barre latérale.')
    if total:st.write('Thème suivi : '+items[0]['theme'])
