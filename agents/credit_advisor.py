import os
import requests
from dotenv import load_dotenv

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
        "model": "openai/gpt-4",  # You can replace with: mistralai/mistral-7b-instruct
        "messages": [
            {"role": "system", "content": "You are a Credit Scoring and Lending Advisor AI. Your job is to analyze applicant data and make smart loan recommendations, considering financial inclusion and local economic realities."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 400
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
    print("💳 Paste credit applicant data (structured or informal). Press Enter twice to submit:\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    applicant_data = "\n".join(lines)

    prompt = f"""
    Analyze the following credit applicant profile and provide:

    - A risk level (Low, Moderate, or High)
    - Recommended loan decision (Approve / Partial / Decline)
    - Suggested loan limit
    - Rationale for decision (especially considering financial inclusion)

    Applicant Info:
    {applicant_data}
    """

    print("🧾 Analyzing credit profile...\n")
    result = query_openrouter(prompt)

    if result:
        print("\n=== Credit Decision Report ===\n")
        print(result)
    else:
        print("❌ No result returned.")
