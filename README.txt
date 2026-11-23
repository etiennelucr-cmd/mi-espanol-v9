MI ESPAÑOL V6 — NOUVELLE INTERFACE 2D
===================================

Ce petit ZIP est une MISE À JOUR VISUELLE DE LA V5 : il ne remplace pas les modules pédagogiques V5.
Il comprend :
  app.py
  requirements.txt
  assets/classe_illustration.webp
  assets/sofia_illustration.webp
  README.txt

INSTALLATION GITHUB — 3 ÉTAPES
----------------------------
1. Ouvrir le dépôt GitHub EXISTANT qui contient déjà la V5.
2. Remplacer app.py et requirements.txt par ceux de ce ZIP ; ajouter les DEUX images dans un dossier assets/ à la racine.
3. Garder, sans les supprimer, les cinq modules V5 :
   - programme.py
   - programmes_officiels.py
   - grammaire.py
   - conjugaison.py
   - progression.py
   Streamlit Cloud doit continuer à lancer app.py.

Ne pas extraire un deuxième répertoire imbriqué dans la racine de GitHub : son contenu doit être AU MÊME NIVEAU que les modules ci-dessus.

CHANGEMENTS
-----------
- Nouvelle bannière dégradée avec illustration vectorielle 2D nette.
- Portrait illustré de Sofía et ses élèves, réutilisé dans la classe.
- Quatre cartes pédagogiques colorées, progression et récompenses.
- Onglets plus lisibles, sections leçon en cartes rose / bleue / verte.
- Bouton « Écouter et répéter » réel : synthèse vocale via le navigateur (Web Speech API). La disponibilité et la voix dépendent du navigateur, et la prononciation doit être vérifiée par l'apprenant.
- Interface adaptable sur mobile / ordinateur.
- Trois langues et tous les modules pédagogiques conservés.
- Déblocage après validation des acquis, bilans à 80 %, verbes / temps à 3/3.
- Correction préventive du problème KeyError d'un profil ancien : normalize exécuté à chaque visite et après import JSON.

SAUVEGARDES
-----------
Les profils JSON des anciennes versions sont réutilisables, avec les mêmes identifiants de cours V5.
Streamlit Cloud ne conserve pas durablement les fichiers locaux, donc il faut exporter sa progression au format JSON.

TESTS
-----
Compilation Python vérifiée.
Simulation du démarrage espagnol, allemand, italien et Terminale/LLCER ; aucun identifiant de widget dupliqué dans cette simulation.
L'application n'a pas été ouverte dans un navigateur Streamlit réel, faute d'environnement Streamlit dans l'outil de test.
