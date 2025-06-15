import os
from dotenv import load_dotenv
import chainlit as cl
from lib.embeddings import get_retriever
from shared.state import subscribe_to_incidents
import asyncio
import itertools
import json
import logging

from lib.prompts import RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_SYSTEM_PROMPT, RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_USER_PROMPT

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_ollama import ChatOllama

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate

from trulens.core import TruSession
from trulens.dashboard import run_dashboard, stop_dashboard

from rag import IncidentRAGApp
from feedback import create_tru_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[CortexOps]')


llm = None
retriever = None
incident_rag_app = None
tru_recorder = None

session = TruSession()

@cl.on_app_startup
async def on_app_start():
    global llm
    global retriever
    global incident_rag_app
    global tru_recorder

    load_dotenv()
    INDEX_PATH = os.getenv("INDEX_PATH")

    if llm is None:
        llm = create_llm()
    if retriever is None:
        retriever = get_retriever(INDEX_PATH)
    if incident_rag_app is None:
        incident_rag_app = create_incident_rag_app()
    if tru_recorder is None:
        tru_recorder = create_tru_app(incident_rag_app)

    run_dashboard(session, port=8003)

@cl.on_app_shutdown
async def on_app_shutdown():
    stop_dashboard(session)

async def on_new_incident(item):
    logger.info("New incident ticket was raised: %s - %s", item["number"], item["short_description"])

    content = f"⚠️ A new incident ticket was raised.\n\n**{item['number']}** - {item['short_description']}\n**Description**\n{item['description']}"
    payload = {
        "short_description": item["short_description"],
        "description": item["description"]
    }
    await cl.Message(
        content=content,
        actions=[
            cl.Action(name="analyze", payload=payload, label="🧠 Analyze"),
            cl.Action(name="ignore", payload=payload, label="❌ Ignore")
        ]).send()

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(author="assistant", content="⏳ Waiting for a new incident...").send()
    
    # Subscribe to the incident queue
    pubsub = await subscribe_to_incidents()
    
    async def listen_for_incidents():
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message["type"] == "message":
                item = json.loads(message["data"])
                await on_new_incident(item)
            await asyncio.sleep(0.1)  # prevent busy-waiting

    asyncio.create_task(listen_for_incidents())

@cl.action_callback("analyze")
async def on_analyze(action: cl.Action):
    logger.info("Analyzing incident %s - %s", action.payload.get("number"), action.payload.get("short_description"))

    await process_incident(action)
    await cl.Message(author="assistant", content="⏳ Waiting for a new incident...").send()
    

@cl.action_callback("ignore")
async def on_ignore(action: cl.Action):
    logger.info("Ignoring incident %s - %s", action.payload.get("number"), action.payload.get("short_description"))

    payload = action.payload
    await cl.Message(author="assistant", content=f"⚠️ Issue {payload.get('short_description')} was ignored...").send()

async def animate_processing(msg: cl.Message, base_text="🔎 Analyzing incident", delay=0.5):
    """Animate a loading message by updating its content with dots."""
    for dots in itertools.cycle(["", ".", "..", "..."]):
        msg.content = f"{base_text}{dots}"
        await msg.update()
        await asyncio.sleep(delay)

async def process_incident(action: cl.Action):
    global llm
    global incident_rag_app
    global tru_recorder

    processing_msg = cl.Message("🔎 Analyzing incident")
    await processing_msg.send()

    try:
        animation_task = asyncio.create_task(animate_processing(processing_msg))
        
        cb = AsyncIteratorCallbackHandler()
        llm.callbacks = [cb]

        incident = action.payload
        query = f"Short Description: {incident.get('short_description')}\nDescription: {incident.get('description')}"

        # Prepare streaming message
        first_token_received = False
        msg = cl.Message(author="assistant", content="")
        # Run chain and stream results
        async def consume():
            nonlocal first_token_received
            async for token in cb.aiter():
                if not first_token_received:
                    msg.content = "💡 **AI Assistant Response**:\n\n" + token
                    await msg.send()
                    first_token_received = True
                else:
                    await msg.stream_token(token)
            if first_token_received:
                await msg.update()

        async with tru_recorder:
            await asyncio.gather(
                incident_rag_app.full_chain({"input": query}),
                consume()
            )
    finally:
        animation_task.cancel()  # Stop animated loading
        try:
            await animation_task  # Needed to suppress cancellation warning
        except asyncio.CancelledError:
            pass

def create_llm():
    logger.info("Creating LLM using Ollama with model phi3:mini...")
    return ChatOllama(
        temperature=0.7,
        model="phi3:mini",
        num_thread=6,
        streaming=True,
    )

def create_chain(llm):
    logger.info("Creating chain using create_stuff_documents_chain...")
    system_prompt = SystemMessagePromptTemplate.from_template(RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_SYSTEM_PROMPT)
    user_prompt = HumanMessagePromptTemplate.from_template(RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_USER_PROMPT)
    prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

    return create_stuff_documents_chain(llm=llm, prompt=prompt)

def create_incident_rag_app():
    global llm
    global retriever

    logger.info("Creating Incident RAG App...")
    return IncidentRAGApp(retriever, create_chain(llm=llm))