"""Suivi des durées réellement enregistrées (aucun chronométrage fictif)."""
import moteur as m
from referentiel_heures import HEURES_PAR_NIVEAU
OBJECTIFS = HEURES_PAR_NIVEAU
def heures_niveau(niveau):
    seances=m.rows('SELECT COALESCE(SUM(minutes),0) AS minutes FROM sessions WHERE niveau=?',(niveau,))
    tests=m.rows('''SELECT COALESCE(SUM(CASE WHEN secondes BETWEEN 1 AND 7200 THEN secondes ELSE 0 END),0) AS secondes FROM tentatives WHERE niveau=?''',(niveau,))
    # Les tests enregistrés dans tentatives ne sont pas des sessions.
    return round((float(seances[0]['minutes'] or 0)+float(tests[0]['secondes'] or 0)/60)/60,1)
