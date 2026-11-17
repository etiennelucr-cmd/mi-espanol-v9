"""V91: deux parcours scolaires, sans API payante."""
import calendar
import html
from datetime import date, timedelta
import streamlit as st
import rencontres_v63 as social
import social_v80 as db
import academia_v84 as academy

LANGS={'🇪🇸 Espagnol':'es','🇬🇧 Anglais':'en','🇩🇪 Allemand':'de','🇮🇹 Italien':'it'}
THEMES=['Bases vitales','Restaurant et allergies','Transports et orientation','Hôtel et logement','Achats et communication','Santé et urgences','Grand défi de survie']
PHRASES={
'en':[
 [('Hello!','Bonjour !'),('I do not understand.','Je ne comprends pas.'),('Could you speak slowly, please?','Pouvez-vous parler lentement ?')],
 [('I would like some water, please.','Je voudrais de l’eau.'),('I am allergic to nuts.','Je suis allergique aux fruits à coque.'),('Could I have the bill, please?','L’addition, s’il vous plaît.')],
 [('Where is the station?','Où est la gare ?'),('Which platform?','Quel quai ?'),('My train is delayed.','Mon train est retardé.')],
 [('I have a reservation.','J’ai une réservation.'),('The room key does not work.','La clé ne fonctionne pas.'),('What is the Wi-Fi password?','Quel est le mot de passe Wi-Fi ?')],
 [('How much is it?','Combien ça coûte ?'),('Can I pay by card?','Puis-je payer par carte ?'),('Where is the bathroom?','Où sont les toilettes ?')],
 [('I need a doctor.','J’ai besoin d’un médecin.'),('Please call an ambulance.','Appelez une ambulance, s’il vous plaît.'),('I lost my passport.','J’ai perdu mon passeport.')],
 [('I need help.','J’ai besoin d’aide.'),('Could you repeat, please?','Pouvez-vous répéter ?'),('Where can I buy a ticket?','Où acheter un billet ?')]],
'de':[
 [('Guten Tag!','Bonjour !'),('Ich verstehe nicht.','Je ne comprends pas.'),('Können Sie bitte langsamer sprechen?','Pouvez-vous parler plus lentement ?')],
 [('Ich möchte Wasser, bitte.','Je voudrais de l’eau.'),('Ich bin allergisch gegen Nüsse.','Je suis allergique aux fruits à coque.'),('Die Rechnung, bitte.','L’addition, s’il vous plaît.')],
 [('Wo ist der Bahnhof?','Où est la gare ?'),('Welches Gleis?','Quel quai ?'),('Mein Zug hat Verspätung.','Mon train est retardé.')],
 [('Ich habe eine Reservierung.','J’ai une réservation.'),('Der Zimmerschlüssel funktioniert nicht.','La clé ne fonctionne pas.'),('Wie lautet das WLAN-Passwort?','Quel est le mot de passe Wi-Fi ?')],
 [('Wie viel kostet das?','Combien ça coûte ?'),('Kann ich mit Karte bezahlen?','Puis-je payer par carte ?'),('Wo ist die Toilette?','Où sont les toilettes ?')],
 [('Ich brauche einen Arzt.','J’ai besoin d’un médecin.'),('Rufen Sie bitte einen Krankenwagen.','Appelez une ambulance.'),('Ich habe meinen Pass verloren.','J’ai perdu mon passeport.')],
 [('Ich brauche Hilfe.','J’ai besoin d’aide.'),('Können Sie das bitte wiederholen?','Pouvez-vous répéter ?'),('Wo kann ich eine Fahrkarte kaufen?','Où acheter un billet ?')]],
'it':[
 [('Buongiorno!','Bonjour !'),('Non capisco.','Je ne comprends pas.'),('Può parlare più lentamente, per favore?','Pouvez-vous parler plus lentement ?')],
 [('Vorrei dell’acqua, per favore.','Je voudrais de l’eau.'),('Sono allergico alle noci.','Je suis allergique aux fruits à coque (forme masculine).'),('Il conto, per favore.','L’addition, s’il vous plaît.')],
 [('Dov’è la stazione?','Où est la gare ?'),('Quale binario?','Quel quai ?'),('Il mio treno è in ritardo.','Mon train est retardé.')],
 [('Ho una prenotazione.','J’ai une réservation.'),('La chiave della camera non funziona.','La clé ne fonctionne pas.'),('Qual è la password del Wi-Fi?','Quel est le mot de passe Wi-Fi ?')],
 [('Quanto costa?','Combien ça coûte ?'),('Posso pagare con la carta?','Puis-je payer par carte ?'),('Dov’è il bagno?','Où sont les toilettes ?')],
 [('Ho bisogno di un medico.','J’ai besoin d’un médecin.'),('Chiami un’ambulanza, per favore.','Appelez une ambulance.'),('Ho perso il passaporto.','J’ai perdu mon passeport.')],
 [('Ho bisogno di aiuto.','J’ai besoin d’aide.'),('Può ripetere, per favore?','Pouvez-vous répéter ?'),('Dove posso comprare un biglietto?','Où acheter un billet ?')]]}

