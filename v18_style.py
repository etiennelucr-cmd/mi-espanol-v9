import streamlit as st

def apply():
    st.markdown('\n<style>\n.v18-hero{background:linear-gradient(115deg,#258d83,#64c67a)!important;box-shadow:0 12px 30px rgba(26,119,104,.15)}\n.mission-card{display:flex;align-items:center;gap:16px;padding:16px 20px;border-radius:20px;border:1px solid #dfe7ee;background:linear-gradient(120deg,#fff,#f6fbff);margin:6px 0;min-height:100px}\n.mission-ready{border-color:#83d7b1;background:linear-gradient(120deg,#f0fff6,#effbff)}\n.mission-done{background:#f5fff8;border-color:#a2dec1}\n.mission-locked{opacity:.62;background:#f5f6f8}\n.mission-avatar{font-size:42px;background:#fff1dd;border-radius:50%;width:68px;height:68px;display:flex;align-items:center;justify-content:center;flex-shrink:0}\n.mission-label{font-size:11px;font-weight:800;letter-spacing:.08em;color:#27856e}\n.mission-title{font-size:19px;font-weight:800;color:#193650;margin:4px 0}\n.mission-sub{font-size:13px;color:#607586}\n.dialogue-card{background:#f1fbff;border:1px solid #cde9ee;border-radius:22px;padding:20px;margin:12px 0}\n.dialogue-avatar{font-size:38px;margin-right:14px}\n.skill-node{border:1px solid #dce6ed;border-radius:20px;padding:16px 20px;margin:8px 0;background:#fff;display:flex;gap:14px;align-items:center}\n.skill-node.current{border:2px solid #36ae88;background:#effbf5;box-shadow:0 4px 18px #269c7520}\n.skill-node.done{background:#effcf5;border-color:#b6e4ca}\n.skill-node.locked{opacity:.65;background:#f5f6f8}\n.skill-emoji{font-size:30px;min-width:44px;text-align:center}\n.skill-name{font-size:16px;font-weight:750;color:#1b394a}\n.skill-status{font-size:12px;color:#5d7887;margin-top:4px}\n.skill-connector{width:3px;height:16px;background:#c7ded6;margin-left:38px}\n</style>\n',unsafe_allow_html=True)


def apply_v19():
    apply()
    st.markdown('''<style>
    .v19-action{border:1px solid #b9e6d1;border-radius:20px;padding:18px 22px;background:linear-gradient(120deg,#effff5,#f4fbff);margin:14px 0}
    .v19-action p{color:#537083;margin:8px 0 0}
    .v19-topic{border:1px solid #dae6eb;border-radius:18px;padding:18px;min-height:150px;background:#f8fcff}
    .v19-topic-icon{font-size:32px;margin-bottom:10px}
    .v19-topic p{font-size:13px;color:#607586}
    @media(max-width:650px){.v18-hero{padding:1rem!important}.mission-card{padding:12px!important;gap:9px!important}.mission-avatar{width:44px;height:44px;font-size:28px}}
    </style>''',unsafe_allow_html=True)

# Identité visuelle Espagne : palette rouge, or et crème, appliquée à toutes les pages V18–V22.
_ORIGINAL_APPLY = apply
def apply():
    _ORIGINAL_APPLY()
    st.markdown("""<style>
    .v18-hero{background:linear-gradient(120deg,#a90d22,#e33232 60%,#f2a82d)!important;box-shadow:0 12px 28px #ad1a2422!important}
    .mission-ready,.v19-action{border-color:#f1bb57!important;background:linear-gradient(110deg,#fff9e8,#fff0e8)!important}
    .mission-done,.skill-node.done{background:#fff8e5!important;border-color:#efc05b!important}
    .mission-avatar{background:#ffe6ad!important}
    .mission-label{color:#ad1529!important}.mission-title,.skill-name{color:#7c1725!important}
    .skill-node.current{border:2px solid #d71e35!important;background:#fff1e5!important;box-shadow:0 4px 18px #c6252822!important}
    .skill-connector{background:#eab35b!important}
    .dialogue-card{background:#fff7e8!important;border-color:#f4d7a0!important}
    .cecrl-road{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0 20px}
    .cecrl-pill{padding:10px 15px;border-radius:14px;font-weight:800;border:1px solid #e8d3ad}
    .cecrl-open{background:#fff0c6;color:#8b1728;border-color:#e5b24b}
    .cecrl-locked{background:#f4f1ed;color:#8d8985;opacity:.8}
    </style>""",unsafe_allow_html=True)
