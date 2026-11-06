"""
E-Commerce RAG Agent - ApnaMart AI Sales Associate Edition
Adapted from TheGreatBonnie/ecommerce-rag-agent for https://apnamarts.shop/
Using Groq LPU (llama-3.3-70b-versatile / gpt-oss-20b equivalent) and
sentence-transformers/all-mpnet-base-v2 (768-D dense embeddings).
"""

from ecommerce_agent.agent import (
    graph,
    search_ecommerce,
    AgentState,
    Log
)
from ecommerce_agent.ecommerce import (
    search_products,
    get_product_recommendation,
    get_embedding,
    prepare_product_for_embedding,
    setup_mongodb
)
from ecommerce_agent.product_data import (
    initial_products,
    get_products_by_category,
    get_product_by_id
)
from ecommerce_agent.cache_utils import clear_all_caches

__all__ = [
    "graph",
    "search_ecommerce",
    "AgentState",
    "Log",
    "search_products",
    "get_product_recommendation",
    "get_embedding",
    "prepare_product_for_embedding",
    "setup_mongodb",
    "initial_products",
    "get_products_by_category",
    "get_product_by_id",
    "clear_all_caches"
]
