from flask import Flask, request, jsonify
from flask_cors import CORS
from app.scraper.scraper import Scraper
from app.core.chatapi import generate_response, test_response

app = Flask(__name__)


@app.route("/message", methods=["POST"])
def receive_message():
    print(request)
    message_data = request.json
    message_text = message_data["text"]

    answer = generate_response(message_text)
    # answer = await test_response(message_text)

    # "message" value is displayed as the AI's response in the frontend
    return (
        jsonify({"status": "success", "message": f"dit is het antwoord {answer}"}),
        200,
    )


@app.route("/url", methods=["POST"])
def receive_url():
    print("start_scraping")
    message_data = request.json
    url = message_data["url"]

    scraper = Scraper()
    scraper.scrape(url)

    # "message" value is displayed as the AI's response in the frontend
    return jsonify({"status": "success", "message": f"Message received: {url}"}), 200


CORS(app, resources={r"/*": {"origins": "https://api.mijndata.ai"}})


