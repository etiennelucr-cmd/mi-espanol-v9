"""Parcours autonome de survie en voyage : 7 jours, 21 leçons A0–A1."""
import sqlite3
from pathlib import Path
import streamlit as st

# Jour, titre, objectif, trois expressions (espagnol, français), mise en situation.
DATA = [
(1,'Saluer et être poli','Saluer et remercier', [('Hola, buenos días.','Bonjour.'),('Muchas gracias.','Merci beaucoup.'),('Perdón, por favor.','Pardon, s’il vous plaît.')], 'Tu entres dans une boutique. Salue puis remercie le vendeur.'),
(1,'Se présenter','Dire qui tu es',[('Me llamo Luc.','Je m’appelle Luc.'),('Soy de Francia.','Je viens de France.'),('Estoy de vacaciones.','Je suis en vacances.')], 'Tu rencontres une personne à l’hôtel. Présente-toi.'),
(1,'Comprendre et demander','Faire répéter',[('No entiendo.','Je ne comprends pas.'),('¿Puede repetir, por favor?','Pouvez-vous répéter, s’il vous plaît ?'),('¿Habla francés?','Parlez-vous français ?')], 'Une personne parle trop vite. Demande-lui de répéter.'),
(2,'Au café','Commander une boisson',[('Quiero un café con leche.','Je voudrais un café au lait.'),('Un vaso de agua, por favor.','Un verre d’eau, s’il vous plaît.'),('¿Cuánto cuesta?','Combien ça coûte ?')], 'Au café, commande une boisson et demande le prix.'),
(2,'Au restaurant','Commander un repas',[('Una mesa para dos, por favor.','Une table pour deux, s’il vous plaît.'),('Quisiera el menú.','Je voudrais le menu.'),('Sin cebolla, por favor.','Sans oignon, s’il vous plaît.')], 'Au restaurant, demande une table puis le menu.'),
(2,'Payer et demander l’addition','Terminer un repas',[('La cuenta, por favor.','L’addition, s’il vous plaît.'),('¿Puedo pagar con tarjeta?','Puis-je payer par carte ?'),('¿Está incluido el servicio?','Le service est-il compris ?')], 'Demande l’addition et vérifie si tu peux payer par carte.'),
(3,'Demander son chemin','Se repérer',[('¿Dónde está la estación?','Où est la gare ?'),('¿Está lejos de aquí?','Est-ce loin d’ici ?'),('A la derecha, por favor.','À droite, s’il vous plaît.')], 'Tu es perdu. Demande où se trouve la gare.'),
(3,'Métro et bus','Utiliser les transports',[('Un billete, por favor.','Un billet, s’il vous plaît.'),('¿Qué línea tengo que tomar?','Quelle ligne dois-je prendre ?'),('¿Dónde está la parada?','Où est l’arrêt ?')], 'Demande quel métro prendre pour rejoindre le centre.'),
(3,'Taxi et horaires','Arriver à destination',[('Lléveme a esta dirección, por favor.','Conduisez-moi à cette adresse, s’il vous plaît.'),('¿Cuánto tarda?','Combien de temps cela prend-il ?'),('¿A qué hora sale?','À quelle heure part-il ?')], 'Montre une adresse au chauffeur et demande la durée du trajet.'),
(4,'Arriver à l’hôtel','Faire le check-in',[('Tengo una reserva.','J’ai une réservation.'),('¿A qué hora es el desayuno?','À quelle heure est le petit-déjeuner ?'),('¿Dónde está mi habitación?','Où est ma chambre ?')], 'À la réception, annonce ta réservation et demande l’horaire du petit-déjeuner.'),
(4,'Dans la chambre','Demander un service',[('No funciona el aire acondicionado.','La climatisation ne fonctionne pas.'),('Necesito otra toalla.','J’ai besoin d’une autre serviette.'),('¿Cuál es la contraseña del wifi?','Quel est le mot de passe du wifi ?')], 'Demande une serviette supplémentaire et le code wifi.'),
(4,'Départ et bagages','Quitter l’hôtel',[('Quiero dejar mi equipaje.','Je voudrais laisser mes bagages.'),('¿A qué hora es la salida?','À quelle heure doit-on libérer la chambre ?'),('¿Puede llamar un taxi?','Pouvez-vous appeler un taxi ?')], 'Avant ton départ, demande à laisser ta valise à l’accueil.'),
(5,'Faire des achats','Demander un prix',[('¿Cuánto vale esto?','Combien cela coûte-t-il ?'),('Solo estoy mirando.','Je regarde seulement.'),('Es demasiado caro.','C’est trop cher.')], 'Dans un magasin, demande le prix puis explique que tu regardes seulement.'),
(5,'Tailles et couleurs','Acheter un vêtement',[('¿Tiene otra talla?','Avez-vous une autre taille ?'),('Lo quiero en azul.','Je le veux en bleu.'),('¿Puedo probármelo?','Puis-je l’essayer ?')], 'Demande une autre taille et essaie un vêtement.'),
(5,'Au marché','Acheter des aliments',[('Quiero un kilo de naranjas.','Je voudrais un kilo d’oranges.'),('¿Están frescos?','Sont-ils frais ?'),('Medio kilo, por favor.','Un demi-kilo, s’il vous plaît.')], 'Au marché, achète un demi-kilo de fruits.'),
(6,'Faire connaissance','Discuter simplement',[('¿Cómo te llamas?','Comment t’appelles-tu ?'),('¿De dónde eres?','D’où viens-tu ?'),('Mucho gusto.','Enchanté(e).')], 'Rencontre une personne et demande-lui d’où elle vient.'),
(6,'Loisirs et goûts','Dire ce que tu aimes',[('Me gusta la música.','J’aime la musique.'),('Prefiero la playa.','Je préfère la plage.'),('¿Qué recomiendas?','Que recommandes-tu ?')], 'Demande une recommandation pour une activité.'),
(6,'Organiser une sortie','Fixer un rendez-vous',[('¿A qué hora quedamos?','À quelle heure se retrouve-t-on ?'),('Nos vemos mañana.','On se voit demain.'),('Estoy disponible esta tarde.','Je suis disponible cet après-midi.')], 'Propose un rendez-vous pour demain.'),
(7,'À la pharmacie','Expliquer un symptôme',[('Me duele la cabeza.','J’ai mal à la tête.'),('Necesito una farmacia.','J’ai besoin d’une pharmacie.'),('¿Tiene algo para el dolor?','Avez-vous quelque chose contre la douleur ?')], 'À la pharmacie, explique que tu as mal à la tête.'),
(7,'Objets perdus','Demander de l’aide',[('He perdido mi teléfono.','J’ai perdu mon téléphone.'),('¿Puede ayudarme?','Pouvez-vous m’aider ?'),('¿Dónde está la policía?','Où se trouve la police ?')], 'Tu as perdu ton téléphone. Demande de l’aide.'),
(7,'Urgences et imprévus','Réagir en urgence',[('Necesito ayuda urgente.','J’ai besoin d’aide de toute urgence.'),('Llame a una ambulancia, por favor.','Appelez une ambulance, s’il vous plaît.'),('¿Dónde está el hospital?','Où est l’hôpital ?')], 'En cas de problème sérieux, demande immédiatement de l’aide.'),
]
DAY_NAMES = ['','Premiers contacts','Café et restaurant','Se déplacer','À l’hôtel','Faire des achats','Vie quotidienne','Imprévus et sécurité']
# Compléments pratiques : expressions de survie indépendantes des 21 leçons.
BONUS = {
    '🚻 Toilettes et besoins immédiats': [
        ('¿Dónde está el baño?', 'Où sont les toilettes ?'),
        ('¿Puedo usar el baño?', 'Puis-je utiliser les toilettes ?'),
        ('Necesito ir al baño.', 'J’ai besoin d’aller aux toilettes.'),
        ('¿Hay papel higiénico?', 'Y a-t-il du papier toilette ?'),
        ('¿Dónde puedo beber agua?', 'Où puis-je boire de l’eau ?'),
    ],
    '🍕 Commander une pizza': [
        ('Quisiera una pizza margarita, por favor.', 'Je voudrais une pizza margherita, s’il vous plaît.'),
        ('Una pizza para llevar, por favor.', 'Une pizza à emporter, s’il vous plaît.'),
        ('¿Qué tamaño tiene?', 'Quelle taille fait-elle ?'),
        ('Sin aceitunas, por favor.', 'Sans olives, s’il vous plaît.'),
        ('¿Cuánto cuesta la pizza?', 'Combien coûte la pizza ?'),
    ],
    '🛗 Ascenseur et bâtiment': [
        ('¿Dónde está el ascensor?', 'Où est l’ascenseur ?'),
        ('¿En qué planta está?', 'À quel étage est-ce ?'),
        ('Voy al tercer piso.', 'Je vais au troisième étage.'),
        ('El ascensor no funciona.', 'L’ascenseur ne fonctionne pas.'),
        ('¿Dónde están las escaleras?', 'Où sont les escaliers ?'),
    ],
    '🌧️ Météo et vêtements': [
        ('Está lloviendo.', 'Il pleut.'),
        ('Está nevando.', 'Il neige.'),
        ('Hace frío.', 'Il fait froid.'),
        ('Hace calor.', 'Il fait chaud.'),
        ('Necesito un paraguas.', 'J’ai besoin d’un parapluie.'),
        ('¿Qué tiempo hace mañana?', 'Quel temps fera-t-il demain ?'),
    ],
    '💼 Travail simple': [
        ('¿En qué trabajas?', 'Quel est ton métier ?'),
        ('Trabajo en una oficina.', 'Je travaille dans un bureau.'),
        ('Soy camarero / camarera.', 'Je suis serveur / serveuse.'),
        ('Empiezo a las ocho.', 'Je commence à huit heures.'),
        ('Termino a las cinco.', 'Je termine à cinq heures.'),
        ('Hoy no trabajo.', 'Aujourd’hui, je ne travaille pas.'),
    ],
    '👨‍👩‍👧 Famille et proches': [
        ('Esta es mi madre.', 'Voici ma mère.'),
        ('Este es mi padre.', 'Voici mon père.'),
        ('Tengo un hermano y una hermana.', 'J’ai un frère et une sœur.'),
        ('¿Tienes hijos?', 'As-tu des enfants ?'),
        ('Mi hijo tiene cinco años.', 'Mon fils a cinq ans.'),
        ('Mi hija está aquí.', 'Ma fille est ici.'),
        ('Estoy con mi familia.', 'Je suis avec ma famille.'),
        ('Este es mi marido.', 'Voici mon mari.'),
        ('Esta es mi mujer.', 'Voici ma femme.'),
        ('Estos son mis abuelos.', 'Voici mes grands-parents.'),
    ],
    '🧳 Objets utiles en voyage': [
        ('¿Dónde está mi maleta?', 'Où est ma valise ?'),
        ('Tengo una mochila.', 'J’ai un sac à dos.'),
        ('He perdido mi pasaporte.', 'J’ai perdu mon passeport.'),
        ('Necesito mi documento de identidad.', 'J’ai besoin de ma carte d’identité.'),
        ('¿Dónde está mi teléfono?', 'Où est mon téléphone ?'),
        ('Necesito un cargador.', 'J’ai besoin d’un chargeur.'),
        ('¿Tiene un adaptador de enchufe?', 'Avez-vous un adaptateur de prise ?'),
        ('He perdido mis llaves.', 'J’ai perdu mes clés.'),
        ('Necesito un paraguas.', 'J’ai besoin d’un parapluie.'),
        ('¿Dónde puedo comprar un billete?', 'Où puis-je acheter un billet ?'),
    ],
    '🎭 Lieux et sorties': [
        ('¿Dónde está el cine?', 'Où est le cinéma ?'),
        ('Quiero ir al teatro.', 'Je veux aller au théâtre.'),
        ('¿A qué hora empieza la película?', 'À quelle heure commence le film ?'),
        ('Dos entradas, por favor.', 'Deux billets, s’il vous plaît.'),
        ('¿Dónde está el museo?', 'Où est le musée ?'),
        ('Vamos al parque.', 'Allons au parc.'),
        ('¿Cómo se llega a la playa?', 'Comment va-t-on à la plage ?'),
        ('¿Hay una biblioteca cerca?', 'Y a-t-il une bibliothèque à proximité ?'),
        ('¿Dónde está la oficina de turismo?', 'Où se trouve l’office de tourisme ?'),
        ('¿Está abierto hoy?', 'Est-ce ouvert aujourd’hui ?'),
    ],
}

