"""Extensions compactes du guide de survie V6.7.

200 expressions originales supplémentaires en français / allemand / italien / anglais.
Les 200 expressions antérieures conservent leur position pour les sauvegardes SRS.
Les fiches de vocabulaire sont indépendantes du compteur des 400 expressions.
"""

# Une entrée par mission. Format : français | allemand | italien | anglais.
SUPPLEMENT_RAW = [
'''Oui, bien sûr.|Ja, natürlich.|Sì, certo.|Yes, of course.
Non, merci.|Nein, danke.|No, grazie.|No, thank you.
Ce n'est pas grave.|Das ist nicht schlimm.|Non fa niente.|That's all right.
D'accord, j'ai compris.|In Ordnung, ich habe verstanden.|Va bene, ho capito.|All right, I understand.
Je ne sais pas.|Ich weiß es nicht.|Non lo so.|I don't know.
Je préfère cette option.|Ich bevorzuge diese Möglichkeit.|Preferisco questa opzione.|I prefer this option.
Ce n'est pas ce que je voulais dire.|Das wollte ich nicht sagen.|Non era quello che volevo dire.|That's not what I meant.
Pouvez-vous parler plus fort ?|Können Sie bitte lauter sprechen?|Può parlare più forte, per favore?|Could you speak a little louder, please?
Pouvez-vous utiliser des mots plus simples ?|Können Sie einfachere Wörter benutzen?|Può usare parole più semplici?|Could you use simpler words?
Puis-je utiliser un traducteur sur mon téléphone ?|Darf ich eine Übersetzungs-App auf meinem Handy benutzen?|Posso usare un traduttore sul telefono?|May I use a translation app on my phone?
Pourriez-vous me montrer un exemple ?|Könnten Sie mir ein Beispiel zeigen?|Potrebbe mostrarmi un esempio?|Could you show me an example?
Je suis désolé(e), je suis en retard.|Entschuldigung, ich bin zu spät.|Mi dispiace, sono in ritardo.|I'm sorry I'm late.
Je suis en vacances ici.|Ich bin hier im Urlaub.|Sono qui in vacanza.|I'm here on holiday.
Je voyage seul(e).|Ich reise allein.|Viaggio da solo/a.|I'm travelling alone.
Nous voyageons en famille.|Wir reisen mit der Familie.|Viaggiamo in famiglia.|We're travelling as a family.
Est-ce que vous pourriez me conseiller ?|Könnten Sie mir etwas empfehlen?|Potrebbe consigliarmi qualcosa?|Could you recommend something?
Merci pour votre patience.|Vielen Dank für Ihre Geduld.|Grazie per la pazienza.|Thank you for your patience.''',
'''Aujourd'hui, c'est lundi.|Heute ist Montag.|Oggi è lunedì.|Today is Monday.
Le rendez-vous est mardi.|Der Termin ist am Dienstag.|L'appuntamento è martedì.|The appointment is on Tuesday.
Je suis disponible mercredi.|Ich habe am Mittwoch Zeit.|Sono disponibile mercoledì.|I'm free on Wednesday.
Nous arrivons jeudi.|Wir kommen am Donnerstag an.|Arriviamo giovedì.|We're arriving on Thursday.
Je pars vendredi.|Ich reise am Freitag ab.|Parto venerdì.|I'm leaving on Friday.
C'est ouvert samedi ?|Ist es am Samstag geöffnet?|È aperto sabato?|Is it open on Saturday?
C'est fermé dimanche.|Am Sonntag ist es geschlossen.|È chiuso domenica.|It's closed on Sunday.
Quelle est la date d'aujourd'hui ?|Welches Datum haben wir heute?|Che giorno è oggi?|What's today's date?
Quel mois sommes-nous ?|Welchen Monat haben wir?|In che mese siamo?|What month is it?
Je reste jusqu'à la fin du mois.|Ich bleibe bis zum Monatsende.|Resto fino alla fine del mese.|I'm staying until the end of the month.
Je pars la semaine prochaine.|Ich reise nächste Woche ab.|Parto la settimana prossima.|I'm leaving next week.
Je suis arrivé(e) la semaine dernière.|Ich bin letzte Woche angekommen.|Sono arrivato/a la settimana scorsa.|I arrived last week.
Est-ce pour aujourd'hui ou demain ?|Ist das für heute oder morgen?|È per oggi o per domani?|Is that for today or tomorrow?
Je voudrais réserver pour le 15.|Ich möchte für den 15. reservieren.|Vorrei prenotare per il 15.|I'd like to book for the 15th.
Pouvez-vous confirmer la date ?|Können Sie das Datum bestätigen?|Può confermare la data?|Could you confirm the date?
Quelle heure est-il ?|Wie spät ist es?|Che ore sono?|What time is it?
Il est huit heures.|Es ist acht Uhr.|Sono le otto.|It's eight o'clock.
Il est huit heures et demie.|Es ist halb neun.|Sono le otto e mezza.|It's half past eight.
Il est huit heures et quart.|Es ist Viertel nach acht.|Sono le otto e un quarto.|It's quarter past eight.
Il est neuf heures moins le quart.|Es ist Viertel vor neun.|Sono le nove meno un quarto.|It's quarter to nine.
Le départ est à 14 h 30.|Die Abfahrt ist um vierzehn Uhr dreißig.|La partenza è alle quattordici e trenta.|Departure is at 2:30 p.m.
Rendez-vous dans dix minutes.|Treffen wir uns in zehn Minuten.|Ci vediamo tra dieci minuti.|Let's meet in ten minutes.
À quelle heure dois-je revenir ?|Um wie viel Uhr soll ich zurückkommen?|A che ora devo tornare?|What time should I come back?
C'est trop tôt pour moi.|Das ist zu früh für mich.|È troppo presto per me.|That's too early for me.
C'est trop tard pour moi.|Das ist zu spät für mich.|È troppo tardi per me.|That's too late for me.
Cela prend une heure environ.|Das dauert ungefähr eine Stunde.|Ci vuole circa un'ora.|It takes about an hour.
Je voudrais deux billets.|Ich hätte gern zwei Fahrkarten.|Vorrei due biglietti.|I'd like two tickets.
Nous sommes trois personnes.|Wir sind drei Personen.|Siamo tre persone.|There are three of us.
Une seule nuit, s'il vous plaît.|Nur eine Nacht, bitte.|Solo una notte, per favore.|Just one night, please.
Je dois attendre cinq minutes.|Ich muss fünf Minuten warten.|Devo aspettare cinque minuti.|I need to wait five minutes.
Cela coûte dix euros.|Das kostet zehn Euro.|Costa dieci euro.|It costs ten euros.
J'ai vingt euros en espèces.|Ich habe zwanzig Euro in bar.|Ho venti euro in contanti.|I have twenty euros in cash.
Le billet coûte trente euros.|Die Fahrkarte kostet dreißig Euro.|Il biglietto costa trenta euro.|The ticket costs thirty euros.
Avez-vous la monnaie sur cinquante euros ?|Können Sie auf fünfzig Euro herausgeben?|Ha il resto di cinquanta euro?|Do you have change for fifty euros?
La caution est de cent euros.|Die Kaution beträgt hundert Euro.|La cauzione è di cento euro.|The deposit is one hundred euros.
C'est mon premier jour ici.|Das ist mein erster Tag hier.|È il mio primo giorno qui.|It's my first day here.
Je reviens dans deux jours.|Ich komme in zwei Tagen wieder.|Torno tra due giorni.|I'll be back in two days.''',
'''Le petit-déjeuner est-il compris ?|Ist das Frühstück inbegriffen?|La colazione è inclusa?|Is breakfast included?
Je voudrais une table près de la fenêtre.|Ich hätte gern einen Tisch am Fenster.|Vorrei un tavolo vicino alla finestra.|I'd like a table by the window.
Pourriez-vous me conseiller un plat local ?|Könnten Sie mir ein regionales Gericht empfehlen?|Potrebbe consigliarmi un piatto tipico?|Could you recommend a local dish?
Est-ce épicé ?|Ist das scharf?|È piccante?|Is it spicy?
Sans piment, s'il vous plaît.|Ohne Chili, bitte.|Senza peperoncino, per favore.|No chilli, please.
Je voudrais du café sans caféine.|Ich hätte gern entkoffeinierten Kaffee.|Vorrei un caffè decaffeinato.|I'd like a decaf coffee.
Je voudrais du thé sans sucre.|Ich hätte gern Tee ohne Zucker.|Vorrei un tè senza zucchero.|I'd like tea without sugar.
Ce plat contient-il des arachides ?|Enthält dieses Gericht Erdnüsse?|Questo piatto contiene arachidi?|Does this dish contain peanuts?
Ce plat contient-il des crustacés ?|Enthält dieses Gericht Schalentiere?|Questo piatto contiene crostacei?|Does this dish contain shellfish?
J'ai une allergie alimentaire grave.|Ich habe eine schwere Lebensmittelallergie.|Ho una grave allergia alimentare.|I have a severe food allergy.
Pouvez-vous vérifier les ingrédients ?|Können Sie die Zutaten überprüfen?|Può controllare gli ingredienti?|Could you check the ingredients?
Pouvez-vous apporter des couverts ?|Können Sie Besteck bringen?|Può portare delle posate?|Could you bring some cutlery?
Une portion plus petite, s'il vous plaît.|Eine kleinere Portion, bitte.|Una porzione più piccola, per favore.|A smaller portion, please.
Je voudrais partager ce plat.|Ich möchte dieses Gericht teilen.|Vorrei dividere questo piatto.|I'd like to share this dish.
Puis-je emporter les restes ?|Kann ich die Reste mitnehmen?|Posso portare via gli avanzi?|Could I take the leftovers with me?
Est-ce que le service est compris ?|Ist die Bedienung inbegriffen?|Il servizio è incluso?|Is service included?''',
'''L'accueil se trouve au rez-de-chaussée ?|Ist die Rezeption im Erdgeschoss?|La reception è al piano terra?|Is reception on the ground floor?
Ma chambre est au deuxième étage.|Mein Zimmer ist im zweiten Stock.|La mia camera è al secondo piano.|My room is on the second floor.
Je voudrais une chambre calme.|Ich hätte gern ein ruhiges Zimmer.|Vorrei una camera tranquilla.|I'd like a quiet room.
Où est le coffre-fort ?|Wo ist der Safe?|Dov'è la cassaforte?|Where is the safe?
Je n'arrive pas à ouvrir ma porte.|Ich kann meine Tür nicht öffnen.|Non riesco ad aprire la porta.|I can't open my door.
Quel est le code d'entrée ?|Wie lautet der Eingangscode?|Qual è il codice d'ingresso?|What's the entry code?
L'ascenseur va-t-il au dernier étage ?|Fährt der Aufzug bis in die oberste Etage?|L'ascensore arriva all'ultimo piano?|Does the lift go to the top floor?
Y a-t-il un escalier de secours ?|Gibt es eine Nottreppe?|C'è una scala di emergenza?|Is there an emergency staircase?
Il manque une couverture.|Eine Decke fehlt.|Manca una coperta.|A blanket is missing.
L'eau de la douche est froide.|Das Wasser in der Dusche ist kalt.|L'acqua della doccia è fredda.|The shower water is cold.
Puis-je demander un réveil à six heures ?|Kann ich einen Weckruf um sechs Uhr bestellen?|Posso chiedere la sveglia alle sei?|Could I request a wake-up call at six?
Le ménage a-t-il déjà été fait ?|Wurde das Zimmer schon gereinigt?|La camera è già stata pulita?|Has the room been cleaned yet?
Je voudrais prolonger mon séjour d'une nuit.|Ich möchte meinen Aufenthalt um eine Nacht verlängern.|Vorrei prolungare il soggiorno di una notte.|I'd like to extend my stay by one night.''',
'''Où dois-je descendre ?|Wo muss ich aussteigen?|Dove devo scendere?|Where should I get off?
C'est le prochain arrêt ?|Ist das die nächste Haltestelle?|È la prossima fermata?|Is this the next stop?
Ce billet est-il valable aujourd'hui ?|Ist diese Fahrkarte heute gültig?|Questo biglietto è valido oggi?|Is this ticket valid today?
Faut-il composter ce billet ?|Muss ich die Fahrkarte entwerten?|Devo convalidare il biglietto?|Do I need to validate this ticket?
Le quai a-t-il changé ?|Hat sich der Bahnsteig geändert?|È cambiato il binario?|Has the platform changed?
Où est la borne à billets ?|Wo ist der Fahrkartenautomat?|Dov'è la biglietteria automatica?|Where is the ticket machine?
Je cherche le terminal numéro deux.|Ich suche Terminal zwei.|Cerco il terminal numero due.|I'm looking for terminal two.
Combien d'arrêts reste-t-il ?|Wie viele Haltestellen sind es noch?|Quante fermate mancano?|How many stops are left?
Y a-t-il une liaison directe ?|Gibt es eine Direktverbindung?|C'è un collegamento diretto?|Is there a direct connection?
Le dernier bus part à quelle heure ?|Wann fährt der letzte Bus ab?|A che ora parte l'ultimo autobus?|What time does the last bus leave?''',
'''Allez tout droit.|Gehen Sie geradeaus.|Vada sempre dritto.|Go straight ahead.
Tournez à gauche.|Biegen Sie links ab.|Giri a sinistra.|Turn left.
Tournez à droite.|Biegen Sie rechts ab.|Giri a destra.|Turn right.
Prenez la première rue à gauche.|Nehmen Sie die erste Straße links.|Prenda la prima strada a sinistra.|Take the first street on the left.
Prenez la deuxième rue à droite.|Nehmen Sie die zweite Straße rechts.|Prenda la seconda strada a destra.|Take the second street on the right.
C'est juste en face.|Es ist direkt gegenüber.|È proprio di fronte.|It's directly opposite.
C'est à côté de la banque.|Es ist neben der Bank.|È accanto alla banca.|It's next to the bank.
C'est derrière le musée.|Es ist hinter dem Museum.|È dietro al museo.|It's behind the museum.
C'est devant la gare.|Es ist vor dem Bahnhof.|È davanti alla stazione.|It's in front of the station.
C'est entre la poste et la pharmacie.|Es ist zwischen der Post und der Apotheke.|È tra l'ufficio postale e la farmacia.|It's between the post office and the pharmacy.
C'est au coin de la rue.|Es ist an der Straßenecke.|È all'angolo della strada.|It's on the street corner.
Continuez jusqu'au feu rouge.|Gehen Sie bis zur Ampel weiter.|Prosegua fino al semaforo.|Continue until the traffic lights.
Traversez au passage piéton.|Überqueren Sie die Straße am Zebrastreifen.|Attraversi sulle strisce pedonali.|Cross at the pedestrian crossing.
Passez le pont.|Überqueren Sie die Brücke.|Attraversi il ponte.|Cross the bridge.
Au rond-point, prenez la deuxième sortie.|Nehmen Sie im Kreisverkehr die zweite Ausfahrt.|Alla rotonda prenda la seconda uscita.|At the roundabout, take the second exit.
Avant la place, tournez à droite.|Biegen Sie vor dem Platz rechts ab.|Prima della piazza giri a destra.|Turn right before the square.
Après l'église, tournez à gauche.|Biegen Sie nach der Kirche links ab.|Dopo la chiesa giri a sinistra.|Turn left after the church.
C'est au bout de la rue.|Es ist am Ende der Straße.|È in fondo alla strada.|It's at the end of the street.
C'est à environ deux cents mètres.|Es ist ungefähr zweihundert Meter entfernt.|È a circa duecento metri.|It's about two hundred metres away.
Cela prend cinq minutes à pied.|Zu Fuß dauert es fünf Minuten.|Ci vogliono cinque minuti a piedi.|It's a five-minute walk.
Le bâtiment est sur votre gauche.|Das Gebäude ist auf Ihrer linken Seite.|L'edificio è alla sua sinistra.|The building is on your left.
Le bâtiment est sur votre droite.|Das Gebäude ist auf Ihrer rechten Seite.|L'edificio è alla sua destra.|The building is on your right.
L'entrée est à l'arrière.|Der Eingang ist hinten.|L'ingresso è sul retro.|The entrance is at the back.
La sortie se trouve en bas.|Der Ausgang ist unten.|L'uscita è al piano di sotto.|The exit is downstairs.
Montez au premier étage.|Gehen Sie in den ersten Stock.|Salga al primo piano.|Go up to the first floor.
Descendez au sous-sol.|Gehen Sie ins Untergeschoss.|Scenda al piano interrato.|Go down to the basement.
Prenez l'escalier mécanique.|Nehmen Sie die Rolltreppe.|Prenda la scala mobile.|Take the escalator.
Le rez-de-chaussée est en bas.|Das Erdgeschoss ist unten.|Il piano terra è in basso.|The ground floor is downstairs.
Je suis devant l'entrée principale.|Ich stehe vor dem Haupteingang.|Sono davanti all'ingresso principale.|I'm in front of the main entrance.
Le GPS ne fonctionne pas.|Das GPS funktioniert nicht.|Il GPS non funziona.|The GPS isn't working.
Quel numéro de rue cherchez-vous ?|Welche Hausnummer suchen Sie?|Che numero civico cerca?|What street number are you looking for?
Est-ce de l'autre côté de la rue ?|Ist es auf der anderen Straßenseite?|È dall'altra parte della strada?|Is it on the other side of the road?
Le chemin est-il bien indiqué ?|Ist der Weg gut ausgeschildert?|Il percorso è ben segnalato?|Is the route clearly signposted?
Pouvez-vous me dire où je suis ?|Können Sie mir sagen, wo ich bin?|Può dirmi dove mi trovo?|Could you tell me where I am?''',
'''Avez-vous cet article en noir ?|Haben Sie diesen Artikel in Schwarz?|Ha questo articolo in nero?|Do you have this item in black?
Je cherche quelque chose de moins cher.|Ich suche etwas Günstigeres.|Cerco qualcosa di meno costoso.|I'm looking for something cheaper.
Puis-je voir une autre taille ?|Kann ich eine andere Größe sehen?|Posso vedere un'altra taglia?|Could I see another size?
Où est la caisse ?|Wo ist die Kasse?|Dov'è la cassa?|Where is the till?
Pouvez-vous emballer ceci ?|Können Sie das einpacken?|Può incartarlo?|Could you wrap this, please?
Est-ce le prix final ?|Ist das der Endpreis?|È il prezzo finale?|Is that the final price?
Puis-je avoir un sac ?|Kann ich eine Tüte bekommen?|Posso avere un sacchetto?|Could I have a bag?
Ce produit est en rupture de stock.|Dieses Produkt ist ausverkauft.|Questo prodotto è esaurito.|This product is out of stock.
Quand sera-t-il de nouveau disponible ?|Wann ist es wieder verfügbar?|Quando sarà di nuovo disponibile?|When will it be back in stock?
Je voudrais déposer une réclamation.|Ich möchte eine Beschwerde einreichen.|Vorrei presentare un reclamo.|I'd like to make a complaint.''',
'''À quelle heure ouvre le musée ?|Um wie viel Uhr öffnet das Museum?|A che ora apre il museo?|What time does the museum open?
L'entrée est-elle incluse dans le billet ?|Ist der Eintritt im Ticket enthalten?|L'ingresso è incluso nel biglietto?|Is admission included in the ticket?
Combien de temps dure la visite ?|Wie lange dauert die Besichtigung?|Quanto dura la visita?|How long does the visit take?
Y a-t-il un vestiaire ?|Gibt es eine Garderobe?|C'è un guardaroba?|Is there a cloakroom?
Où puis-je laisser mon sac ?|Wo kann ich meine Tasche lassen?|Dove posso lasciare la borsa?|Where can I leave my bag?
Faut-il respecter une tenue particulière ?|Gibt es eine Kleiderordnung?|È richiesto un abbigliamento particolare?|Is there a dress code?
Y a-t-il un accès gratuit le dimanche ?|Ist der Eintritt sonntags kostenlos?|L'ingresso è gratuito la domenica?|Is admission free on Sundays?
Est-ce qu'il va pleuvoir cet après-midi ?|Wird es heute Nachmittag regnen?|Pioverà oggi pomeriggio?|Is it going to rain this afternoon?
Où puis-je acheter un parapluie ?|Wo kann ich einen Regenschirm kaufen?|Dove posso comprare un ombrello?|Where can I buy an umbrella?
Puis-je entrer sans réservation ?|Kann ich ohne Reservierung hineingehen?|Posso entrare senza prenotazione?|Can I go in without a booking?''',
'''Je ne me sens pas en sécurité.|Ich fühle mich nicht sicher.|Non mi sento al sicuro.|I don't feel safe.
Pouvez-vous appeler les secours ?|Können Sie den Rettungsdienst rufen?|Può chiamare i soccorsi?|Could you call the emergency services?
Je me suis blessé(e) au pied.|Ich habe mich am Fuß verletzt.|Mi sono ferito/a al piede.|I've injured my foot.
J'ai des vertiges.|Mir ist schwindelig.|Ho le vertigini.|I feel dizzy.
J'ai du mal à respirer.|Ich bekomme schlecht Luft.|Faccio fatica a respirare.|I'm having trouble breathing.
Je dois prendre ce médicament chaque jour.|Ich muss dieses Medikament jeden Tag nehmen.|Devo prendere questo farmaco ogni giorno.|I need to take this medicine every day.
Avez-vous une pharmacie de garde ?|Gibt es eine Notdienstapotheke?|C'è una farmacia di turno?|Is there an out-of-hours pharmacy?
Je voudrais déclarer un vol.|Ich möchte einen Diebstahl anzeigen.|Vorrei denunciare un furto.|I'd like to report a theft.
J'ai besoin d'une attestation pour mon assurance.|Ich brauche eine Bescheinigung für meine Versicherung.|Mi serve un documento per la mia assicurazione.|I need a document for my insurance company.''',
'''Le logement n'est pas conforme à la réservation.|Die Unterkunft entspricht nicht der Buchung.|L'alloggio non corrisponde alla prenotazione.|The accommodation doesn't match the booking.
Il y a une mauvaise odeur dans la chambre.|Im Zimmer riecht es unangenehm.|C'è un cattivo odore nella camera.|There's a bad smell in the room.
Je voudrais parler au responsable.|Ich möchte mit der verantwortlichen Person sprechen.|Vorrei parlare con il responsabile.|I'd like to speak to the manager.
Pouvez-vous envoyer quelqu'un pour réparer cela ?|Können Sie jemanden schicken, um das zu reparieren?|Può mandare qualcuno a ripararlo?|Could you send someone to fix this?
Quand le problème sera-t-il résolu ?|Wann wird das Problem behoben sein?|Quando sarà risolto il problema?|When will the problem be fixed?
Pourriez-vous proposer une autre solution ?|Könnten Sie eine andere Lösung anbieten?|Potrebbe proporre un'altra soluzione?|Could you offer another solution?
J'ai besoin d'une confirmation par écrit.|Ich brauche eine schriftliche Bestätigung.|Ho bisogno di una conferma scritta.|I need written confirmation.
Je n'ai plus de connexion Internet.|Ich habe keine Internetverbindung mehr.|Non ho più connessione a Internet.|I no longer have an internet connection.''',
'''Où est le hall des arrivées ?|Wo ist die Ankunftshalle?|Dov'è la sala arrivi?|Where is the arrivals hall?
Où puis-je faire enregistrer ma valise ?|Wo kann ich meinen Koffer aufgeben?|Dove posso imbarcare la valigia?|Where can I check in my suitcase?
La porte d'embarquement a changé.|Das Gate hat sich geändert.|Il gate d'imbarco è cambiato.|The boarding gate has changed.
Est-ce que je dois passer la douane ?|Muss ich durch den Zoll?|Devo passare la dogana?|Do I need to go through customs?
J'ai un visa valable jusqu'à cette date.|Ich habe ein Visum, das bis zu diesem Datum gültig ist.|Ho un visto valido fino a questa data.|I have a visa valid until this date.
Où est le comptoir des correspondances ?|Wo ist der Transferschalter?|Dov'è il banco dei transiti?|Where is the transfer desk?
Je cherche la sortie pour les taxis.|Ich suche den Ausgang zu den Taxis.|Cerco l'uscita per i taxi.|I'm looking for the taxi exit.
Puis-je sortir de l'aéroport pendant l'escale ?|Darf ich den Flughafen während des Zwischenstopps verlassen?|Posso uscire dall'aeroporto durante lo scalo?|Can I leave the airport during the stopover?''',
'''Où déposer le verre à recycler ?|Wo kann ich Altglas entsorgen?|Dove posso buttare il vetro da riciclare?|Where can I recycle glass?
À quel jour passe la collecte des déchets ?|An welchem Tag wird der Müll abgeholt?|In quale giorno si raccoglie la spazzatura?|Which day is rubbish collected?
Comment régler le chauffage ?|Wie stelle ich die Heizung ein?|Come si regola il riscaldamento?|How do I adjust the heating?
Le disjoncteur a sauté.|Die Sicherung ist rausgeflogen.|È scattato l'interruttore generale.|The circuit breaker has tripped.
Où se trouve le robinet d'arrêt ?|Wo ist der Absperrhahn?|Dov'è il rubinetto generale?|Where is the stopcock?
Est-ce que l'eau du robinet est potable ?|Ist das Leitungswasser trinkbar?|L'acqua del rubinetto è potabile?|Is tap water safe to drink?
Où faut-il laisser les draps ?|Wo soll ich die Bettwäsche lassen?|Dove devo lasciare le lenzuola?|Where should I leave the bed linen?
Y a-t-il une règle pour le bruit le soir ?|Gibt es abends Ruhezeiten?|Ci sono orari di silenzio la sera?|Are there quiet hours in the evening?''',
'''Faut-il un permis de conduire international ?|Brauche ich einen internationalen Führerschein?|Serve una patente di guida internazionale?|Do I need an international driving permit?
Quelle est la limite de vitesse ici ?|Wie hoch ist hier die Geschwindigkeitsbegrenzung?|Qual è il limite di velocità qui?|What's the speed limit here?
Cette route est-elle fermée ?|Ist diese Straße gesperrt?|Questa strada è chiusa?|Is this road closed?
Où puis-je payer le péage ?|Wo kann ich die Maut bezahlen?|Dove posso pagare il pedaggio?|Where can I pay the toll?
Que couvre l'assurance de location ?|Was deckt die Mietwagenversicherung ab?|Che cosa copre l'assicurazione dell'auto a noleggio?|What does the rental car insurance cover?
Où se trouve le triangle de signalisation ?|Wo ist das Warndreieck?|Dov'è il triangolo di emergenza?|Where is the warning triangle?
Je dois signaler un accident à l'agence.|Ich muss der Autovermietung einen Unfall melden.|Devo segnalare un incidente all'autonoleggio.|I need to report an accident to the rental company.''',
'''Je voudrais connaître les horaires des marées.|Ich möchte die Gezeitenzeiten wissen.|Vorrei conoscere gli orari delle maree.|I'd like to know the tide times.
Y a-t-il un risque d'orage ?|Besteht Gewittergefahr?|C'è rischio di temporali?|Is there a risk of thunderstorms?
Puis-je boire cette eau ?|Kann ich dieses Wasser trinken?|Posso bere quest'acqua?|Can I drink this water?
Je cherche de la crème solaire.|Ich suche Sonnencreme.|Cerco una crema solare.|I'm looking for sunscreen.
Y a-t-il un endroit pour se mettre à l'abri ?|Gibt es einen Ort, an dem man Schutz finden kann?|C'è un posto dove ripararsi?|Is there somewhere to take shelter?''',
'''Où puis-je imprimer ma carte d'embarquement ?|Wo kann ich meine Bordkarte ausdrucken?|Dove posso stampare la carta d'imbarco?|Where can I print my boarding pass?
Combien pèse ma valise ?|Wie viel wiegt mein Koffer?|Quanto pesa la mia valigia?|How much does my suitcase weigh?
Puis-je m'enregistrer en ligne ?|Kann ich online einchecken?|Posso fare il check-in online?|Can I check in online?
À quelle heure dois-je être à l'aéroport ?|Wann muss ich am Flughafen sein?|A che ora devo essere in aeroporto?|What time should I be at the airport?
Je voudrais réserver un transfert tôt le matin.|Ich möchte einen Transfer am frühen Morgen buchen.|Vorrei prenotare un trasferimento al mattino presto.|I'd like to book an early-morning transfer.
Puis-je recevoir la facture par courriel ?|Kann ich die Rechnung per E-Mail bekommen?|Posso ricevere la fattura via e-mail?|Could you email me the invoice?
Avez-vous vérifié si j'ai tout laissé en ordre ?|Haben Sie überprüft, ob ich alles in Ordnung hinterlassen habe?|Ha verificato se ho lasciato tutto in ordine?|Have you checked that I've left everything in order?
Puis-je payer les frais restants maintenant ?|Kann ich die restlichen Gebühren jetzt bezahlen?|Posso pagare le spese rimanenti adesso?|Can I pay the remaining charges now?''',
]

