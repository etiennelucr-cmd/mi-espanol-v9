# Correctif Supabase — Mi Español V80

La mémoire sociale V80 utilise désormais la section `[postgres]` déjà configurée dans Streamlit Secrets si `SOCIAL_DATABASE_URL` est absent. Aucun changement de secrets n’est nécessaire. Les caractères spéciaux du mot de passe sont transmis directement à psycopg, sans construction manuelle d’URL.

La sauvegarde reste accessible depuis le profil social V80. Un code de profil n’est **pas** une authentification sécurisée : ne pas enregistrer de données sensibles. La table `social_world_v80` est créée au premier chargement ou enregistrement si le compte PostgreSQL a les droits requis.

Le fonctionnement réel de la base distante n’a pas pu être testé ici, faute d’accès aux secrets.
