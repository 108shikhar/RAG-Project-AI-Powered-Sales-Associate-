import os
import math
import re
import numpy as np
import httpx
from typing import List, Optional

HF_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
HF_API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{HF_MODEL_NAME}"
HF_ROUTER_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL_NAME}"

class EmbeddingService:
    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        self.dim = 768

    def set_token(self, token: str):
        self.hf_token = token.strip() if token else None

    async def get_embedding(self, text: str) -> List[float]:
        text_clean = text.strip()
        if not text_clean:
            return [0.0] * self.dim

        # Attempt Hugging Face Serverless Cloud API
        if self.hf_token:
            for url in [HF_API_URL, HF_ROUTER_URL]:
                try:
                    async with httpx.AsyncClient(timeout=12.0) as client:
                        headers = {
                            "Authorization": f"Bearer {self.hf_token}",
                            "Content-Type": "application/json"
                        }
                        payload = {"inputs": text_clean, "options": {"wait_for_model": True}}
                        resp = await client.post(url, json=payload, headers=headers)
                        if resp.status_code == 200:
                            data = resp.json()
                            if isinstance(data, list):
                                if len(data) > 0 and isinstance(data[0], list):
                                    data = data[0]
                                if len(data) == self.dim:
                                    vec = np.array(data, dtype=np.float32)
                                    norm = np.linalg.norm(vec)
                                    if norm > 1e-8:
                                        vec = vec / norm
                                    return [round(float(x), 6) for x in vec]
                except Exception as e:
                    print(f"[EmbeddingService] HF Warning: {e}")
                    continue

        return self._fallback_embedding(text_clean)

    def _fallback_embedding(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        words = re.findall(r'\b\w+\b', text.lower())
        
        for i, word in enumerate(words):
            w_hash = hash(word)
            pos1 = abs(w_hash) % self.dim
            pos2 = abs(w_hash * 31 + i) % self.dim
            pos3 = abs(w_hash * 101) % self.dim
            
            weight = 1.0 / math.sqrt(i + 1)
            vec[pos1] += 1.2 * weight
            vec[pos2] += 0.8 * weight
            vec[pos3] -= 0.5 * weight
            
            if i < len(words) - 1:
                bi_word = word + "_" + words[i+1]
                b_hash = abs(hash(bi_word)) % self.dim
                vec[b_hash] += 1.5 * weight

        norm = np.linalg.norm(vec)
        if norm > 1e-8:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return [round(float(x), 6) for x in vec]

    
    def embed_text(self, text: str) -> List[float]:
        """Synchronous embedding method for sentence-transformers/all-mpnet-base-v2."""
        import asyncio
        text_clean = text.strip()
        if not text_clean:
            return [0.0] * self.dim
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(lambda: asyncio.run(self.get_embedding(text_clean))).result()
            else:
                return asyncio.run(self.get_embedding(text_clean))
        except Exception:
            return self._fallback_embedding(text_clean)

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        u = np.array(vec1, dtype=np.float32)
        v = np.array(vec2, dtype=np.float32)
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if norm_u < 1e-8 or norm_v < 1e-8:
            return 0.0
        return float(np.dot(u, v) / (norm_u * norm_v))
