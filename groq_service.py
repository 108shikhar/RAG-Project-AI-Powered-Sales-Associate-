import os
import json
import httpx
from typing import List, Dict, Any, Optional

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

class GroqService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    def set_api_key(self, key: str):
        self.api_key = key.strip() if key else None

    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.5) -> str:
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": 1000
                    }
                    resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[GroqService] API Error: {e}")
        return self._simulate_chat_response(messages)

    async def transform_prompt_to_semantic_query(
        self,
        user_message: str,
        category: Optional[str],
        sub_category: Optional[str],
        collected_attributes: Dict[str, Any]
    ) -> str:
        system_prompt = (
            "You are an expert E-Commerce Sales Associate LLM for ApnaMart (https://apnamarts.shop/ - Slogan: 'Sab Kuch, Ek Hi Jagah'). "
            "Your task is to analyze the customer's request and synthesize ONE clear, concise, highly descriptive semantic sentence "
            "capturing their target product, category, subcategory, type, occasion/spec, size/purpose, color, budget, and key preferences.\n"
            "Output ONLY the synthesized sentence, nothing else.\n"
            "Example format: 'User wants M-sized navy blue suit for office wear on ApnaMart matching requirement: I want a suit for interview'"
        )

        user_content = (
            f"Customer Message: {user_message}\n"
            f"Category: {category or 'Not specified'}\n"
            f"Subcategory: {sub_category or 'Not specified'}\n"
            f"Collected Details: {json.dumps(collected_attributes)}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        if self.api_key:
            try:
                result = await self.chat_completion(messages, temperature=0.2)
                if result and len(result) > 10:
                    return result.strip('"').strip("'")
            except Exception as e:
                print(f"[GroqService] Transform error: {e}")

        target = collected_attributes.get("type") or sub_category or category or "item"
        occasion = collected_attributes.get("occasion", "everyday / purpose")
        size = collected_attributes.get("size", "")
        color = collected_attributes.get("color", "")
        cat_str = category or "ApnaMart"

        parts = ["User wants"]
        if size:
            parts.append(f"{size}")
        if color:
            parts.append(f"{color}")
        parts.append(f"{target.lower()} in {cat_str}")
        if occasion:
            parts.append(f"for {occasion.lower()} purpose")
        parts.append(f"on ApnaMart matching requirement: '{user_message.strip()}'")

        return " ".join(parts)

    async def generate_consultative_pitch(
        self,
        query_sentence: str,
        products: List[Dict[str, Any]],
        user_message: str
    ) -> str:
        system_prompt = (
            "You are 'ApnaMart Sahayak' (Aarav), the polite, knowledgeable, and value-driven AI Personal Shopping Assistant "
            "for ApnaMart (https://apnamarts.shop/ - 'Sab Kuch, Ek Hi Jagah'). You guide shoppers across India to find genuine, "
            "high-value products with fast delivery and great discounts. Greet warmly, highlight the #1 recommendation and why it fits "
            "their specific requirement (features, quality, price), explain the other top picks, and encourage them to add to bag. "
            "Use warm, courteous English mixed with natural Indian warmth."
        )

        prod_summary = []
        for i, p in enumerate(products, 1):
            score_pct = int(round(p.get('similarity_score', 0.9) * 100))
            prod_summary.append(
                f"{i}. {p['name']} (₹{p['price']}, {p.get('discount', 'Super Deal')}) - Match: {score_pct}%. "
                f"Category: {p.get('category')}, Sub: {p.get('sub_category')}. "
                f"Colors: {', '.join(p.get('colors', []))}. "
                f"Sizes: {', '.join(p.get('sizes', []))}. "
                f"Occasion: {', '.join(p.get('occasion', []))}. "
                f"Description: {p['description']}"
            )

        user_content = (
            f"Customer Requirement: {query_sentence}\n"
            f"Original Query: {user_message}\n"
            f"Top Retrieved ApnaMart Products:\n" + "\n".join(prod_summary)
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        if self.api_key:
            try:
                pitch = await self.chat_completion(messages, temperature=0.6)
                if pitch:
                    return pitch
            except Exception as e:
                print(f"[GroqService] Pitch error: {e}")

        top_item = products[0] if products else None
        top_name = top_item['name'] if top_item else "our top-rated product"
        top_price = top_item['price'] if top_item else 499
        top_discount = top_item.get('discount', 'Mega Discount') if top_item else 'Special Deal'
        top_cat = top_item.get('category', 'ApnaMart') if top_item else 'ApnaMart'

        return (
            f"Namaste! Welcome to ApnaMart — Sab Kuch, Ek Hi Jagah! 🙏🛍️\n\n"
            f"Aapki requirement ke anusaar, mera #1 recommendation hai **{top_name}** at just **₹{top_price}** ({top_discount}). "
            f"Yeh 100% verified genuine ApnaMart product hai, jo aapke specific occasion aur budget ke hisaab se best fit baithta hai.\n\n"
            f"Neeche maine aapke liye top 5 matches curate kiye hain with live vector similarity scores. "
            f"Aap direct 'Add to Bag' par click karke order place kar sakte hain ya mujhse aur koi query poochh sakte hain!"
        )

    def _simulate_chat_response(self, messages: List[Dict[str, str]]) -> str:
        return "Namaste! Main hoon aapka ApnaMart Sahayak. Bataiye aaj aapke liye kya search karoon? (Sab Kuch, Ek Hi Jagah!)"
