"""Synthèse pédagogique multi-activités et radio, sans API externe obligatoire."""
from collections import defaultdict
from datetime import date
import random
import streamlit as st
import streamlit.components.v1 as components
import moteur as m
import pedagogie as p

RADIO_SITE = 'https://www.espana.fm/'

def radio():
    with st.expander('📻 Radio española · ambiance immersive (déplier)', expanded=False):
        st.caption('Écoute les radios espagnoles depuis España FM. Choisis une station sur le site ; la lecture nécessite une action de ta part.')
        st.link_button('▶ Ouvrir España FM et choisir une radio', RADIO_SITE)
        st.caption('Le site externe peut afficher des contenus ou publicités tiers.')
        if st.checkbox('Essayer le site intégré (si autorisé)', key='radio_embed'):
            components.iframe(RADIO_SITE, height=340, scrolling=True)

def synthese(niveau):
    """Priorise les erreurs de toutes les activités évaluées; oral/autoéval = signal non noté."""
    vus={r['lecon_id'] for r in m.rows("SELECT DISTINCT lecon_id FROM sessions WHERE niveau=? AND type='Cours' AND lecon_id IS NOT NULL",(niveau,))}
    vus.update(r['id'] for r in m.rows("SELECT id FROM lecons WHERE niveau=? AND statut IN ('en cours','terminé')",(niveau,)))
    if not vus:return []
    # Les erreurs ne doivent provenir que de leçons déjà étudiées.
    codes_vus={str(l['id']) for l in m.COURS.get(niveau,[]) if l['id'] in vus}
    scores=defaultdict(lambda: {'erreurs':0,'total':0,'reussites':0,'sources':set(),'exemples':[]})
    raw=m.rows('''SELECT r.competence, t.type, COUNT(*) total,
        SUM(CASE WHEN r.correct=0 THEN 1 ELSE 0 END) erreurs
        FROM reponses r JOIN tentatives t ON t.id=r.tentative_id
        WHERE t.niveau=? AND t.lecon_id IS NOT NULL AND t.lecon_id IN (SELECT id FROM lecons WHERE niveau=? AND statut IN ('en cours','terminé')) GROUP BY r.competence,t.type''',(niveau,niveau))
    for r in raw:
        s=scores[r['competence']];s['total']+=r['total'];s['erreurs']+=r['erreurs'];s['sources'].add(r['type'])
    for r in m.rows('''SELECT r.competence,q.enonce,q.bonne,q.explication,r.choix,t.type
        FROM reponses r JOIN tentatives t ON t.id=r.tentative_id
        LEFT JOIN questions q ON q.id=r.question_id
        WHERE t.niveau=? AND r.correct=0 AND t.lecon_id IS NOT NULL AND t.lecon_id IN (SELECT id FROM lecons WHERE niveau=? AND statut IN ('en cours','terminé')) ORDER BY r.id DESC LIMIT 250''',(niveau,niveau)):
        s=scores[r['competence']]
        if len(s['exemples'])<2 and r['enonce']:
            s['exemples'].append((r['enonce'],r['choix'],r['bonne'],r['explication']))
    for r in m.rows('SELECT code,nom,maitrise,prochaine_revision FROM competences WHERE niveau=? AND essais>0',(niveau,)):
        if not any(str(r['code']).startswith(ident+'-') for ident in codes_vus):continue
        s=scores[r['code']];s['nom']=r['nom'];s['maitrise']=r['maitrise'];s['due']=r['prochaine_revision'] and r['prochaine_revision']<=date.today().isoformat()
    # Les productions écrites sont évaluées par comparaison stricte, pas par compétence grammaticale.
    ecrits=m.rows('''SELECT consigne,reponse,attendu,valide FROM productions
        WHERE niveau=? ORDER BY id DESC LIMIT 150''',(niveau,))
    phrases_vues={fr for l in m.COURS.get(niveau,[]) if l['id'] in vus for es,fr in (l.get('exemples',[])+l.get('expressions',[]))}
    ecrits=[x for x in ecrits if x['consigne'] in phrases_vues]
    echec=[x for x in ecrits if x['valide']==0]
    if ecrits:
        s=scores['__ecrit__'];s.update({'nom':'Expression écrite — traductions','total':sum(x['valide'] is not None for x in ecrits), 'erreurs':len(echec),'maitrise':1-len(echec)/max(1,sum(x['valide'] is not None for x in ecrits)),'due':False})
        s['sources'].add('Expression écrite')
        for r in echec[:2]:s['exemples'].append((f'Traduis : {r["consigne"]}',r['reponse'],r['attendu'],'Réécris la traduction sans regarder la solution. Plusieurs traductions peuvent être acceptables.'))
    ranked=sorted([(k,v) for k,v in scores.items() if v['total']>0 and v['erreurs']>0 and (k=='__ecrit__' or any(str(k).startswith(ident+'-') for ident in codes_vus))],key=lambda x:(-(x[1]['erreurs']/x[1]['total']),-x[1]['erreurs'],x[1].get('maitrise',1)))
    return ranked