def _easter(y):
 a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3;h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451;mo=(h+l-7*m+114)//31;day=(h+l-7*m+114)%31+1
 return date(y,mo,day)
def _holiday(day):
 y=day.year;e=_easter(y)
 return day in {date(y,m,d) for m,d in [(1,1),(5,1),(5,8),(7,14),(8,15),(11,1),(11,11),(12,25)]} | {e+timedelta(days=n) for n in [1,39,50]}
def _breaks(text):
 out=[]
 for line in text.splitlines():
  try:
   a,b=[date.fromisoformat(s.strip()) for s in line.split(';',1)]
   if a<=b:out.append((a,b))
  except (ValueError,TypeError):pass
 return out
def _schoolday(day,breaks):return day.weekday()<5 and not _holiday(day) and not any(a<=day<=b for a,b in breaks)
def _nth_day(start,n,breaks):
 cur=start;count=0
 for _ in range(3000):
  if _schoolday(cur,breaks):
   if count==n:return cur
   count+=1
  cur+=timedelta(days=1)
 return cur

def _save(world):
 profile=st.session_state.get('v80_profile')
 if profile and db.db_enabled():
  try:db.save(profile,world);return True
  except Exception:return False
 return False

def _visual_timetable(school, breaks):
 """Grille hebdomadaire illustrative liée au calendrier réel de la scolarité."""
 st.markdown("""<style>
 .v94-grid{display:grid;grid-template-columns:42px repeat(5,minmax(95px,1fr));gap:4px;overflow-x:auto;min-width:580px}
 .v94-cell{background:#f6f8ff;border:1px solid #dae5ff;min-height:47px;padding:5px;border-radius:7px;font-size:12px}
 .v94-head{background:#dbe9ff;text-align:center;font-weight:750;min-height:38px}
 .v94-slot{color:white;border-radius:8px;padding:7px;font-size:12px;line-height:1.3;box-shadow:0 2px 4px #0001}
 .v94-wrap{overflow-x:auto;border-radius:17px;background:white;padding:10px}
 </style>""",unsafe_allow_html=True)
 st.markdown('### 📅 Mon emploi du temps interactif')
 start=date.fromisoformat(school['start'])
 offset=st.session_state.get('v94_week_offset',0)
 monday=date.today()-timedelta(days=date.today().weekday())+timedelta(weeks=offset)
 a,b,c=st.columns([1,3,1])
 with a:
  if st.button('◀ Semaine précédente',key='v94_prev'):st.session_state.v94_week_offset=offset-1;st.rerun()
 with b:st.markdown(f'**{monday:%d/%m/%Y} — {monday+timedelta(days=4):%d/%m/%Y}**')
 with c:
  if st.button('Suivante ▶',key='v94_next'):st.session_state.v94_week_offset=offset+1;st.rerun()
 view=st.segmented_control('Affichage',['Jour','Semaine','Mois'],default='Semaine',key='v94_view')
 subjects=['📘 Espagnol','📚 Vocabulaire','✏️ Grammaire','🎧 Compréhension','🏛️ Culture','🎯 Exercices']
 colors=['#0867e9','#ff7900','#09a73e','#8b25d4','#f23871','#e8b400']
 filters=st.multiselect('Mes matières',subjects,default=subjects,key='v94_subjects')
 names=[('Présentations et salutations','Ser y estar','Dialogue au café'),('La famille','Parler de son quotidien','Révision et pratique'),('La vie en Espagne','Les adjectifs','Décrire une ville'),('Une journée à Madrid','La ville','Activités interactives'),('Bilan de la semaine','Fêtes et traditions','Révision : ser y estar')]
 hours=[9,11,15]
 events=[]
 for j in range(5):
  day=monday+timedelta(days=j)
  if not _schoolday(day,breaks):continue
  for k,h in enumerate(hours):
   sub=(j*3+k)%len(subjects);events.append((day,h,subjects[sub],names[j][k],colors[sub]))
 if view=='Mois':
  st.calendar if False else None
  st.info(f'Mois de {monday:%m/%Y} · Utilise les flèches pour parcourir les semaines. Les jours non scolaires sont exclus.')
 if view=='Jour':
  selected=st.date_input('Journée',value=monday,key='v94_day')
  for d,h,subject,title,color in events:
   if d==selected and subject in filters:st.markdown(f'<div class="v94-slot" style="background:{color};margin:8px 0">{h}:00–{h+1}:00 · <b>{html.escape(subject)}</b> · {html.escape(title)}</div>',unsafe_allow_html=True)
 else:
  cells=['<div class="v94-cell v94-head">Heure</div>']+[f'<div class="v94-cell v94-head">{(monday+timedelta(days=j)):%a %d/%m}</div>' for j in range(5)]
  for h in range(8,18):
   cells.append(f'<div class="v94-cell v94-head">{h}:00</div>')
   for j in range(5):
    d=monday+timedelta(days=j)
    e=next((x for x in events if x[0]==d and x[1]==h and x[2] in filters),None)
    content=f'<div class="v94-slot" style="background:{e[4]}"><b>{h}:00–{h+1}:00</b><div>{html.escape(e[2])}</div>{html.escape(e[3])}</div>' if e else ('🌴 Repos' if not _schoolday(d,breaks) and h==9 else '')
    cells.append(f'<div class="v94-cell">{content}</div>')
  st.markdown('<div class="v94-wrap"><div class="v94-grid">'+''.join(cells)+'</div></div>',unsafe_allow_html=True)
 st.caption('Créneaux indicatifs, non réservés : les devoirs et validations réels restent suivis ci-dessous.')
 with st.expander('➕ Ajouter un cours personnel'):
  with st.form('v94_add_course'):
   d=st.date_input('Date du cours',value=date.today());title=st.text_input('Titre du cours');subject=st.selectbox('Matière',subjects);hour=st.selectbox('Heure',list(range(8,18)))
   if st.form_submit_button('Ajouter') and title.strip():school.setdefault('personal_courses',[]).append({'date':d.isoformat(),'title':title,'subject':subject,'hour':hour});st.success('Cours ajouté à ma liste personnelle.')
 for e in school.get('personal_courses',[]):st.caption(f"📌 {e['date']} · {e['hour']}:00 · {e['subject']} — {e['title']}")

