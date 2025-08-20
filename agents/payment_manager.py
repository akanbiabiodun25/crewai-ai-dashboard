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
        # Change to cheaper model like mistralai/mistral-7b-instruct if needed
        "model": "openai/gpt-4",
        "messages": [
            {"role": "system", "content": "You are a smart Payment Operations Assistant. Analyze the input and summarize any failed, duplicate, or suspicious transactions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
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
    print("💳 Paste a list of payment records (e.g. from logs, emails, or transaction system). Press Enter twice to submit:")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    payment_data = "\n".join(lines)

    prompt = f"""
    Analyze the following payment records and return:
    - Any failed transactions
    - Any duplicate payments
    - Any refunds issued or missing
    - A short summary of suspicious patterns

    Payment Logs:
    {payment_data}
    """

    print("🧾 Analyzing payments...\n")
    result = query_openrouter(prompt)

    if result:
        print("\n=== Payment Summary Report ===\n")
        print(result)
    else:
        print("❌ No result returned.")
