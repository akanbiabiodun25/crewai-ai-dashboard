import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, render_template
import webbrowser

# Load API key from .env
load_dotenv()

app = Flask(__name__)


def run_agent(prompt, agent_type):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "❌ ERROR: OPENROUTER_API_KEY not found in .env"

    model_map = {
        "fintech": "openai/gpt-4",
        "support": "openai/gpt-4",
        "payment": "openai/gpt-4",
        "credit": "openai/gpt-4"
    }

    role_map = {
        "fintech": "You are a senior Fintech Data Analyst.",
        "support": "You are a customer support summarizer.",
        "payment": "You are a payment auditor for finance operations.",
        "credit": "You are a Credit Scoring and Lending Advisor AI. Analyze applicant data and return smart loan decisions, especially considering financial inclusion."
    }

    payload = {
        "model": model_map.get(agent_type, "openai/gpt-4"),
        "messages": [
            {"role": "system", "content": role_map.get(agent_type)},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 200
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
        return f"❌ HTTP error: {http_err}\n🔁 Response: {response.text}"
    except Exception as err:
        return f"❌ Unexpected error: {err}"


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        agent = request.form["agent"]
        user_input = request.form["user_input"]

        if agent == "fintech":
            prompt = f"""Analyze market trends and financial data related to: {user_input}. Provide 5 key insights."""
        elif agent == "support":
            prompt = f"""Summarize this customer support chat:\n{user_input}\nInclude issue, sentiment, action taken, and summary."""
        elif agent == "payment":
            prompt = f"""Analyze the following payment records and detect failed, duplicate or refund-needed transactions:\n{user_input}"""
        elif agent == "credit":
            prompt = f"""Analyze the following credit applicant profile and provide:
            - A risk level (Low, Moderate, or High)
            - Recommended loan decision (Approve / Partial / Decline)
            - Suggested loan limit
            - Rationale for decision (especially considering financial inclusion)

            Applicant Info:
            {user_input}
            """
        else:
            prompt = user_input

        result = run_agent(prompt, agent)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
