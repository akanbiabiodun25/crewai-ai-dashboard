import os
import io
import pytesseract
import pdfplumber
import speech_recognition as sr
from dotenv import load_dotenv
from flask import Flask, request, render_template
import requests
from werkzeug.utils import secure_filename
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def extract_text_from_pdf(file_stream):
    with pdfplumber.open(file_stream) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])


def extract_text_from_image(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image)


def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)


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
        "regulatory": "You are a regulatory compliance officer. Identify legal or policy risks in the financial domain.",
        "portfolio": "You are an investment portfolio recommender. Suggest optimal strategies and allocations.",
        "onboarding": "You are a customer onboarding specialist. Explain features and resolve new user questions.",
        "monitor": "You are a transaction monitoring agent. Flag unusual, failed or duplicate activities.",
        "reporter": "You are a business intelligence reporter. Generate an executive summary from financial or customer data.",
        "leadgen": "You are a lead generation bot. Qualify potential clients and propose offers.",
        "fraud": "You are a fraud detection bot. Find fraud signals or abuse patterns from input.",
        "closer": "You are an account closure assistant. Guide the customer empathetically and resolve final concerns."
    }

    payload = {
        "model": model_map.get(agent_type, "openai/gpt-4"),
        "messages": [
            {"role": "system", "content": role_map.get(agent_type)},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
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
        return f"❌ HTTP error: {http_err}\n🔁 Response: {response.text}"
    except Exception as err:
        return f"❌ Unexpected error: {err}"


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        agent = request.form.get("agent")
        user_input = request.form.get("user_input", "")

        # Priority: Audio > Image > File > Text
        if "audio_file" in request.files and request.files["audio_file"].filename:
            audio_file = request.files["audio_file"]
            filename = secure_filename(audio_file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            audio_file.save(path)
            user_input = transcribe_audio(path)
        elif "image_file" in request.files and request.files["image_file"].filename:
            image_file = request.files["image_file"]
            user_input = extract_text_from_image(image_file)
        elif "text_file" in request.files and request.files["text_file"].filename:
            text_file = request.files["text_file"]
            filename = text_file.filename
            if filename.endswith(".pdf"):
                user_input = extract_text_from_pdf(text_file)
            else:
                user_input = text_file.read().decode("utf-8")

        # Define agent-specific prompts
        if agent == "fintech":
            prompt = f"Analyze market trends and financial data related to: {user_input}. Provide 5 key insights."
        elif agent == "support":
            prompt = f"Summarize this customer support chat:\n{user_input}\nInclude issue, sentiment, action taken, and summary."
        elif agent == "payment":
            prompt = f"Analyze the following payment records and detect failed, duplicate or refund-needed transactions:\n{user_input}"
        elif agent == "credit":
            prompt = f"""Analyze the following credit applicant profile and provide:
            - Risk level (Low / Moderate / High)
            - Lending decision (Approve / Partial / Decline)
            - Recommended loan amount
            - Rationale considering financial inclusion\n\n{user_input}"""
        else:
            prompt = user_input

        result = run_agent(prompt, agent)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
