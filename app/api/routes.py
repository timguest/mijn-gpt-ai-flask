from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from app.scraper.scraper import Scraper
from app.core.chatapi import generate_response, download_blob
import os
app = Flask(__name__)


@app.route("/message", methods=["POST"])
def receive_message():
    print(request.json)
    message_data = request.json
    message_text = message_data.get("text")
    company = message_data.get("company")

    # Specify your bucket name and blob name
    bucket_name = 'bucket_storing_data_clients'
    source_blob_name = f'{company}/data.txt'
    destination_file_name = f'{company}_data.txt'

    # Get the local file path after downloading
    local_file_path = download_blob(bucket_name, source_blob_name, destination_file_name)

    answer = generate_response(message_text, local_file_path)
    # answer = await test_response(message_text)

    # "message" value is displayed as the AI's response in the frontend
    return (
        jsonify({"status": "success", "message": f"{answer}"}),
        200,
    )


@app.route("/url", methods=["POST"])
def receive_url():
    print("start_scraping")
    message_data = request.json
    url = message_data["url"]
    #
    scraper = Scraper()
    domain_info = scraper.scrape(url)

    return jsonify({"status": "success", "domainInfo": domain_info, "message": domain_info})


@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, '../static'), 'demo.html')

if __name__ == '__main__':
    app.run(debug=True)
