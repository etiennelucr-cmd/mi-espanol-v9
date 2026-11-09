"""V42 ergonomic styles; no database changes."""
import streamlit as st

def apply():
    st.markdown("""<style>
    .block-container{max-width:1360px!important;padding-top:.7rem!important;padding-bottom:2rem!important}
    header[data-testid="stHeader"]{background:transparent}
    section[data-testid="stSidebar"]{background:#fff0d1}
    .v18-hero{padding:1.35rem 1.7rem!important;margin-bottom:.8rem!important;border-radius:20px!important;background:linear-gradient(110deg,#a5092b,#e53b2f 58%,#efa22e)!important}
    .v18-hero h1{font-size:clamp(1.7rem,3vw,2.5rem)!important}
    .v18-hero p{font-size:1.04rem!important}
    h2{font-size:1.7rem!important;margin-top:.9rem!important}
    h3{font-size:1.3rem!important}
    div[data-testid="stMetric"]{background:#fffdf8!important;border:1px solid #edcb90!important;border-radius:16px!important;padding:15px!important;min-height:105px}
    div[data-testid="stMetricValue"]{font-size:clamp(1.5rem,2vw,2.15rem)!important;color:#a20e2d}
    div[data-testid="stMetricLabel"]{font-size:.93rem!important}
    div[data-testid="stVerticalBlockBorderWrapper"] img{height:175px!important;width:100%!important;object-fit:contain!important;object-position:center!important;border-radius:12px;background:#fff0d8}
    div.stButton>button{min-height:43px!important;font-size:.98rem!important;border-radius:12px!important}
    .mission-card{min-height:108px!important;padding:17px!important;background:#fffdf7!important;border-color:#ecc48c!important}
    .mission-ready{background:#fff2e5!important;border:2px solid #eeb052!important}
    .mission-title{font-size:1.14rem!important;color:#92102b!important}
    .mission-sub{font-size:.91rem!important;color:#725d55!important}
    .mission-label{color:#a91c33!important}
    .dialogue-card{background:#fff5e7!important;border-color:#eac992!important}
    @media(max-width:800px){.block-container{padding:.6rem .8rem 2rem!important}.v18-hero{padding:1rem!important}div[data-testid="stVerticalBlockBorderWrapper"] img{height:125px!important}.mission-card{min-height:90px!important;padding:10px!important}}
    </style>""",unsafe_allow_html=True)
