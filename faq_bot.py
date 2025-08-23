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

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")

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

    model_map = {key: "openai/gpt-4" for key in [
        "fintech", "support", "payment", "credit", "faq", "sales", "hiring",
        "regulatory", "portfolio", "onboarding", "monitor", "reporter", "leadgen", "fraud", "closer"
    ]}

    role_map = {
        "fintech": "You are a senior Fintech Data Analyst...",
        "support": "You are a support ticket summarizer...",
        "payment": "You are a payments manager...",
        "credit": "You are a credit advisor...",
        "faq": "You are a friendly Customer Support FAQ Bot...",
        "sales": "You are a sales conversion agent...",
        "hiring": "You are a hiring screening agent...",
        "regulatory": "You are a regulatory compliance officer...",
        "portfolio": "You are an investment portfolio recommender...",
        "onboarding": "You are a customer onboarding specialist...",
        "monitor": "You are a transaction monitoring agent...",
        "reporter": "You are a business intelligence reporter...",
        "leadgen": "You are a lead generation bot...",
        "fraud": "You are a fraud detection bot...",
        "closer": "You are an account closure assistant..."
    }

    payload = {
        "model": model_map.get(agent_type),
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
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
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

        if "audio_file" in request.files and request.files["audio_file"].filename:
            audio_file = request.files["audio_file"]
            path = os.path.join(
                app.config["UPLOAD_FOLDER"], secure_filename(audio_file.filename))
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

        prompt = user_input
        result = run_agent(prompt, agent)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
