"""Thème visuel commun à toutes les sections Streamlit."""
import streamlit as st
from pathlib import Path

def apply():
    css = Path(__file__).with_name("espana_v24.css").read_text(encoding="utf-8")
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)
