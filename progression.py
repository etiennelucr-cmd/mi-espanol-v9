"""Règles de déblocage déterministes et testables indépendamment de Streamlit."""


def is_chapter_unlocked(records, keys, chapter_index):
    """Un chapitre reste révisable; le prochain exige tous les acquis précédents."""
    if not (0 <= chapter_index < len(keys)):
        return False
    return all(records.get(key) is True for key in keys[:chapter_index])


def available_indices(records, keys):
    return [i for i in range(len(keys)) if is_chapter_unlocked(records,keys,i)]


def unlocked_groups(exams, names):
    """Les niveaux N+1 exigent les bilans validés de tous les niveaux précédents."""
    return [name for i,name in enumerate(names) if all(exams.get(previous) is True for previous in names[:i])]


def current_school_grade(exams, max_index):
    """Première classe dont le bilan n'est pas validé, ou Terminale si tout est acquis."""
    position=0
    while position<max_index and exams.get(str(position)) is True:
        position+=1
    return position


def score_passes(score, total):
    """Bilan à 80 % minimum, 4/4 ou 4/5, sans limite de tentatives."""
    return total>0 and score*5>=total*4
