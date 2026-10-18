"""Parcours progressif de conjugaison, évaluations internes non certificatives."""
import json
import random
import time
from datetime import date, datetime, timedelta
from collections import defaultdict
from pathlib import Path
import pandas as pd
import streamlit as st
import moteur as m

PERSONNES=['yo','tú','él/ella/usted','nosotros/as','vosotros/as','ellos/ellas/ustedes']
PARCOURS={
 'A1':[('presente','Présent de l’indicatif'),('perfecto','Passé composé (pretérito perfecto)')],
 'A2':[('indefinido','Passé simple (pretérito indefinido)'),('imperfecto','Imparfait'),('futuro','Futur simple')],
 'B1':[('condicional','Conditionnel simple'),('subj_pres','Présent du subjonctif'),('imperativo','Impératif affirmatif')],
 'B2':[('pluscuamperfecto','Plus-que-parfait'),('subj_imp','Imparfait du subjonctif'),('futuro_perfecto','Futur antérieur')],
 'C1':[('condicional_compuesto','Conditionnel passé'),('subj_perfecto','Passé du subjonctif'),('subj_pluscuam','Plus-que-parfait du subjonctif')],
 'C2':[('preterito_anterior','Passé antérieur (littéraire)'),('futuro_subj','Futur du subjonctif (rare)'),('futuro_subj_perfecto','Futur antérieur du subjonctif (rare)')]
}
EXPLICATIONS={
 'presente':('Actions habituelles, faits actuels.','Cada día hablo español. — Chaque jour je parle espagnol.'),
 'perfecto':('Passé lié au présent ; haber au présent + participe passé.','Hoy he hablado con Ana. — Aujourd’hui, j’ai parlé avec Ana.'),
 'indefinido':('Action passée achevée et datée.','Ayer hablé con Ana. — Hier, j’ai parlé avec Ana.'),
 'imperfecto':('Habitudes et descriptions dans le passé.','De niño hablaba mucho. — Enfant, je parlais beaucoup.'),
 'futuro':('Action future ou hypothèse.','Mañana hablaré con Ana. — Demain, je parlerai avec Ana.'),
 'condicional':('Hypothèse, souhait ou politesse.','Hablaría más si tuviera tiempo. — Je parlerais davantage si j’avais le temps.'),
 'subj_pres':('Souhait, doute ou jugement après certaines expressions.','Quiero que hables español. — Je veux que tu parles espagnol.'),
 'imperativo':('Ordre, conseil ou invitation ; formes affirmatives.','¡Habla más despacio! — Parle plus lentement !'),
 'pluscuamperfecto':('Action antérieure à une autre action passée.','Ya había hablado. — J’avais déjà parlé.'),
 'subj_imp':('Subjonctif dans un contexte passé ou hypothétique.','Quería que hablaras. — Je voulais que tu parles.'),
 'futuro_perfecto':('Action qui sera achevée à un moment futur.','Mañana habré terminado. — Demain, j’aurai terminé.'),
 'condicional_compuesto':('Conséquence hypothétique non réalisée dans le passé.','Habría hablado si hubiera podido. — J’aurais parlé si j’avais pu.'),
 'subj_perfecto':('Action passée envisagée subjectivement.','Espero que hayas hablado. — J’espère que tu as parlé.'),
 'subj_pluscuam':('Irréel du passé ou antériorité au subjonctif.','Ojalá hubieras hablado. — Si seulement tu avais parlé.'),
 'preterito_anterior':('Temps littéraire marquant une antériorité immédiate.','Apenas hube hablado, salí. — À peine eus-je parlé que je sortis.'),
 'futuro_subj':('Forme archaïque, encore visible dans des textes juridiques.','Quien hablare... — Quiconque parlera...'),
 'futuro_subj_perfecto':('Forme archaïque d’antériorité au futur du subjonctif.','Quien hubiere hablado... — Quiconque aura parlé...')
}
PRESENT_HABER=['he','has','ha','hemos','habéis','han']
IMPERF_HABER=['había','habías','había','habíamos','habíais','habían']
FUT_HABER=['habré','habrás','habrá','habremos','habréis','habrán']
COND_HABER=['habría','habrías','habría','habríamos','habríais','habrían']
SUBJ_HABER=['haya','hayas','haya','hayamos','hayáis','hayan']
SUBJ_IMP_HABER=['hubiera','hubieras','hubiera','hubiéramos','hubierais','hubieran']
ANT_HABER=['hube','hubiste','hubo','hubimos','hubisteis','hubieron']
FUT_SUBJ_HABER=['hubiere','hubieres','hubiere','hubiéremos','hubiereis','hubieren']


