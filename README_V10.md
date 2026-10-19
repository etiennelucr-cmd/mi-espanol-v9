# Mi Español V10 — version de prévisualisation à tester

Ne pas remplacer la branche principale avant validation sur une branche de test Streamlit.

## Inclus
- Planning hebdomadaire comme source du thème prioritaire dans expression écrite, oral, contrôles et révisions.
- Compteur **estimatif** de mots acquis près de XP (au moins deux productions correctes enregistrées, lexique du niveau). Les QCM ne permettent pas actuellement une attribution fiable mot par mot.
- Progression des thèmes validés via Coach IA (19/20), distincte du compteur lexical.
- Objectifs lexicaux indicatifs CECRL, non officiels.
- Révisions directement visibles, traductions de phrases et correction enregistrée ; 20 phrases différentes nécessaires pour attribuer une note /20.
- Suppression des entrées Tableau de bord et Axe de progression.
- Coach : liste des thèmes et leçon repliables.
- Conjugaison : menu des groupes réguliers et explications supplémentaires.

## Limites connues avant production
- Les cours et contrôles restent en partie fondés sur les QCM disponibles : le catalogue actuel ne garantit pas 20 à 30 traductions distinctes par thème.
- La correction des traductions reste stricte ; les synonymes et traductions alternatives correctes peuvent être rejetés.
- La progression lexicale est une estimation partielle, pas une mesure complète du vocabulaire reconnu dans toutes les activités.
- Les leçons de conjugaison ne disposent pas encore d’explications exhaustives pour chaque temps.
- Tester les tables Supabase existantes, l’enregistrement et la navigation sur une branche de test avant déploiement.
- Ne pas transférer .env, mots de passe, fichiers .db ni secrets dans GitHub.
