# Mi Español V18 — Mode Aventure (prototype jouable)

## Nouveautés
- Nouvelle entrée « 🎮 Jouer et apprendre » en première position dans la navigation.
- Cinq missions à dialogues et déblocage progressif, avec Lucía, Carlos et Sofía.
- Mini-jeu de vocabulaire basé sur `contenu.json`.
- XP, pièces et badges de découverte.
- Anciennes pages et moteurs conservés.

## Démarrage
1. Installer Python et les dépendances : `pip install -r requirements.txt`.
2. Configurer les secrets Streamlit existants (`APP_PASSWORD`, `postgres`) dans `.streamlit/secrets.toml` ou dans Streamlit Cloud. Ne jamais publier les secrets.
3. Lancer `streamlit run app.py`.
4. Se connecter et choisir « 🎮 Jouer et apprendre ».

## Limites de cette première version
- XP, pièces et missions sont stockés en `st.session_state` : ils disparaissent quand la session Streamlit est perdue. Aucune table PostgreSQL n'a été modifiée.
- Les missions sont des scénarios fixes et ne modifient pas les scores CECRL historiques.
- Pas encore d'avatar animé, de sons, de boutique, ni de parcours personnalisés.
- Tests effectués : compilation syntaxique des scripts Python. Tests d'intégration avec Supabase et navigateur non effectués.
