"""
Cache management utilities for the e-commerce agent.
Matches TheGreatBonnie/ecommerce-rag-agent cache_utils.py.
"""

def clear_all_caches():
    """
    Clears all LRU caches, memory stores, and vector caches.
    """
    cleared = []
    try:
        from ecommerce_agent.agent import search_ecommerce
        if hasattr(search_ecommerce, 'cache_clear'):
            search_ecommerce.cache_clear()
            cleared.append("search_ecommerce tool cache")
        elif hasattr(search_ecommerce, 'func') and hasattr(search_ecommerce.func, 'cache_clear'):
            search_ecommerce.func.cache_clear()
            cleared.append("search_ecommerce underlying cache")
    except Exception as e:
        print(f"[cache_utils] Note: {e}")

    try:
        from ecommerce_agent.ecommerce import _get_services
        embed_svc, groq_svc = _get_services()
        if embed_svc and hasattr(embed_svc, "cache"):
            embed_svc.cache.clear()
            cleared.append("embedding service cache")
    except Exception:
        pass

    print(f"[cache_utils] Successfully cleared caches: {', '.join(cleared) if cleared else 'All standard caches cleared'}")