def _school(world):
 st.markdown('### 🇪🇸 Mon école d’espagnol · A1 à C2')
 school=world.setdefault('v91_school',{})
 school.setdefault('start',date.today().isoformat());school.setdefault('tasks',{});school.setdefault('vacations','')
 st.caption('📚 Leçons, devoirs datés, contrôle, rattrapage et repos scolaire. Les jours de cours font avancer le planning, pas les week-ends.')
 with st.expander('⚙️ Mon calendrier scolaire'):
  school['start']=st.date_input('Date de début de ma scolarité',date.fromisoformat(school['start']),key='v91_start').isoformat()
  st.caption('Les jours fériés nationaux français sont pris en compte. Ajoute les dates officielles de tes vacances scolaires pour ta zone : une ligne par période, au format AAAA-MM-JJ;AAAA-MM-JJ.')
  school['vacations']=st.text_area('Mes vacances scolaires (dates de début et de fin)',value=school['vacations'],key='v91_vacations',height=95)
 breaks=_breaks(school['vacations']);today=date.today();start=date.fromisoformat(school['start'])
 if today<start:st.info('La rentrée est prévue le '+start.strftime('%d/%m/%Y'))
 elif not _schoolday(today,breaks):st.success('🌴 Aujourd’hui : repos scolaire. Révisions facultatives uniquement !')
 else:st.success('🏫 Aujourd’hui : journée de classe !')
 index=0;d=start
 while d<today and index<1500:
  if _schoolday(d,breaks):index+=1
  d+=timedelta(days=1)
 unit=index//5+1
 st.caption(f'📅 Semaine pédagogique {unit}')
 st.markdown('👩‍🏫 **Classe de Sofía** · Lucía · Diego · Emma · Pablo')
 # Affichage compact côte à côte sur grand écran ; empilé sur mobile.
 timetable_col, activities_col = st.columns([1.2, 1], gap='small')
 with timetable_col:
  _visual_timetable(school,breaks)
 with activities_col:
  _school_activities(world, school, breaks, start, today, unit)

