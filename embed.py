import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Files
CATALOG_JSON = "catalog.json"
INDEX_FILE   = "shl_index.faiss"
EMB_FILE     = "embeddings.npy"
ID_FILE      = "ids.npy"
MODEL_NAME   = "all-MiniLM-L6-v2"

def build_index():
    # 1) Load the scraped catalog
    with open(CATALOG_JSON, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # 2) Prepare texts to embed (e.g. name + type)
    texts = [item["name"] + " " + item["testType"] for item in catalog]

    # 3) Compute embeddings
    embedder = SentenceTransformer(MODEL_NAME)
    embs = embedder.encode(texts, convert_to_numpy=True)

    # 4) Handle single-item edge case
    embs = np.array(embs)
    if embs.ndim == 1:
        embs = embs.reshape(1, -1)

    # 5) Build a FAISS index
    dim = embs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embs)

    # 6) Persist index and arrays
    faiss.write_index(index, INDEX_FILE)
    np.save(EMB_FILE, embs)
    np.save(ID_FILE, np.arange(len(catalog)))

    print(f"Built FAISS index ({embs.shape[0]} vectors of dimension {dim})")

if __name__ == "__main__":
    build_index()
