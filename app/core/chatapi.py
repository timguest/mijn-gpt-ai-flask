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
load_dotenv()

import os
script_dir = os.path.dirname(__file__)  # Path to the directory of the current script
data_path = os.path.join(script_dir, "..", "scraper", "scraped_data", "jandebelastingman", "data.txt")



client = openai.OpenAI(
    api_key=getenv("OPENAI_API_KEY")
)

thread = client.beta.threads.create()

file = client.files.create(
    file = open(data_path, "rb"),
    purpose='assistants'
)

# Add the file to the assistant
assistant = client.beta.assistants.create(
    instructions="You are an intelligent assistant dedicated to offering clear, concise support and guidance. Your "
                 "role is to provide accurate"
                 "answers to questions, relying solely on information from the provided PDF "
                 "documentation. You are programmed to communicate in an easy-to-understand, non-technical "
                 "language, ensuring accessibility for all users, regardless of their familiarity with "
                 "dishwashers. Your tone is friendly, approachable, and professional, aiding in delivering "
                 "instructions and explanations that are both informative and easy to comprehend. Importantly, "
                 "you are programmed to not fabricate responses. If a query falls outside the scope of the "
                 "provided documentation, you will politely inform the user that the information is not "
                 "available, rather than offering speculative or made-up answers. This approach ensures that "
                 "users receive reliable and accurate information, enhancing their experience and trust. Keep the answers"
                 "relevant and short.",
    model="gpt-4-1106-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
)


async def test_response(message_text):
    client = AsyncOpenAI()
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion)


def generate_response(question: str) -> str:
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
