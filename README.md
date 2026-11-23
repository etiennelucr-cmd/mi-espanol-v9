# 🇪🇸 Mi Español — École des langues V5 · programmes renforcés

**Application Streamlit légère, du CP à la Terminale, à son rythme.** Elle associe un parcours de maîtrise de la langue espagnole (lecture, grammaire, conjugaison, rédaction) à des ateliers inspirés des **programmes français d'espagnol langue vivante (LVE)**. Ce sont deux types de programmes différents : les classes françaises d'espagnol ne constituent pas la scolarité suivie par un élève natif espagnol. Les leçons ici sont **originales**, non officielles.

## Nouveautés de la V5

- **104 chapitres scolaires originaux** : 48 chapitres hérités de la V4 + 56 nouveaux ateliers liés aux compétences et axes culturels des textes de 2025 et 2026.
- **CP → CM2** : expression et compréhension orales, interaction, lecture progressive, écriture, découverte culturelle et médiation, avec progression par cycle.
- **6e → 3e** : les axes culturels inscrits au programme d'espagnol du collège sont déclinés en chapitres avec objectifs, texte court, exemples et activité. En 6e : 5 axes. En 5e, 4e et 3e : 6 axes, dont le sixième consacré à un pays ou à une aire géographique.
- **Seconde, Première, Terminale** : 6 axes culturels par classe (ex. transitions, identités, mémoires, monde virtuel, métissages).
- **Spécialité LLCER** : onglet facultatif accessible à partir de la Première avec les œuvres littéraires ou cinématographiques figurant dans les programmes limitatifs applicables ; exercices de méthode originaux, qui ne remplacent pas la lecture ni le visionnage.
- Maintien des **30 ateliers A1 à C2**, des **24 chapitres de grammaire**, des **18 verbes**, des **20 temps ou formes de conjugaison**, et des **20 missions de survie** en allemand / italien.
- Le déblocage reste conditionné aux acquis, sans date limite.

### Chapitres ajoutés par classe

| Classe | Chapitres au total | Ateliers ajoutés |
|---|---:|---:|
| CP, CE1, CE2, CM1, CM2 | 7 par classe | 3 par classe |
| 6e | 9 | 5 axes |
| 5e, 4e, 3e | 10 par classe | 6 axes par classe |
| Seconde, Première, Terminale | 10 par classe | 6 axes par classe |

## Progression et évaluation

- À l'ouverture : **CP chapitre 1**, **A1 atelier 1**, **grammaire A1 règle 1**, **verbe hablar**, **allemand mission 1**, **italien mission 1**.
- Un chapitre se débloque si le **QCM du précédent est réussi (1/1)**. Les anciens chapitres restent consultables.
- La **classe suivante** se débloque lorsque **tous les chapitres de la classe** sont réussis, puis que le bilan est validé à **80 %**, et que l'élève utilise le bouton pour passer de classe. La V5 exige également les nouveaux ateliers avant le passage en classe, même si un bilan V4 a déjà été réussi.
- Le **niveau CECRL** suivant se débloque après les 5 ateliers de son niveau et un bilan à 80 %. La grammaire (4 règles par niveau) fonctionne de même.
- Chaque **verbe** et chaque **temps** se débloque après un défi à **3/3**. Les niveaux d'allemand et d'italien se débloquent mission par mission.
- La **bibliothèque LLCER** est distincte du parcours scolaire et de la progression CECRL ; ses exercices de méthodologie ne sont pas des attestations de lecture.
- Les productions orales/écrites proposées **ne sont pas corrigées automatiquement** : réussir un QCM ne démontre pas une maîtrise complète de ces compétences. Aucun certificat CECRL ou diplôme scolaire n'est délivré.

## Installations GitHub / Streamlit Cloud

Décompressez le ZIP, ouvrez le dossier `Mi_Espanol_Ecole_V5` et transférez **tous les fichiers Python et `requirements.txt`** dans votre dépôt. Sur Streamlit Cloud, le fichier principal est `app.py`.

En local :

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aucun serveur ou service externe n'est nécessaire pour les cours ; l'application reste légère.

## Sauvegardes

Les profils JSON V2, V3 et V4 peuvent être importés. **Les anciens acquis sont conservés.** Les nouveaux chapitres doivent être réussis pour accéder au bilan V5 d'une classe en cours. La sauvegarde est maintenue pendant la session ; sur Streamlit Cloud, **exportez votre profil JSON** pour éviter de perdre vos progrès lors d'un redémarrage. `MI_ESPANOL_LOCAL_SAVE=1` active une sauvegarde locale uniquement sur une installation personnelle, pas une persistance fiable sur Community Cloud. Ne publiez jamais les profils JSON sur GitHub.

## Documents officiels utilisés comme références

**France — espagnol langue vivante :**

1. [BO n° 12 du 19 mars 2026 · Programme des langues vivantes à l'école élémentaire](https://www.education.gouv.fr/bo/2026/Hebdo12/MENE2602911A). Entrée progressive : CP/CM1 à la rentrée 2026, CE1/CE2/CM2 à la rentrée 2027.
2. [Éduscol · ressources pour l'école élémentaire](https://eduscol.education.gouv.fr/7058/ressources-d-accompagnement-pour-les-langues-vivantes-etrangeres-et-regionales-l-ecole-elementaire).
3. [BO n° 22 du 29 mai 2025 · programmes de langues vivantes au collège et au lycée](https://www.education.gouv.fr/bo/2025/Hebdo22/MENE2504621A). Entrée en vigueur progressive au collège : 6e en 2025, 5e en 2026, 4e en 2027, 3e en 2028. Au lycée : seconde en 2025 ; première et terminale en 2026.
4. [Éduscol · ressources de collège](https://eduscol.education.gouv.fr/4758/ressources-d-accompagnement-pour-les-langues-vivantes-etrangeres-et-regionales-au-college).
5. [Éduscol · ressources de lycée](https://eduscol.education.gouv.fr/5811/programmes-et-ressources-en-langues-vivantes-voie-gt).
6. [BO · œuvres limitatives LLCER première 2025-2027](https://www.education.gouv.fr/bo/2025/Hebdo25/MENE2504606N).
7. [BO · œuvres limitatives LLCER terminale 2026-2028](https://www.education.gouv.fr/bo/2026/Hebdo21/MENE2611474N).

**Espagne — langue maternelle et espagnol langue étrangère :** les liens vers la LOMLOE, les modules de Lengua Castellana et le Plan curriculaire de l'Instituto Cervantes sont disponibles dans l'onglet « Profil & sources ».

**Attention :** les programmes de l'enseignement français de l'espagnol visent des objectifs CECRL selon LVA/LVB/LVC : une Terminale ne correspond pas automatiquement au niveau C2. Le parcours C1/C2 est un perfectionnement indépendant.

## Contrôles réalisés

Syntaxe Python, 104 leçons et leurs réponses, 30 ateliers CECRL, 24 règles, 360 tableaux de conjugaison, verrous de progression, simulations de navigation en espagnol/allemand/italien et ouverture du module LLCER. **Aucun test réel du navigateur Streamlit Cloud n'a été réalisé ici.**
