# Mi Español V41 — Refonte ludique cumulative

## Nouveautés réellement intégrées
- Trois portraits illustrés (Lucía, Carlos, Sofía) générés pour l’application, affichés à l’accueil et pendant les dialogues.
- Trois mini-jeux : quiz express, traduction active, phrases à reconstruire, avec mots du lexique CECRL et niveau accessible.
- Suivi de précision des mini-jeux, tentatives datées et récompenses de session.
- Tableau de bord unique **en lecture seule** qui réunit indicateurs du moteur historique, thèmes CECRL, missions, défis de l’arbre et mini-jeux, sans mélanger les définitions.
- Sauvegarde JSON V41 et synchronisation V29 compatibles avec le nouvel historique de mini-jeux ; import V27/V28 conservé.
- Navigation V41 et styles Espagne V40 conservés.

## Limites importantes
- Les résultats historiques des examens, de l’oral et des conjugaisons ne sont **pas** migrés vers un modèle de données unique. Le tableau les distingue au lieu d’inventer une note globale.
- Les mini-jeux ne certifient jamais le CECRL ; les règles de déblocage existantes restent actives.
- Synchronisation PostgreSQL optionnelle, uniquement après saisie d’une clé et activation ; le déploiement distant n’a pas été testé.
- Les trois illustrations sont des portraits, pas un système complet d’animation des personnages.
