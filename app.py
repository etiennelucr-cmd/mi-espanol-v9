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
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import math
import random
import streamlit as st
import streamlit.components.v1 as components
from programme import CLASSES, EQUIVALENCES, SCOLAIRE, CECRL, SOURCES
from programmes_officiels import PROGRAMMES, LLCER, LLCER_EXERCICES
from grammaire import GRAMMAIRE
from conjugaison import PERSONS, IMP_PERSONS, VERBS, TENSES, conjugate, participle, gerund
from progression import available_indices, unlocked_groups, current_school_grade, score_passes
from survie_400 import SUPPLEMENTS, VOCABULARY

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

# Guide du voyageur : 15 missions thématiques ; expressions de référence disponibles
# dans le guide express même si une mission est verrouillée (cas d'urgence).
# Format phrase : (français, allemand poli en Sie, italien poli en Lei).
TRAVEL_GUIDE = [
    ('Premiers contacts', 'Saluer, demander de répéter et se faire comprendre', [
        ('Bonjour !', 'Guten Tag!', 'Buongiorno!'),
        ('Excusez-moi.', 'Entschuldigung.', 'Mi scusi.'),
        ('Parlez-vous anglais ?', 'Sprechen Sie Englisch?', 'Parla inglese?'),
        ('Je ne comprends pas.', 'Ich verstehe nicht.', 'Non capisco.'),
        ('Pouvez-vous répéter, s’il vous plaît ?', 'Können Sie das bitte wiederholen?', 'Può ripetere, per favore?'),
        ('Parlez plus lentement, s’il vous plaît.', 'Sprechen Sie bitte langsamer.', 'Parli più lentamente, per favore.'),
        ('Merci beaucoup.', 'Vielen Dank.', 'Grazie mille.'),
    ]),
    ('Prix, horaires et informations', 'Comprendre les prix, horaires et moyens de paiement', [
        ('Combien ça coûte ?', 'Wie viel kostet das?', 'Quanto costa?'),
        ('À quelle heure cela commence ?', 'Um wie viel Uhr beginnt das?', 'A che ora comincia?'),
        ('Pouvez-vous l’écrire ?', 'Können Sie das bitte aufschreiben?', 'Può scriverlo, per favore?'),
        ('Puis-je payer par carte ?', 'Kann ich mit Karte bezahlen?', 'Posso pagare con la carta?'),
        ('Où est le distributeur de billets ?', 'Wo ist der nächste Geldautomat?', 'Dov’è il bancomat più vicino?'),
        ('Est-ce ouvert aujourd’hui ?', 'Ist das heute geöffnet?', 'È aperto oggi?'),
        ('Je voudrais un reçu, s’il vous plaît.', 'Ich hätte gern eine Quittung, bitte.', 'Vorrei una ricevuta, per favore.'),
    ]),
    ('Restaurant et alimentation', 'Commander, demander les toilettes et signaler une allergie', [
        ('Je voudrais une bouteille d’eau.', 'Ich hätte gern eine Flasche Wasser.', 'Vorrei una bottiglia d’acqua.'),
        ('L’addition, s’il vous plaît.', 'Die Rechnung, bitte.', 'Il conto, per favore.'),
        ('Avez-vous un menu en anglais ?', 'Haben Sie eine Speisekarte auf Englisch?', 'Avete un menù in inglese?'),
        ('Je suis végétarien / végétarienne.', 'Ich bin Vegetarier / Vegetarierin.', 'Sono vegetariano / vegetariana.'),
        ('Je suis allergique aux fruits à coque.', 'Ich bin allergisch gegen Nüsse.', 'Sono allergico/a alla frutta a guscio.'),
        ('Où sont les toilettes ?', 'Wo ist die Toilette?', 'Dov’è il bagno?'),
        ('C’est à emporter.', 'Zum Mitnehmen, bitte.', 'Da asporto, per favore.'),
    ]),
    ('Hôtel, clés et ascenseur', 'Réception, clé perdue, carte en panne et ascenseur', [
        ('J’ai une réservation.', 'Ich habe eine Reservierung.', 'Ho una prenotazione.'),
        ('J’ai perdu la clé de ma chambre.', 'Ich habe meinen Zimmerschlüssel verloren.', 'Ho perso la chiave della camera.'),
        ('Où est l’ascenseur ?', 'Wo ist der Aufzug?', 'Dov’è l’ascensore?'),
        ('Ma carte de chambre ne fonctionne pas.', 'Meine Zimmerkarte funktioniert nicht.', 'La tessera della mia camera non funziona.'),
        ('Puis-je avoir une autre clé ?', 'Kann ich bitte einen Ersatzschlüssel bekommen?', 'Posso avere una chiave di ricambio, per favore?'),
        ('L’ascenseur est en panne.', 'Der Aufzug ist kaputt.', 'L’ascensore è guasto.'),
        ('Je suis coincé(e) dans l’ascenseur.', 'Ich stecke im Aufzug fest.', 'Sono bloccato/a nell’ascensore.'),
        ('Où puis-je déposer mes bagages ?', 'Wo kann ich mein Gepäck abstellen?', 'Dove posso lasciare i bagagli?'),
    ]),
    ('Transports et aéroport', 'Billets, retards, correspondances et bagages', [
        ('Un billet, s’il vous plaît.', 'Eine Fahrkarte, bitte.', 'Un biglietto, per favore.'),
        ('Où est le quai ?', 'Wo ist der Bahnsteig?', 'Dov’è il binario?'),
        ('Ce train va-t-il à la gare centrale ?', 'Fährt dieser Zug zum Hauptbahnhof?', 'Questo treno va alla stazione centrale?'),
        ('J’ai raté mon train.', 'Ich habe meinen Zug verpasst.', 'Ho perso il treno.'),
        ('Le train a-t-il du retard ?', 'Hat der Zug Verspätung?', 'Il treno è in ritardo?'),
        ('Où est l’arrêt de bus ?', 'Wo ist die Bushaltestelle?', 'Dov’è la fermata dell’autobus?'),
        ('Mes bagages ne sont pas arrivés.', 'Mein Gepäck ist nicht angekommen.', 'Il mio bagaglio non è arrivato.'),
        ('Pouvez-vous appeler un taxi ?', 'Können Sie bitte ein Taxi rufen?', 'Può chiamare un taxi, per favore?'),
    ]),
    ('Chemin, étages et objets', 'Se repérer, chercher un objet et retrouver ce qu’on a perdu', [
        ('Où se trouve cette adresse ?', 'Wo ist diese Adresse?', 'Dov’è questo indirizzo?'),
        ('Je cherche mes clés.', 'Ich suche meine Schlüssel.', 'Sto cercando le mie chiavi.'),
        ('Où puis-je trouver un chargeur ?', 'Wo finde ich ein Ladegerät?', 'Dove posso trovare un caricabatterie?'),
        ('À quel étage est-ce ?', 'In welchem Stockwerk ist das?', 'A che piano si trova?'),
        ('Dois-je aller à gauche ou à droite ?', 'Muss ich nach links oder nach rechts gehen?', 'Devo andare a sinistra o a destra?'),
        ('Est-ce loin à pied ?', 'Ist das zu Fuß weit?', 'È lontano a piedi?'),
        ('J’ai perdu mon téléphone.', 'Ich habe mein Handy verloren.', 'Ho perso il telefono.'),
        ('Où sont les objets trouvés ?', 'Wo ist das Fundbüro?', 'Dov’è l’ufficio oggetti smarriti?'),
    ]),
    ('Achats et services', 'Chercher un produit, régler un problème ou faire un retour', [
        ('Je cherche une pharmacie.', 'Ich suche eine Apotheke.', 'Cerco una farmacia.'),
        ('Avez-vous une taille plus grande ?', 'Haben Sie das eine Nummer größer?', 'Ce l’ha di una taglia più grande?'),
        ('Je peux essayer ?', 'Kann ich das anprobieren?', 'Posso provarlo?'),
        ('Je voudrais rendre cet article.', 'Ich möchte diesen Artikel zurückgeben.', 'Vorrei restituire questo articolo.'),
        ('Cela ne fonctionne pas.', 'Das funktioniert nicht.', 'Non funziona.'),
        ('Où puis-je acheter une carte SIM ?', 'Wo kann ich eine SIM-Karte kaufen?', 'Dove posso comprare una scheda SIM?'),
        ('Est-ce que vous acceptez les espèces ?', 'Nehmen Sie Bargeld an?', 'Accettate contanti?'),
    ]),
    ('Sorties et vie quotidienne', 'Visites, réservations, météo et connexion', [
        ('Je voudrais réserver pour deux personnes.', 'Ich möchte für zwei Personen reservieren.', 'Vorrei prenotare per due persone.'),
        ('Où puis-je acheter des billets ?', 'Wo kann ich Eintrittskarten kaufen?', 'Dove posso acquistare i biglietti?'),
        ('Est-ce gratuit ?', 'Ist der Eintritt kostenlos?', 'L’ingresso è gratuito?'),
        ('Quel temps fera-t-il demain ?', 'Wie wird das Wetter morgen?', 'Che tempo farà domani?'),
        ('Quel est le mot de passe du Wi-Fi ?', 'Wie lautet das WLAN-Passwort?', 'Qual è la password del Wi-Fi?'),
        ('À quelle heure fermez-vous ?', 'Um wie viel Uhr schließen Sie?', 'A che ora chiudete?'),
        ('Puis-je prendre une photo ici ?', 'Darf ich hier ein Foto machen?', 'Posso fare una foto qui?'),
    ]),
    ('Santé, sécurité et urgences', 'Demander immédiatement de l’aide, soigner et signaler un vol', [
        ('J’ai besoin d’aide.', 'Ich brauche Hilfe.', 'Ho bisogno di aiuto.'),
        ('Appelez une ambulance !', 'Rufen Sie einen Krankenwagen!', 'Chiami un’ambulanza!'),
        ('J’ai besoin d’un médecin.', 'Ich brauche einen Arzt.', 'Ho bisogno di un medico.'),
        ('J’ai très mal ici.', 'Ich habe hier starke Schmerzen.', 'Ho molto dolore qui.'),
        ('Je suis allergique à ce médicament.', 'Ich bin gegen dieses Medikament allergisch.', 'Sono allergico/a a questo farmaco.'),
        ('On m’a volé mon sac.', 'Meine Tasche wurde gestohlen.', 'Mi hanno rubato la borsa.'),
        ('J’ai perdu mon passeport.', 'Ich habe meinen Reisepass verloren.', 'Ho perso il passaporto.'),
        ('Appelez la police !', 'Rufen Sie die Polizei!', 'Chiami la polizia!'),
    ]),
    ('Imprévus et dépannage', 'Pannes, changements de programme, bagages et documents', [
        ('Il y a un problème avec ma réservation.', 'Es gibt ein Problem mit meiner Reservierung.', 'C’è un problema con la mia prenotazione.'),
        ('Il n’y a pas d’eau chaude.', 'Es gibt kein warmes Wasser.', 'Non c’è acqua calda.'),
        ('La climatisation ne fonctionne pas.', 'Die Klimaanlage funktioniert nicht.', 'L’aria condizionata non funziona.'),
        ('J’ai besoin d’un nouveau billet.', 'Ich brauche eine neue Fahrkarte.', 'Ho bisogno di un nuovo biglietto.'),
        ('Pouvez-vous m’aider à retrouver mon sac ?', 'Können Sie mir helfen, meine Tasche wiederzufinden?', 'Può aiutarmi a ritrovare la mia borsa?'),
        ('Je souhaite changer ma réservation.', 'Ich möchte meine Reservierung ändern.', 'Vorrei modificare la mia prenotazione.'),
        ('Où se trouve le consulat ?', 'Wo befindet sich das Konsulat?', 'Dove si trova il consolato?'),
        ('Pouvez-vous appeler la réception ?', 'Können Sie bitte die Rezeption anrufen?', 'Può chiamare la reception, per favore?'),
    ]),
]