def numero_es(n):
    """Convertit un entier de 1 à 5000 en espagnol courant."""
    if not 1 <= n <= 5000:
        raise ValueError('Le nombre doit être compris entre 1 et 5000.')
    units = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez',
             'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete',
             'dieciocho', 'diecinueve', 'veinte', 'veintiuno', 'veintidós', 'veintitrés',
             'veinticuatro', 'veinticinco', 'veintiséis', 'veintisiete', 'veintiocho', 'veintinueve']
    tens = ['', '', '', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa']
    hundreds = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos',
                'seiscientos', 'setecientos', 'ochocientos', 'novecientos']
    if n < 30:
        return units[n]
    if n < 100:
        return tens[n // 10] + (' y ' + units[n % 10] if n % 10 else '')
    if n == 100:
        return 'cien'
    if n < 1000:
        return hundreds[n // 100] + (' ' + numero_es(n % 100) if n % 100 else '')
    return ('mil' if n // 1000 == 1 else units[n // 1000] + ' mil') + (' ' + numero_es(n % 1000) if n % 1000 else '')

def page_bonus():
    st.subheader('🧰 Kit de survie : situations concrètes')
    st.caption('Situations concrètes : toilettes, repas, famille, bagages, lieux, météo, travail et nombres de 1 à 5 000.')
    topic = st.selectbox('Choisis une situation', list(BONUS), key='voyage_bonus_theme')
    phrases = BONUS[topic]
    for es, fr in phrases:
        st.markdown(f'**🇪🇸 {es}**  \n🇫🇷 {fr}')
    st.markdown('#### ✏️ Exercice rapide')
    import hashlib
    idx = int(hashlib.sha256(topic.encode('utf-8')).hexdigest(), 16) % len(phrases)
    es, fr = phrases[idx]
    other = [v for k, v in phrases if v != fr][:2]
    options = [other[0], fr, other[1]]
    choice = st.radio(f'Que signifie « {es} » ?', options, index=None, key='bonus_q_' + topic)
    if choice is not None:
        if choice == fr:
            st.success('Bonne réponse !')
        else:
            st.error('Réessaie : relis les expressions ci-dessus.')
    st.divider()
    st.subheader('🔢 Les nombres de 1 à 5 000')
    st.caption('Utile pour les prix, les numéros de chambre, les horaires et les quantités.')
    number = st.number_input('Choisis un nombre', min_value=1, max_value=5000, value=2450, step=1, key='voyage_nombre')
    st.info(f'**{number:,} → {numero_es(int(number))}**'.replace(',', ' '))
    with st.expander('Repères pour apprendre à compter'):
        for n in [1, 5, 10, 15, 20, 21, 30, 40, 50, 100, 101, 200, 500, 1000, 1500, 2000, 5000]:
            st.write(f'{n} — {numero_es(n)}')
    st.caption('Attention : devant un nom masculin, « uno » devient généralement « un » (par exemple : veintiún euros).')

DB = Path(__file__).with_name('voyage_survie_progression.sqlite3')

def _connection():
    db = sqlite3.connect(str(DB), timeout=5)
    db.execute('CREATE TABLE IF NOT EXISTS lecons_terminees (lesson INTEGER PRIMARY KEY, score INTEGER NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    return db

def _load():
    try:
        with _connection() as db:
            return dict(db.execute('SELECT lesson,score FROM lecons_terminees').fetchall())
    except (OSError, sqlite3.Error):
        return st.session_state.get('voyage_progression_session', {})

def _save(lesson, score):
    state=st.session_state.setdefault('voyage_progression_session', {})
    state[lesson]=max(score,state.get(lesson,0))
    try:
        with _connection() as db:
            db.execute('INSERT INTO lecons_terminees(lesson,score) VALUES(?,?) ON CONFLICT(lesson) DO UPDATE SET score=max(score,excluded.score),updated_at=CURRENT_TIMESTAMP',(lesson,score))
    except (OSError,sqlite3.Error):
        st.warning('Sauvegarde locale indisponible : résultat conservé pour cette session seulement.')

def page():
    st.title('🧳 Mon guide de voyage en espagnol')
    st.markdown('**Parler, comprendre et se débrouiller au quotidien en Espagne.**')
    st.caption('7 jours · 21 leçons courtes · 8 thèmes pratiques · Exercices et mises en situation · Débutant A0–A1')
    st.info('☀️ Commence par les 7 jours pour apprendre les bases, ou ouvre le kit pratique pour retrouver immédiatement une phrase utile.')
    section=st.radio('Que souhaites-tu consulter ?', ['📅 Mon itinéraire · 7 jours', '🧰 Expressions de survie'], horizontal=True, key='voyage_section')
    if section == '🧰 Expressions de survie':
        page_bonus()
        return
    progress=_load()
    completed=sum(i in progress for i in range(1,22))
    st.progress(completed/21, text=f'{completed}/21 leçons terminées')
    st.markdown('### 🗺️ Mon itinéraire')
    for d in range(1,8):
        st.caption(f'**Jour {d} · {DAY_NAMES[d]}** — ' + ' · '.join(item[1] for item in DATA if item[0] == d))
    st.divider()
    day=st.selectbox('Choisis ton jour',range(1,8),format_func=lambda d:f'Jour {d} · {DAY_NAMES[d]}',key='voyage_jour')
    indices=[i for i,item in enumerate(DATA) if item[0]==day]
    selected=st.selectbox('Choisis ta leçon',indices,format_func=lambda i:f'{"✅ " if i+1 in progress else "📖 "}{DATA[i][1]}',key=f'voyage_lecon_{day}')
    _,name,objective,phrases,scenario=DATA[selected]
    st.subheader(f'Leçon {selected+1}/21 · {name}')
    st.info('🎯 Objectif : '+objective)
    st.markdown('#### 📚 Cours et expressions utiles')
    for es,fr in phrases:
        st.markdown(f'**🇪🇸 {es}**  \n🇫🇷 {fr}')
    st.markdown('#### 💬 Dialogue de la vie quotidienne')
    st.write('🧑 **Voyageur :** '+phrases[0][0])
    st.write('👤 **Interlocuteur :** '+phrases[1][0])
    st.write('🧑 **Voyageur :** '+phrases[2][0])
    st.caption('Dialogue d’entraînement : phrases utiles à réutiliser selon la situation.')
    st.markdown('#### ✏️ Exercices : retrouve la traduction')
    # Distracteurs pris dans d'autres leçons du même parcours, toujours distincts.
    all_fr=[pair[1] for entry in DATA for pair in entry[3]]
    with st.form(f'voyage_quiz_{selected}'):
        answers=[]
        for j,(es,fr) in enumerate(phrases):
            wrong=[]
            for offset in (7,19,35,44):
                candidate=all_fr[(selected*3+j+offset)%len(all_fr)]
                if candidate!=fr and candidate not in wrong:
                    wrong.append(candidate)
                if len(wrong)==2:break
            options=[fr]+wrong
            # Rotation déterministe de la bonne réponse.
            shift=(selected+j)%3
            options=options[shift:]+options[:shift]
            answers.append(st.radio(f'{j+1}. {es}',options,index=None,key=f'voyage_q_{selected}_{j}'))
        submit=st.form_submit_button('Corriger mes réponses',type='primary')
    if submit:
        score=sum(a==p[1] for a,p in zip(answers,phrases))
        st.session_state[f'voyage_result_{selected}']=(score,answers)
        import suivi_langues_v48
        suivi_langues_v48.enregistrer("es", f"voyage_lecon_{selected+1}", score, 3)
        suivi_langues_v48.enregistrer_phrases("es", f"voyage_lecon_{selected+1}", phrases, answers)
        if score==3:_save(selected+1,score)
    result=st.session_state.get(f'voyage_result_{selected}')
    if result:
        score,old_answers=result
        (st.success if score==3 else st.warning)(f'Résultat : {score}/3'+(' · Leçon validée !' if score==3 else ' · Réessaie pour valider.'))
        for j,(_,fr) in enumerate(phrases):
            st.write(('✅ ' if old_answers[j]==fr else '❌ ')+f'Question {j+1} : **{fr}**')
    st.markdown('#### 🎭 Mise en situation')
    st.write(scenario)
    st.caption('Entraîne-toi à voix haute ou écris ta réponse. La réponse libre n’est pas notée automatiquement.')
    st.text_area('Ta réponse en espagnol',key=f'voyage_libre_{selected}',height=90)
    with st.expander('Voir les expressions utiles pour cette situation'):
        for es,_ in phrases:st.write('• '+es)
    st.divider()
    st.caption('Les résultats sont enregistrés dans un fichier SQLite local si le stockage est accessible. Sur certains hébergements cloud, ce stockage peut être temporaire. Aucun niveau CECRL ni autre suivi existant n’est modifié.')
