"""Diagnostic léger des temps d'exécution (aucune donnée personnelle ni SQL)."""
import time
import streamlit as st

START=time.perf_counter()
COUNTS={}

def record(label, seconds):
    count, total, longest = COUNTS.get(label,(0,0.0,0.0))
    COUNTS[label]=(count+1,total+seconds,max(longest,seconds))

def report():
    total=time.perf_counter()-START
    with st.sidebar.expander('⏱️ Diagnostic V16.2 (facultatif)',expanded=False):
        st.caption('Mesures de ce chargement uniquement ; aucune requête SQL ni information personnelle affichée.')
        st.metric('Temps serveur mesuré',f'{total:.2f} s')
        for label,(count,seconds,longest) in sorted(COUNTS.items(),key=lambda x:-x[1][1]):
            st.write(f'**{label}** : {seconds:.2f} s · {count} appel(s) · max {longest:.2f} s')
        st.caption('Si le navigateur reste lent malgré un temps serveur court, la latence peut venir du réseau ou de l’affichage Streamlit. Un premier démarrage peut aussi inclure le réveil du serveur.')
