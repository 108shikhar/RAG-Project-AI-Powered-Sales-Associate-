import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.embedding_service import EmbeddingService
from backend.groq_service import GroqService
from backend.pipeline import SalesAssociatePipeline

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    ENV_FILE.touch()

app = FastAPI(
    title="ApnaMart AI Sales Assistant (ApnaMart Sahayak)",
    description="Agentic RAG shopping assistant for ApnaMart (https://apnamarts.shop/ - 'Sab Kuch, Ek Hi Jagah') using Groq LPU and sentence-transformers/all-mpnet-base-v2",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_svc = GroqService(api_key=os.getenv("GROQ_API_KEY"))
embed_svc = EmbeddingService(hf_token=os.getenv("HUGGINGFACE_API_KEY"))
pipeline = SalesAssociatePipeline(groq_service=groq_svc, embedding_service=embed_svc)

TAXONOMY = {
    "Fashion": {
        "subcategories": {
            "Men": {
                "types": ["Suit", "Shirt", "Jeans", "T-Shirt", "Lower / Track Pant", "Hoodie"],
                "occasions": ["Office Wear", "Interview", "Wedding", "Festive", "Daily Wear"],
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Navy Blue", "Charcoal Black", "White", "Sky Blue", "Dark Blue"]
            },
            "Women": {
                "types": ["Saree", "Kurti", "Top", "Suit / Blazer Set"],
                "occasions": ["Wedding", "Festive", "Office Wear", "Daily Wear", "Party"],
                "sizes": ["Free Size", "S", "M", "L", "XL"],
                "colors": ["Red Zari", "Royal Blue", "Golden Yellow", "Floral Mustard", "Pink"]
            },
            "Kids": {
                "types": ["Girl's Top", "Girl's Traditional Suit", "Casuals"],
                "occasions": ["Festive", "Birthday Party", "Casual Outing"],
                "sizes": ["4-5 Yrs", "6-7 Yrs", "8-9 Yrs", "10-12 Yrs"],
                "colors": ["Baby Pink", "Sky Blue", "Lavender", "Gold & Pink"]
            }
        }
    },
    "Mobiles": {
        "subcategories": {
            "Smartphones": {
                "types": ["5G Smartphone", "5G Flagship", "Budget Smartphone"],
                "occasions": ["Daily Use", "Gaming", "Photography"],
                "sizes": ["128GB Storage", "256GB Storage", "64GB Storage"],
                "colors": ["Midnight Black", "Aurora Blue", "Cosmic Blue"]
            },
            "Accessories": {
                "types": ["Fast Charger", "Mobile Back Cover", "Charging Cable"],
                "occasions": ["Daily Travel", "Office", "Home"],
                "sizes": ["33W Fast Charge", "Standard Fit"],
                "colors": ["Classic White", "Matte Black", "Red"]
            }
        }
    },
    "Electronics": {
        "subcategories": {
            "Audio": {
                "types": ["Wireless Bluetooth Headphones", "Portable Bluetooth Speaker", "True Wireless Earbuds"],
                "occasions": ["Daily Commute", "Gym & Workout", "Party & Home Leisure"],
                "sizes": ["Over-Ear Cushion", "Compact 10W", "Standard In-Ear"],
                "colors": ["Matte Black", "Space Gray", "Rugged Blue"]
            },
            "Wearables": {
                "types": ["Smart Fitness Watch", "Calling Smartwatch"],
                "occasions": ["Daily Office", "Fitness Tracking", "Sports"],
                "sizes": ["Standard Dial", "Curved AMOLED"],
                "colors": ["Pitch Black", "Steel Silver"]
            }
        }
    },
    "Beauty": {
        "subcategories": {
            "Makeup": {
                "types": ["Matte Lipstick Combo", "Makeup Brush Kit (12 pcs)"],
                "occasions": ["Office Wear", "Party & Bridal", "Daily Glam"],
                "sizes": ["Set of 3 (Standard)", "12-Piece Set with Pouch"],
                "colors": ["Berry Nude", "Ruby Red", "Rose Gold & Black"]
            },
            "Men Shaving": {
                "types": ["Trimmer", "Clean Shave Shaver"],
                "occasions": ["Daily Beard Styling", "Clean Shave", "Body Grooming"],
                "sizes": ["Complete 5-in-1 Kit", "Single Cordless Trimmer"],
                "colors": ["Midnight Matte Black"]
            }
        }
    },
    "Sports": {
        "subcategories": {
            "Footwear": {
                "types": ["Men's Running Shoes"],
                "occasions": ["Running", "Gym & Workout", "Morning Walk"],
                "sizes": ["UK 7", "UK 8", "UK 9", "UK 10"],
                "colors": ["Black & Neon Green", "Navy White"]
            },
            "Gear": {
                "types": ["Basketball Size 7", "Badminton Racket Set", "Home Gym Dumbbells"],
                "occasions": ["Outdoor Court", "Tournament", "Practice"],
                "sizes": ["Size 7 (Official)", "Standard Adult Set"],
                "colors": ["Classic Orange", "Metallic"]
            }
        }
    },
    "Toys": {
        "subcategories": {
            "Educational": {
                "types": ["Building Blocks STEM Toy", "Learning Puzzle"],
                "occasions": ["Creative Learning", "Birthday Gift", "Indoor Play"],
                "sizes": ["120-Piece Kit", "Standard Board"],
                "colors": ["Vibrant Multicolor"]
            },
            "Vehicles": {
                "types": ["Friction Pull-Back Toy Cars"],
                "occasions": ["Toddler Play", "Birthday Return Gift"],
                "sizes": ["Pack of 4 Cars"],
                "colors": ["Multicolor"]
            }
        }
    },
    "Home & Kitchen": {
        "subcategories": {
            "Cookware": {
                "types": ["Stainless Steel Cookware Set", "Fast Boil Electric Kettle"],
                "occasions": ["Daily Cooking", "Kitchen Upgrade", "Festive Meals"],
                "sizes": ["5-Piece Induction Set", "1.8L Kettle"],
                "colors": ["Mirror Finish Silver", "Brushed Steel"]
            },
            "Storage": {
                "types": ["Airtight Storage Jar Set"],
                "occasions": ["Kitchen Organizing", "Food Storage"],
                "sizes": ["Set of 6 (1000ml each)"],
                "colors": ["Transparent Glass Look"]
            }
        }
    },
    "Grocery": {
        "subcategories": {
            "Staples": {
                "types": ["Premium Basmati Rice", "Organic Whole Wheat Atta", "Pure Mustard Oil"],
                "occasions": ["Biryani & Daily Meals", "Everyday Cooking"],
                "sizes": ["5kg Pack", "10kg Bag", "1L Pouch"],
                "colors": ["Aged Long Grain", "Natural Golden"]
            }
        }
    }
}

class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5

class ConfigRequest(BaseModel):
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None
    huggingface_api_key: Optional[str] = None

@app.get("/api/taxonomy")
async def get_taxonomy():
    return TAXONOMY

@app.get("/api/products")
async def get_products(category: Optional[str] = None, sub_category: Optional[str] = None):
    prods = pipeline.products
    if category:
        prods = [p for p in prods if p.get("category", "").lower() == category.lower()]
    if sub_category:
        prods = [p for p in prods if p.get("sub_category", "").lower() == sub_category.lower()]
    return prods


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    category: Optional[str] = None

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ApnaMart AI Sales Associate",
        "reference_repo": "TheGreatBonnie/ecommerce-rag-agent",
        "storefront": "https://apnamarts.shop/",
        "products_indexed": len(pipeline.products),
        "embedding_model": "sentence-transformers/all-mpnet-base-v2",
        "embedding_dimensions": 768,
        "llm": groq_svc.model if groq_svc.api_key else "llama-3.3-70b-versatile (Groq LPU)"
    }

