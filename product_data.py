"""
Product catalog module for the ApnaMart AI Sales Associate.
Contains all 103 verified products scraped from https://apnamarts.shop/
covering 8 departments: Fashion, Mobiles, Electronics, Home & Kitchen,
Beauty, Sports, Toys, and Grocery.
Each item includes rich metadata, live Supabase storage image URLs,
and pre-computed 768-dimensional embeddings from sentence-transformers/all-mpnet-base-v2.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "Dataset" / "products.json"
FALLBACK_PATH = BASE_DIR / "data" / "products.json"

def load_initial_products() -> List[Dict[str, Any]]:
    """Load the complete product catalog into memory."""
    for path in [DATA_PATH, FALLBACK_PATH, Path("./Dataset/products.json"), Path("./data/products.json")]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    prods = json.load(f)
                    print(f"[product_data] Loaded {len(prods)} products from {path}")
                    return prods
            except Exception as e:
                print(f"[product_data] Error reading {path}: {e}")
    print("[product_data] Warning: No products.json found!")
    return []

# Matches TheGreatBonnie initial_products variable
initial_products: List[Dict[str, Any]] = load_initial_products()

def get_products_by_category(category: str) -> List[Dict[str, Any]]:
    """Retrieve all products matching a category name."""
    cat_norm = category.lower().strip()
    return [p for p in initial_products if p.get("category", "").lower().strip() == cat_norm]

def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single product by unique ID."""
    p_id_str = str(product_id).strip()
    for p in initial_products:
        if str(p.get("id")).strip() == p_id_str:
            return p
    return None
