from pathlib import Path
import streamlit as st

def apply():
    css=Path(__file__).with_name('v40_espana.css').read_text(encoding='utf-8')
    st.markdown('<style>'+css+'</style>',unsafe_allow_html=True)
