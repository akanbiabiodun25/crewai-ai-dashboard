import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def query_openrouter(prompt: str):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY not found in .env")
        return ""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        # or try: openrouter/mistral-7b, openrouter/claude-3-sonnet
        "model": "openai/gpt-4",
        "messages": [
            {"role": "system", "content": "You are a senior Fintech Data Analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500

    }

    try:
        print("🔍 Sending request to OpenRouter...")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Response received")

        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error: {http_err}")
        print("🔁 Response:", response.text)
    except Exception as err:
        print(f"❌ Unexpected error: {err}")
        try:
            print("🔁 Raw response:", response.json())
        except:
            print("⚠️ Unable to decode JSON.")

    return ""


if __name__ == "__main__":
    topic = input("Enter financial topic: ").strip()

    prompt = f"""
    Analyze current market trends and financial data in the domain of: {topic}.
    Provide a bullet-point summary of 5 key insights in less than 300 words.
    """

    print("🧾 Prompt:\n", prompt)

    result = query_openrouter(prompt)

    if result:
        print("\n=== Fintech Market Analysis ===\n")
        print(result)
    else:
        print("❌ No result returned.")
