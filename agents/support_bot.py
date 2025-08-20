import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
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
        # You can change to mistralai/mistral-7b-instruct if low on tokens
        "model": "openai/gpt-4",
        "messages": [
            {"role": "system", "content": "You are an AI Customer Support Analyst who summarizes support interactions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
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
    print("📝 Paste a customer support chat or complaint (press Enter twice to submit):")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    conversation = "\n".join(lines)

    prompt = f"""
    Analyze the following customer support chat or email and summarize the following:
    - The main issue the customer is facing
    - The customer's sentiment (angry, neutral, satisfied, etc.)
    - Action taken or recommended
    - One-line summary of the entire interaction

    Support Text:
    {conversation}
    """

    print("🧾 Generating summary...\n")
    result = query_openrouter(prompt)

    if result:
        print("\n=== Customer Support Summary ===\n")
        print(result)
    else:
        print("❌ No result returned.")
