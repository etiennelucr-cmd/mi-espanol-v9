"""V25 — Projection pédagogique dans le Parcours CECRL."""
from datetime import date, timedelta
import streamlit as st
import moteur as m
import parcours_v10 as pv
import arbre_competences_v18 as arbre
import suivi_temps_v17 as suivi
from referentiel_heures import HEURES_PAR_NIVEAU, HEURES_CUMULEES

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
ACTIVITIES = [
    ("📚 Mission CECRL et vocabulaire", 15),
    ("🔤 Conjugaison et grammaire", 10),
    ("🎧 Écoute et expression orale", 10),
    ("🧠 Révisions espacées et mini-jeux", 10),
]

def _when(hours, weekly_hours):
    weeks = hours / weekly_hours
    return (date.today() + timedelta(days=round(weeks*7))).strftime("%m/%Y")

def page():
    st.title("🇪🇸 Ma progression et mes objectifs")
    st.caption("Parcours CECRL → onglet de suivi. Les résultats des leçons validées sont lus depuis le parcours historique.")
    level = m.preference("niveau_suivi", "A1")
    if level not in LEVELS: level = "A1"
    st.subheader("📍 Où j'en suis après mes leçons")
    valid, total = pv.progression(level)
    valid = max(0, int(valid or 0)); total = max(0, int(total or 0))
    a,b,c = st.columns(3)
    a.metric("Niveau suivi",level)
    b.metric("Thèmes validés",f"{valid}/{total}")
    c.metric("Validation du niveau",f"{valid/total:.0%}" if total else "—")
    st.progress(min(1,valid/total) if total else 0)
    st.caption("Cette progression provient des validations du parcours CECRL, pas des XP. Elle ne certifie pas à elle seule un niveau.")
    s = arbre.state()
    attempts = s.get("attempts", [])
    if attempts:
        st.caption(f"🎮 Mini-défis enregistrés dans la session : {len(attempts)} réponses, "
                   f"{sum(bool(x.get('correct')) for x in attempts)/len(attempts):.0%} de réussite.")
    else:
        st.caption("🎮 Aucun mini-défi enregistré dans cette session.")
    st.divider()
    st.subheader("🗓️ Mon rythme d'apprentissage")
    minutes = st.slider("Minutes d'étude par jour",15,120,45,5,key="v25_daily_minutes")
    days = st.slider("Jours d'étude par semaine",1,7,6,key="v25_weekly_days")
    weekly = minutes*days/60
    st.info(f"Ton rythme prévu : **{minutes} min × {days} jours = {weekly:.1f} h/semaine**.")
    st.subheader("🛤️ Ton parcours sur les prochaines années")
    st.caption("Référentiel commun : 60, 120, 180, 240, 300, 360 heures par niveau, "
               "soit 1 260 heures cumulées d'A1 à C2. Ce sont des repères pédagogiques, "
               "pas des exigences officielles du CECRL.")
    try:
        completed_hours = sum(max(0, float(suivi.heures_niveau(n))) for n in LEVELS)
        hours_current = max(0, float(suivi.heures_niveau(level)))
        st.metric("Heures enregistrées (tous niveaux)", f"{completed_hours:.1f} h")
        st.caption("Heures issues du suivi des sessions et des tentatives chronométrées ; "
                   "certaines activités non chronométrées peuvent manquer.")
    except Exception:
        hours_current = 0.0
        st.warning("Le suivi des heures n'est pas disponible. Les prévisions utilisent 0 heure enregistrée.")
    index = LEVELS.index(level)
    st.caption(f"Niveau suivi : {level}. Les niveaux antérieurs sont considérés comme déjà parcourus "
               "pour la projection, sans présumer de leur certification.")
    remaining_current = max(0.0, HEURES_PAR_NIVEAU[level] - hours_current)
    remaining = 0.0
    for i, lv in enumerate(LEVELS):
        if i < index:
            st.write(f"**{lv}** · niveau antérieur au niveau suivi")
            st.progress(1.0)
            continue
        remaining += remaining_current if i == index else HEURES_PAR_NIVEAU[lv]
        st.markdown(f"**{lv}** · objectif indicatif : {HEURES_PAR_NIVEAU[lv]} h dans ce niveau "
                    f"({HEURES_CUMULEES[lv]} h cumulées depuis A1) · "
                    f"échéance estimée : **{_when(remaining,weekly)}**")
        st.progress(min(1.0, HEURES_CUMULEES[lv] / HEURES_CUMULEES['C2']))
    st.caption("Les barres montrent la place de chaque niveau dans le parcours total, "
               "pas le pourcentage de compétences acquises. Les échéances supposent un rythme constant ; "
               "les heures ne remplacent jamais les validations pédagogiques.")
    st.divider()
    st.subheader(f"⏱️ Comment utiliser tes {minutes} minutes")
    allocated=[round(minutes*part/45) for _,part in ACTIVITIES]
    allocated[-1] += minutes-sum(allocated)
    for (title,_),duration in zip(ACTIVITIES,allocated):
        st.write(f"**{duration} min** · {title}")
        st.progress(duration/minutes)
    st.caption("Plan suggéré, à adapter selon les difficultés révélées par tes leçons.")
    st.divider()
    st.subheader("🎯 Prochaine étape")
    if total and valid>=total:
        st.success("Tous les thèmes de ce niveau sont validés. Passe l'évaluation de fin de niveau avant de poursuivre.")
    else:
        st.info(f"Il reste {max(0,total-valid)} thème(s) à valider en {level}." if total else
                "Aucun total de thèmes disponible pour ce niveau.")
    st.caption("Les prévisions ne déduisent pas automatiquement tes heures réelles : le suivi du temps et les validations restent deux sources distinctes.")
