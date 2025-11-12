# backend/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import weaviate
import tiktoken
import time, uuid, numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

WEAVIATE_URL = "https://b9ko8bdcq2yk66jxftwppq.c0.asia-southeast1.gcp.weaviate.cloud"
WEAVIATE_APIKEY = "YWl0UkhuZW5sVVZTaHBYYl9JV1JVZ0xzUFllRnJLQkRKUm96SGNsUTRjRHhvQ0FNbWFUdTlJTWhOWFhnPV92MjAw"

model = SentenceTransformer("all-MiniLM-L6-v2")
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_APIKEY),
)

try:
    tokenizer = tiktoken.get_encoding("cl100k_base")
except Exception:
    tokenizer = None

# ----------------------------------
def ensure_schema():
    try:
        existing = client.schema.get()
        if any(c.get("class") == "Chunk" for c in existing.get("classes", [])):
            return
    except Exception:
        pass
    schema = {
        "classes": [
            {
                "class": "Chunk",
                "vectorizer": "none",
                "properties": [
                    {"name": "content", "dataType": ["text"]},
                    {"name": "html", "dataType": ["text"]},
                    {"name": "url", "dataType": ["text"]},
                    {"name": "path", "dataType": ["text"]},
                ],
            }
        ]
    }
    client.schema.create(schema)

ensure_schema()
# ----------------------------------

def extract_element_chunks(html):
    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style", "noscript", "iframe", "svg"]):
        s.decompose()
    tags = ["article", "section", "main", "header", "footer", "p", "h1", "h2", "h3", "li", "div"]
    candidates = []
    for tag in tags:
        for el in soup.find_all(tag):
            text = el.get_text(" ", strip=True)
            if len(text) < 20:
                continue
            html_snip = str(el)
            path = el.name
            if el.get("id"):
                path += f"#{el.get('id')}"
            elif el.get("class"):
                path += "." + ".".join(el.get("class")[:2])
            candidates.append({"text": text, "html": html_snip, "path": path})
    if not candidates:
        body = soup.body or soup
        candidates = [{"text": body.get_text(" ", strip=True), "html": str(body)[:2000], "path": "/"}]
    return candidates

def tokenize_and_chunk_texts(candidates, token_size=200):
    chunks = []
    for c in candidates:
        txt, html, path = c["text"], c["html"], c["path"]
        if tokenizer:
            toks = tokenizer.encode(txt)
            for i in range(0, len(toks), token_size):
                sub = tokenizer.decode(toks[i:i+token_size]).strip()
                if len(sub) > 10:
                    chunks.append({"text": sub, "html": html, "path": path})
        else:
            words = txt.split()
            for i in range(0, len(words), int(token_size/2)):
                sub = " ".join(words[i:i+int(token_size/2)]).strip()
                if len(sub) > 10:
                    chunks.append({"text": sub, "html": html, "path": path})
    return chunks

def deduplicate_chunks(chunks, threshold=0.9):
    """Remove exact and near-duplicate chunks."""
    unique_chunks = []
    seen_texts = set()
    embeddings = []

    for ch in chunks:
        text = ch["text"].strip()
        # Exact duplicate check
        if text.lower() in seen_texts:
            continue

        vec = model.encode(text)
        # Near-duplicate check
        if embeddings:
            sims = np.dot(embeddings, vec) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(vec) + 1e-9)
            if np.any(sims > threshold):
                continue  # skip very similar
        seen_texts.add(text.lower())
        embeddings.append(vec)
        unique_chunks.append(ch)

    print(f"[DEDUP] Reduced {len(chunks)} → {len(unique_chunks)} unique chunks")
    return unique_chunks
# ----------------------------------

@app.get("/search")
def search(url: str = Query(...), query: str = Query(...)):
    start_time = time.time()
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return {"results": [], "error": "URL must start with http:// or https://"}

    try:
        html = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).text
    except Exception as e:
        return {"results": [], "error": f"Fetch error: {e}"}

    candidates = extract_element_chunks(html)
    chunks = tokenize_and_chunk_texts(candidates, token_size=200)
    chunks = deduplicate_chunks(chunks, threshold=0.9)
    if not chunks:
        return {"results": [], "error": "No content extracted."}
    print(f"[DEBUG] Indexing {len(chunks)} unique chunks from {url}")

    try:
        client.schema.delete_all()
    except Exception:
        pass
    ensure_schema()

    for ch in chunks:
        vec = model.encode(ch["text"]).tolist()
        client.data_object.create(
            {"content": ch["text"], "html": ch["html"], "url": url, "path": ch["path"]},
            "Chunk",
            vector=vec,
            uuid=str(uuid.uuid4()),
        )

    q_vec = model.encode(query).tolist()
    res = (
        client.query.get("Chunk", ["content", "html", "url", "path"])
        .with_near_vector({"vector": q_vec})
        .with_additional(["certainty"])
        .with_limit(10)
        .do()
    )
    hits = res.get("data", {}).get("Get", {}).get("Chunk", []) or []
    matches = [
        {
            "content": h["content"],
            "html": h["html"],
            "score": round(h["_additional"]["certainty"] * 100, 2),
            "path": h.get("path", "/"),
        }
        for h in hits
    ]
    print(f"[DEBUG] Returned {len(matches)} matches in {time.time() - start_time:.2f}s")
    return {"results": matches}