def _school_activities(world, school, breaks, start, today, unit):
 st.markdown('#### 📋 Mes activités et validations')
 activities=['📖 Cours + vocabulaire','✍️ Conjugaison et entraînement','🎭 Mission de survie','📝 Devoir à rendre','🎓 Contrôle et bilan']
 for i,act in enumerate(activities):
  due=_nth_day(start,(unit-1)*5+i,breaks)
  key=due.isoformat();done=school['tasks'].get(key,False)
  with st.container(border=True):
   st.markdown(('✅ **Terminé** · ' if done else '📌 **À réaliser** · ')+due.strftime('%d/%m/%Y')+' · '+act)
   if done:
    st.success('Travail validé : bravo ! ⭐')
   elif due>today:
    st.caption('🔒 Ce cours sera accessible à sa date prévue.')
   else:
    with st.expander('📖 Commencer le cours et valider mes acquis'):
     st.write('👩‍🏫 Sofía : ¡Hola! Réponds aux questions pour valider cette activité.')
     questions=[
      ('Comment dire « Je suis » pour se présenter ?', ['Soy','Tengo','Voy'], 'Soy'),
      ('Comment demander « Où est la gare ? » ?', ['¿Dónde está la estación?','¿Cuánto cuesta?','¿Cómo te llamas?'], '¿Dónde está la estación?'),
      ('Comment dire « Je voudrais de l’eau » ?', ['Quiero agua, por favor.','Soy agua.','Está agua.'], 'Quiero agua, por favor.'),
      ('Quel verbe complète « Yo ___ español » ?', ['hablo','hablas','hablan'], 'hablo'),
      ('Comment demander l’addition ?', ['La cuenta, por favor.','La calle, por favor.','La llave, por favor.'], 'La cuenta, por favor.')]
     q,opts,expected=questions[i]
     answer=st.radio(q,opts,index=None,key='v92_school_quiz_'+key)
     if st.button('🎓 Vérifier et valider',key='v92_school_check_'+key,disabled=answer is None):
      if answer==expected:
       school['tasks'][key]=True
       school.setdefault('results',{})[key]={'score':100,'date':today.isoformat(),'activity':act}
       _save(world);st.success('¡Muy bien! Activité validée. ⭐');st.rerun()
      else:st.warning('Pas encore. Relis la question et réessaie ; aucune pénalité.')
 st.caption('Les échéances tombent uniquement sur les jours de classe. Les devoirs en retard restent accessibles sans pénalité.')
 st.markdown('#### 👩‍🏫 Leçon et exercices avec Sofía')
 st.info('Retrouve les cours interactifs de Sofía dans l’onglet 📖 Cours interactifs ci-dessus.')
 with st.expander('📝 Mon devoir évolutif'):
  levels=['A1','A2','B1','B2','C1','C2'];lv=st.selectbox('Niveau du devoir',levels,key='v91_homework_level')
  prompts={'A1':'Écris 5 phrases pour te présenter (nom, origine, ville, goûts, âge).','A2':'Raconte ton dernier week-end au passé en 6 phrases.','B1':'Écris un message de 8 phrases pour résoudre un problème de réservation.','B2':'Rédige une réclamation polie avec arguments et solution proposée.','C1':'Défends ton opinion sur un sujet de société avec des nuances.','C2':'Reformule un problème complexe dans deux registres de langue.'}
  st.info(prompts[lv]);key=f'{unit}:{lv}'
  school.setdefault('homework',{})[key]=st.text_area('Mon devoir (brouillon conservé dans ma progression)',value=school.get('homework',{}).get(key,''),key='v91_homework_text')
  if st.button('💾 Enregistrer mon devoir',key='v91_save_homework'):
   _save(world);st.success('Devoir conservé dans ta progression. Correction automatique détaillée non disponible pour les textes libres.')
 st.caption('ℹ️ Les devoirs sont des brouillons et le planning est un suivi personnel : la notation automatique des rédactions et les examens certifiants restent à développer.')

