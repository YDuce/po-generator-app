"""AI helper stub for price/category suggestions (v1.5)."""

import os
import requests

class AIClient:
    def suggest_category(self, title: str, brand: str, attrs: dict) -> list[int]:
        return []
    def suggest_price(self, cost: float, msrp: float, comps: list[float]) -> float:
        return round(cost * 1.2, 2)

class HuggingFaceClient(AIClient):
    def __init__(self, token=None):
        self.token = token or os.getenv('HF_API_TOKEN')
    def suggest_category(self, title: str, brand: str, attrs: dict) -> list[int]:
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"inputs": f"{title} {brand} {attrs}"}
        resp = requests.post(
            "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
            headers=headers, json=data
        )
        result = resp.json()
        text = result.get("choices", [{}])[0].get("text", "Custom")
        # Map to category_id (stub: always return [1])
        return [1]

def get_ai_client():
    if os.getenv("OPENAI_API_KEY"):
        return AIClient()  # Replace with OpenAIClient()
    elif os.getenv("HF_API_TOKEN"):
        return HuggingFaceClient(os.getenv("HF_API_TOKEN"))
    else:
        return AIClient()

def suggest_category_and_price(product_attrs):
    # TODO: Implement AI suggestion logic
    return {"category": None, "price": None}

def suggest_category(product) -> str:
    """Placeholder until AI model integrated."""
    return "Default"
