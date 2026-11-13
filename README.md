# Mi Español V58 — Carte illustrée interactive

## Démarrer

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dans **Explorer les villes**, sélectionne une langue et une ville. La carte illustrée comporte quatre bâtiments cliquables, chacun ouvrant une mission existante. Des boutons Streamlit restent disponibles sous la carte pour une navigation accessible au clavier. Les huit autres lieux sont dans le volet complémentaire.

La carte affiche le nombre de missions réussies (score au moins 2/3 dans les visites enregistrées) et le niveau local. La disposition passe de quatre bâtiments par ligne à deux sur téléphone. Les mêmes destinations et missions sont accessibles sur ordinateur et mobile.

Les personnages et dialogues restent des simulations guidées. Pas de déplacement libre dans un monde 3D ni de reconnaissance vocale. Les données historiques locales restent stockées dans la base SQLite existante, qui n'est pas incluse dans le ZIP.

## Vérifications

Syntaxe Python et intégrité du ZIP vérifiées. Rendu Streamlit à tester en déploiement, notamment le comportement des liens de bâtiments sur Streamlit Cloud.


## V59 — Histoires interactives

Dans Explorer les villes > bâtiment > Histoire interactive, trois scènes liées réagissent aux choix. Les scénarios sont guidés et non génératifs. Défi classique, puzzles, carnet et SOS restent accessibles. Les résultats sont enregistrés par langue, ville et lieu.
