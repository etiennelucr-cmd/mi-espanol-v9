# Mi Español V16 — dossier complet

Nouveautés :
- En-tête de barre latérale avec drapeau espagnol, nom Mi Español V16, date française et horloge en direct (heure de Paris).
- Saint du jour pour quelques dates documentées. Les autres dates indiquent explicitement « Saint du jour non renseigné » : pas de faux prénom.
- Répétition espacée persistante en préférences Supabase : délais 1, 3, 7, 14, 30, 60 jours, suivi des réussites par phrase et thème prioritaire.
- Conversations guidées écrites (restaurant, hôtel, présentation). Pas de correction par IA dans cette version : conseils de réponse et historique de la session uniquement.
- Maîtrise durable séparée : au moins trois réussites consécutives sur des jours espacés.
- Progression des thèmes validés inchangée, QCM et contrôles V15 conservés.

Limites : le calendrier des saints est partiel. La répétition utilise une comparaison textuelle stricte et les phrases du thème prioritaire. Les conversations sont scénarisées, sans correction grammaticale automatique. Les données SRS sont stockées dans les préférences Supabase existantes ; aucune migration SQL n'est nécessaire. L'accès existant reste protégé par APP_PASSWORD.

Tests : compilation de tous les modules Python réussie. Pas de test en direct avec Supabase ni Streamlit.
Installation : décompresser, envoyer le contenu à la racine du dépôt GitHub main ; préserver .streamlit/secrets.toml hors du dépôt.
