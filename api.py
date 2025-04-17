from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import requests
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json

# Load catalog & index
catalog = json.load(open('catalog.json'))
index = faiss.read_index('shl_index.faiss')
ids = np.load('ids.npy')
embedder = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI()

class RecommendRequest(BaseModel):
    query_text: Optional[str] = None
    jd_url: Optional[str] = None

class Assessment(BaseModel):
    name: str
    url: HttpUrl
    remoteTesting: str
    adaptiveIRT: str
    duration: Optional[str] = None
    testType: Optional[str]  = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post(
    "/recommend",
    response_model=List[Assessment],
    summary="Recommend SHL Assessments"
)
def recommend(req: RecommendRequest):
    # 1) Determine input text
    if req.jd_url:
        r = requests.get(req.jd_url)
        text = r.text
    elif req.query_text:
        text = req.query_text
    else:
        raise HTTPException(status_code=400, detail="Provide query_text or jd_url")

    # 2) Embed and search
    q_emb = embedder.encode([text])[0].astype("float32")
    D, I = index.search(np.array([q_emb]), k=10)

    # 3) Build response
    results: List[Assessment] = []
    for idx in I[0]:
        item = catalog[int(ids[idx])]
        results.append(item)
    return results
