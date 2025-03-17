
from flask import Flask, render_template, request, jsonify
import openai
import speech_recognition as sr
from gtts import gTTS
import os
import requests
import json
import paho.mqtt.client as mqtt
from googletrans import Translator

app = Flask(__name__)

# OpenAI API Key (GPT-4 को लागि)
openai.api_key = "YOUR_OPENAI_API_KEY"

# MQTT Broker Config (IoT Smart Device Control)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smart_home/control"

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

translator = Translator()

# 🧠 AI Chatbot (NLP)
def chatbot_response(user_input):
    try:
        translated_text = translator.translate(user_input, src='ne', dest='en').text
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": translated_text}]
        )
        reply = response['choices'][0]['message']['content']
        return translator.translate(reply, src='en', dest='ne').text
    except Exception as e:
        return "माफ गर्नुहोस्, म उत्तर दिन सक्दिन।"

# 📰 News Update
def get_news():
    API_KEY = "YOUR_NEWS_API_KEY"
    url = f"https://newsapi.org/v2/top-headlines?country=np&apiKey={API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data.get("articles", [])
    return [article["title"] for article in articles[:5]]

# 🗣 Speech-to-Text (Voice Recognition)
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="ne-NP")
        return text
    except:
        return "माफ गर्नुहोस्, मैले बुझ्न सकिन।"

# 🔊 Text-to-Speech (Nepali Voice Output)
def text_to_speech(text):
    tts = gTTS(text=text, lang="ne")
    tts.save("response.mp3")
    os.system("start response.mp3")

# 💡 IoT Smart Device Control
def control_device(command):
    mqtt_client.publish(MQTT_TOPIC, command)
    return f"स्मार्ट डिभाइसलाई '{command}' आदेश दिइयो।"

# 📌 API Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    bot_reply = chatbot_response(user_message)
    return jsonify({"reply": bot_reply})

@app.route("/news", methods=["GET"])
def news():
    return jsonify({"news": get_news()})

@app.route("/voice", methods=["GET"])
def voice():
    spoken_text = speech_to_text()
    return jsonify({"voice_text": spoken_text})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.json["text"]
    text_to_speech(text)
    return jsonify({"status": "Speaking"})

@app.route("/device", methods=["POST"])
def device():
    command = request.json["command"]
    response = control_device(command)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)