"""Connexion Supabase pour Mi Español Cloud.

Ce module ne modifie pas la base. Les identifiants restent dans les Secrets
Streamlit, jamais dans GitHub.
"""
from contextlib import contextmanager

import psycopg
import streamlit as st


@contextmanager
def connexion_cloud():
    """Ouvre une transaction PostgreSQL sécurisée, refermée automatiquement."""
    cfg = st.secrets["postgres"]
    with psycopg.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 5432)),
        dbname=cfg.get("dbname", "postgres"),
        user=cfg["user"],
        password=cfg["password"],
        sslmode="require",
        connect_timeout=15,
    ) as conn:
        yield conn