def formes(verbe,temps,donnees):
    """Formes vérifiées pour les verbes réguliers et les 4 paradigmes fournis."""
    if temps in ('presente','indefinido','imperfecto','futuro'):
        i={'presente':2,'indefinido':3,'imperfecto':4,'futuro':5}[temps]
        return donnees[i]
    # Éviter de présenter des participes irréguliers comme réguliers.
    if not verbe.endswith(('ar','er','ir')) or verbe in {'ser','estar','haber','tener','ir','hacer','poder','querer','decir','venir','saber','poner','leer','escribir'}:
        return None
    radical,grp=verbe[:-2],verbe[-2:]
    part=radical+('ado' if grp=='ar' else 'ido')
    if temps in ('perfecto','pluscuamperfecto','futuro_perfecto','condicional_compuesto','subj_perfecto','subj_pluscuam','preterito_anterior','futuro_subj_perfecto'):
        aux={'perfecto':PRESENT_HABER,'pluscuamperfecto':IMPERF_HABER,'futuro_perfecto':FUT_HABER,'condicional_compuesto':COND_HABER,'subj_perfecto':SUBJ_HABER,'subj_pluscuam':SUBJ_IMP_HABER,'preterito_anterior':ANT_HABER,'futuro_subj_perfecto':FUT_SUBJ_HABER}[temps]
        return [a+' '+part for a in aux]
    if temps=='condicional':return [verbe+x for x in ['ía','ías','ía','íamos','íais','ían']]
    if temps=='subj_pres':
        return [radical+x for x in (['e','es','e','emos','éis','en'] if grp=='ar' else ['a','as','a','amos','áis','an'])]
    if temps=='subj_imp':
        return [radical+x for x in (['ara','aras','ara','áramos','arais','aran'] if grp=='ar' else ['iera','ieras','iera','iéramos','ierais','ieran'])]
    if temps=='futuro_subj':
        return [radical+x for x in (['are','ares','are','áremos','areis','aren'] if grp=='ar' else ['iere','ieres','iere','iéremos','iereis','ieren'])]
    if temps=='imperativo':
        # Pas de forme impérative « yo » ; tu, usted, nosotros, vosotros, ustedes.
        if grp=='ar':return ['—',radical+'a',radical+'e',radical+'emos',radical+'ad',radical+'en']
        return ['—',radical+'e',radical+'a',radical+'amos',radical+('ed' if grp=='er' else 'id'),radical+'an']
    return None


