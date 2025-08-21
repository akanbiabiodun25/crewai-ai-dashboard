# agents/faq_bot.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def query_openrouter(prompt: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY not found in .env")
        return None

    print("\n🧾 Generating FAQ response...\n")
    payload = {
        "model": "openai/gpt-4",
        "messages": [
            {"role": "system", "content": "You are a friendly Customer Support FAQ Bot. You reply using clear, helpful responses pulled from known company policy and FAQ tone. You do not hallucinate."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print("🔍 Sending request to OpenRouter...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Response received")
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error: {http_err}\n🔁 Response: {response.text}")
    except Exception as err:
        print(f"❌ Unexpected error: {err}")
    return None


if __name__ == "__main__":
    print("📝 Ask a common customer support question:")
    user_question = input(">> ")
    result = query_openrouter(user_question)
    if result:
        print("\n=== FAQ Bot Response ===\n")
        print(result)
    else:
        print("❌ No response from FAQ Bot.")