EXPECTED_NEW=[17,37,16,13,10,34,10,10,9,8,8,8,7,5,8]

def parse_supplements():
    groups=[]
    for mission,raw in enumerate(SUPPLEMENT_RAW):
        lines=[]
        for n,line in enumerate(raw.strip().splitlines(),1):
            parts=tuple(item.strip() for item in line.split('|'))
            if len(parts)!=4 or not all(parts):
                raise ValueError(f'V6.7 mission {mission+1}, phrase {n} : quatre langues requises')
            lines.append(parts)
        if len(lines)!=EXPECTED_NEW[mission]:
            raise ValueError(f'V6.7 mission {mission+1}: {len(lines)} ajouts au lieu de {EXPECTED_NEW[mission]}')
        groups.append(lines)
    if sum(map(len,groups))!=200:
        raise ValueError('200 phrases supplémentaires attendues')
    return groups

SUPPLEMENTS=parse_supplements()

# Mots utiles pour COMPRENDRE une réponse. Ces fiches sont indépendantes des 400 phrases.
VOCABULARY={
    '🧭 Directions et lieux': [
        ('à gauche','links','a sinistra','left'),('à droite','rechts','a destra','right'),
        ('tout droit','geradeaus','sempre dritto','straight ahead'),
        ('en face','gegenüber','di fronte','opposite'),('à côté','nebenan','accanto','next to'),
        ('derrière','hinter','dietro','behind'),('devant','vor','davanti','in front of'),
        ('entre','zwischen','tra','between'),('au coin','an der Ecke','all’angolo','on the corner'),
        ('avant','vor','prima','before'),('après','nach','dopo','after'),
        ('près','nah','vicino','near'),('loin','weit','lontano','far'),
        ('en haut','oben','in alto','upstairs / above'),
        ('en bas','unten','in basso','downstairs / below'),
        ('premier étage','erster Stock','primo piano','first floor'),
        ('deuxième étage','zweiter Stock','secondo piano','second floor'),
        ('rez-de-chaussée','Erdgeschoss','piano terra','ground floor'),
        ('sous-sol','Untergeschoss','piano interrato','basement'),
        ('sortie','Ausgang','uscita','exit'),('entrée','Eingang','entrata','entrance'),
    ],
    '📅 Jours de la semaine': [
        ('lundi','Montag','lunedì','Monday'),('mardi','Dienstag','martedì','Tuesday'),
        ('mercredi','Mittwoch','mercoledì','Wednesday'),('jeudi','Donnerstag','giovedì','Thursday'),
        ('vendredi','Freitag','venerdì','Friday'),('samedi','Samstag','sabato','Saturday'),
        ('dimanche','Sonntag','domenica','Sunday'),
    ],
    '🗓️ Mois de l’année': [
        ('janvier','Januar','gennaio','January'),('février','Februar','febbraio','February'),
        ('mars','März','marzo','March'),('avril','April','aprile','April'),
        ('mai','Mai','maggio','May'),('juin','Juni','giugno','June'),
        ('juillet','Juli','luglio','July'),('août','August','agosto','August'),
        ('septembre','September','settembre','September'),('octobre','Oktober','ottobre','October'),
        ('novembre','November','novembre','November'),('décembre','Dezember','dicembre','December'),
    ],
    '🔢 Nombres et quantités': [
        ('zéro','null','zero','zero'),('un','eins','uno','one'),('deux','zwei','due','two'),
        ('trois','drei','tre','three'),('quatre','vier','quattro','four'),
        ('cinq','fünf','cinque','five'),('six','sechs','sei','six'),
        ('sept','sieben','sette','seven'),('huit','acht','otto','eight'),
        ('neuf','neun','nove','nine'),('dix','zehn','dieci','ten'),
        ('onze','elf','undici','eleven'),('douze','zwölf','dodici','twelve'),
        ('treize','dreizehn','tredici','thirteen'),('quatorze','vierzehn','quattordici','fourteen'),
        ('quinze','fünfzehn','quindici','fifteen'),('seize','sechzehn','sedici','sixteen'),
        ('dix-sept','siebzehn','diciassette','seventeen'),
        ('dix-huit','achtzehn','diciotto','eighteen'),('dix-neuf','neunzehn','diciannove','nineteen'),
        ('vingt','zwanzig','venti','twenty'),('trente','dreißig','trenta','thirty'),
        ('quarante','vierzig','quaranta','forty'),('cinquante','fünfzig','cinquanta','fifty'),
        ('soixante','sechzig','sessanta','sixty'),('soixante-dix','siebzig','settanta','seventy'),
        ('quatre-vingts','achtzig','ottanta','eighty'),('quatre-vingt-dix','neunzig','novanta','ninety'),
        ('cent','hundert','cento','one hundred'),('mille','tausend','mille','one thousand'),
    ],
    '🕒 Heure et fréquence': [
        ('maintenant','jetzt','adesso','now'),('plus tard','später','più tardi','later'),
        ('tôt','früh','presto','early'),('tard','spät','tardi','late'),
        ('aujourd’hui','heute','oggi','today'),('demain','morgen','domani','tomorrow'),
        ('hier','gestern','ieri','yesterday'),('après-demain','übermorgen','dopodomani','the day after tomorrow'),
        ('le matin','morgens','di mattina','in the morning'),
        ('à midi','mittags','a mezzogiorno','at midday'),
        ('l’après-midi','nachmittags','nel pomeriggio','in the afternoon'),
        ('ce soir','heute Abend','stasera','this evening'),
        ('à minuit','um Mitternacht','a mezzanotte','at midnight'),
        ('une demi-heure','eine halbe Stunde','mezz’ora','half an hour'),
        ('un quart d’heure','eine Viertelstunde','un quarto d’ora','a quarter of an hour'),
        ('tous les jours','jeden Tag','ogni giorno','every day'),
    ],
    '💬 Réponses fréquentes': [
        ('oui','ja','sì','yes'),('non','nein','no','no'),
        ('bien sûr','natürlich','certo','of course'),
        ('peut-être','vielleicht','forse','maybe'),
        ('attendez','warten Sie','aspetti','please wait'),
        ('ouvert','geöffnet','aperto','open'),('fermé','geschlossen','chiuso','closed'),
        ('complet','ausgebucht','al completo','fully booked'),
        ('disponible','verfügbar','disponibile','available'),
        ('en panne','kaputt','guasto','out of order'),
        ('gratuit','kostenlos','gratuito','free of charge'),
        ('payant','kostenpflichtig','a pagamento','charged'),
        ('autorisé','erlaubt','consentito','allowed'),
        ('interdit','verboten','vietato','forbidden'),
        ('entrée uniquement','nur Eingang','solo entrata','entrance only'),
        ('sortie uniquement','nur Ausgang','solo uscita','exit only'),
    ],
    '🧳 Objets et petits besoins': [
        ('clé','Schlüssel','chiave','key'),('carte magnétique','Schlüsselkarte','tessera magnetica','key card'),
        ('billet','Fahrkarte / Ticket','biglietto','ticket'),
        ('chargeur','Ladegerät','caricabatterie','charger'),
        ('prise','Steckdose','presa elettrica','socket'),
        ('adaptateur','Steckdosenadapter','adattatore','adapter'),
        ('valise','Koffer','valigia','suitcase'),('sac','Tasche','borsa','bag'),
        ('parapluie','Regenschirm','ombrello','umbrella'),
        ('serviette','Handtuch','asciugamano','towel'),
        ('pharmacie','Apotheke','farmacia','pharmacy'),
        ('toilettes','Toilette','bagno','toilet'),
        ('bouteille d’eau','Wasserflasche','bottiglia d’acqua','water bottle'),
        ('portefeuille','Portemonnaie','portafoglio','wallet'),
        ('passeport','Reisepass','passaporto','passport'),
    ],
}

assert all(len(v)==4 and all(v) for rows in VOCABULARY.values() for v in rows)
