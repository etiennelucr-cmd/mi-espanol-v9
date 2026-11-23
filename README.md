# Mi Español · École des langues V3

Une application Streamlit légère, 100 % à votre rythme.

## Ce qui est inclus

- **Espagnol scolaire** : 12 classes du CP à la Terminale, 48 leçons originales distinctes (4 par classe), mini-lectures, exercices corrigés, défis d'écriture et évaluations de passage. Chaque classe est associée à un **équivalent espagnol indicatif** (1.º de Primaria à 2.º de Bachillerato).
- **Espagnol langue étrangère** : 30 ateliers originaux répartis entre **A1, A2, B1, B2, C1 et C2** (5 par niveau), avec des évaluations de révision. Les classes et les niveaux CECRL ne sont **pas** identiques. Les bilans ne valent pas certification.
- **Atelier conjugaison** : 18 verbes (3 réguliers et 15 irréguliers usuels), 20 temps et formes, tableau des 6 personnes, gérondif et participe passé, quiz de 3 questions.
- **Allemand / italien** : 10 missions de survie par langue, conservées depuis la V2. « A1++ » est une étiquette interne pour un A1 renforcé, **pas une catégorie officielle du CECRL**.
- **Progression libre** : aucun jour imposé, aucune date limite ; passage dans la classe suivante après validation des 4 leçons et réussite du bilan (3/4).
- Profil exportable / importable en JSON, compatible avec la sauvegarde de la V2 (les 8 anciennes leçons de démonstration ne valident pas les nouvelles leçons).

## Lancement

```bash
pip install -r requirements.txt
streamlit run app.py
```

Sur Streamlit Community Cloud, le fichier principal est `app.py`.

## Sauvegarde

Par défaut, la progression est **gardée pendant la session Streamlit** et exportable via JSON. Sur Streamlit Cloud, la mémoire d'une session et les fichiers locaux ne constituent pas un stockage persistant. Il faut **exporter et réimporter le fichier JSON** ou relier une vraie base de données pour une sauvegarde permanente multiutilisateur.

Pour un usage **sur un ordinateur personnel uniquement**, activer la sauvegarde locale automatique :

```
MI_ESPANOL_LOCAL_SAVE=1 streamlit run app.py
```

Le fichier `ma_progression_locale.json` sera créé à côté du code. Ne le publiez pas sur GitHub.

## Références pédagogiques

Le contenu est **original** et seulement **inspiré** des contenus de l'Instituto Cervantes (PCIC) pour les niveaux CECRL, du currículo LOMLOE espagnol pour les compétences scolaires de Lengua Castellana y Literatura, et des tableaux de conjugaison de référence. Ce n'est pas le programme intégral de l'État espagnol, ni un manuel homologué, ni une préparation complète aux examens. Ces modules constituent une base évolutive.

- https://cvc.cervantes.es/ensenanza/biblioteca_ele/plan_curricular/indice.htm
- https://educagob.educacionfpydeportes.gob.es/curriculo/curriculo-lomloe/menu-curriculos-basicos/ed-primaria/areas/lengua-castellana/criterios-evaluacion-primer-ciclo.html
- https://educagob.educacionfpydeportes.gob.es/curriculo/curriculo-lomloe/menu-curriculos-basicos/ed-secundaria-obligatoria/materias/lengua-castellana/desarrollo.html
- https://educagob.educacionfpydeportes.gob.es/curriculo/curriculo-lomloe/menu-curriculos-basicos/bachillerato/materias/lengua-castellana/desarrollo.html
- https://descargas.intef.es/recursos_educativos/It_didac/Leng_ESO/1/04/04_El_verbo_tiempo_modo_voz/tiempo_modo_y_voz.html
