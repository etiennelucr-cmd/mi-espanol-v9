"""Export/import portable de la progression Aventure (sans secrets ni identifiants)."""
import json
from datetime import datetime
import streamlit as st

FIELDS = ('completed', 'attempts', 'xp', 'coins', 'seen')

def export_data(state):
    return json.dumps({'format': 'mi-espanol-aventure-v22', 'exported_at': datetime.now().isoformat(timespec='seconds'), 'progress': {k: state.get(k, {} if k == 'completed' else [] if k in ('attempts','seen') else 0) for k in FIELDS}}, ensure_ascii=False, indent=2).encode('utf-8')

def import_data(raw):
    if len(raw)>2_000_000:
        raise ValueError('Fichier trop volumineux.')
    data=json.loads(raw)
    if data.get('format') != 'mi-espanol-aventure-v22' or not isinstance(data.get('progress'),dict):
        raise ValueError('Format de sauvegarde non reconnu.')
    p=data['progress']
    if not isinstance(p.get('completed'),dict) or not isinstance(p.get('attempts'),list):
        raise ValueError('Données de progression invalides.')
    if len(p['attempts'])>20000 or len(p['completed'])>2000:
        raise ValueError('Sauvegarde trop volumineuse.')
    clean={
        'completed':{str(k):max(0,min(5,int(v))) for k,v in p['completed'].items() if isinstance(k,str)},
        'attempts':[{'date':str(a['date']),'level':str(a['level']),'theme':str(a['theme']),'correct':bool(a['correct']),'word':str(a.get('word',''))} for a in p['attempts'] if isinstance(a,dict) and all(k in a for k in ('date','level','theme','correct'))],
        'xp':max(0,int(p.get('xp',0))), 'coins':max(0,int(p.get('coins',0))),
        'seen':[tuple(x) for x in p.get('seen',[]) if isinstance(x,(list,tuple)) and len(x)==3][-100:],
        'active':None,'answer':None,
    }
    return clean

def panel(state):
    with st.expander('💾 Sauvegarder / restaurer mon aventure'):
        st.caption('Sauvegarde manuelle de tes mini-défis, XP et étapes de l’arbre. Les résultats historiques de PostgreSQL ne sont pas inclus.')
        st.download_button('⬇️ Exporter ma progression',data=export_data(state),file_name='mi-espanol-progression-v22.json',mime='application/json',key='v22_export')
        uploaded=st.file_uploader('Importer une sauvegarde V22',type=['json'],key='v22_import_file')
        if uploaded is not None and st.button('Restaurer cette sauvegarde',key='v22_restore'):
            try:
                restored=import_data(uploaded.getvalue())
                st.session_state['v18_arbre']=restored
                st.success('Progression restaurée pour cette session.')
                st.rerun()
            except (ValueError,TypeError,KeyError,UnicodeDecodeError) as exc:
                st.error(f'Import impossible : {exc}')
