# Mi Español V57 — villes illustrées et interactives

## Démarrage

```bash
pip install -r requirements.txt
streamlit run app.py
```

## V57

- Navigation à quatre entrées de V56 conservée.
- Nouvelle carte de ville stylisée, avec quatre lieux mis en avant, accessibles au toucher et au clavier.
- 12 destinations dans quatre langues, avec 12 lieux touristiques accessibles par destination.
- Personnage associé à chaque lieu, niveaux découverte/autonomie/imprévu, scènes à choix et puzzles conservés.
- Mêmes activités sur ordinateur et téléphone, colonnes réorganisées par Streamlit.
- Suivi par langue, ville et lieu préexistant conservé.

**Limites :** la carte est une illustration stylisée en CSS avec des boutons Streamlit, et non un jeu animé ou une vraie carte géographique. Les personnages n'ont pas encore de dialogues libres. Les progrès SQLite locaux peuvent ne pas être persistants sur certains hébergements cloud.

Les données de progression locales ne sont pas incluses dans le ZIP.
