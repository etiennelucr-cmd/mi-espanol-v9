# Mi Español V80 — Immersion sociale (version progressive)

La V80 conserve le jeu existant et les trois colonnes de « Mes rencontres ».

## Nouveautés réellement intégrées
- Réponses libres via une API d'IA **facultative** (OpenAI), contextualisées par l'historique récent, la personnalité et le niveau indicatif de chaque langue.
- Mémoire explicite des messages précédents, utilisée pour contextualiser les prochaines réponses.
- Sauvegarde/chargement PostgreSQL **facultatifs**, par code de profil, avec synchronisation après les actions.
- Mode scénarisé utilisable sans clé API ni base de données.
- Personnages, publications, commentaires, invitations et voyages existants préservés.

## Configuration Streamlit Cloud
Dans les secrets Streamlit (ne jamais committer les clés) :

```toml
OPENAI_API_KEY = "..."
SOCIAL_AI_MODEL = "gpt-4o-mini"
SOCIAL_DATABASE_URL = "postgresql://..."
```

Les deux services sont indépendants. Sans `OPENAI_API_KEY`, dialogues scénarisés. Sans `SOCIAL_DATABASE_URL`, mémoire limitée à la session.

Dans « Mes rencontres » > « Sauvegarde et IA · V80 », saisir un code de profil (6 à 64 caractères), puis « Charger mon profil » une fois. Les modifications suivantes sont enregistrées dans PostgreSQL. Pour reprendre sur un autre appareil, saisir le même code.

**Attention sécurité** : le code de profil est un identifiant non authentifié, **pas un compte utilisateur sécurisé**. Quiconque connaît le code peut accéder à l'histoire correspondante. N'y stockez pas de données personnelles sensibles. Pour un usage public/multi-utilisateurs, intégrer une authentification robuste et des contrôles d'accès côté serveur avant de déployer la sauvegarde.

## Limites
- L'IA répond aux messages **uniquement si l'API est configurée** ; les publications et événements restent générés par règles.
- Les relances sont calculées au retour dans l'application, sans notifications hors ligne.
- La personnalité et les souvenirs sont une première implémentation, **pas une simulation autonome complète des Sims**.
- Le niveau CECRL reste indicatif et n'est pas une certification.
- Une clé API peut entraîner des coûts ; une limite de consommation côté fournisseur est recommandée.
