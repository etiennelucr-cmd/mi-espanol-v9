"""Mi Español : test isolé de quiz avec enregistrement Supabase.
À utiliser sur une application Streamlit de TEST, pas en remplacement de app.py.
"""
import hmac
import json
import random
from datetime import datetime

import streamlit as st
from cloud_db import connexion_cloud

st.set_page_config(page_title="Mi Español — test cloud", page_icon="🇪🇸")
st.title("🇪🇸 Mi Español — test des exercices")
st.caption("Branche de test : un questionnaire et son enregistrement dans Supabase.")

try:
    expected = st.secrets["APP_PASSWORD"]
except (KeyError, FileNotFoundError):
    st.error("APP_PASSWORD manque dans les Secrets de cette application de test.")
    st.stop()

if not st.session_state.get("auth_ok", False):
    with st.form("connexion"):
        pwd = st.text_input("Mot de passe personnel", type="password")
        login = st.form_submit_button("Se connecter")
    if login:
        st.session_state.auth_ok = hmac.compare_digest(pwd, expected)
        if not st.session_state.auth_ok:
            st.error("Mot de passe incorrect")
    if not st.session_state.get("auth_ok", False):
        st.stop()

niveau = st.selectbox("Niveau", ["A1", "A2", "B1", "B2", "C1", "C2"])

if st.button("Préparer 5 questions"):
    try:
        with connexion_cloud() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id, competence, enonce, options, bonne, explication
                               FROM public.questions WHERE niveau = %s
                               ORDER BY random() LIMIT 5""", (niveau,))
                data = cur.fetchall()
        st.session_state.quiz = [
            {"id": r[0], "competence": r[1], "enonce": r[2],
             "options": json.loads(r[3]) if isinstance(r[3], str) else r[3],
             "bonne": r[4], "explication": r[5]}
            for r in data
        ]
        st.session_state.quiz_niveau = niveau
        st.session_state.quiz_done = False
        st.session_state.quiz_started = datetime.now()
    except Exception:
        st.error("Lecture impossible. Vérifie la connexion Supabase de l'application de test.")

quiz = st.session_state.get("quiz", [])
if quiz:
    if st.session_state.get("quiz_done"):
        st.success("Résultat enregistré dans Supabase.")
        st.metric("Score", f"{st.session_state.quiz_score} / {len(quiz)}")
        for q in quiz:
            st.write(f"**{q['enonce']}** — {q['bonne']}")
            if q["explication"]:
                st.caption(q["explication"])
    else:
        with st.form("quiz_form"):
            answers = {}
            for i, q in enumerate(quiz):
                choices = list(q["options"])
                random.Random(str(q["id"])).shuffle(choices)
                answers[q["id"]] = st.radio(
                    f"{i+1}. {q['enonce']}", choices, index=None,
                    key=f"answer_{q['id']}"
                )
            submit = st.form_submit_button("Corriger et enregistrer")
        if submit:
            if any(value is None for value in answers.values()):
                st.warning("Réponds aux cinq questions avant de valider.")
            else:
                score = sum(answers[q["id"]] == q["bonne"] for q in quiz)
                now = datetime.now().isoformat(timespec="seconds")
                elapsed = max(0, int((datetime.now() - st.session_state.quiz_started).total_seconds()))
                try:
                    with connexion_cloud() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""INSERT INTO public.tentatives
                                (date, type, niveau, lecon_id, score, total, secondes)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                RETURNING id""", (now, "Exercice", st.session_state.quiz_niveau,
                                                    None, score, len(quiz), elapsed))
                            attempt_id = cur.fetchone()[0]
                            for q in quiz:
                                cur.execute("""INSERT INTO public.reponses
                                    (tentative_id, question_id, competence, choix, correct, date)
                                    VALUES (%s, %s, %s, %s, %s, %s)""",
                                    (attempt_id, q["id"], q["competence"], answers[q["id"]],
                                     int(answers[q["id"]] == q["bonne"]), now))
                    st.session_state.quiz_score = score
                    st.session_state.quiz_done = True
                    st.rerun()
                except Exception:
                    st.error("Enregistrement impossible. Aucune réponse de ce test n'a été validée. "
                             "Il faudra vérifier les colonnes et les identifiants des tables Supabase.")
