from flask import Flask, request, jsonify
from flask_cors import CORS
from app.scraper.scraper import Scraper
from app.core.chatapi import generate_response, download_blob





def receive_message():
    print(request)
    message_data = request.json
    message_text = message_data["text"]
    # Specify your bucket name and blob name
    bucket_name = 'bucket_storing_data_clients'
    source_blob_name = 'jandebelastingman_data.txt'
    destination_file_name = 'jandebelastingman_data.txt'

    # Get the local file path after downloading
    local_file_path = download_blob(bucket_name, source_blob_name, destination_file_name)

    answer = generate_response(message_text, local_file_path)
    # answer = await test_response(message_text)

    # "message" value is displayed as the AI's response in the frontend
    return (
        jsonify({"status": "success", "message": f"dit is het antwoord {answer}"}),
        200,
    )



def receive_url(url):
    print("start_scraping")


    scraper = Scraper()
    scraper.scrape(url)

    # "message" value is displayed as the AI's response in the frontend
    return jsonify({"status": "success", "message": f"Message received: {url}"}), 200





receive_url('https://dehoogewaerder.nl/')