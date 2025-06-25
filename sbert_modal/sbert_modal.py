import modal
from fastapi import Request

app = modal.App("sbert-embedder")

image = (
    modal.Image.debian_slim()
    .pip_install("sentence-transformers", "torch", "fastapi[standard]")
)

@app.function(image=image, cpu=2)
@modal.fastapi_endpoint(method="POST")
async def embed(request: Request):
    from sentence_transformers import SentenceTransformer

    body = await request.json()
    text = body["text"]

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embedding = model.encode(text)

    return {"embedding": embedding.tolist()}
