# Mi Español V12 — dossier complet

Contenu : ensemble du dépôt Mi Español basé sur l'archive `mi-espanol-v9-main(1).zip` fournie par l'utilisateur, avec le correctif V11 intégré et l'amélioration V12.

## Changements V12
- Contrôles : 20 consignes distinctes par séance, sans phrases identiques dans le même lot.
- Révisions : idem.
- Répartition équilibrée des exemples de chaque leçon ; suppression des paires inversées considérées comme nouvelles.
- Historique des 300 dernières consignes de chaque rubrique et thème, enregistré dans les préférences de la base Supabase après correction, pour privilégier les consignes non encore utilisées.
- Tous les niveaux A1, A2, B1, B2, C1, C2 sont pris en charge par le même moteur.
- QCM de 30 questions de V11 conservé.

## Limite pédagogique importante
Les leçons sources contiennent en général seulement 11 à 12 exemples traduits. Pour obtenir 20 consignes sans inventer de traductions, le moteur assemble deux phrases attestées. Les consignes sont uniques mais certaines propositions se retrouveront dans plusieurs consignes. Ce correctif ne crée donc pas 20 phrases originales et indépendantes par thème. Le temps verbal du planning est repris dans la fiche de conjugaison quand elle propose une paire traduite, sans garantie que les 20 consignes utilisent ce temps.

## Installation
Décompresser l'archive, envoyer les fichiers à la racine du dépôt GitHub `mi-espanol-v9` sur la branche `main`, en conservant le dossier `.streamlit` et les sous-dossiers. Ne pas envoyer de secrets Supabase.

## Vérification
Compilation Python de tous les fichiers réussie. Test local du moteur de génération : 20 consignes distinctes pour chaque leçon des six niveaux. Pas de test en direct avec Streamlit ni Supabase.