def points_faibles(niveau):
    st.subheader(f'🎯 Points faibles à travailler — niveau {niveau} uniquement')
    ranked=synthese(niveau)
    if not ranked:
        st.info('Pas encore assez de réponses évaluées. Fais un quiz, un contrôle ou un exercice écrit pour recevoir des exemples ciblés.')
    for code,item in ranked[:6]:
        taux=item['erreurs']/max(1,item['total'])
        with st.expander(f"{'🔴' if taux>=.5 else '🟠'} {item.get('nom',m.nom_competence(code))} · {item['erreurs']} erreur(s) / {item['total']} réponse(s)",expanded=taux>=.5):
            st.caption('Sources : '+', '.join(sorted(item['sources'])))
            for enonce,choix,bonne,explication in item['exemples']:
                st.write('**À retravailler :**',enonce)
                st.write('Ta réponse :',choix or 'Non renseignée')
                st.write('**Correction :**',bonne or 'À revoir')
                if explication:st.info(explication)
            if not item['exemples']:
                lecon=next((l for l in m.COURS[niveau] if code.startswith(l['id']+'-')),None)
                if lecon:
                    for es,fr in lecon['exemples'][:2]:st.write(f'**Exemple :** {es} — {fr}')
            st.caption('Méthode : reformule à voix haute, écris une phrase personnelle, puis refais un quiz ciblé.')
            if code!='__ecrit__':
                if st.button('🧪 10 questions ciblées sur cette notion',key='target_'+code):
                    st.session_state['v7_cible']=(niveau,code)
    if 'v7_cible' in st.session_state:
        niv,code=st.session_state['v7_cible']
        if niv==niveau:
            questions=m.banque_ciblee(niveau,[code],10)
            if questions:
                st.info('Ouvre la rubrique Révisions pour t’entraîner ; les questions disponibles ciblent en priorité cette compétence.')
                st.caption(f'{len(questions)} question(s) disponibles dans la banque ciblée.')
            else:st.warning('Pas encore de nouvelles questions disponibles pour cette notion.')
    st.divider()
    st.subheader('📝 Autres signaux d’apprentissage')
    evals=p.profil(niveau)
    for dimension,score in evals.items():
        if score is not None and score<2.5:
            st.write(f'• **{dimension}** : auto-évaluation {score}/4 — prévoir une pratique spécifique.')
    audios=m.rows('SELECT COUNT(*) n FROM pratiques_audio WHERE niveau=?',(niveau,))[0]['n']
    st.caption(f'Pratiques orales enregistrées sur {niveau} : {audios}. Elles sont prises en compte comme activité, pas comme preuve de maîtrise (pas de reconnaissance vocale).')
    st.caption('Les contrôles, quiz, révisions, remédiations et exercices écrits alimentent les faiblesses. Les leçons terminées, l’oral et les auto-évaluations complètent le contexte, sans être assimilés à des erreurs notées.')
