# Mi Español V62 — Correctif des bâtiments

Cette version corrige le retour à la page de départ / la perte de session lors du clic sur les bâtiments.

## Correction
Les liens HTML `<a href="?...">` de la carte ont été remplacés par des boutons Streamlit natifs. La sélection est enregistrée dans `st.session_state` puis l’application effectue `st.rerun()` sans rechargement complet du navigateur.

La carte et les bâtiments restent visibles en deux colonnes adaptées au tactile. Les activités, les 4 langues et la progression sont conservées.

## Installation
`pip install -r requirements.txt` puis `streamlit run app.py`.

Test manuel recommandé : choisir Madrid, entrer dans Pizzeria via le bâtiment, revenir à Carte, recommencer avec Barcelone et sur téléphone.
