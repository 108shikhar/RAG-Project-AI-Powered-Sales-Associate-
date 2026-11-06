"""
LangGraph Agent Workflow Module for ApnaMart AI Sales Associate.
Adapted from TheGreatBonnie/ecommerce-rag-agent.
Implements:
- AgentState with real-time logs, progress tracking, and search stages
- @tool search_ecommerce tool with LRU caching
- 5-node StateGraph:
  1. extract_intent
  2. synthesize_query
  3. embed_query
  4. retrieve_and_rank
  5. generate_pitch
"""

import time
import json
from functools import lru_cache
from typing import List, Dict, Any, Optional, TypedDict
from typing_extensions import Literal

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState

from ecommerce_agent.ecommerce import (
    setup_mongodb,
    search_products,
    get_product_recommendation,
    get_embedding
)
from ecommerce_agent.product_data import initial_products

# Initialize collection at module startup
collection = setup_mongodb()

class Log(TypedDict):
    """Real-time log of an agent action."""
    message: str
    done: bool

class AgentState(MessagesState):
    """
    Enhanced state for the e-commerce sales agent with comprehensive tracking.
    Matches and extends TheGreatBonnie/ecommerce-rag-agent AgentState.
    """
    logs: List[Log] = []
    processing_status: str = "idle"
    current_query: str = ""
    search_stage: str = ""
    progress_percentage: int = 0
    active_filters: dict = {}
    matched_products_count: int = 0
    filtered_products_count: int = 0
    processing_time: float = 0.0
    search_history: list = []
    error_message: str = ""
    
    # Sales Associate specific fields
    category: Optional[str] = None
    sub_category: Optional[str] = None
    attributes: dict = {}
    query_sentence: str = ""
    query_vector: List[float] = []
    top_products: List[dict] = []
    sales_pitch: str = ""
    trace_logs: List[dict] = []

@tool
@lru_cache(maxsize=100)
def search_ecommerce(query: str) -> str:
    """
    Search for products and get AI-powered recommendations based on user query.
    Interfaces directly with the 768-D vector search and consultative pitch engine.
    """
    if collection is None:
        return "I apologize, but the ApnaMart search system is currently initializing. Please try again."

    try:
        start_time = time.time()
        relevant_products = search_products(collection, query, limit=5)
        recommendation = get_product_recommendation(relevant_products, query)
        elapsed = round(time.time() - start_time, 2)
        print(f"[search_ecommerce] Found {len(relevant_products)} products in {elapsed}s")
        return recommendation
    except Exception as e:
        return f"Error executing product search: {str(e)}"

# --- LangGraph Multi-Node Workflow ---

def extract_intent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 1: Extract intent, category, slot attributes, and constraints."""
    user_msg = ""
    if state.get("messages"):
        last_msg = state["messages"][-1]
        user_msg = getattr(last_msg, "content", str(last_msg))
    elif state.get("current_query"):
        user_msg = state["current_query"]

    msg_lower = user_msg.lower()
    attrs = dict(state.get("attributes") or {})

    # Detect Category
    cat_detected = state.get("category")
    if not cat_detected:
        for cat in ["Fashion", "Mobiles", "Electronics", "Home & Kitchen", "Beauty", "Sports", "Toys", "Grocery"]:
            if cat.lower() in msg_lower:
                cat_detected = cat
                break
    if not cat_detected:
        if any(w in msg_lower for w in ["suit", "shirt", "pant", "kurta", "saree", "blazer", "dress", "hoodie", "jeans"]):
            cat_detected = "Fashion"
        elif any(w in msg_lower for w in ["phone", "mobile", "charger", "5g", "oneplus", "realme", "samsung"]):
            cat_detected = "Mobiles"
        elif any(w in msg_lower for w in ["headphone", "earbuds", "watch", "smartwatch", "speaker", "laptop"]):
            cat_detected = "Electronics"
        elif any(w in msg_lower for w in ["cookware", "kettle", "bottle", "cooker", "mixer"]):
            cat_detected = "Home & Kitchen"
        elif any(w in msg_lower for w in ["serum", "lipstick", "cream", "sunscreen", "trimmer", "perfume"]):
            cat_detected = "Beauty"
        elif any(w in msg_lower for w in ["shoe", "shoes", "cricket", "bat", "football", "dumbbell", "yoga"]):
            cat_detected = "Sports"
        elif any(w in msg_lower for w in ["toy", "rc car", "teddy", "blocks", "puzzle", "drone"]):
            cat_detected = "Toys"
        elif any(w in msg_lower for w in ["rice", "atta", "oil", "tea", "dal", "dry fruits"]):
            cat_detected = "Grocery"
        else:
            cat_detected = "Fashion"

    # Extract slots (size, color, occasion, price)
    for sz in ["S", "M", "L", "XL", "XXL", "28", "30", "32", "34", "36", "38"]:
        if f" {sz.lower()} " in f" {msg_lower} " or f"{sz.lower()}-size" in msg_lower:
            attrs["size"] = sz
            break

    for col in ["Navy Blue", "Black", "White", "Sky Blue", "Red", "Grey", "Green", "Olive", "Yellow"]:
        if col.lower() in msg_lower:
            attrs["color"] = col
            break

    for occ in ["Office Wear", "Interview", "Wedding", "Festive", "Daily Wear", "Casual", "Gym"]:
        if occ.lower() in msg_lower or occ.split()[0].lower() in msg_lower:
            attrs["occasion"] = occ
            break

    return {
        "current_query": user_msg,
        "category": cat_detected,
        "attributes": attrs,
        "search_stage": "intent_extracted",
        "progress_percentage": 20,
        "logs": (state.get("logs") or []) + [{"message": f"Identified category: {cat_detected}", "done": True}]
    }

def synthesize_query_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 2: Synthesize multi-turn attributes into a coherent query sentence."""
    cat = state.get("category", "General")
    attrs = state.get("attributes", {})
    raw_msg = state.get("current_query", "")

    parts = []
    if attrs.get("size"):
        parts.append(f"{attrs['size']}-sized")
    if attrs.get("color"):
        parts.append(f"{attrs['color']}")
    if attrs.get("type"):
        parts.append(attrs['type'])
    elif cat:
        parts.append(cat)
    if attrs.get("occasion"):
        parts.append(f"for {attrs['occasion']}")

    if parts:
        query_sentence = f"Customer wants {' '.join(parts)}. {raw_msg}".strip()
    else:
        query_sentence = raw_msg or f"Best selling products in {cat}"

    return {
        "query_sentence": query_sentence,
        "search_stage": "query_synthesized",
        "progress_percentage": 40,
        "logs": (state.get("logs") or []) + [{"message": f"Synthesized requirement: '{query_sentence}'", "done": True}]
    }

