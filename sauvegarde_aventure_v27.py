"""Export et restauration manuels des mini-jeux (pas des validations CECRL)."""
import json
from datetime import datetime
import streamlit as st
import aventure_v18 as av
import arbre_competences_v18 as arbre
import mini_jeux_v41 as games

SCHEMA=41
def snapshot():
    a=av._state(); b=arbre.state(); g=games.state()
    return {
        "format":"mi-espanol-aventure", "version":SCHEMA,
        "exporte_le":datetime.now().isoformat(timespec="seconds"),
        "missions":{"xp":int(a.get("xp",0)),"pieces":int(a.get("pieces",0)),
                    "terminees":list(a.get("terminees",[]))},
        "mini_jeux_v41":{"xp":int(g.get("xp",0)),"coins":int(g.get("coins",0)),"attempts":list(g.get("attempts",[]))},
        "arbre":{"xp":int(b.get("xp",0)),"coins":int(b.get("coins",0)),
                 "completed":dict(b.get("completed",{})),
                 "attempts":list(b.get("attempts",[])),
                 "seen":[list(x) for x in b.get("seen",[])]},
    }
def _number(v):
    if type(v) is not int or not 0<=v<=10000000: raise ValueError("Compteur invalide")
    return v
def restore(data):
    if not isinstance(data,dict) or data.get("format")!="mi-espanol-aventure" or data.get("version") not in (27,28,41):
        raise ValueError("Format de sauvegarde V27/V28/V41 non reconnu")
    a=data.get("missions"); b=data.get("arbre")
    if not isinstance(a,dict) or not isinstance(b,dict):raise ValueError("Données incomplètes")
    xp=_number(a.get("xp")); coins=_number(a.get("pieces"))
    done=a.get("terminees")
    if not isinstance(done,list) or len(done)>100 or any(type(x)!=int or x<0 or x>=len(av.MISSIONS) for x in done):
        raise ValueError("Missions invalides")
    bx=_number(b.get("xp")); bc=_number(b.get("coins"))
    completed=b.get("completed"); attempts=b.get("attempts"); seen=b.get("seen")
    if not isinstance(completed,dict) or len(completed)>1000 or any(not isinstance(k,str) or len(k)>150 or type(v)!=int or v not in range(6) for k,v in completed.items()):
        raise ValueError("Étapes invalides")
    if not isinstance(attempts,list) or len(attempts)>20000 or any(not isinstance(x,dict) for x in attempts):
        raise ValueError("Historique invalide")
    if not isinstance(seen,list) or len(seen)>100 or any(not isinstance(x,list) or len(x)!=3 or any(not isinstance(y,str) for y in x) for x in seen):
        raise ValueError("Mots vus invalides")
    game_data=data.get('mini_jeux_v41',{})
    if not isinstance(game_data,dict):raise ValueError('Mini-jeux invalides')
    gx=_number(game_data.get('xp',0));gc=_number(game_data.get('coins',0))
    ga=game_data.get('attempts',[])
    if not isinstance(ga,list) or len(ga)>2000 or any(not isinstance(x,dict) or type(x.get('correct')) is not bool or
        not isinstance(x.get('mode'),str) or len(x.get('mode',''))>80 or
        not isinstance(x.get('date'),str) or len(x.get('date',''))>40 or
        not isinstance(x.get('level'),str) or x.get('level') not in ('A1','A2','B1','B2','C1','C2')
        for x in ga):raise ValueError('Historique mini-jeux invalide')
    aa=av._state();bb=arbre.state();gg=games.state()
    aa.update(xp=xp,pieces=coins,terminees=list(dict.fromkeys(done)),mission=None,etape=0,choix=None,jeu=None)
    bb.update(xp=bx,coins=bc,completed=completed,attempts=attempts,seen=[tuple(x) for x in seen],active=None,answer=None)
    gg.update(xp=gx,coins=gc,attempts=ga,question=None,answer=None,round=0)

def page():
    st.subheader("💾 Sauvegarder mon aventure")
    st.caption("Sauvegarde manuelle des missions, récompenses et mini-défis. Les résultats historiques, les examens et les validations CECRL ne sont pas modifiés.")
    st.download_button("⬇️ Exporter mon aventure (JSON)",
                       data=json.dumps(snapshot(),ensure_ascii=False,indent=2),
                       file_name="mi-espanol-aventure-v41.json",mime="application/json",
                       key="v27_export")
    f=st.file_uploader("Restaurer une sauvegarde V27/V28/V41",type=["json"],key="v27_import")
    if f is not None:
        try:
            raw=f.getvalue()
            if len(raw)>2_000_000:raise ValueError("Fichier trop volumineux")
            parsed=json.loads(raw.decode("utf-8"))
            if st.button("Confirmer la restauration (remplace les mini-jeux de cette session)",key="v27_confirm"):
                restore(parsed)
                st.success("Aventure restaurée dans cette session.")
                st.rerun()
        except (ValueError,UnicodeDecodeError,TypeError) as exc:
            st.error(f"Impossible de restaurer : {exc}")
    st.info("Export manuel : garde le fichier en lieu sûr. Les données CECRL historiques ne sont pas modifiées.")