# MI ESPAÑOL V6.3 · Guide A1++ de 30 jours, 15 situations et 4 langues de travail.
# La liste V6.2 (allemand/italien) est conservée à l'identique dans les 10 premiers modules.
# Chaque phrase est maintenant (français, allemand, italien, anglais).
EN_CORE = [
 [
   'Hello!', 'Excuse me.', 'Do you speak English?', "I don't understand.",
   'Could you repeat that, please?', 'Could you speak more slowly, please?', 'Thank you very much.',
 ],
 [
   'How much does it cost?', 'What time does it start?', 'Could you write it down?',
   'Can I pay by card?', 'Where is the nearest ATM?', 'Is it open today?',
   "I'd like a receipt, please.",
 ],
 [
   "I'd like a bottle of water.", 'The bill, please.', 'Do you have a menu in English?',
   "I'm vegetarian.", "I'm allergic to nuts.", 'Where is the toilet?',
   'To take away, please.',
 ],
 [
   'I have a reservation.', 'I have lost my room key.', 'Where is the lift?',
   "My room key card doesn't work.", 'Could I have a replacement key, please?',
   'The lift is out of order.', "I'm stuck in the lift.",
   'Where can I leave my luggage?',
 ],
 [
   'One ticket, please.', 'Where is the platform?', 'Does this train go to the main station?',
   'I missed my train.', 'Is the train delayed?', 'Where is the bus stop?',
   "My luggage hasn't arrived.", 'Could you call a taxi, please?',
 ],
 [
   'Where is this address?', "I'm looking for my keys.", 'Where can I find a phone charger?',
   'Which floor is it on?', 'Should I turn left or right?', 'Is it far on foot?',
   "I've lost my phone.", 'Where is the lost property office?',
 ],
 [
   "I'm looking for a pharmacy.", 'Do you have a larger size?', 'Can I try it on?',
   "I'd like to return this item.", "It doesn't work.",
   'Where can I buy a SIM card?', 'Do you accept cash?',
 ],
 [
   "I'd like to book for two people.", 'Where can I buy tickets?', 'Is it free?',
   'What will the weather be like tomorrow?', "What's the Wi-Fi password?",
   'What time do you close?', 'May I take a photo here?',
 ],
 [
   'I need help.', 'Call an ambulance!', 'I need a doctor.',
   'I have severe pain here.', "I'm allergic to this medicine.",
   'My bag has been stolen.', "I've lost my passport.", 'Call the police!',
 ],
 [
   'There is a problem with my booking.', 'There is no hot water.',
   "The air conditioning doesn't work.", 'I need a new ticket.',
   'Could you help me find my bag?', "I'd like to change my booking.",
   'Where is the consulate?', 'Could you call reception, please?',
 ],
]

# Les ajouts enrichissent les 10 missions déjà acquises, sans changer leurs identifiants.
# Format : français | allemand poli | italien poli | anglais courant.
_EXTRA_RAW = [
'''Bonsoir, avez-vous un moment ?|Guten Abend, haben Sie einen Moment Zeit?|Buonasera, ha un momento?|Good evening, do you have a moment?
Je parle seulement un peu allemand / italien / anglais.|Ich spreche nur ein wenig Deutsch.|Parlo solo un po' di italiano.|I only speak a little English.
Pouvez-vous me montrer sur votre téléphone ?|Können Sie es mir auf Ihrem Handy zeigen?|Può mostrarmelo sul suo telefono?|Could you show me on your phone?
Comment dit-on cela dans votre langue ?|Wie sagt man das auf Deutsch?|Come si dice in italiano?|How do you say that in English?
Je viens de France.|Ich komme aus Frankreich.|Vengo dalla Francia.|I'm from France.
Je suis ici pour un mois.|Ich bin für einen Monat hier.|Sono qui per un mese.|I'm here for a month.
Je ne parle pas bien cette langue.|Ich spreche diese Sprache nicht gut.|Non parlo bene questa lingua.|I don't speak this language very well.
Puis-je vous poser une question ?|Darf ich Ihnen eine Frage stellen?|Posso farle una domanda?|May I ask you a question?''',
'''Pouvez-vous me donner la monnaie ?|Können Sie mir bitte Wechselgeld geben?|Può darmi il resto, per favore?|Could you give me my change, please?
Puis-je avoir une facture ?|Kann ich bitte eine Rechnung bekommen?|Posso avere una fattura, per favore?|Could I have an invoice, please?
Où puis-je changer de l'argent ?|Wo kann ich Geld wechseln?|Dove posso cambiare dei soldi?|Where can I exchange money?
Mon paiement a été refusé.|Meine Zahlung wurde abgelehnt.|Il mio pagamento è stato rifiutato.|My payment was declined.
Ma carte a été avalée par le distributeur.|Der Geldautomat hat meine Karte eingezogen.|Il bancomat ha trattenuto la mia carta.|The ATM has kept my card.
Combien de temps faut-il attendre ?|Wie lange muss man warten?|Quanto tempo bisogna aspettare?|How long is the wait?
Est-ce compris dans le prix ?|Ist das im Preis inbegriffen?|È compreso nel prezzo?|Is that included in the price?
Est-ce qu'il y a une réduction ?|Gibt es einen Rabatt?|C'è uno sconto?|Is there a discount?''',
'''Une table pour une personne, s'il vous plaît.|Einen Tisch für eine Person, bitte.|Un tavolo per una persona, per favore.|A table for one, please.
Je ne mange pas de viande.|Ich esse kein Fleisch.|Non mangio carne.|I don't eat meat.
Est-ce que ce plat contient du lait ?|Enthält dieses Gericht Milch?|Questo piatto contiene latte?|Does this dish contain milk?
Pouvez-vous faire ce plat sans gluten ?|Können Sie dieses Gericht ohne Gluten zubereiten?|Può preparare questo piatto senza glutine?|Can you make this dish gluten-free?
Puis-je avoir de l'eau du robinet ?|Kann ich Leitungswasser haben?|Posso avere dell'acqua del rubinetto?|Could I have tap water?
Ce n'est pas ce que j'ai commandé.|Das habe ich nicht bestellt.|Non è quello che ho ordinato.|This isn't what I ordered.
Où est le supermarché le plus proche ?|Wo ist der nächste Supermarkt?|Dov'è il supermercato più vicino?|Where is the nearest supermarket?''',
'''Le chauffage ne fonctionne pas.|Die Heizung funktioniert nicht.|Il riscaldamento non funziona.|The heating isn't working.
La chambre est trop bruyante.|Das Zimmer ist zu laut.|La camera è troppo rumorosa.|The room is too noisy.
Puis-je changer de chambre ?|Kann ich das Zimmer wechseln?|Posso cambiare camera?|Can I change rooms?
À quelle heure dois-je quitter la chambre ?|Bis wann muss ich auschecken?|A che ora devo lasciare la camera?|What time is check-out?
Y a-t-il des escaliers ?|Gibt es eine Treppe?|Ci sono delle scale?|Are there any stairs?
Pouvez-vous m'aider à porter ma valise ?|Können Sie mir mit meinem Koffer helfen?|Può aiutarmi con la valigia?|Could you help me with my suitcase?
Je suis bloqué dehors.|Ich habe mich ausgesperrt.|Sono rimasto/a chiuso/a fuori.|I'm locked out.''',
'''Où se trouve la porte d'embarquement ?|Wo ist das Abfluggate?|Dov'è il gate d'imbarco?|Where is the boarding gate?
À quelle heure part le prochain bus ?|Wann fährt der nächste Bus ab?|A che ora parte il prossimo autobus?|When is the next bus?
Dois-je changer de train ?|Muss ich umsteigen?|Devo cambiare treno?|Do I need to change trains?
Où puis-je acheter un pass de transport ?|Wo kann ich eine Tageskarte kaufen?|Dove posso comprare un abbonamento per i mezzi?|Where can I buy a transport pass?
Ce siège est-il libre ?|Ist dieser Platz frei?|Questo posto è libero?|Is this seat free?
J'ai oublié un objet dans le taxi.|Ich habe etwas im Taxi vergessen.|Ho dimenticato qualcosa nel taxi.|I left something in the taxi.
Je dois aller à cette adresse.|Ich muss zu dieser Adresse.|Devo andare a questo indirizzo.|I need to go to this address.''',
'''Pouvez-vous me l'indiquer sur la carte ?|Können Sie es mir auf der Karte zeigen?|Può indicarmelo sulla mappa?|Could you show me on the map?
Comment aller au centre-ville ?|Wie komme ich ins Stadtzentrum?|Come arrivo in centro?|How do I get to the city centre?
Y a-t-il un passage piéton ?|Gibt es einen Zebrastreifen?|C'è un attraversamento pedonale?|Is there a pedestrian crossing?
Est-ce accessible en fauteuil roulant ?|Ist das rollstuhlgerecht?|È accessibile in sedia a rotelle?|Is it wheelchair accessible?
Je crois que je suis perdu(e).|Ich glaube, ich habe mich verlaufen.|Credo di essermi perso/a.|I think I'm lost.
Pouvez-vous m'indiquer une rue plus calme ?|Können Sie mir eine ruhigere Straße zeigen?|Può indicarmi una strada più tranquilla?|Could you point me towards a quieter street?
J'ai trouvé un objet, où puis-je le déposer ?|Ich habe etwas gefunden. Wo kann ich es abgeben?|Ho trovato un oggetto. Dove posso consegnarlo?|I found something. Where can I hand it in?''',
'''Où est le bureau de poste ?|Wo ist die Post?|Dov'è l'ufficio postale?|Where is the post office?
Je cherche une batterie externe.|Ich suche eine Powerbank.|Cerco un caricabatterie portatile.|I'm looking for a power bank.
Je cherche un adaptateur de prise.|Ich suche einen Steckdosenadapter.|Cerco un adattatore per la presa elettrica.|I'm looking for a plug adapter.
Y a-t-il une prise électrique ?|Gibt es eine Steckdose?|C'è una presa elettrica?|Is there a power socket?
Puis-je recevoir un colis ici ?|Kann ich hier ein Paket empfangen?|Posso ricevere un pacco qui?|Can I receive a parcel here?
Cet article est-il sous garantie ?|Hat dieser Artikel Garantie?|Questo articolo è in garanzia?|Is this item under warranty?
Je cherche une laverie automatique.|Ich suche einen Waschsalon.|Cerco una lavanderia a gettoni.|I'm looking for a laundrette.
Pouvez-vous m'aider à utiliser cette machine ?|Können Sie mir helfen, dieses Gerät zu benutzen?|Può aiutarmi a usare questa macchina?|Could you help me use this machine?''',
'''Dois-je réserver à l'avance ?|Muss ich im Voraus reservieren?|Devo prenotare in anticipo?|Do I need to book in advance?
Y a-t-il des places disponibles ?|Sind noch Plätze frei?|Ci sono ancora posti disponibili?|Are there any places available?
Puis-je recharger mon téléphone ici ?|Kann ich mein Handy hier aufladen?|Posso ricaricare il telefono qui?|Can I charge my phone here?
Où est l'entrée ?|Wo ist der Eingang?|Dov'è l'ingresso?|Where is the entrance?
Où est la sortie ?|Wo ist der Ausgang?|Dov'è l'uscita?|Where is the exit?
Peut-on louer un vélo ici ?|Kann man hier ein Fahrrad mieten?|Si può noleggiare una bicicletta qui?|Can I hire a bicycle here?
Est-ce adapté aux enfants ?|Ist das für Kinder geeignet?|È adatto ai bambini?|Is it suitable for children?
Y a-t-il une visite guidée en anglais ?|Gibt es eine Führung auf Englisch?|C'è una visita guidata in inglese?|Is there a guided tour in English?''',
'''Je me sens mal.|Mir geht es nicht gut.|Non mi sento bene.|I feel unwell.
J'ai de la fièvre.|Ich habe Fieber.|Ho la febbre.|I have a fever.
J'ai perdu mon portefeuille.|Ich habe mein Portemonnaie verloren.|Ho perso il portafoglio.|I've lost my wallet.
Où est l'hôpital le plus proche ?|Wo ist das nächste Krankenhaus?|Dov'è l'ospedale più vicino?|Where is the nearest hospital?
J'ai besoin de médicaments.|Ich brauche Medikamente.|Ho bisogno di medicine.|I need some medicine.
Je suis diabétique.|Ich habe Diabetes.|Ho il diabete.|I have diabetes.
Mon enfant a besoin d'aide.|Mein Kind braucht Hilfe.|Mio figlio / mia figlia ha bisogno di aiuto.|My child needs help.
J'ai besoin d'un interprète.|Ich brauche einen Dolmetscher / eine Dolmetscherin.|Ho bisogno di un interprete.|I need an interpreter.''',
'''Le Wi-Fi ne fonctionne pas.|Das WLAN funktioniert nicht.|Il Wi-Fi non funziona.|The Wi-Fi isn't working.
Mon téléphone n'a plus de batterie.|Der Akku meines Handys ist leer.|Il telefono è scarico.|My phone has run out of battery.
Il manque une serviette.|Ein Handtuch fehlt.|Manca un asciugamano.|A towel is missing.
Il y a une fuite d'eau.|Es gibt ein Wasserleck.|C'è una perdita d'acqua.|There's a water leak.
La fenêtre ne se ferme pas.|Das Fenster lässt sich nicht schließen.|La finestra non si chiude.|The window won't close.
Pourriez-vous venir voir le problème ?|Könnten Sie sich das Problem bitte ansehen?|Potrebbe venire a vedere il problema?|Could you come and take a look at the problem?
Est-ce que je peux être remboursé(e) ?|Kann ich eine Rückerstattung bekommen?|Posso ottenere un rimborso?|Can I get a refund?''',
]

