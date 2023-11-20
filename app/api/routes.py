from flask import Flask, request, jsonify
from flask_cors import CORS
from app.scraper.scraper import Scraper
from app.core.chatapi import generate_response, download_blob

app = Flask(__name__)


@app.route("/message", methods=["POST"])
def receive_message():
    print(request)
    message_data = request.json
    message_text = message_data["text"]
    # Specify your bucket name and blob name
    bucket_name = 'bucket_storing_data_clients'
    source_blob_name = 'dehoogewaerder_data.txt'
    destination_file_name = 'dehoogewaerder_data.txt'

    # Get the local file path after downloading
    local_file_path = download_blob(bucket_name, source_blob_name, destination_file_name)

    answer = generate_response(message_text, local_file_path)
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


# Configure CORS to allow both production and local development domains
CORS(app, resources={r"/*": {"origins": ["https://api.mijndata.ai", "http://127.0.0.1:8087"]}})



