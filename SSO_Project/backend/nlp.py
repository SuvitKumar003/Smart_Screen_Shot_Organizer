# backend/nlp.py
import spacy
from typing import List, Dict

# load a medium model if available; fallback to small
try:
    nlp = spacy.load("en_core_web_md")
except:
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        # if user hasn't installed, prompt installation in README
        raise RuntimeError("Install spaCy model: python -m spacy download en_core_web_sm")

def extract_tags_and_entities(text: str, top_k_tags: int = 8) -> (List[str], Dict):
    doc = nlp(text)
    # entities
    entities = {}
    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)
    # simple keyword extraction: take noun chunks and most frequent lemmas
    from collections import Counter
    lemmas = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha and token.pos_ in ("NOUN","PROPN","ADJ")]
    common = [w for w,c in Counter(lemmas).most_common(top_k_tags)]
    # augment with named entities text
    tag_set = set(common)
    for ents in entities.values():
        for e in ents:
            tag_set.add(e.lower())
    tags = list(tag_set)
    return tags, entities