@app.post("/api/search")
async def search_endpoint(req: SearchRequest):
    from ecommerce_agent.ecommerce import search_products, setup_mongodb
    col = setup_mongodb()
    filters = {}
    if req.category:
        filters["category"] = req.category
    results = search_products(col, req.query, limit=req.limit or 5, extra_filters=filters)
    return {"query": req.query, "results": results, "count": len(results)}

@app.post("/api/recommend")
async def recommend_endpoint(req: SearchRequest):
    from ecommerce_agent.agent import search_ecommerce
    rec = search_ecommerce(req.query)
    return {"query": req.query, "recommendation": rec}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        result = await pipeline.run(
            user_message=req.message,
            category=req.category,
            sub_category=req.sub_category,
            attributes=req.attributes,
            top_k=req.top_k or 5
        )
        return {
            "query_sentence": result.get("query_sentence", ""),
            "attributes": result.get("attributes", {}),
            "top_products": result.get("top_products", []),
            "sales_pitch": result.get("sales_pitch", ""),
            "trace_logs": result.get("trace_logs", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    return {
        "groq_configured": bool(groq_svc.api_key),
        "groq_model": groq_svc.model,
        "hf_configured": bool(embed_svc.hf_token),
        "total_catalog_products": len(pipeline.products)
    }

@app.post("/api/config")
async def update_config(req: ConfigRequest):
    if req.groq_api_key is not None:
        groq_svc.set_api_key(req.groq_api_key)
        set_key(str(ENV_FILE), "GROQ_API_KEY", req.groq_api_key)
    if req.groq_model:
        groq_svc.model = req.groq_model
        set_key(str(ENV_FILE), "GROQ_MODEL", req.groq_model)
    if req.huggingface_api_key is not None:
        embed_svc.set_token(req.huggingface_api_key)
        set_key(str(ENV_FILE), "HUGGINGFACE_API_KEY", req.huggingface_api_key)
    return {"status": "ok", "message": "Settings updated successfully"}

# Mount static files
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(str(static_dir / "index.html"))
