from dotenv import load_dotenv
import time
from os import getenv
import asyncio
from openai import AsyncOpenAI
from .constants import system_prompt
from pathlib import Path
from time import sleep

load_dotenv()


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


async def generate_response(message_text: str) -> str:
    client = AsyncOpenAI(api_key=getenv("OPENAI_API_KEY"))

    training_data = (
        Path(__file__).parent.parent
        / "scraper"
        / "scraped_data"
        / "scrapethissite"
        / "data.txt"
    )
    file = await client.files.create(
        file=open(training_data, "rb"),
        purpose="assistants",
    )

    # Add the file to the assistant
    assistant = await client.beta.assistants.create(
        instructions=system_prompt,
        model="gpt-3.5-turbo-1106",
        tools=[{"type": "retrieval"}],
        file_ids=[file.id],
    )

    thread = await client.beta.threads.create()

    _ = await client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=message_text
    )

    _ = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    current_messages = len(messages.data)

    while len(messages.data) == current_messages:
        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        sleep(1)


    answer = messages.data[0].content[0].text.value

    return answer