def embed_query_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 3: Convert synthesized requirement to 768-D dense vector via all-mpnet-base-v2."""
    query_sentence = state.get("query_sentence", state.get("current_query", ""))
    vec = get_embedding(query_sentence)

    return {
        "query_vector": vec,
        "search_stage": "vector_embedded",
        "progress_percentage": 60,
        "logs": (state.get("logs") or []) + [{"message": "Encoded query into 768-D vector via all-mpnet-base-v2", "done": True}]
    }

def retrieve_and_rank_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 4: Execute vector cosine similarity and constraint ranking."""
    query_str = state.get("query_sentence", "")
    filters = {}
    if state.get("category"):
        filters["category"] = state["category"]

    results = search_products(collection, query_str, limit=5, extra_filters=filters)

    return {
        "top_products": results,
        "matched_products_count": len(results),
        "filtered_products_count": len(results),
        "search_stage": "products_retrieved",
        "progress_percentage": 80,
        "logs": (state.get("logs") or []) + [{"message": f"Retrieved {len(results)} top candidate products via cosine similarity", "done": True}]
    }

def generate_pitch_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 5: Consultative sales pitch delivery by ApnaMart Sahayak."""
    products = state.get("top_products", [])
    query = state.get("query_sentence", "")
    attrs = state.get("attributes", {})
    user_context = f"Preferences: Size={attrs.get('size', 'Any')}, Color={attrs.get('color', 'Any')}, Occasion={attrs.get('occasion', 'Any')}"

    pitch = get_product_recommendation(products, query, user_persona=user_context)

    ai_msg = AIMessage(content=pitch)
    messages = list(state.get("messages") or []) + [ai_msg]

    return {
        "sales_pitch": pitch,
        "messages": messages,
        "search_stage": "completed",
        "progress_percentage": 100,
        "processing_status": "done",
        "logs": (state.get("logs") or []) + [{"message": "Consultative recommendation ready", "done": True}]
    }

# Build LangGraph workflow
workflow = StateGraph(AgentState)
workflow.add_node("extract_intent", extract_intent_node)
workflow.add_node("synthesize_query", synthesize_query_node)
workflow.add_node("embed_query", embed_query_node)
workflow.add_node("retrieve_and_rank", retrieve_and_rank_node)
workflow.add_node("generate_pitch", generate_pitch_node)

workflow.set_entry_point("extract_intent")
workflow.add_edge("extract_intent", "synthesize_query")
workflow.add_edge("synthesize_query", "embed_query")
workflow.add_edge("embed_query", "retrieve_and_rank")
workflow.add_edge("retrieve_and_rank", "generate_pitch")
workflow.add_edge("generate_pitch", END)

graph = workflow.compile()
print("[ecommerce_agent.agent] LangGraph workflow compiled successfully!")
