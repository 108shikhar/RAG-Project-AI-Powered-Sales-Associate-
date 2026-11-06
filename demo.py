"""
FastAPI Server & Web Application for ApnaMart AI Sales Associate.
Matches TheGreatBonnie/ecommerce-rag-agent demo.py with full support for:
- /health endpoint
- /api/chat & /api/pipeline endpoints
- /api/search & /api/recommend endpoints
- /api/products & /api/categories endpoints
- Interactive ApnaMart storefront with floating AI Sales Associate
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ecommerce_agent.agent import graph, search_ecommerce, collection
from ecommerce_agent.ecommerce import search_products, get_product_recommendation, get_embedding
from ecommerce_agent.product_data import initial_products, get_products_by_category

load_dotenv()

app = FastAPI(
    title="ApnaMart AI Sales Associate (TheGreatBonnie Clone)",
    description="Agentic E-commerce RAG assistant for https://apnamarts.shop/ with Groq LPU & 768-D all-mpnet-base-v2",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    category: Optional[str] = None

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ApnaMart AI Sales Associate",
        "reference_repo": "TheGreatBonnie/ecommerce-rag-agent",
        "storefront": "https://apnamarts.shop/",
        "products_indexed": len(initial_products),
        "embedding_model": "sentence-transformers/all-mpnet-base-v2",
        "embedding_dimensions": 768,
        "llm": "Groq LPU (llama-3.3-70b-versatile / gpt-oss-20b equivalent)"
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    initial_state = {
        "current_query": req.message,
        "category": req.category,
        "sub_category": req.sub_category,
        "attributes": req.attributes or {},
        "logs": []
    }
    final_state = await graph.ainvoke(initial_state)
    return {
        "reply": final_state.get("sales_pitch", ""),
        "products": final_state.get("top_products", []),
        "synthesized_query": final_state.get("query_sentence", ""),
        "trace_logs": final_state.get("logs", [])
    }

@app.post("/api/pipeline")
async def pipeline_endpoint(req: ChatRequest):
    return await chat_endpoint(req)

@app.post("/api/search")
def search_endpoint(req: SearchRequest):
    filters = {}
    if req.category:
        filters["category"] = req.category
    products = search_products(collection, req.query, limit=req.limit or 5, extra_filters=filters)
    return {"query": req.query, "results": products, "count": len(products)}

@app.post("/api/recommend")
def recommend_endpoint(req: SearchRequest):
    recommendation = search_ecommerce(req.query)
    return {"recommendation": recommendation}

@app.get("/api/products")
def list_products(category: Optional[str] = None):
    if category:
        return {"products": get_products_by_category(category)}
    return {"products": initial_products, "total": len(initial_products)}

# Mount static files
BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(static_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ecommerce_agent.demo:app", host="127.0.0.1", port=8000, reload=False)
