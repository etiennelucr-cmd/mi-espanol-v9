# Mi Español V16.1 — optimisation de navigation

À partir de l’archive GitHub fournie le 19 octobre 2026.

- Regroupement des scores Coach IA par niveau en une seule requête SQL, au lieu d’une requête par thème.
- Regroupement des contrôles de conjugaison par niveau en une seule requête SQL, au lieu d’une requête par temps.
- Mise en cache 15 secondes des deux agrégats, invalidée après toute écriture SQL.
- Calcul de projection de date désactivé par défaut ; bouton « Afficher une estimation de date » pour le demander.
- Le pourcentage des thèmes validés reste inchangé.
- Les données pédagogiques, les fonctionnalités V16, les secrets Streamlit et la base Supabase sont conservés.

Les temps réels dépendent aussi de la latence Supabase et du démarrage Streamlit Cloud. Aucun test en direct Supabase n'a été effectué.

Installation : décompresser et envoyer les fichiers du dossier sur GitHub main, conserver la structure et les secrets hors dépôt.
