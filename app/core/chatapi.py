from dotenv import load_dotenv
import time
from os import getenv
import asyncio
from openai import AsyncOpenAI
from .constants import system_prompt
from pathlib import Path
from time import sleep
import openai
import json
from google.cloud import storage
from google.oauth2.service_account import Credentials
import os

load_dotenv()

if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    # Set the environment variable for local development
    local_key_path = '/Users/tim.guest/PycharmProjects/mijn-gpt-ai-flask/mijngpt-ai-d56736999e85.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = local_key_path

client = openai.OpenAI(
    api_key=getenv("OPENAI_API_KEY")
)


def generate_response(question: str, local_file_path) -> str:
    thread = client.beta.threads.create()

    file = client.files.create(
        file=open(local_file_path, "rb"),
        purpose='assistants'
    )

    # Add the file to the assistant
    assistant = client.beta.assistants.create(
        instructions="You are an advanced intelligent assistant designed to provide precise and succinct support to "
                     "users. Operating within a website widget, your primary role is to assist customers by "
                     "delivering answers based on a specific text file provided to you. It's imperative that your "
                     "responses are accurate, strictly derived from the contents of the provided file, "
                     "and contextually appropriate. Ensure your answers are relevant and concise, avoiding any "
                     "conjecture or deviation from the source material",
        model="gpt-4-1106-preview",
        tools=[{"type": "retrieval"}],
        file_ids=[file.id]
    )

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )

    def run_assistant(client, assistant_id, thread_id):
        # Runs the assistant with the given thread and assistant IDs.
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while run.status == "in_progress" or run.status == "queued":

            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run.status == "completed":
                return client.beta.threads.messages.list(
                    thread_id=thread_id
                )
            time.sleep(1)

    messages = run_assistant(client, assistant.id, thread.id)
    message_dict = json.loads(messages.model_dump_json())
    most_recent_message = message_dict['data'][0]
    answer = most_recent_message['content'][0]['text']['value']

    return answer


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket to a writable directory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    # Save to a writable location
    writable_destination = os.path.join('/tmp', destination_file_name)
    blob.download_to_filename(writable_destination)

    # Return the path to the downloaded file
    return writable_destination


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the specified bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