def init():
    with m.connexion() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS conjugaison_tests (
            id INTEGER PRIMARY KEY, date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            niveau TEXT NOT NULL, temps TEXT NOT NULL, type TEXT NOT NULL,
            score INTEGER NOT NULL, total INTEGER NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS conjugaison_reponses (
            id INTEGER PRIMARY KEY, test_id INTEGER NOT NULL, niveau TEXT NOT NULL,
            temps TEXT NOT NULL, verbe TEXT NOT NULL, personne INTEGER NOT NULL,
            correct INTEGER NOT NULL, date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')


def statut(niveau,temps):
    r=m.rows('SELECT MAX(CAST(score AS REAL)/total) meilleur,COUNT(*) essais FROM conjugaison_tests WHERE niveau=? AND temps=? AND type="Contrôle" AND total>=20',(niveau,temps))[0]
    return (r['meilleur'] or 0),r['essais']


def autorisations():
    accessibles=['A1']
    for n in m.NIVEAUX[:-1]:
        if all(statut(n,t)[0]>=.95 for t,_ in PARCOURS[n]):accessibles.append(m.NIVEAUX[m.NIVEAUX.index(n)+1])
        else:break
    return accessibles


def banque(temps,verbes,taille=20,niveau=None,exclure=None):
    """Priorité aux erreurs récentes et aux notions peu évaluées ; acquis espacés."""
    pool=[(v,i,val) for v,d in verbes.items() for i,val in enumerate(formes(v,temps,d) or []) if val!='—']
    if len(pool)<taille:return []
    stats=defaultdict(lambda: [0,0,0])
    if niveau:
        for r in m.rows("""SELECT verbe,personne,COUNT(*) essais,
                SUM(correct) succes,MAX(id) dernier FROM conjugaison_reponses
                WHERE niveau=? AND temps=? GROUP BY verbe,personne""",(niveau,temps)):
            stats[(r['verbe'],r['personne'])]=[r['essais'],r['succes'],r['dernier']]
    exclus=set(exclure or [])
    rng=random.Random()
    def priorite(q):
        essais,succes,dernier=stats[(q[0],q[1])]
        if not essais:return 1.2+rng.random()*.25
        erreurs=essais-succes
        taux=succes/essais
        # Une notion réussie est réintroduite de temps en temps pour vérifier la rétention.
        return (1-taux)*2 + (0.7 if erreurs else 0) + 0.3/(essais+1)+rng.random()*.45
    pool.sort(key=lambda q:(q in exclus,-priorite(q)))
    return pool[:taille]


def progression(niveau):
    result=[]
    for t,nom in PARCOURS[niveau]:
        meilleur,essais=statut(niveau,t)
        result.append({'Temps':nom,'Meilleur contrôle':f'{meilleur:.0%}',
                       'Objectif': '95 %','État':'✅ Validé' if meilleur>=.95 else '🔒 À travailler',
                       'Progrès vers 95 %':min(1,meilleur/.95)})
    return result


def estimation(niveau):
    """Projection indicative à partir de contrôles distincts sur plusieurs jours."""
    rows=m.rows("""SELECT date,temps,MAX(CAST(score AS REAL)/total) ratio
        FROM conjugaison_tests WHERE niveau=? AND type='Contrôle' AND total>=20
        GROUP BY substr(date,1,10),temps ORDER BY date""",(niveau,))
    jours=sorted(set(r['date'][:10] for r in rows))
    if len(jours)<3 or (date.fromisoformat(jours[-1])-date.fromisoformat(jours[0])).days<2:
        return None
    by_day=defaultdict(dict)
    for r in rows:by_day[r['date'][:10]][r['temps']]=max(r['ratio'],by_day[r['date'][:10]].get(r['temps'],0))
    cumul={t:0 for t,_ in PARCOURS[niveau]}
    serie=[]
    for jour in jours:
        for t,ratio in by_day[jour].items():cumul[t]=max(cumul.get(t,0),ratio)
        serie.append((date.fromisoformat(jour),sum(min(1,v/.95) for v in cumul.values())/len(cumul)))
    debut,fin=serie[0],serie[-1]
    ecart=(fin[0]-debut[0]).days
    pente=(fin[1]-debut[1])/ecart if ecart else 0
    if pente<=0.001 or fin[1]>=1:return None
    attente=(1-fin[1])/pente
    if attente<1 or attente>365:return None
    return date.today()+timedelta(days=round(attente))


def page():
    init()
    verbes=json.loads((Path(__file__).resolve().parent/'verbes.json').read_text(encoding='utf-8'))
    st.title('📗 Verbes et conjugaisons — parcours A1 → C2')
    st.caption('Tirages adaptatifs : erreurs prioritaires, acquis espacés et nouveaux exercices après chaque correction. Leçons, fiches de révision, QCM et contrôles. Chaque temps est validé à 95 % minimum sur un contrôle de 20 questions (19/20). Progression sauvegardée dans SQLite.')
    acces=autorisations()
    cols=st.columns(6)
    for col,n in zip(cols,m.NIVEAUX):
        col.metric(n,'🔓' if n in acces else '🔒')
    n=st.selectbox('Niveau de conjugaison accessible',acces,key='conj_niveau')
    choix=PARCOURS[n]
    libelles={t:nom for t,nom in choix}
    courant=next((code for code,_ in choix if statut(n,code)[0]<.95),choix[-1][0])
    st.info('📌 Temps prioritaire : **'+libelles[courant]+'**. Il reste au programme jusqu’à 19/20 au contrôle.')
    t=st.selectbox('Temps à apprendre',list(libelles),index=list(libelles).index(courant),format_func=lambda x:libelles[x]+(' 🔒' if statut(n,x)[0]<.95 and list(libelles).index(x)>list(libelles).index(courant) else ''),key='conj_temps')
    if list(libelles).index(t)>list(libelles).index(courant):
        st.warning('Valide d’abord le temps prioritaire à 95 %.');return
    meilleur,essais=statut(n,t)
    st.subheader('📊 Progression des temps')
    suivi=progression(n)
    st.dataframe(pd.DataFrame([{k:v for k,v in x.items() if k!='Progrès vers 95 %'} for x in suivi]),hide_index=True,use_container_width=True)
    st.progress(sum(x['Progrès vers 95 %'] for x in suivi)/len(suivi),text=f'Progression globale vers les objectifs : {sum(x["Progrès vers 95 %"] for x in suivi)/len(suivi):.0%}')
    if len(acces)>m.NIVEAUX.index(n)+1:st.success('Le niveau suivant est déjà débloqué.')
    else:
        prevision=estimation(n)
        if prevision:st.info(f'Date indicative de déblocage du niveau suivant : {prevision.strftime("%d/%m/%Y")}. Projection fondée sur la tendance de tes contrôles ; elle ne garantit pas la date réelle.')
        else:st.caption('Estimation du déblocage : effectue des contrôles sur au moins 3 jours distincts, avec une progression mesurable, pour obtenir une date indicative.')
    st.progress(min(1,meilleur),text=f'Meilleur contrôle : {meilleur:.0%} · seuil 95 % · {essais} contrôle(s)')
    description,exemple=EXPLICATIONS[t]
    tabs=st.tabs(['📚 Leçon','🗒️ Fiche de révision','🧠 QCM','🧪 Contrôle'])
    eligibles={v:d for v,d in verbes.items() if formes(v,t,d)}
    with tabs[0]:
        st.subheader(libelles[t])
        st.write(description)
        st.info(exemple)
        st.caption('Pour les temps avancés, seuls les verbes dont les formes sont prises en charge sont proposés. Les irrégularités restantes seront enrichies ultérieurement.')
        v=st.selectbox('Verbe',list(eligibles),format_func=lambda x:f'{x} — {eligibles[x][1]}',key='conj_verbe')
        st.dataframe(pd.DataFrame({'Personne':PERSONNES,'Conjugaison':formes(v,t,eligibles[v])}),hide_index=True,use_container_width=True)
    with tabs[1]:
        st.markdown(f'**À retenir :** {description}')
        st.write('**Exemple :**',exemple)
        for v,d in list(eligibles.items())[:5]:
            with st.expander(f'{v} — {d[1]}'):
                st.table(pd.DataFrame({'Personne':PERSONNES,'Forme':formes(v,t,d)}))
        st.caption('Méthode : lis la règle, récite les six formes, cache le tableau, écris-les puis vérifie. Révise les erreurs le lendemain et trois jours après.')
    for tab,typ,taille in [(tabs[2],'QCM',10),(tabs[3],'Contrôle',20)]:
        with tab:
            prefix=f'conj_{typ}_{n}_{t}'
            qkey=prefix+'_lot'
            if qkey not in st.session_state:
                st.session_state[qkey]=banque(t,eligibles,taille,niveau=n)
                st.session_state[prefix+'_debut']=time.monotonic()
            lot=st.session_state[qkey]
            correction=st.session_state.pop(prefix+'_correction',None)
            if correction:
                st.success(f"{typ} enregistré : {correction['score']}/{correction['total']} ({correction['score']/correction['total']:.0%})")
                if typ=='Contrôle' and correction['score']/correction['total']>=.95:st.success('Temps validé ! Le niveau suivant se débloquera lorsque tous les temps de ce niveau seront validés.')
                for question,rep in correction['erreurs']:
                    st.write(f'❌ {question[0]} — {PERSONNES[question[1]]} : **{question[2]}** (ta réponse : {rep or "aucune"})')
                    st.caption('Règle : '+EXPLICATIONS[t][0]+' Exemple : '+EXPLICATIONS[t][1])
            if not lot:
                st.warning('Banque de questions insuffisante pour ce temps.');continue
            with st.form(prefix+'_form'):
                reponses=[]
                for i,(v,personne,bonne) in enumerate(lot):
                    autres=list({f for w,d in eligibles.items() for f in (formes(w,t,d) or []) if f not in ('—',bonne)})
                    # Distracteurs stables pendant les reruns de Streamlit.
                    rng=random.Random(f'{prefix}:{i}:{v}:{personne}:{bonne}')
                    options=[bonne]+rng.sample(autres,min(3,len(autres)))
                    rng.shuffle(options)
                    reponses.append(st.radio(f'{i+1}. {v} — {PERSONNES[personne]}',options,index=None,key=f'{prefix}_{st.session_state.get(prefix+"_tour",0)}_{i}'))
                valider=st.form_submit_button('Corriger et enregistrer',type='primary')
            if valider:
                if any(r is None for r in reponses):st.warning('Réponds à toutes les questions avant de valider.')
                else:
                    score=sum(r==q[2] for q,r in zip(lot,reponses))
                    with m.connexion() as c:
                        cur=c.execute('INSERT INTO conjugaison_tests(niveau,temps,type,score,total) VALUES(?,?,?,?,?)',(n,t,typ,score,len(lot)))
                        test_id=cur.lastrowid
                        c.executemany('INSERT INTO conjugaison_reponses(test_id,niveau,temps,verbe,personne,correct) VALUES(?,?,?,?,?,?)',[(test_id,n,t,q[0],q[1],int(r==q[2])) for q,r in zip(lot,reponses)])
                    # Temps actif approximatif, borné à 2 heures par évaluation.
                    secondes=max(0,min(7200,int(time.monotonic()-st.session_state.get(prefix+'_debut',time.monotonic()))))
                    if secondes:
                        m.enregistrer_session('Verbes et conjugaisons',secondes/60,n)
                    st.session_state[prefix+'_debut']=time.monotonic()
                    st.session_state[prefix+'_correction']={'score':score,'total':len(lot),'erreurs':[(q,r) for q,r in zip(lot,reponses) if r!=q[2]]}
                    st.session_state[prefix+'_tour']=st.session_state.get(prefix+'_tour',0)+1
                    st.session_state[qkey]=banque(t,eligibles,taille,niveau=n,exclure=lot)
                    st.rerun()
