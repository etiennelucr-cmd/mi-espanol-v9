"""Optional V80 social services: AI dialogue and durable per-profile PostgreSQL state.
No credentials in source. Gracefully falls back to the local scripted game.
"""
import json
import os
import re
from datetime import date
import requests


def secret(name):
    try:
        import streamlit as st
        return str(st.secrets.get(name, os.environ.get(name, ''))).strip()
    except Exception:
        return os.environ.get(name, '').strip()


def database_url():
    return secret('SOCIAL_DATABASE_URL')


def ai_enabled():
    return bool(secret('OPENAI_API_KEY'))


def db_enabled():
    return bool(database_url())


def profile_id(raw):
    raw=(raw or '').strip()
    return raw if re.fullmatch(r'[a-zA-Z0-9_-]{6,64}',raw) else None


def _connection():
    import psycopg
    return psycopg.connect(database_url(),connect_timeout=5)


def load(profile):
    """Return persisted world or None; never share state between profiles."""
    if not (db_enabled() and profile_id(profile)):
        return None
    with _connection() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS social_world_v80 (profile_id TEXT PRIMARY KEY, world JSONB NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())')
        row=conn.execute('SELECT world FROM social_world_v80 WHERE profile_id=%s',(profile,)).fetchone()
        return row[0] if row else None


def save(profile,world):
    if not (db_enabled() and profile_id(profile)):
        return False
    payload=json.dumps(world,ensure_ascii=False,default=str)
    if len(payload)>1_500_000:
        raise ValueError('Sauvegarde trop volumineuse')
    with _connection() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS social_world_v80 (profile_id TEXT PRIMARY KEY, world JSONB NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())')
        conn.execute('INSERT INTO social_world_v80(profile_id,world) VALUES (%s,%s::jsonb) ON CONFLICT(profile_id) DO UPDATE SET world=EXCLUDED.world,updated_at=NOW()', (profile,payload))
    return True


PERSONALITIES={
 'Lucía':'chaleureuse, attentive, sociable, aime organiser des soirées',
 'Carlos':'spontané, drôle, parfois impulsif, aime voyager',
 'Elena':'réservée, réfléchie, indépendante, aime les animaux',
 'Pablo':'espiègle, curieux, bavard, adore son animal',
 'Oliver':'sociable, drôle, passionné par sa ville',
 'Giulia':'créative, chaleureuse, aime sa famille et les sorties',
}
LANGUAGES={'es':'espagnol','en':'anglais','de':'allemand','it':'italien'}


def answer(lang,person,city,level,pet,history,user_text,memories=None):
    """Generate a single character reply. Raises on unavailable/failed API."""
    key=secret('OPENAI_API_KEY')
    if not key:raise RuntimeError('Clé IA absente')
    model=secret('SOCIAL_AI_MODEL') or 'gpt-4o-mini'
    history=history[-12:]
    context='\n'.join(f"{'Utilisateur' if m.get('who')=='you' else person}: {str(m.get('text',''))[:600]}" for m in history)
    memory='; '.join(str(m)[:180] for m in (memories or [])[-8:])
    system=(f'Tu incarnes {person}, personnage fictif vivant à {city}. Personnalité: {PERSONALITIES.get(person,"amical, avec sa propre vie")}. '
            f'Ton animal de compagnie s’appelle {pet}. Réponds UNIQUEMENT en {LANGUAGES[lang]}, niveau CECRL {level} approximatif. '
            'A1: 1-2 phrases très simples; A2: 2-3 phrases simples; B1: 2-4 phrases naturelles, avec opinions. '
            'Reste cohérent avec le passé; n’invente pas de souvenirs non fournis. '
            'Tu peux avoir des humeurs, projets et relations, mais évite la pression culpabilisante et les promesses de notification. '
            'Réponds comme dans une messagerie, pas comme un professeur. Ne corrige pas systématiquement la grammaire. '
            f'Souvenirs confirmés: {memory or "aucun"}.')
    payload={'model':model,'temperature':0.75,'max_tokens':180,
             'messages':[{'role':'system','content':system},
                         {'role':'user','content':f'Historique:\n{context}\n\nDernier message utilisateur: {user_text[:600]}\nRéponds à ce dernier message.'}]}
    resp=requests.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=payload,timeout=18)
    resp.raise_for_status()
    content=resp.json()['choices'][0]['message']['content'].strip()
    if not content:raise RuntimeError('Réponse vide')
    return content[:900]


def remember(world,lang,name,message):
    """Keep a short, explicit factual memory of player utterances (not inferred facts)."""
    key=f'{lang}:{name}'
    memories=world.setdefault('memories',{}).setdefault(key,[])
    cleaned=' '.join(message.split())[:180]
    if len(cleaned)>8 and cleaned not in memories:
        memories.append(f'{date.today().isoformat()}: l’utilisateur a dit «{cleaned}»')
    world['memories'][key]=memories[-12:]
