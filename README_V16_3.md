# Mi Español V16.3 — accélération et mesures complémentaires

Cette version utilise le ZIP GitHub de V16.2 fourni par l’utilisateur.

- Cache des lectures SELECT de Supabase **par session**, pendant 45 secondes au maximum.
- Invalidation immédiate de ce cache lors des écritures SQL effectuées par cette session (enregistrement des réponses, préférences, etc.).
- Réduction de trois lectures identiques de la préférence de niveau à une seule dans la barre latérale.
- Mesures complémentaires : progression des thèmes, en-tête, nombre de lectures SQL évitées.
- Les trois fonctionnalités V16 et les contrôles/révisions existants sont conservés.

**Limites** : une autre session peut modifier la base sans invalider ce cache ; ses changements seront visibles après 45 secondes maximum. Le premier chargement peut rester lent. La mesure serveur n’inclut pas tout le chargement du navigateur. Les données de réponse sont toujours enregistrées immédiatement. Aucune migration Supabase requise.

**Tests** : compilation Python uniquement ; pas de test direct Supabase/Streamlit Cloud. Une baisse à quelques secondes ne peut pas être garantie.

**Installation** : décompresser puis téléverser les fichiers du dossier à la racine du dépôt GitHub `mi-espanol-v9` sur `main`, sans écraser les secrets Streamlit. Tester plusieurs changements de page après un premier chargement, puis regarder le panneau Diagnostic V16.2.
