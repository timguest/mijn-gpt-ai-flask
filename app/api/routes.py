from flask import Flask, request, jsonify
from flask_cors import CORS
from ..scraper.scraper import Scraper
from ..core.chatapi import generate_response, test_response

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOW_LIST}})


@app.route("/message", methods=["POST"])
async def receive_message():
    print(request)
    message_data = request.json
    message_text = message_data["text"]

    # res = await generate_response(message_text)
    # answer = await test_response(message_text)
    res = "Hey, the endpoint is working anyway ;) "

    # "message" value is displayed as the AI's response in the frontend
    return (
        jsonify({"status": "success", "message": res}),
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
