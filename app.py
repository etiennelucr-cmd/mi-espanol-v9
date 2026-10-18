"""Mi Español — tableau de bord cloud de vérification (lecture seule)."""
import hmac
import streamlit as st
import psycopg
from psycopg import sql

st.set_page_config(page_title="Mi Español — progression", page_icon="🇪🇸")
st.title("🇪🇸 Mi Español — progression cloud")
st.caption("Étape de vérification : consultation uniquement. Les exercices et Ollama ne sont pas encore migrés.")

try:
    expected = st.secrets["APP_PASSWORD"]
    cfg = st.secrets["postgres"]
except (KeyError, FileNotFoundError):
    st.error("Configuration manquante. Renseigne APP_PASSWORD et [postgres] dans les Secrets Streamlit.")
    st.stop()

password = st.text_input("Mot de passe personnel", type="password")
if not password:
    st.stop()
if not hmac.compare_digest(password, expected):
    st.error("Mot de passe incorrect")
    st.stop()

names = ["competences", "comprehension_orale", "conjugaison_reponses", "conjugaison_tests",
         "evaluations_cecrl", "lecons", "objectifs", "pratiques_audio", "preferences",
         "productions", "progression_jour", "questions", "recompenses", "reponses",
         "sessions", "tentatives"]
try:
    with psycopg.connect(host=cfg["host"], port=int(cfg.get("port", 5432)),
                         user=cfg["user"], password=cfg["password"],
                         dbname=cfg.get("dbname", "postgres"),
                         sslmode="require", connect_timeout=15) as conn:
        with conn.cursor() as cur:
            counts = {}
            for name in names:
                cur.execute(sql.SQL("SELECT COUNT(*) FROM public.{}").format(sql.Identifier(name)))
                counts[name] = cur.fetchone()[0]
except Exception:
    st.error("Impossible de lire la base Supabase. Vérifie les paramètres de connexion dans les Secrets et l'état du projet.")
    st.stop()

st.success("Connexion Supabase réussie — lecture seule")
st.metric("Enregistrements des 16 tables", sum(counts.values()))
st.metric("Leçons", counts["lecons"])
st.metric("Questions", counts["questions"])
st.metric("Réponses", counts["reponses"])
st.dataframe([{"Table": name, "Enregistrements": count} for name, count in counts.items()], hide_index=True, use_container_width=True)
st.info("Ce tableau de bord ne remplace pas encore Mi Español. Il sert à vérifier l'accès sécurisé à la progression migrée.")
