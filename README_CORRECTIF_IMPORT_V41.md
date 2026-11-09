# V41 — correctif ImportError du thème

Erreur : `from v18_style import apply_v26_global` dans `app.py`.

Correction : import protégé avec style de repli minimal si le module déployé est ancien.

## Installation Streamlit Cloud
1. Sauvegarder le dépôt et les données.
2. Copier **tous les fichiers** de cette archive à la racine du dépôt GitHub, en remplaçant les anciens fichiers. Ne pas déposer le ZIP tel quel.
3. Vérifier que `app.py` et `v18_style.py` proviennent de la même archive, et que `v18_style.py` contient `def apply_v26_global():`.
4. Commit et redémarrer/rebooter l'application dans Streamlit Cloud.
5. Si l'erreur persiste, lire les logs complets : un ImportError peut aussi venir d'une dépendance interne.

Le correctif ne modifie ni les données ni les validations CECRL.
