MI ESPAÑOL — PAQUET DE TEST CLOUD (BRANCHE cloud-test UNIQUEMENT)

Ce paquet est une adaptation de travail, pas encore validée en production.
Il vise à conserver l'interface locale en remplaçant la persistance SQLite par PostgreSQL/Supabase.

Contenu :
- app.py : interface originale locale
- moteur.py : adaptateur PostgreSQL pour l'API moteur
- pedagogie.py : init sans DDL au démarrage
- conjugaison_parcours.py : init sans DDL, SQL PostgreSQL
- coach_parcours.py : révisions espacées dans la table Supabase existante
- extension.py, coach_quotidien.py, planning_adaptatif.py
- contenu.json, verbes.json
- requirements.txt

AVANT DE DEPLOYER :
1. N'envoyer ces fichiers que sur la branche cloud-test.
2. Vérifier dans Supabase que les tables et colonnes nécessaires existent.
3. Les modules app/extension/conjugaison peuvent encore nécessiter des ajustements SQL et de schéma.
4. Ne fusionner vers main qu'après test complet.
5. Secrets Streamlit attendus : APP_PASSWORD et [postgres] (host, port, dbname, user, password).
6. Ne jamais inclure espagnol_v2.db ni aucun secret.
