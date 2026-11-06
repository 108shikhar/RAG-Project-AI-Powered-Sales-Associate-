import os
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END

from backend.embedding_service import EmbeddingService
from backend.groq_service import GroqService

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "Dataset" / "products.json"

class SalesAgentState(TypedDict, total=False):
    user_message: str
    category: Optional[str]
    sub_category: Optional[str]
    attributes: Dict[str, Any]
    query_sentence: str
    query_vector: List[float]
    top_products: List[Dict[str, Any]]
    sales_pitch: str
    trace_logs: List[Dict[str, Any]]
    top_k: int

class SalesAssociatePipeline:
    def __init__(self, groq_service: Optional[GroqService] = None, embedding_service: Optional[EmbeddingService] = None):
        self.groq = groq_service or GroqService()
        self.embedder = embedding_service or EmbeddingService()
        self.products = self._load_products()
        self.graph = None
        self._build_graph()

    def _load_products(self) -> List[Dict[str, Any]]:
        path = DATA_PATH if DATA_PATH.exists() else (BASE_DIR / "data" / "products.json")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"[LangGraph Pipeline] Loaded {len(data)} ApnaMart products into memory.")
                return data
        print("[LangGraph Pipeline] Warning: products.json not found!")
        return []

    def _build_graph(self):
        workflow = StateGraph(SalesAgentState)
        workflow.add_node("extract_intent", self._extract_intent_node)
        workflow.add_node("synthesize_query", self._synthesize_query_node)
        workflow.add_node("embed_query", self._embed_query_node)
        workflow.add_node("retrieve_and_rank", self._retrieve_and_rank_node)
        workflow.add_node("generate_pitch", self._generate_pitch_node)
        
        workflow.set_entry_point("extract_intent")
        workflow.add_edge("extract_intent", "synthesize_query")
        workflow.add_edge("synthesize_query", "embed_query")
        workflow.add_edge("embed_query", "retrieve_and_rank")
        workflow.add_edge("retrieve_and_rank", "generate_pitch")
        workflow.add_edge("generate_pitch", END)
        
        self.graph = workflow.compile()
        print("[LangGraph Pipeline] StateGraph successfully compiled with 5 nodes.")

    # --- LangGraph Node Handlers ---

    async def _extract_intent_node(self, state: SalesAgentState) -> Dict[str, Any]:
        t0 = time.time()
        msg_lower = state["user_message"].lower()
        res = dict(state.get("attributes") or {})

        # Category resolution across ALL ApnaMart categories
        if state.get("category"):
            res["category"] = state["category"]
        elif any(w in msg_lower for w in ["suit", "shirt", "pant", "saree", "kurti", "kurta", "jeans", "top", "hoodie", "lower", "dress", "fashion", "clothes"]):
            res["category"] = "Fashion"
        elif any(w in msg_lower for w in ["phone", "mobile", "smartphone", "5g", "charger", "android"]):
            res["category"] = "Mobiles"
        elif any(w in msg_lower for w in ["headphone", "earbud", "watch", "smartwatch", "speaker", "audio", "electronics"]):
            res["category"] = "Electronics"
        elif any(w in msg_lower for w in ["lipstick", "brush", "serum", "trimmer", "grooming", "makeup", "beauty", "shaving"]):
            res["category"] = "Beauty"
        elif any(w in msg_lower for w in ["shoe", "running", "basketball", "bat", "badminton", "fitness", "sports", "gym"]):
            res["category"] = "Sports"
        elif any(w in msg_lower for w in ["toy", "block", "car", "puzzle", "kids", "game"]):
            res["category"] = "Toys"
        elif any(w in msg_lower for w in ["cookware", "jar", "kettle", "kitchen", "utensil", "container", "home"]):
            res["category"] = "Home & Kitchen"
        elif any(w in msg_lower for w in ["rice", "oil", "atta", "grocery", "staple", "food"]):
            res["category"] = "Grocery"

        cat = res.get("category")

        # Subcategory resolution
        if state.get("sub_category"):
            res["sub_category"] = state["sub_category"]
        elif cat == "Fashion":
            if any(w in msg_lower for w in ["women", "woman", "saree", "kurti", "girl"]):
                if any(w in msg_lower for w in ["girl's", "kids", "child", "baby"]):
                    res["sub_category"] = "Kids"
                else:
                    res["sub_category"] = "Women"
            elif any(w in msg_lower for w in ["kid", "boy", "child", "girl's"]):
                res["sub_category"] = "Kids"
            else:
                res["sub_category"] = "Men"
        elif cat == "Mobiles":
            if "charger" in msg_lower or "cable" in msg_lower or "cover" in msg_lower:
                res["sub_category"] = "Accessories"
            else:
                res["sub_category"] = "Smartphones"
        elif cat == "Electronics":
            if "watch" in msg_lower:
                res["sub_category"] = "Wearables"
            else:
                res["sub_category"] = "Audio"

        # Explicit Product Type resolution
        if "suit" in msg_lower:
            res["type"] = "Suit"
        elif "shirt" in msg_lower:
            res["type"] = "Shirt"
        elif "jeans" in msg_lower:
            res["type"] = "Jeans"
        elif "saree" in msg_lower:
            res["type"] = "Saree"
        elif "kurti" in msg_lower:
            res["type"] = "Kurti"
        elif "5g" in msg_lower or "flagship" in msg_lower:
            res["type"] = "5G Flagship"
        elif "headphone" in msg_lower:
            res["type"] = "Wireless Bluetooth Headphones"
        elif "watch" in msg_lower:
            res["type"] = "Smart Fitness Watch"
        elif "speaker" in msg_lower:
            res["type"] = "Portable Bluetooth Speaker"
        elif "lipstick" in msg_lower:
            res["type"] = "Matte Lipstick Combo"
        elif "brush" in msg_lower:
            res["type"] = "Makeup Brush Kit"
        elif "trimmer" in msg_lower:
            res["type"] = "Trimmer"
        elif "shoe" in msg_lower or "running" in msg_lower:
            res["type"] = "Men's Running Shoes"
        elif "basketball" in msg_lower:
            res["type"] = "Basketball"
        elif "block" in msg_lower:
            res["type"] = "Building Blocks STEM Toy"
        elif "car" in msg_lower:
            res["type"] = "Friction Pull-Back Toy Cars"
        elif "cookware" in msg_lower:
            res["type"] = "Stainless Steel Cookware Set"
        elif "jar" in msg_lower:
            res["type"] = "Airtight Storage Jar Set"
        elif "rice" in msg_lower:
            res["type"] = "Premium Basmati Rice"

        # Occasions
        for occ in ["interview", "wedding", "office wear", "office", "party", "daily wear", "daily use", "festive", "gaming", "photography", "workout", "running", "cooking"]:
            if re.search(r'\b' + re.escape(occ) + r'\b', msg_lower):
                res["occasion"] = occ.title()
                break

        # Precise Size / Spec extraction (avoiding substring collisions)
        for s in ["XXL", "XL", "XS", "M", "L", "S", "256GB", "128GB", "64GB", "5kg", "10kg", "10W", "33W", "UK 7", "UK 8", "UK 9", "UK 10"]:
            pattern_size = r'(?:\b|size\s*|size-)' + re.escape(s.lower()) + r'(?:\b|-size)'
            if re.search(pattern_size, msg_lower):
                res["size"] = s
                break

        # Colors
        colors_found = []
        for c in ["navy blue", "navy", "black", "blue", "charcoal", "white", "red", "green", "pink", "maroon", "yellow", "orange", "silver", "gold"]:
            if re.search(r'\b' + re.escape(c) + r'\b', msg_lower):
                colors_found.append(c.title())
        if colors_found:
            res["colors"] = list(set(colors_found))

        logs = list(state.get("trace_logs") or [])
        logs.append({
            "step": 1,
            "title": "Intent & Slot Extraction (LangGraph Node 1)",
            "status": "completed",
            "duration_ms": int((time.time() - t0) * 1000),
            "details": res
        })

        return {"attributes": res, "trace_logs": logs}

    async def _synthesize_query_node(self, state: SalesAgentState) -> Dict[str, Any]:
        t1 = time.time()
        attrs = state.get("attributes") or {}
        query_sentence = await self.groq.transform_prompt_to_semantic_query(
            user_message=state["user_message"],
            category=attrs.get("category"),
            sub_category=attrs.get("sub_category"),
            collected_attributes=attrs
        )
        logs = list(state.get("trace_logs") or [])
        logs.append({
            "step": 2,
            "title": "LLM Semantic Query Synthesis (LangGraph Node 2 - Groq LPU)",
            "status": "completed",
            "duration_ms": int((time.time() - t1) * 1000),
            "details": {
                "synthesized_sentence": query_sentence,
                "model_used": self.groq.model if self.groq.api_key else "ApnaMart Guided Synthesizer"
            }
        })
        return {"query_sentence": query_sentence, "trace_logs": logs}

    async def _embed_query_node(self, state: SalesAgentState) -> Dict[str, Any]:
        t2 = time.time()
        query_vector = await self.embedder.get_embedding(state["query_sentence"])
        logs = list(state.get("trace_logs") or [])
        logs.append({
            "step": 3,
            "title": "sentence-transformers/all-mpnet-base-v2 (LangGraph Node 3 - 768-D)",
            "status": "completed",
            "duration_ms": int((time.time() - t2) * 1000),
            "details": {
                "model": "sentence-transformers/all-mpnet-base-v2",
                "embedding_dimensions": len(query_vector),
                "vector_sample": [round(x, 4) for x in query_vector[:6]],
                "provider": "Hugging Face Cloud Inference" if self.embedder.hf_token else "ApnaMart Semantic Embedder"
            }
        })
        return {"query_vector": query_vector, "trace_logs": logs}

    async def _retrieve_and_rank_node(self, state: SalesAgentState) -> Dict[str, Any]:
        t3 = time.time()
        attrs = state.get("attributes") or {}
        query_vec = state["query_vector"]
        top_k = state.get("top_k", 5)

        scored = []
        target_cat = (attrs.get("category") or "").strip().lower()
        target_sub = (attrs.get("sub_category") or "").strip().lower()
        target_type = (attrs.get("type") or "").strip().lower()
        target_occ = (attrs.get("occasion") or "").strip().lower()
        target_size = (attrs.get("size") or "").strip().lower()
        target_colors = [c.lower() for c in attrs.get("colors") or []]

        for p in self.products:
            prod_cat = p.get("category", "").lower()
            prod_sub = p.get("sub_category", "").lower()
            prod_name = p.get("name", "").lower()
            prod_type = p.get("type", "").lower()
            prod_desc = p.get("description", "").lower()
            prod_vector = p.get("embedding", [])

            # Compute pure cosine similarity
            cos_sim = 0.0
            if prod_vector and len(prod_vector) == len(query_vec):
                cos_sim = EmbeddingService.cosine_similarity(query_vec, prod_vector)

            # Categorical Relevance & Re-ranking Boost
            boost = 0.0
            if target_cat and target_cat in prod_cat:
                boost += 0.35
            elif target_cat:
                boost -= 0.15

            if target_sub and (target_sub in prod_sub or target_sub in prod_name):
                boost += 0.20

            if target_type and (target_type in prod_type or target_type in prod_name or target_type in prod_desc):
                boost += 0.25

            if target_occ:
                prod_occs = [o.lower() for o in p.get("occasion", [])]
                if any(target_occ in o for o in prod_occs):
                    boost += 0.10

            if target_size:
                prod_sizes = [s.lower() for s in p.get("sizes", [])]
                if any(target_size in s for s in prod_sizes):
                    boost += 0.08

            if target_colors:
                prod_colors = [c.lower() for c in p.get("colors", [])]
                if any(tc in pc for tc in target_colors for pc in prod_colors):
                    boost += 0.12

            final_score = cos_sim + boost
            scored.append({
                **p,
                "similarity_score": round(max(0.45, min(0.99, (cos_sim + 1) / 2 + boost * 0.3)), 3),
                "_ranking_score": final_score
            })

        # Sort descending by blended ranking score
        scored.sort(key=lambda x: x["_ranking_score"], reverse=True)
        top_candidates = scored[:top_k]

        logs = list(state.get("trace_logs") or [])
        logs.append({
            "step": 4,
            "title": "Cosine Similarity Vector Search (LangGraph Node 4 - Top-5 Retrieval)",
            "status": "completed",
            "duration_ms": int((time.time() - t3) * 1000),
            "details": {
                "total_catalog_scanned": len(self.products),
                "top_retrieved_count": len(top_candidates),
                "top_similarity": top_candidates[0]["similarity_score"] if top_candidates else 0.0,
                "top_product_name": top_candidates[0]["name"] if top_candidates else "None"
            }
        })

        return {"top_products": top_candidates, "trace_logs": logs}

    async def _generate_pitch_node(self, state: SalesAgentState) -> Dict[str, Any]:
        t4 = time.time()
        pitch = await self.groq.generate_consultative_pitch(
            query_sentence=state["query_sentence"],
            products=state["top_products"],
            user_message=state["user_message"]
        )
        logs = list(state.get("trace_logs") or [])
        logs.append({
            "step": 5,
            "title": "ApnaMart Sahayak Consultative Delivery (LangGraph Node 5)",
            "status": "completed",
            "duration_ms": int((time.time() - t4) * 1000),
            "details": {
                "persona": "ApnaMart Sahayak (Aarav)",
                "slogan": "Sab Kuch, Ek Hi Jagah",
                "pitch_preview": pitch[:120] + "..."
            }
        })
        return {"sales_pitch": pitch, "trace_logs": logs}

    async def run(self, user_message: str, category: Optional[str] = None, sub_category: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None, top_k: int = 5) -> Dict[str, Any]:
        initial_state: SalesAgentState = {
            "user_message": user_message,
            "category": category,
            "sub_category": sub_category,
            "attributes": attributes or {},
            "top_k": top_k,
            "trace_logs": []
        }
        final_state = await self.graph.ainvoke(initial_state)
        return final_state
