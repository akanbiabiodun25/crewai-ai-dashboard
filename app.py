import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, render_template
import webbrowser

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
        "credit": "openai/gpt-4",
        "faq": "openai/gpt-4",
        "sales": "openai/gpt-4",
        "hiring": "openai/gpt-4",
        "regulatory": "openai/gpt-4",
        "portfolio": "openai/gpt-4",
        "onboarding": "openai/gpt-4",
        "monitor": "openai/gpt-4",
        "reporter": "openai/gpt-4",
        "leadgen": "openai/gpt-4",
        "fraud": "openai/gpt-4",
        "closer": "openai/gpt-4"
    }

    role_map = {
        "fintech": "You are a senior Fintech Data Analyst. Analyze market trends and give insights.",
        "support": "You are a support ticket summarizer. Extract key points and sentiment.",
        "payment": "You are a payments manager. Understand and respond to billing-related issues.",
        "credit": "You are a credit advisor. Analyze applicant data and give lending advice.",
        "faq": "You are a friendly Customer Support FAQ Bot. Answer user questions using known FAQ-style responses. Avoid making things up.",
        "sales": "You are a sales conversion agent. Respond persuasively but politely. Convert leads. Handle discounts softly. Escalate if needed.",
        "hiring": "You are a hiring screening agent. Score candidates against job descriptions as Strong Fit, Moderate Fit, or Poor Fit. Justify clearly in 2–3 bullet points.",
        "regulatory": "You are a regulatory compliance officer. Check input for legal or compliance risks.",
        "portfolio": "You are an investment advisor. Suggest portfolio allocation based on user goals, risk tolerance, and capital.",
        "onboarding": "You are a customer onboarding assistant. Review user data and return a checklist of missing or invalid KYC information.",
        "monitor": "You are a transaction monitoring agent. Detect abnormal patterns, spikes, and suspicious activities.",
        "reporter": "You are a business intelligence assistant. Generate a clean executive summary or HTML report from raw input data.",
        "leadgen": "You are a lead generation assistant. Extract warm leads and summarize their interests.",
        "fraud": "You are a fraud detection agent. Detect suspicious activities and provide reasons.",
        "closer": "You are an account closure assistant. Check if the closure request is valid and list any required actions."
    }

    payload = {
        "model": model_map.get(agent_type, "openai/gpt-4"),
        "messages": [
            {"role": "system", "content": role_map.get(agent_type)},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 400
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
            prompt = f"Analyze market trends and financial data related to: {user_input}. Provide 5 key insights."
        elif agent == "support":
            prompt = f"Summarize this customer support chat:\n{user_input}\nInclude issue, sentiment, action taken, and summary."
        elif agent == "payment":
            prompt = f"Analyze the following payment records and detect failed, duplicate or refund-needed transactions:\n{user_input}"
        elif agent == "credit":
            prompt = f"""Analyze the following credit applicant profile and provide:
- A risk level (Low, Moderate, or High)
- Recommended loan decision (Approve / Partial / Decline)
- Suggested loan limit
- Rationale for decision (especially considering financial inclusion)

Applicant Info:
{user_input}"""
        elif agent == "faq":
            prompt = user_input
        elif agent == "sales":
            prompt = f"Sales inquiry:\n{user_input}\nCraft a persuasive response to convert them, handling any objections kindly."
        elif agent == "hiring":
            prompt = f"Review the following resume or application:\n{user_input}\nReturn fit score and justification."
        elif agent == "regulatory":
            prompt = f"Review this company or financial data for compliance issues:\n{user_input}"
        elif agent == "portfolio":
            prompt = f"Suggest an investment portfolio based on this user's profile:\n{user_input}"
        elif agent == "onboarding":
            prompt = f"Analyze this KYC form for missing or invalid information:\n{user_input}"
        elif agent == "monitor":
            prompt = f"Review the following transaction log and detect:\n- Unusual activity\n- Potential fraud or AML red flags\n{user_input}"
        elif agent == "reporter":
            prompt = f"Summarize the following operational data into a business report:\n{user_input}"
        elif agent == "leadgen":
            prompt = f"Analyze this content to extract potential leads:\n{user_input}"
        elif agent == "fraud":
            prompt = f"Detect any fraudulent behavior in this data:\n{user_input}"
        elif agent == "closer":
            prompt = f"Analyze this account closure request:\n{user_input}\nReturn next steps, if any."
        else:
            prompt = user_input

        result = run_agent(prompt, agent)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
