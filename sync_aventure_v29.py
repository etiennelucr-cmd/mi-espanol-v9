"""Sauvegarde optionnelle PostgreSQL, isolée par clé privée choisie par l'utilisateur.
Aucune identité implicite : jamais de stockage commun à tous les visiteurs.
"""
import hashlib, hmac, json
import streamlit as st
from cloud_db import connexion_cloud
import sauvegarde_aventure_v27 as save

DDL="""CREATE TABLE IF NOT EXISTS mi_espanol_aventure_v29 (
 profile_hash TEXT PRIMARY KEY, data JSONB NOT NULL,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"""

def _profile():
    secret=st.session_state.get('v29_private_key','')
    if len(secret)<12:raise ValueError('Utilise une clé privée d’au moins 12 caractères.')
    # Identifiant opaque : le secret ne quitte pas la session.
    return hashlib.sha256(('mi-espanol-v29:'+secret).encode()).hexdigest()

def save_remote():
    key=_profile(); payload=save.snapshot()
    with connexion_cloud() as conn:
        conn.execute(DDL)
        conn.execute("INSERT INTO mi_espanol_aventure_v29(profile_hash,data) VALUES (%s,%s::jsonb) ON CONFLICT(profile_hash) DO UPDATE SET data=EXCLUDED.data,updated_at=NOW()",
            (key,json.dumps(payload,ensure_ascii=False)))

def load_remote():
    key=_profile()
    with connexion_cloud() as conn:
        conn.execute(DDL)
        row=conn.execute('SELECT data FROM mi_espanol_aventure_v29 WHERE profile_hash=%s',(key,)).fetchone()
    if row is None:return False
    save.restore(row[0] if isinstance(row[0],dict) else json.loads(row[0]))
    return True

def autosave():
    if not (st.session_state.get('v29_sync_enabled') and st.session_state.get('v29_sync_armed')):return
    try:
        payload=save.snapshot();payload.pop('exporte_le',None)
        digest=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        if digest!=st.session_state.get('v29_last_saved'):
            save_remote()
            st.session_state.v29_last_saved=digest
            st.session_state.v29_sync_error=None
    except Exception as exc:
        st.session_state.v29_sync_error=str(exc)

def panel():
    st.subheader('☁️ Synchronisation de mon aventure')
    st.caption('Optionnelle. Une clé privée personnelle identifie ta sauvegarde. Ne partage pas cette clé : elle permet de retrouver et remplacer tes données d’aventure.')
    st.text_input('Ma clé privée (12 caractères minimum)',type='password',key='v29_private_key')
    c1,c2=st.columns(2)
    with c1:
        if st.button('📥 Charger depuis PostgreSQL',key='v29_load'):
            try:
                if load_remote():
                    st.session_state.v29_last_saved=None
                    st.session_state.v29_sync_armed=True
                    st.success('Sauvegarde chargée.');st.rerun()
                else:st.info('Aucune sauvegarde pour cette clé.')
            except Exception as exc:st.error(f'Chargement impossible : {exc}')
    with c2:
        if st.button('📤 Enregistrer maintenant',key='v29_save'):
            try:
                save_remote()
                st.session_state.v29_sync_armed=True
                st.success('Sauvegarde enregistrée.')
            except Exception as exc:st.error(f'Enregistrement impossible : {exc}')
    st.checkbox('Activer la sauvegarde automatique pendant cette session',key='v29_sync_enabled',disabled=len(st.session_state.get('v29_private_key',''))<12)
    if not st.session_state.get('v29_sync_armed'):
        st.caption('Pour éviter tout écrasement, charge d’abord ta sauvegarde distante ou enregistre explicitement cette session.')
    if st.session_state.get('v29_sync_error'):st.warning('Synchronisation non disponible : '+st.session_state.v29_sync_error)
    st.caption('Ne synchronise pas les notes, examens ou validations CECRL. Le chargement est manuel pour éviter d’écraser une progression sans confirmation.')