# Cinq missions additionnelles qui complètent les anciens acquis pour couvrir un séjour d'un mois.
_NEW_RAW = [
('Arrivée et aéroport', 'Documents, bagages, guichets et contrôle', '''Voici mon passeport.|Hier ist mein Reisepass.|Ecco il mio passaporto.|Here is my passport.
Voici mon billet électronique.|Hier ist mein elektronisches Ticket.|Ecco il mio biglietto elettronico.|Here is my e-ticket.
Où se trouve l'enregistrement ?|Wo ist der Check-in-Schalter?|Dov'è il banco del check-in?|Where is the check-in desk?
Mon vol est annulé.|Mein Flug wurde gestrichen.|Il mio volo è stato cancellato.|My flight has been cancelled.
Où puis-je récupérer mes bagages ?|Wo kann ich mein Gepäck abholen?|Dove posso ritirare i bagagli?|Where can I collect my luggage?
Je n'ai qu'un bagage à main.|Ich habe nur Handgepäck.|Ho solo un bagaglio a mano.|I only have hand luggage.
Où est le contrôle de sécurité ?|Wo ist die Sicherheitskontrolle?|Dov'è il controllo di sicurezza?|Where is security screening?
Où puis-je faire une déclaration de perte ?|Wo kann ich eine Verlustmeldung machen?|Dove posso fare una denuncia di smarrimento?|Where can I report a lost item?
Combien de temps dure l'escale ?|Wie lange dauert der Zwischenstopp?|Quanto dura lo scalo?|How long is the stopover?
Pouvez-vous m'aider avec ce formulaire ?|Können Sie mir bei diesem Formular helfen?|Può aiutarmi con questo modulo?|Could you help me with this form?'''),
('Appartement et vie quotidienne', 'Location, ménage, linge, voisins et équipements', '''Je loue cet appartement pour un mois.|Ich habe diese Wohnung für einen Monat gemietet.|Ho affittato questo appartamento per un mese.|I'm renting this flat for a month.
Où sont les poubelles ?|Wo sind die Mülltonnen?|Dove sono i bidoni della spazzatura?|Where are the bins?
Comment fonctionne la machine à laver ?|Wie funktioniert die Waschmaschine?|Come funziona la lavatrice?|How does the washing machine work?
Où puis-je acheter de la lessive ?|Wo kann ich Waschmittel kaufen?|Dove posso comprare il detersivo?|Where can I buy laundry detergent?
Il n'y a plus de papier toilette.|Das Toilettenpapier ist alle.|È finita la carta igienica.|We've run out of toilet paper.
Comment ouvrir cette porte ?|Wie öffne ich diese Tür?|Come si apre questa porta?|How do I open this door?
L'électricité est coupée.|Der Strom ist ausgefallen.|È saltata la corrente.|The power has gone out.
Où est le compteur d'eau ?|Wo ist der Wasserzähler?|Dov'è il contatore dell'acqua?|Where is the water meter?
Puis-je utiliser la cuisine ?|Darf ich die Küche benutzen?|Posso usare la cucina?|Can I use the kitchen?
Je dois joindre le propriétaire.|Ich muss den Vermieter kontaktieren.|Devo contattare il proprietario.|I need to contact the landlord. '''),
('Voiture et déplacements', 'Location, stationnement, carburant et petites pannes', '''Je voudrais louer une voiture.|Ich möchte ein Auto mieten.|Vorrei noleggiare un'auto.|I'd like to hire a car.
Où puis-je me garer ?|Wo kann ich parken?|Dove posso parcheggiare?|Where can I park?
Le parking est-il payant ?|Ist das Parken hier kostenpflichtig?|Il parcheggio è a pagamento?|Do I have to pay to park here?
Je cherche une station-service.|Ich suche eine Tankstelle.|Cerco un distributore di benzina.|I'm looking for a petrol station.
Quel carburant dois-je utiliser ?|Welchen Kraftstoff muss ich tanken?|Quale carburante devo usare?|Which fuel should I use?
La voiture ne démarre pas.|Das Auto springt nicht an.|L'auto non parte.|The car won't start.
J'ai un pneu crevé.|Ich habe einen platten Reifen.|Ho una gomma a terra.|I have a flat tyre.
J'ai besoin d'une dépanneuse.|Ich brauche einen Abschleppwagen.|Ho bisogno di un carro attrezzi.|I need a tow truck.
J'ai eu un petit accident.|Ich hatte einen kleinen Unfall.|Ho avuto un piccolo incidente.|I've had a minor accident.
Où est l'agence de location ?|Wo ist die Autovermietung?|Dov'è l'agenzia di autonoleggio?|Where is the car rental office?'''),
('Loisirs, plage et excursions', 'Promenades, nature, billets et sécurité', '''Où commence le sentier ?|Wo beginnt der Wanderweg?|Dove inizia il sentiero?|Where does the trail start?
Combien de temps dure la promenade ?|Wie lange dauert die Wanderung?|Quanto dura la passeggiata?|How long does the walk take?
Est-ce dangereux de nager ici ?|Ist es gefährlich, hier zu schwimmen?|È pericoloso nuotare qui?|Is it dangerous to swim here?
Où peut-on louer un parasol ?|Wo kann man einen Sonnenschirm mieten?|Dove posso noleggiare un ombrellone?|Where can I hire a beach umbrella?
Je cherche un endroit à l'ombre.|Ich suche einen Platz im Schatten.|Cerco un posto all'ombra.|I'm looking for somewhere in the shade.
La plage est-elle surveillée ?|Ist dieser Strand bewacht?|Questa spiaggia è sorvegliata?|Is there a lifeguard on this beach?
Où se trouve le point de rendez-vous ?|Wo ist der Treffpunkt?|Dov'è il punto d'incontro?|Where is the meeting point?
J'ai besoin d'eau potable.|Ich brauche Trinkwasser.|Ho bisogno di acqua potabile.|I need drinking water.
Le chemin est-il ouvert ?|Ist der Weg geöffnet?|Il sentiero è aperto?|Is the trail open?
Pouvez-vous prendre une photo de nous ?|Können Sie ein Foto von uns machen?|Può farci una foto?|Could you take a photo of us?'''),
('Fin du séjour et retour', 'Départ, bagages, colis, remboursements et remerciements', '''Je pars demain matin.|Ich reise morgen früh ab.|Parto domani mattina.|I'm leaving tomorrow morning.
Puis-je laisser mes bagages ici jusqu'à ce soir ?|Kann ich mein Gepäck bis heute Abend hier lassen?|Posso lasciare qui i bagagli fino a stasera?|Can I leave my luggage here until this evening?
Je voudrais envoyer un colis en France.|Ich möchte ein Paket nach Frankreich schicken.|Vorrei spedire un pacco in Francia.|I'd like to send a parcel to France.
Où puis-je acheter un timbre ?|Wo kann ich eine Briefmarke kaufen?|Dove posso comprare un francobollo?|Where can I buy a stamp?
Puis-je récupérer ma caution ?|Kann ich meine Kaution zurückbekommen?|Posso riavere la cauzione?|Can I get my deposit back?
J'ai besoin d'une facture finale.|Ich brauche eine Schlussrechnung.|Ho bisogno di una fattura finale.|I need a final invoice.
Pouvez-vous m'indiquer l'itinéraire le plus rapide vers l'aéroport ?|Können Sie mir den schnellsten Weg zum Flughafen zeigen?|Può indicarmi il percorso più veloce per l'aeroporto?|Could you show me the quickest route to the airport?
Où dois-je rendre la clé ?|Wo muss ich den Schlüssel abgeben?|Dove devo restituire la chiave?|Where should I return the key?
Merci pour votre accueil !|Vielen Dank für Ihre Gastfreundschaft!|Grazie per l'ospitalità!|Thank you for your hospitality!
J'ai passé un excellent séjour.|Ich hatte einen wunderschönen Aufenthalt.|Ho trascorso un soggiorno bellissimo.|I've had a wonderful stay.'''),
]

