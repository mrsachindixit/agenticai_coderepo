
import os
import json
import numpy as np
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils.ollama_client import embed

# Path to pre-built RAG index
INDEX = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'module01_raw',
    '1.8_rag_basic',
    'index.json'
)

def cosine(a,b):
    a=np.array(a); b=np.array(b)
    return float(a@b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9)

def test_index_exists():
    assert os.path.exists(INDEX), 'Run build_index.py to create the RAG index.'

def test_retrieval_reasonable_if_index_present():
    if not os.path.exists(INDEX):
        return
    with open(INDEX,'r',encoding='utf-8') as f:
        idx=json.load(f)
    q='How do agents use tools and memory?'
    qv=embed(q)[0]
    scores=[cosine(qv, r['vec']) for r in idx]
    assert max(scores) > 0.2
