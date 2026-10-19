# Mi Español V13 — dossier complet

Ce ZIP contient l'application complète basée sur l'archive fournie par l'utilisateur et le correctif V12.

## Modifications
- Contrôles et révisions : aucune concaténation de deux exemples pour remplir les 20 lignes.
- 20 consignes distinctes par leçon, pour les 156 leçons A1 à C2.
- Couverture des exemples de la leçon en priorité, puis variations bilingues prudentes (noms propres et marqueurs de contexte pour des affirmations simples).
- Historique des consignes déjà utilisées conservé (mécanisme V12).
- QCM de 30 questions conservé.

## Limites
Il ne s'agit PAS d'une banque de 20 phrases entièrement nouvelles, rédigées manuellement pour chaque leçon. Plusieurs phrases sont des variantes d'une même structure : le système ne peut pas créer 3 120 phrases originales fiables à partir des 1 752 exemples sources sans enrichissement éditorial. Le temps verbal du planning n'est pas systématiquement intégré aux 20 phrases. La correction reste stricte.

## Tests
Compilation de tous les fichiers Python réussie.
Génération de 20 paires distinctes vérifiée pour chaque leçon A1, A2, B1, B2, C1, C2.
Aucun test en direct sur Supabase ou Streamlit.

## Installation
Décompresser puis envoyer les fichiers à la racine du dépôt GitHub sur `main`.
Conserver le dossier `.streamlit` déjà présent et ne pas transmettre de secrets.
