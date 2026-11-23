"""Correctif Mi Español V5 -> V5.1 : compatibilité des profils anciens.
À exécuter une fois dans le dossier qui contient app.py.
"""
from pathlib import Path

app = Path(__file__).with_name('app.py')
if not app.is_file():
    app = Path.cwd() / 'app.py'
if not app.is_file():
    raise SystemExit('app.py introuvable. Place ce script à côté du fichier app.py de la V5.')

source = app.read_text(encoding='utf-8')
original = """if 'profile' not in st.session_state:
    st.session_state.profile = load_profile()
p = st.session_state.profile"""
fixed = """if 'profile' not in st.session_state:
    st.session_state.profile = load_profile()
# Corrige les profils V2/V3/V4 conservés en session : initialise grammar_exams,
# grammar, verbs, tenses, llcer, etc. sans effacer les réussites existantes.
st.session_state.profile = normalize(st.session_state.profile)
p = st.session_state.profile"""

if fixed in source:
    print('Le correctif V5.1 est déjà installé, aucune modification nécessaire.')
elif source.count(original) != 1:
    raise SystemExit('Structure de app.py différente : aucun fichier modifié. Mets à jour à partir de la V5 officielle.')
else:
    backup = app.with_name('app.py.avant_v5_1.bak')
    backup.write_text(source, encoding='utf-8')
    app.write_text(source.replace(original,fixed,1), encoding='utf-8')
    print('Corrigé :',app)
    print('Copie de sauvegarde :',backup)
