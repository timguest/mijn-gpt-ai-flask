from dotenv import load_dotenv
from os import getenv
import asyncio
from openai import AsyncOpenAI
from .constants import system_prompt

load_dotenv()


async def generate_response(message_text: str) -> str:
    client = AsyncOpenAI(api_key=getenv("OPENAI_API_KEY"))

    file = await client.files.create(
        file=open("backend/app/scraper/scraped_data/jandebelastingman/data.txt", "rb"),
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

    message = await client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=message_text
    )

    run = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value

    return answer