def _survival(world,lang):
 data=world.setdefault('v91_survival',{}).setdefault(lang,{'done':[],'answers':{}})
 st.markdown('### 🧳 École express · 7 jours pour se débrouiller')
 st.progress(len(data['done'])/7,text=f"{len(data['done'])}/7 missions validées")
 day=st.selectbox('Choisis ta journée',list(range(7)),format_func=lambda i:f'Jour {i+1} — {THEMES[i]}',key='v91_day_'+lang)
 st.markdown(f'#### 🎬 Jour {day+1} — {THEMES[day]}')
 st.caption('Professeur : écoute/lecture, vocabulaire essentiel, exercice de mise en situation et mission.')
 pairs=PHRASES[lang][day]
 for original,french in pairs:st.markdown(f'**💬 {original}**  \n{french}')
 st.markdown('#### 🎮 Mini-mission : retrouve la bonne expression')
 q=day%len(pairs);target,meaning=pairs[q]
 options=[target,PHRASES[lang][(day+1)%7][q][0],PHRASES[lang][(day+2)%7][q][0]]
 answer=st.radio(f'Comment dire : « {meaning} » ?',options,index=None,key=f'v91_quiz_{lang}_{day}')
 if st.button('Vérifier ma mission',key=f'v91_verify_{lang}_{day}'):
  if answer==target:
   if day not in data['done']:data['done'].append(day)
   _save(world);st.success('🎉 Bravo ! Mission réussie. Tu peux passer à la suivante.')
  else:st.warning('Essaie encore ! Relis les phrases et utilise-les dans une vraie situation.')
 with st.expander('🆘 SOS linguistique — phrases essentielles'):
  for pair in [PHRASES[lang][0][1],PHRASES[lang][0][2],PHRASES[lang][5][0],PHRASES[lang][5][1],PHRASES[lang][4][2]]:st.write(f'{pair[0]} — {pair[1]}')
 st.caption('Ces sept missions constituent une initiation pratique, pas une certification A1/B1. Prononciation et compréhension orale avancée non évaluées.')

def page():
 st.markdown("""<style>.v91-class{background:linear-gradient(115deg,#fff1d6,#efeaff);border:1px solid #eadcf2;padding:18px 22px;border-radius:22px;margin:12px 0;color:#4d3264}.v91-class strong{font-size:1.3rem}</style>""",unsafe_allow_html=True)
 st.markdown('<div class="v91-class"><strong>🏫 Ma classe · Bienvenue !</strong><p>Une vraie école d’espagnol et trois parcours express pour voyager.</p></div>',unsafe_allow_html=True)
 world=social.store()
 if st.session_state.get('v80_profile') and db.db_enabled() and st.session_state.get('v80_loaded_profile')!=st.session_state.get('v80_profile'):
  try:
   saved=db.load(st.session_state['v80_profile'])
   if saved:st.session_state.v63_world=saved;world=saved
   st.session_state.v80_loaded_profile=st.session_state['v80_profile']
  except Exception:pass
 choice=st.radio('Choisis ta classe',list(LANGS),horizontal=True,key='v91_lang')
 lang=LANGS[choice]
 if lang=='es':
  tab1,tab2,tab3,tab4,tab5=st.tabs(['📅 Emploi du temps','📖 Cours interactifs','📝 Devoirs','📈 Progression','📚 Ressources'])
  with tab1:_school(world)
  with tab2:academy.render(world,'es')
  with tab3:st.info('Les devoirs évolutifs sont accessibles dans Emploi du temps, après les activités de la semaine.')
  with tab4:st.write('Activités validées :',len(world.get('v91_school',{}).get('results',{})))
  with tab5:st.write('📚 Espagnol CECRL A1 à C2 · grammaire, vocabulaire, culture et situations de la vie quotidienne.')
 else:_survival(world,lang)
 with st.expander('💾 Sauvegarde de ma classe'):
  st.caption('Pour conserver la progression entre appareils, charge d’abord ton profil dans Rencontres, puis reviens ici.')
  if st.button('Enregistrer ma progression',key='v91_save'):
   if _save(world):st.success('Progression enregistrée dans le profil Supabase.')
   else:st.warning('Profil Supabase non chargé ou base indisponible : progression conservée dans cette session seulement.')
