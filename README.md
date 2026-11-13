# Mi Español V55 — Voyage ludique responsive

Application Streamlit : 4 langues, 12 villes, 12 univers touristiques, aventures adaptatives et puzzles de phrases.

## Démarrage

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement sur Streamlit Community Cloud

Définir `APP_PASSWORD` dans les **Secrets** de Streamlit et configurer les éventuels autres secrets requis par votre stockage. Ne jamais publier de mots de passe dans GitHub.

## V55

- Identité visuelle plus contrastée (bordeaux, terracotta, sable chaud)
- Navigation et cartes adaptées aux petits écrans, boutons tactiles plus grands
- Contenu et navigation préservés sur ordinateur et téléphone
- Historique de versions README redondant et caches Python retirés du ZIP

**Limites :** les aventures restent des scénarios à choix ; il n'y a pas encore de dialogues génératifs ou de personnages animés. La persistance SQLite locale peut être éphémère sur hébergement cloud. Le CSS responsive est à valider visuellement sur appareils réels.