def _parse_translations(raw):
    result=[]
    for line in raw.strip().splitlines():
        fields=tuple(field.strip() for field in line.split('|'))
        if len(fields)!=4 or not all(fields):
            raise ValueError(f'Phrase invalide : {line!r}')
        result.append(fields)
    return result

assert len(EN_CORE)==len(TRAVEL_GUIDE)==10
_OLD_GUIDE=TRAVEL_GUIDE
TRAVEL_GUIDE=[]
for _idx, (_name,_description,_phrases) in enumerate(_OLD_GUIDE):
    if len(_phrases)!=len(EN_CORE[_idx]):
        raise ValueError('Traductions anglaises manquantes : '+_name)
    _full=[(*_phrase,EN_CORE[_idx][_j]) for _j,_phrase in enumerate(_phrases)]
    _full.extend(_parse_translations(_EXTRA_RAW[_idx]))
    TRAVEL_GUIDE.append((_name,_description,_full))
for _name,_description,_raw in _NEW_RAW:
    TRAVEL_GUIDE.append((_name,_description,_parse_translations(_raw)))

# V6.7 : 200 phrases supplémentaires, distribuées dans les 15 missions.
# Les 200 premières conservent leur index : les cartes de répétition espacée
# et toutes les réussites des anciennes versions restent donc valides.
_ORIGINAL_COUNTS=[len(phrases) for _,_,phrases in TRAVEL_GUIDE]
assert len(TRAVEL_GUIDE)==len(SUPPLEMENTS)==15
TRAVEL_GUIDE=[(title,description,phrases+SUPPLEMENTS[i])
              for i,(title,description,phrases) in enumerate(TRAVEL_GUIDE)]

MISSIONS=[(title,description,phrases[0],phrases[1]) for title,description,phrases in TRAVEL_GUIDE]
GUIDE_DAYS=len(MISSIONS)*2
TOTAL_EXPRESSIONS=sum(len(rows) for _,_,rows in TRAVEL_GUIDE)
assert len(MISSIONS)==15 and GUIDE_DAYS==30
assert len(_OLD_GUIDE)==10
assert TOTAL_EXPRESSIONS==400 and all(len(group)>=15 for _,_,group in TRAVEL_GUIDE)

# Révisions intercalées : les acquis de 1, 3 et 6 missions auparavant sont sollicités.
# Révision accessible dès le jour 2 de la mission, sans date limite.
def mixed_review(mission_index, max_items=2):
    if mission_index <= 0:return []
    sources=[]
    for ago in (1,3,6,mission_index):
        previous=mission_index-ago
        if previous>=0 and previous not in sources:
            sources.append(previous)
    results=[]
    for source in sources[:max_items]:
        group=TRAVEL_GUIDE[source][2]
        phrase=group[(mission_index+source*3)%len(group)]
        results.append((source,phrase))
    return results

