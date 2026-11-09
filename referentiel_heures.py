"""Référentiel indicatif unique pour toute l'application. Non normatif CECRL."""
NIVEAUX = ("A1", "A2", "B1", "B2", "C1", "C2")
HEURES_PAR_NIVEAU = dict(zip(NIVEAUX, (60, 120, 180, 240, 300, 360)))
HEURES_CUMULEES = {}
_total = 0
for _niveau in NIVEAUX:
    _total += HEURES_PAR_NIVEAU[_niveau]
    HEURES_CUMULEES[_niveau] = _total