# Examen court : 3 phrases historiques + 3 expressions nouvelles V6.7,
# et 2 rappels intercalés. Les 400 cartes sont ensuite mélangées par le SRS.
def mission_questions(mission_index):
    phrases=TRAVEL_GUIDE[mission_index][2]
    old_size=_ORIGINAL_COUNTS[mission_index]
    extras=len(phrases)-old_size
    assert extras>=3
    indices=[1,4,7,old_size,old_size+extras//2,len(phrases)-1]
    core=[(mission_index,phrases[k]) for k in indices]
    return core+mixed_review(mission_index)



# Mini-jeux d'entretien (une fois les 15 missions validées).
# Un item = une expression précise du guide. Les dates de rappel appartiennent au
# profil JSON pour rester compatibles avec les sauvegardes V2 à V6.5.
REVIEW_DELAYS=(1,3,7,14,30,60)  # jours après réussites successives
REVIEW_TRACKS=('travel_german','travel_italian','travel_english')
REVIEW_FORMATS=('traduction','compréhension','situation','traduction','compréhension')


def review_card_ids():
    return [(m,i) for m,(_,_,phrases) in enumerate(TRAVEL_GUIDE) for i in range(len(phrases))]


def review_due(section, today):
    """Cartes à reprendre maintenant; les nouvelles expressions sont dues immédiatement."""
    state=p.get('review_cards',{}).get(section,{})
    known, unseen=[] , []
    for mission,i in review_card_ids():
        key=f'{mission}:{i}'
        record=state.get(key)
        if not isinstance(record,dict):
            unseen.append((mission,i));continue
        raw=record.get('due','')
        try: target=date.fromisoformat(raw)
        except (ValueError,TypeError): target=today
        if target<=today: known.append((mission,i))
    return known,unseen


def diverse_sample(items,amount):
    """Varie les missions et les expressions avant de compléter si nécessaire."""
    remaining=items[:]
    random.shuffle(remaining)
    result=[];used_missions=set()
    for item in remaining:
        if item[0] not in used_missions and len(result)<amount:
            result.append(item);used_missions.add(item[0])
    for item in remaining:
        if len(result)>=amount:break
        if item not in result:result.append(item)
    return result


def make_review_deck(section,language_index,today,free=False,limit=5):
    """Sélection aléatoire stable pendant le quiz; anciens acquis + nouvelles cartes."""
    reviewed,unseen=review_due(section,today)
    if free:
        chosen=diverse_sample(review_card_ids(),limit)
    else:
        # Si possible : 2 cartes déjà étudiées et 3 encore neuves.
        chosen=diverse_sample(reviewed,min(2,len(reviewed),limit))
        remaining=limit-len(chosen)
        chosen+=diverse_sample([x for x in unseen if x not in chosen],remaining)
        remaining=limit-len(chosen)
        if remaining:chosen+=diverse_sample([x for x in reviewed if x not in chosen],remaining)
    if not chosen:return None
    formats=list(REVIEW_FORMATS)
    random.shuffle(formats)
    deck=[]
    for i,(mission,phrase_idx) in enumerate(chosen):
        phrase=TRAVEL_GUIDE[mission][2][phrase_idx]
        kind=formats[i%len(formats)]
        if kind=='compréhension':
            correct=phrase[0]
            distractors=[p[0] for _,_,items in TRAVEL_GUIDE for p in items if p[0]!=correct]
            question=f'🧠 Que signifie « {phrase[language_index]} » ?'
        else:
            correct=phrase[language_index]
            distractors=[p[language_index] for _,_,items in TRAVEL_GUIDE for p in items if p[language_index]!=correct]
            if kind=='situation':
                question=f'🧳 En voyage · {TRAVEL_GUIDE[mission][0]} : que dire pour « {phrase[0]} » ?'
            else:
                question=f'🎯 Comment dire « {phrase[0]} » ?'
        pool=list(dict.fromkeys(distractors))
        options=[correct]+random.sample(pool,min(2,len(pool)))
        random.shuffle(options)
        deck.append({'key':f'{mission}:{phrase_idx}','mission':mission,'phrase':phrase_idx,
                     'kind':kind,'question':question,'options':options,'correct':correct,
                     'translation':phrase[language_index],'french':phrase[0]})
    return {'id':str(random.randrange(1,10**12)),'mode':'libre' if free else 'espacé',
            'cards':deck,'finished':False,'results':[],'date':today.isoformat()}


def apply_review_result(section,deck,answers,today):
    """Planifie 1, 3, 7, 14, 30 puis 60 jours; erreurs revues demain.
    Une série n'est notée qu'une seule fois; aucun acquis ni étoile retiré.
    """
    if deck.get('finished'):return None
    if len(answers)!=len(deck['cards']) or any(x is None for x in answers):return None
    state=p.setdefault('review_cards',{}).setdefault(section,{})
    results=[]
    for card,answer in zip(deck['cards'],answers):
        correct=(answer==card['correct'])
        record=state.get(card['key'])
        if not isinstance(record,dict):record={}
        if deck['mode']=='espacé':
            streak=max(0,min(int(record.get('streak',0)),len(REVIEW_DELAYS)))
            streak=min(streak+1,len(REVIEW_DELAYS)) if correct else 0
            days=REVIEW_DELAYS[streak-1] if correct else 1
            state[card['key']]={'streak':streak,'due':(today+timedelta(days=days)).isoformat(),
                 'seen':int(record.get('seen',0))+1,'last':today.isoformat(),
                 'correct':int(record.get('correct',0))+(1 if correct else 0)}
        results.append({'correct':correct,'answer':answer,'expected':card['correct'],
                        'french':card['french'],'translated':card['translation']})
    stats=p.setdefault('review_stats',{}).setdefault(section,{})
    stats['sessions']=int(stats.get('sessions',0))+1
    stats['answers']=int(stats.get('answers',0))+len(answers)
    stats['correct']=int(stats.get('correct',0))+sum(x['correct'] for x in results)
    stats['last']=today.isoformat()
    deck['finished']=True;deck['results']=results
    p['last_language']={'travel_german':'🇩🇪 Allemand',
                        'travel_italian':'🇮🇹 Italien',
                        'travel_english':'🇬🇧 Anglais'}[section]
    persist()
    return results


def render_review_corner(section,language_index,today):
    """Section Streamlit à afficher une fois le guide intégral acquis."""
    st.markdown('### 🎲 Mes révisions surprises')
    total=done_count(section,[str(i) for i in range(len(MISSIONS))])
    if total<len(MISSIONS):
        st.info(f'🔒 Cette salle de révision s’ouvre après les 15 missions. Encore {len(MISSIONS)-total} mission(s) à valider. Les rappels des anciennes missions sont déjà inclus dans leurs quiz.')
        return
    st.success('🏆 Guide terminé ! Place aux mini-jeux pour garder tes réflexes en voyage.')
    reviewed,unseen=review_due(section,today)
    state=p.get('review_cards',{}).get(section,{})
    mastered=sum(isinstance(row,dict) and int(row.get('streak',0))>=3 for row in state.values())
    col1,col2,col3=st.columns(3)
    col1.metric('⏰ Cartes à revoir',len(reviewed))
    col2.metric('🌱 Phrases à découvrir',len(unseen))
    col3.metric('🏅 Bien mémorisées',f'{mastered}/{TOTAL_EXPRESSIONS}')
    st.caption('Révisions espacées : **J+1, J+3, J+7, J+14, J+30 puis J+60** après des réussites successives. Si tu te trompes, la phrase revient le lendemain, sans pénalité. Libre à toi de jouer plus ou moins souvent.')
    key='review_deck_'+section
    deck=st.session_state.get(key)
    if deck is None:
        c1,c2=st.columns(2)
        with c1:
            if st.button('🎯 Révision du jour · 5 questions',key='start_due_'+section,
                         disabled=not (reviewed or unseen),type='primary',use_container_width=True):
                st.session_state[key]=make_review_deck(section,language_index,today)
                st.rerun()
        with c2:
            if st.button('🌈 Jeu libre · 5 surprises',key='start_free_'+section,use_container_width=True):
                st.session_state[key]=make_review_deck(section,language_index,today,free=True)
                st.rerun()
        if not (reviewed or unseen):
            next_due=[]
            for item in state.values():
                if isinstance(item,dict):
                    try:next_due.append(date.fromisoformat(item.get('due','')))
                    except (ValueError,TypeError):pass
            if next_due:st.info('👏 Aucun rappel en attente ! Prochaine révision prévue : '+min(next_due).strftime('%d/%m/%Y')+'. Tu peux jouer librement en attendant.')
        else:
            st.caption(f'📌 {len(reviewed)+len(unseen)} expression(s) disponibles aujourd’hui. Les 15 thèmes se mélangent aléatoirement.')
        return
    st.caption('🎴 Série de '+str(len(deck['cards']))+' défis · '+('Répétition espacée' if deck['mode']=='espacé' else 'Révision libre, dates inchangées'))
    if deck.get('finished'):
        score=sum(item['correct'] for item in deck['results'])
        st.success(f'✨ Bravo pour ta révision ! **{score}/{len(deck["results"])}** · même les erreurs t’aident à progresser.')
        for item in deck['results']:
            icon='✅' if item['correct'] else '🌱'
            st.markdown(f'{icon} **{item["french"]}** → {item["translated"]}')
        if st.button('🎲 Une autre mini-révision',key='another_'+section,use_container_width=True):
            st.session_state[key]=None;st.rerun()
        return
    with st.form('review_form_'+section+'_'+deck['id']):
        answers=[]
        for i,card in enumerate(deck['cards'],1):
            answers.append(st.radio(f'{i}. {card["question"]}',card['options'],index=None,
                                    key=f'review_ans_{section}_{deck["id"]}_{i}'))
        submitted=st.form_submit_button('✨ Corriger ma mini-révision',type='primary',use_container_width=True)
    if submitted:
        result=apply_review_result(section,deck,answers,today)
        if result is None:st.warning('Choisis une réponse à chaque question pour terminer ton mini-jeu.')
        else:
            score=sum(x['correct'] for x in result)
            st.success(f'🎉 {score}/{len(result)} ! Les prochains rappels sont enregistrés dans ton profil.')
            for item in result:
                if not item['correct']:
                    st.caption('🌱 À retenir : '+item['french']+' → '+item['translated'])
            st.rerun()  # Affiche immédiatement le bilan et le bouton Nouvelle série.


def new_profile():
    return {'version':67,'name':'Élève','grade':0,'school':{},'school_exams':{},
            'cefr':{},'cefr_exams':{},'grammar':{},'grammar_exams':{},
            'verbs':{},'tenses':{},'conjugation':{},'german':{},'italian':{},'english':{},
            'travel_german':{},'travel_italian':{},'travel_english':{},
            'llcer':{},'notes':{},'stars':0,'legacy_spanish':{},'last_language':'',
            'forecast_sessions':{},'validation_log':[],
            'review_cards':{},'review_stats':{}}


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
    default['version']=67
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
    # Une réponse réussie compte comme activité même lors d'une révision.
    p['last_language']={'travel_german':'🇩🇪 Allemand',
                        'travel_italian':'🇮🇹 Italien',
                        'travel_english':'🇬🇧 Anglais'}.get(section,'🇪🇸 Espagnol')
    if p[section].get(key) is True:
        persist()
        return False
    p[section][key]=True
    p['stars']+=points
    if section in ('cefr','cefr_exams','school','school_exams','grammar','grammar_exams',
                   'verbs','tenses','travel_german','travel_italian','travel_english'):
        p.setdefault('validation_log',[]).append({
            'day':datetime.now(ZoneInfo('Europe/Paris')).date().isoformat(),
            'section':section,'key':str(key)})
        p['validation_log']=p['validation_log'][-400:]
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


# Statistiques fondées uniquement sur les acquis validés et les étapes du programme.
# Les parcours scolaires, CECRL, grammaire, verbes et temps forment ensemble
# le parcours espagnol. La LLCER optionnelle n'entre pas dans son dénominateur.
def progress_all_languages(profile):
    # Conserver les clés réelles et ne jamais compter les clés inconnues d'un vieux JSON.
    school_keys=[school_key(g,i) for g in range(len(CLASSES)) for i in range(len(SCOLAIRE[CLASSES[g]]))]
    school_exam_keys=[str(g) for g in range(len(CLASSES))]
    cefr_keys=[cefr_key(level,i) for level in CECRL for i in range(len(CECRL[level]))]
    cefr_exam_keys=list(CECRL)
    grammar_keys=[grammar_key(level,i) for level in GRAMMAIRE for i in range(len(GRAMMAIRE[level]))]
    grammar_exam_keys=list(GRAMMAIRE)
    categories=[('school',school_keys),('school_exams',school_exam_keys),
                ('cefr',cefr_keys),('cefr_exams',cefr_exam_keys),
                ('grammar',grammar_keys),('grammar_exams',grammar_exam_keys),
                ('verbs',VERBS),('tenses',TENSE_ORDER)]
    spanish_total=sum(len(keys) for _,keys in categories)
    spanish_done=sum(sum(profile.get(bucket,{}).get(key) is True for key in keys) for bucket,keys in categories)
    accessible_cefr=unlocked_groups(profile.get('cefr_exams',{}),list(CECRL))
    cefr_label=accessible_cefr[-1] if accessible_cefr else 'A1'
    if profile.get('cefr_exams',{}).get('C2') is True:
        cefr_label='C2 validé'
    spanish_level=f"{CLASSES[profile['grade']]} · {cefr_label if cefr_label.endswith('validé') else cefr_label+' en cours'}"
    result=[{'label':'🇪🇸 Espagnol','track':'spanish','done':spanish_done,'total':spanish_total,
             'level':spanish_level,'unit':'acquis','color':'esp'}]
    for label,track,color in [('🇩🇪 Allemand','travel_german','de'),
                              ('🇮🇹 Italien','travel_italian','it'),
                              ('🇬🇧 Anglais','travel_english','en')]:
        total=len(MISSIONS)
        done=sum(profile.get(track,{}).get(str(i)) is True for i in range(total))
        level='Guide terminé' if done==total else f'Mission {done+1}/{total} · A1++'
        result.append({'label':label,'track':track,'done':done,'total':total,
                       'level':level,'unit':'missions','color':color})
    for item in result:
        item['percent']=100*item['done']/item['total'] if item['total'] else 0.0
    return result


# Prévisions non contractuelles : 2 séances courtes par validation, configurables par langue.
# Elles concernent des jalons INTERNES au logiciel, et non une certification CECRL.
FORECAST_TRACKS=('spanish','travel_german','travel_italian','travel_english')
PACE_OPTIONS=[1,2,3,4,5,6,7,10,14]


def paris_today():
    return datetime.now(ZoneInfo('Europe/Paris')).date()


def observed_validations_per_week(profile, sections, now):
    """Rythme des validations lorsque l'historique comporte assez de jours de recul."""
    entries=[]
    for event in profile.get('validation_log',[]):
        if not isinstance(event,dict) or event.get('section') not in sections:
            continue
        try:day=date.fromisoformat(event.get('day',''))
        except (ValueError,TypeError):continue
        if 0 <= (now-day).days <= 56:
            entries.append((day,str(event.get('section')),str(event.get('key'))))
    entries=sorted(set(entries))
    if len(entries)<4 or (entries[-1][0]-entries[0][0]).days < 7:
        return None
    duration=(entries[-1][0]-entries[0][0]).days
    rate=7*(len(entries)-1)/duration
    return min(12,max(0.25,rate))


def projected_day(remaining, pace_sessions, today, observed_rate=None):
    if remaining<=0:return 'Acquis ✓'
    if observed_rate is not None:
        days=math.ceil(7*remaining/observed_rate)
    else:
        days=math.ceil(7*remaining*2/max(1,pace_sessions))
    days=min(36500,days)
    return (today+timedelta(days=days)).strftime('%d/%m/%Y')


def language_forecasts(profile, pace, today=None, use_history=False):
    today=today or paris_today()
    results={}
    # Espagnol : premier niveau CECRL dont le bilan n'a pas encore été réussi.
    upcoming=next((level for level in CECRL if profile.get('cefr_exams',{}).get(level) is not True),None)
    grade_index=max(0,min(len(CLASSES)-1,profile.get('grade',0)))
    grade=CLASSES[grade_index]
    if upcoming is None:
        cefr_title,cefr_remaining='Ateliers C2 terminés',0
    else:
        cefr_title=f'Bilan interne {upcoming}'
        cefr_remaining=(sum(profile.get('cefr',{}).get(f'{upcoming}:{i}') is not True
                             for i in range(len(CECRL[upcoming])))+1)
    school_done=sum(profile.get('school',{}).get(f'{grade_index}:{i}') is True
                    for i in range(len(SCOLAIRE[grade])))
    school_remaining=(len(SCOLAIRE[grade])-school_done+
                      (0 if profile.get('school_exams',{}).get(str(grade_index)) is True else 1))
    school_title=f'Bilan de {grade}' if grade_index==len(CLASSES)-1 else f'Passage {grade} → {CLASSES[grade_index+1]}'
    rate_es=observed_validations_per_week(profile, {'school','school_exams','cefr','cefr_exams'},today) if use_history else None
    results['spanish']={
       'items':[(cefr_title,projected_day(cefr_remaining,pace['spanish'],today,rate_es)),
                (school_title,projected_day(school_remaining,pace['spanish'],today,rate_es))],
       'source':'rythme constaté' if rate_es is not None else 'rythme choisi'}
    # Voyages : jalons de 5, 10 puis 15 missions, sans prétention de niveau CECRL.
    for track in FORECAST_TRACKS[1:]:
        n=sum(profile.get(track,{}).get(str(i)) is True for i in range(len(MISSIONS)))
        target=next((x for x in (5,10,len(MISSIONS)) if n<x),None)
        rate=observed_validations_per_week(profile,{track},today) if use_history else None
        if target is None:
            rows=[('Guide de voyage terminé','Acquis ✓')]
        else:
            title='Guide complet de survie' if target==len(MISSIONS) else f'Palier {target} missions'
            rows=[(title,projected_day(target-n,pace[track],today,rate))]
        results[track]={'items':rows,
                        'source':'rythme constaté' if rate is not None else 'rythme choisi'}
    return results


def render_language_progress(items,selected_language,last_language,forecasts=None):
    # La moyenne des 4 taux donne le même poids à chaque langue, indépendamment
    # de la longueur bien différente de l'école espagnole et des guides de voyage.
    global_pct=sum(item['percent'] for item in items)/len(items)
    best=max(items,key=lambda item:item['percent']) if items else None
    best_label=best['label'] if best and best['percent']>0 else 'À découvrir'
    recent=last_language if last_language in [item['label'] for item in items] else 'Non renseignée'
    head=(f'<div class="language-overview-title"><div>📊 <strong>Mes progrès par langue</strong>'
          f'<span class="language-overview-hint">Basés sur les validations · sans pression</span></div>'
          f'<div class="language-global">🌟 Progression globale <strong>{round(global_pct)} %</strong></div></div>')
    global_bar=(f'<div class="language-global-bar" role="progressbar" '
                f'aria-label="Progression globale" aria-valuenow="{round(global_pct)}" '
                f'aria-valuemin="0" aria-valuemax="100">'
                f'<div class="language-global-fill" style="width:{global_pct:.3f}%"></div></div>')
    cards=[]
    for item in items:
        pct=round(item['percent'])
        selected=' active' if item['label']==selected_language else ''
        estimate=(forecasts or {}).get(item['track'],{})
        rows=estimate.get('items',[])
        forecast_rows=''.join(
           '<div class="forecast-line"><span>🎯 '+html.escape(name)+'</span>'+
           '<strong>'+html.escape(day)+'</strong></div>' for name,day in rows)
        forecast_html=('<div class="forecast-rows">'+forecast_rows+'</div>') if forecast_rows else ''
        cards.append(f"""<div class="language-card {item['color']}{selected}">
           <div class="language-card-top"><strong>{html.escape(item['label'])}</strong>
           <span class="language-pct">{pct} %</span></div>
           <div class="language-level">{html.escape(item['level'])}</div>
           <div class="language-bar" role="progressbar" aria-label="{html.escape(item['label'],quote=True)}"
                aria-valuenow="{pct}" aria-valuemin="0" aria-valuemax="100">
             <div class="language-fill" style="width:{item['percent']:.3f}%"></div></div>
           <div class="language-count">{item['done']}/{item['total']} {item['unit']} validés</div>
           {forecast_html}
        </div>""")
    footer=f"""<div class="language-overview-footer"><span>🏅 Langue la plus avancée : <strong>{html.escape(best_label)}</strong></span>
       <span>📍 Dernière langue travaillée : <strong>{html.escape(recent)}</strong></span>
       <span class="language-overview-small">Moyenne des 4 parcours · le détail de l’espagnol comprend aussi les bilans.</span></div>"""
    return f'<section class="language-overview" aria-label="Progression des quatre langues">{head}{global_bar}<div class="language-grid">{"".join(cards)}</div>{footer}</section>'


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

/* V6.4 : suivi de la progression des 4 langues. */
.language-overview{background:rgba(255,255,255,.82);border:1px solid #ecdce9;
  border-radius:21px;margin:13px 0 16px;padding:13px 15px 11px;box-shadow:0 7px 20px #70497915}
.language-overview-title{display:flex;align-items:center;justify-content:space-between;gap:12px;
  color:#552c74;font-size:1.03rem;margin-bottom:11px;flex-wrap:wrap}
.language-overview-hint{display:inline-block;margin-left:12px;font-size:.76rem;font-weight:600;color:#88778d}
.language-global{padding:7px 11px;border-radius:999px;background:#f2e8fb;font-weight:800;
  white-space:nowrap;font-size:.86rem}
.language-global strong{font-size:1.12rem;color:#682e97;margin-left:5px}
.language-global-bar{height:6px;background:#efe5f4;border-radius:99px;overflow:hidden;margin:-2px 0 11px}
.language-global-fill{height:100%;background:linear-gradient(90deg,#9859d1,#eea074);border-radius:99px} 
.language-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.language-card{border-radius:16px;padding:12px 13px 10px;border:2px solid transparent;
  background:linear-gradient(135deg,#fff8fb,#fae8f3);min-width:0}
.language-card.active{border-color:#9b72c7;box-shadow:0 0 0 2px #e9d8f8}
.language-card.de{background:linear-gradient(135deg,#f8fbff,#e3efff)}
.language-card.it{background:linear-gradient(135deg,#f8fefa,#e1f5e9)}
.language-card.en{background:linear-gradient(135deg,#fffaf2,#ffeed4)}
.language-card-top{display:flex;align-items:center;justify-content:space-between;gap:6px;color:#35264c;font-size:.94rem}
.language-pct{font-weight:900;font-size:1.26rem;color:#843991;white-space:nowrap}
.language-card.de .language-pct{color:#2466aa}.language-card.it .language-pct{color:#248456}
.language-card.en .language-pct{color:#a3640f}
.language-level{color:#6c5874;font-size:.79rem;font-weight:750;margin:4px 0 10px;
  overflow-wrap:anywhere}
.language-bar{height:10px;border-radius:99px;background:#e9dae9;overflow:hidden}
.language-card.de .language-bar{background:#d6e7f7}.language-card.it .language-bar{background:#d7ebde}
.language-card.en .language-bar{background:#f1dfbc}
.language-fill{height:100%;background:linear-gradient(90deg,#b177cb,#7947b5);border-radius:99px;transition:width .3s}
.language-card.de .language-fill{background:linear-gradient(90deg,#5ab4ff,#3474bd)}
.language-card.it .language-fill{background:linear-gradient(90deg,#65c69c,#258a62)}
.language-card.en .language-fill{background:linear-gradient(90deg,#f1b85b,#dc8429)}
.language-count{margin-top:6px;font-size:.78rem;color:#705e75}
.language-overview-footer{display:flex;flex-wrap:wrap;gap:7px 19px;margin:10px 2px 0;color:#644b70;font-size:.77rem}
.language-overview-small{color:#8a7a92}
@media(max-width:980px){.language-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .language-overview-hint{display:block;margin-left:0}}
@media(max-width:480px){.language-overview{padding:10px 9px}
  .language-grid{gap:7px}.language-card{padding:9px 8px}.language-card-top{font-size:.8rem}
  .language-pct{font-size:1.07rem}.language-level,.language-count{font-size:.73rem}
  .language-global{font-size:.78rem}}

/* V6.5 : estimations de jalons par langue, sans imposer de date limite. */
.forecast-rows{border-top:1px solid #dfd2e2;margin-top:9px;padding-top:7px;display:grid;gap:5px}
.forecast-line{font-size:.75rem;display:flex;align-items:flex-start;justify-content:space-between;
 gap:6px;flex-wrap:wrap;color:#65526d;line-height:1.35}
.forecast-line strong{color:#472b62;white-space:nowrap;font-size:.79rem}
.forecast-intro{font-size:.76rem;color:#806c88;margin:-4px 0 5px}
@media(max-width:480px){.forecast-line{font-size:.71rem}.forecast-line strong{font-size:.74rem}}
</style>'''
st.markdown(CSS,unsafe_allow_html=True)

# Tous les visuels sont locaux, sans lien réseau et en définition nette (webp).
HERO_B64=b64_asset('classe_illustration.webp')
SOFIA_B64=b64_asset('sofia_illustration.webp')
hero_img=(f'<img class="hero-art" alt="Illustration 2D d’une salle de classe avec tableau ¡Hola!" src="data:image/webp;base64,{HERO_B64}"/>' if HERO_B64 else '')
st.markdown(f'''<div class="hero-school"><div class="hero-copy">
<h1>🇪🇸 Mi Español · Mon école des langues</h1>
<div class="subtitle">Progresse à ton rythme du CP à la Terminale !</div>
<div class="tags"><span>🎓 Espagnol scolaire</span><span>🌍 A1 → C2</span><span>🌱 Allemand, italien et anglais de survie</span><span>⭐ {int(p['stars'])} étoiles</span></div>
</div>{hero_img}</div>''',unsafe_allow_html=True)

st.markdown('<div class="lang-caption">🌍 Choisis ton parcours :</div>',unsafe_allow_html=True)
lang=st.segmented_control('Langue',['🇪🇸 Espagnol','🇩🇪 Allemand','🇮🇹 Italien','🇬🇧 Anglais'],default='🇪🇸 Espagnol',key='language_label',label_visibility='collapsed') or '🇪🇸 Espagnol'
# Afficher toutes les langues au même endroit, même lorsque l'onglet change.
# Chaque estimation repose sur des étapes concrètes et peut être adaptée sans imposer de délai.
with st.expander('📅 Mes prévisions de niveaux · ajuster le rythme (facultatif)',expanded=False):
    st.caption('Dates indicatives : deux séances courtes estimées par validation. Elles ne garantissent pas un niveau officiel A1/A2/C1/C2.')
    pace_columns=st.columns(4)
    chosen_pace={}
    labels={'spanish':'🇪🇸 Espagnol','travel_german':'🇩🇪 Allemand',
            'travel_italian':'🇮🇹 Italien','travel_english':'🇬🇧 Anglais'}
    for col,track_name in zip(pace_columns,FORECAST_TRACKS):
        with col:
            previous=p.get('forecast_sessions',{}).get(track_name,4)
            idx=PACE_OPTIONS.index(previous) if previous in PACE_OPTIONS else 3
            value=st.selectbox(labels[track_name]+' · séances/semaine',PACE_OPTIONS,index=idx,
                               key='forecast_pace_'+track_name)
            chosen_pace[track_name]=value or PACE_OPTIONS[idx]
    if chosen_pace!=p.get('forecast_sessions',{}):
        p['forecast_sessions']=chosen_pace
        persist()
    forecast_mode=st.radio('Base du calcul',
            ['Rythme choisi','Rythme réellement observé (si disponible)'],
            horizontal=True,key='forecast_mode') or 'Rythme choisi'
    if forecast_mode!='Rythme choisi':
        st.caption('Le rythme observé est utilisé après au moins 4 validations distinctes réparties sur 7 jours ; sinon le rythme choisi reste appliqué.')
    st.caption('Les paliers allemand / italien / anglais correspondent au guide du touriste, **pas à une certification CECRL A1**.')
forecast_data=language_forecasts(p,chosen_pace,use_history=(forecast_mode!='Rythme choisi'))
progress_items=progress_all_languages(p)
st.markdown(render_language_progress(progress_items,lang,p.get('last_language',''),forecast_data),
            unsafe_allow_html=True)
st.caption('📅 Prévisions indicatives selon la fréquence de travail · parcours sans date limite. Les 15 missions restent les mêmes, enrichies de 400 expressions. Les QCM ne constituent pas une certification linguistique.')

esp=lang=='🇪🇸 Espagnol'
track={'🇩🇪 Allemand':'travel_german','🇮🇹 Italien':'travel_italian','🇬🇧 Anglais':'travel_english'}.get(lang,'travel_german')
if esp:
    grade=int(p['grade'])
    s_done=done_count('school',s_keys(grade))
    c_done=sum(done_count('cefr',c_keys(level)) for level in CECRL)
    cards=[('🏫','Ma classe',CLASSES[grade],'rose'),('📖','Leçons du niveau',f'{s_done}/{len(s_keys(grade))}','blue'),('🎯','Ateliers A1–C2',f'{c_done}/{sum(map(len,CECRL.values()))}','mint'),('⭐','Mes étoiles',str(p['stars']),'yellow')]
else:
    m_done=done_count(track,[str(i) for i in range(len(MISSIONS))])
    cards=[('🌍','Mon parcours','A1++','rose'),('🗣️','Missions acquises',f'{m_done}/{len(MISSIONS)}','blue'),('🎯','Phrases utiles',str(sum(len(item[2]) for item in TRAVEL_GUIDE)),'mint'),('⭐','Mes étoiles',str(p['stars']),'yellow')]
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
    options={'travel_german':('Lena',1,'de-DE','german','allemand'),
             'travel_italian':('Giulia',2,'it-IT','italian','italien'),
             'travel_english':('Olivia',3,'en-GB','english','anglais')}
    teacher,ix,code,former,language_name=options[track]
    st.markdown(f'<div class="section-note">🧳 <b>Voyage d’un mois en {language_name}</b> avec {teacher} : <b>{len(MISSIONS)} missions</b> et <b>{TOTAL_EXPRESSIONS} expressions</b> pratiques. Deux petites séances par mission = <b>30 journées indicatives</b>, à ton rythme, sans échéance. <b>117 mots et repères</b> supplémentaires dans le carnet. Les acquis anciens sont révisés dans les nouvelles situations.</div>',unsafe_allow_html=True)
    study,reference,words,plan,revisions=st.tabs(['🧳 Mes 15 missions','🧭 Guide express','🔤 Mots indispensables','🗓️ Mon voyage de 30 jours','🎲 Révisions surprises'])
    with study:
        l,r=st.columns([0.93,2.15],gap='medium')
        with l:
            with st.container(border=True):
                st.markdown('### 🎒 Mon mois de voyage')
                count=done_count(track,[str(i) for i in range(len(MISSIONS))])
                st.progress(count/len(MISSIONS))
                st.caption(f'🧭 {count}/{len(MISSIONS)} missions validées')
                st.info('🌱 Chaque mission comporte 2 séances : découverte, puis révision et validation. Pas de calendrier obligatoire.')
                if p[former]:
                    st.caption('✅ Les acquis de ton ancienne formation sont conservés. Les phrases reviennent dans les révisions des nouvelles missions.')
                if count:
                    st.caption('♻️ Les missions déjà réussies peuvent être refaites pour réviser les nouvelles expressions.')
            with st.container(border=True):
                st.markdown('### 🆘 Guide toujours disponible')
                st.write('En cas de difficulté réelle, consulte **Guide express** : toutes les expressions sont accessibles, même sans avoir réussi les missions.')
                st.caption('En Allemagne et en Italie : 112 est un numéro d’urgence. Ailleurs, vérifie le numéro d’urgence local. En cas de danger, demande immédiatement de l’aide.')
        with r:
            indices=permitted(track,[str(i) for i in range(len(MISSIONS))])
            j=st.selectbox('🧭 Missions accessibles',indices,
                format_func=lambda i:f'Jours {2*i+1}–{2*i+2} · {MISSIONS[i][0]} '+('✓' if p[track].get(str(i)) is True else '🔓'),
                key=f'{track}_mission')
            title,description,phrases=TRAVEL_GUIDE[j]
            st.markdown(f'<div class="lesson-header"><div class="breadcrumb">{html.escape(lang)} · Mission {j+1}/{len(MISSIONS)} · Jours {j*2+1} et {j*2+2}</div><div class="heading">🧳 {html.escape(title)}</div><span class="chip">{html.escape(description)}</span></div>',unsafe_allow_html=True)
            st.markdown('#### 📘 Séance 1 · Découvrir et parler')
            st.caption('Lis, écoute et répète les expressions essentielles (environ 5 à 10 minutes).')
            core=[phrases[k] for k in (0,1,4)]
            for n,phrase in enumerate(core,1):
                fr=phrase[0];translation=phrase[ix]
                st.markdown(f'<div class="lesson-panel {"rule" if n%2 else "example"}" style="min-height:auto;margin-bottom:8px;padding:12px 16px"><div class="head">{html.escape(translation)}</div><p>🇫🇷 {html.escape(fr)}</p></div>',unsafe_allow_html=True)
            tts_button('. '.join(phrase[ix] for phrase in core),code=code,id_suffix=track+str(j))
            st.caption('📚 Chaque mission regroupe les situations utiles, mais aussi ce que tu peux entendre en réponse. Les 400 expressions sont toutes dans le Guide express.')
            with st.expander(f'📚 Apprendre les {len(phrases)} expressions par petits groupes',expanded=False):
                group_size=8
                n_groups=math.ceil(len(phrases)/group_size)
                group_index=st.selectbox('Choisis ton petit groupe',range(n_groups),
                    format_func=lambda k:f'Groupe {k+1}/{n_groups} · phrases {k*group_size+1} à {min((k+1)*group_size,len(phrases))}',
                    key=f'phrase_group_{track}_{j}')
                part=phrases[group_index*group_size:(group_index+1)*group_size]
                for phrase in part:
                    st.markdown('**'+html.escape(phrase[ix])+'**')
                    st.caption('🇫🇷 '+phrase[0])
                tts_button('. '.join(item[ix] for item in part),code=code,
                           id_suffix='mission_group_'+track+str(j)+str(group_index))
                st.caption('🌱 Pas besoin de tout mémoriser en une séance : le mini-quiz et les rappels espacés réactivent ensuite les expressions.')
            st.markdown('#### 🔁 Séance 2 · Réviser et valider')
            review=mixed_review(j)
            if review:
                st.info('♻️ Rappel des missions '+', '.join(str(index+1) for index,_ in review)+'. Les phrases déjà vues reviennent avec les nouvelles situations.')
                with st.expander('👀 Revoir les expressions précédentes avant le quiz'):
                    for prev,phrase in review:
                        st.markdown(f'**Mission {prev+1} · {phrase[ix]}**')
                        st.caption('🇫🇷 '+phrase[0])
            else:
                st.caption('Première mission : révise les nouvelles phrases avant ton défi.')
            questions=mission_questions(j)
            st.caption(f'Pour valider : {len(questions) if j==0 else len(questions)-1}/{len(questions)} bonnes réponses, avec anciennes et nouvelles expressions. Autant de tentatives que nécessaire.')
            with st.form(f'survival_month_form_{track}_{j}'):
                responses=[]
                for qi,(origin,phrase) in enumerate(questions):
                    fr=phrase[0];correct=phrase[ix]
                    suggestions=[item[ix] for item in phrases if item[ix]!=correct]
                    if origin!=j:
                        suggestions += [item[ix] for item in TRAVEL_GUIDE[origin][2] if item[ix]!=correct]
                    choices=sorted(set([correct]+list(dict.fromkeys(suggestions))[:2]),key=str.casefold)
                    assert len(choices)>=3
                    label=f'{qi+1}. '+('♻️ Révision · ' if origin!=j else '')+f'Comment dire « {fr} » ?'
                    responses.append(st.radio(label,choices,index=None,key=f'survival_month_{track}_{j}_{qi}'))
                submitted=st.form_submit_button('✅ Corriger et débloquer la suite',type='primary',use_container_width=True)
            if submitted:
                if any(ans is None for ans in responses):
                    st.warning('Réponds à chaque question pour valider la mission.')
                else:
                    score=sum(answer==phrase[ix] for answer,(_,phrase) in zip(responses,questions))
                    threshold=len(questions) if j==0 else len(questions)-1
                    if score>=threshold:
                        fresh=award(track,str(j),5)
                        st.success(f'🎉 {score}/{len(questions)} : acquis validés ! '+('Mission suivante débloquée.' if fresh else 'Bonne révision de tes acquis !'))
                    else:
                        st.info(f'{score}/{len(questions)}. Objectif : {threshold} bonnes réponses. Relis les phrases et réessaie sans pénalité.')
                    for answer,(origin,phrase) in zip(responses,questions):
                        if answer!=phrase[ix]:
                            st.caption('Révision : '+phrase[0]+' → '+phrase[ix])
            if p[track].get(str(j)) is True:
                st.success('✓ Mission acquise · les phrases nouvelles et anciennes restent disponibles.')
    with reference:
        st.markdown('### 🧭 Guide du touriste · Toutes les situations du mois')
        st.caption(f'{TOTAL_EXPRESSIONS} expressions de survie + {sum(len(v) for v in VOCABULARY.values())} mots et repères dans le carnet, recherche immédiate et écoute. Tout reste accessible même si les missions sont verrouillées.')
        a,b=st.columns([1.1,1.5])
        with a:
            category=st.selectbox('Situation',range(len(TRAVEL_GUIDE)),
                format_func=lambda i:f'{i+1}. {TRAVEL_GUIDE[i][0]}',key='guide_category_'+track)
        with b:
            search=st.text_input('🔍 Chercher une expression',
                placeholder='ascenseur, clé, taxi, restaurant, panne, bagages…',key='guide_search_'+track)
        if search.strip():
            import unicodedata
            def fold(value):
                return ''.join(char for char in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(char))
            term=fold(search.strip())
            selected=[(i,phrase) for i,(_,_,group) in enumerate(TRAVEL_GUIDE) for phrase in group
                      if any(term in fold(text) for text in phrase) or term in fold(TRAVEL_GUIDE[i][0])]
        else:
            selected=[(category,phrase) for phrase in TRAVEL_GUIDE[category][2]]
        st.caption(f'{len(selected)} résultat(s) · {len(TRAVEL_GUIDE)} catégories de voyage')
        if selected:
            st.dataframe([{'Situation':TRAVEL_GUIDE[i][0], 'Français':phrase[0],
                           language_name.capitalize():phrase[ix]} for i,phrase in selected],
                           use_container_width=True,hide_index=True)
            chosen_phrase=st.selectbox('🔊 Écouter une expression',range(len(selected)),
                format_func=lambda i:selected[i][1][0],key='guide_phrase_'+track)
            st.info(selected[chosen_phrase][1][ix])
            tts_button(selected[chosen_phrase][1][ix],code=code,id_suffix='guide_'+track)
        else:
            st.info('Aucun résultat. Essaie un autre terme : clé, ascenseur, gare, visa, chargeur, médicament…')
        st.caption('Expressions de voyage généralistes : vérifie toujours les démarches et numéros propres au pays. En urgence, demande de l’aide sans attendre une leçon.')
    with words:
        st.markdown('### 🔤 Carnet des mots indispensables')
        st.caption('Comprendre ce que répondent les habitants : gauche/droite, jours, mois, nombres, heures, étages, panneaux et objets courants. Consultable immédiatement, même avant la première mission.')
        keys=list(VOCABULARY)
        selected_topic=st.selectbox('📌 Thème à apprendre',keys,key='vocab_theme_'+track)
        pairs=VOCABULARY[selected_topic]
        st.dataframe([{'Français':item[0],language_name.capitalize():item[ix]} for item in pairs],
                     hide_index=True,use_container_width=True)
        if pairs:
            spoken=st.selectbox('🔊 Écouter un mot',range(len(pairs)),
                format_func=lambda k:pairs[k][0],key='vocab_speak_'+track)
            st.info(pairs[spoken][ix])
            tts_button(pairs[spoken][ix],code=code,id_suffix='vocab_word_'+track)
        st.divider()
        st.markdown('#### 🎲 Jeu flash · 5 mots surprises')
        st.caption('Un petit défi gratuit, sans perte d’étoiles et sans changer le déblocage des missions. Mélange toutes les fiches.')
        vkey='vocab_flash_'+track
        if st.button('🎲 Nouveau jeu flash',key='new_vocab_'+track,type='primary'):
            candidates=[(name,item) for name,entries in VOCABULARY.items() for item in entries]
            chosen=random.sample(candidates,min(5,len(candidates)))
            questions=[]
            for name,item in chosen:
                correct=item[ix]
                alternatives=[x[ix] for x in VOCABULARY[name] if x[ix]!=correct]
                choices=[correct]+random.sample(list(dict.fromkeys(alternatives)),2)
                random.shuffle(choices)
                questions.append({'question':item[0],'correct':correct,'options':choices})
            st.session_state[vkey]={'questions':questions,'answers':None,
                                    'id':random.randrange(10**10)}
        vocab_game=st.session_state.get(vkey)
        if vocab_game:
            if vocab_game['answers'] is None:
                with st.form('vocab_form_'+track+'_'+str(vocab_game['id'])):
                    answers=[]
                    for k,item in enumerate(vocab_game['questions'],1):
                        answers.append(st.radio(f'{k}. Comment dit-on « {item["question"]} » ?',item['options'],
                                                index=None,key=f'vocab_{track}_{vocab_game["id"]}_{k}'))
                    submitted=st.form_submit_button('✨ Vérifier mes réponses',use_container_width=True)
                if submitted:
                    if any(a is None for a in answers):
                        st.warning('Réponds aux cinq questions pour voir ton résultat.')
                    else:
                        vocab_game['answers']=answers
                        st.rerun()
            else:
                score=sum(a==q['correct'] for a,q in zip(vocab_game['answers'],vocab_game['questions']))
                st.success(f'🎉 {score}/5 · Bien joué ! Tu peux refaire un jeu différent quand tu veux.')
                for a,q in zip(vocab_game['answers'],vocab_game['questions']):
                    st.write(('✅ ' if a==q['correct'] else '🌱 ')+q['question']+' → '+q['correct'])
    with plan:
        st.markdown('### 🗓️ Plan de voyage · 30 journées, sans échéances')
        st.caption('15 missions × 2 séances courtes (durée variable selon le besoin). C’est un **ordre d’apprentissage**, pas un calendrier : une journée peut être faite quand tu veux, ou répartie sur plusieurs jours.')
        week_ranges=[(0,4),(4,8),(8,12),(12,15)]
        for week,(start,end) in enumerate(week_ranges,1):
            st.markdown(f'#### Semaine {week} · Jours {start*2+1} à {end*2}')
            rows=[]
            for index in range(start,end):
                name=TRAVEL_GUIDE[index][0]
                done=p[track].get(str(index)) is True
                rows.extend([
                    {'Jour':index*2+1,'Activité':f'{name} · découverte','Statut':'✓ Déjà vu' if done else 'À découvrir'},
                    {'Jour':index*2+2,'Activité':f'{name} · révision + mini-quiz','Statut':'✓ Acquis' if done else ('Débloqué' if index in permitted(track,[str(i) for i in range(len(MISSIONS))]) else '🔒 À venir')},
                ])
            st.dataframe(rows,use_container_width=True,hide_index=True)
        st.info('♻️ À chaque nouvelle mission, le mini-quiz reprend aussi des expressions de missions précédentes. Les anciennes réussites sont conservées.')
    with revisions:
        render_review_corner(track,ix,datetime.now(ZoneInfo('Europe/Paris')).date())
    if done_count(track,[str(i) for i in range(len(MISSIONS))])==len(MISSIONS):
        st.success('🏆 Bravo ! Guide terminé : retrouve maintenant les mini-jeux de révision espacée dans l’onglet 🎲 Révisions surprises.')
    with st.expander('✏️ Mon carnet de voyage'):
        note=st.text_area('Mes phrases personnelles',value=p['notes'].get(former,''),key='travel_notes_'+former)
        if st.button('💾 Enregistrer mon carnet',key='save_travel_'+former):
            p['notes'][former]=note;persist();st.success('Carnet enregistré dans la session.')

st.divider()
with st.expander('💾 Exporter / importer ma progression · Important sur Streamlit Cloud'):
    st.download_button('⬇️ Télécharger ma sauvegarde JSON',json.dumps(p,ensure_ascii=False,indent=2),
                       file_name='mi_espanol_progression_v6_6.json',mime='application/json',use_container_width=True,key='export_profile')
    uploaded=st.file_uploader('Importer un profil V2 à V6',type=['json'],key='import_profile')
    if uploaded is not None and st.button('📂 Restaurer le profil',key='restore_profile'):
        try:
            if uploaded.size>2_000_000:raise ValueError('Le fichier dépasse 2 Mo.')
            incoming=json.loads(uploaded.getvalue().decode('utf-8'))
            if not isinstance(incoming,dict) or not any(k in incoming for k in ('grade','school','cefr','grammar','german','italian','english','travel_english','spanish')):
                raise ValueError('Ce fichier ne ressemble pas à une sauvegarde Mi Español.')
            st.session_state.profile=normalize(incoming)
            p=st.session_state.profile
            persist()
            st.success('Progression restaurée : la page va se mettre à jour.')
            st.rerun()
        except (UnicodeError,ValueError,TypeError) as error:st.error(str(error))
    st.caption('Sur Streamlit Cloud, les sauvegardes locales peuvent disparaître. Conserve ce fichier JSON pour retrouver tes résultats. Ne publie jamais ton fichier personnel sur GitHub.')
st.caption(f'🇪🇸 Mi Español V6.7 · 400 expressions par langue, carnet des mots, dates prévisionnelles et révisions espacées · Guide de 30 jours DE/IT/EN : {len(MISSIONS)} missions et {TOTAL_EXPRESSIONS} expressions par langue · Révisions mixtes · Cours d’espagnol inchangés.')
