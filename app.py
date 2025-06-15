# Standard library imports
import asyncio
import itertools
import json
import logging

# Third-party imports
import chainlit as cl
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema.runnable.config import RunnableConfig
from trulens.core import TruSession
from trulens.dashboard import run_dashboard, stop_dashboard

# Local imports
from lib.prompts import RECOMMEND_INCIDENT_RESOLUTION_OPENAI_SYSTEM_PROMPT, RECOMMEND_INCIDENT_RESOLUTION_OPENAI_USER_PROMPT
from shared.state import subscribe_to_incidents
from tools import is_query_valid, search_incidents, search_kb
from tru_app_meta import APP_INFERENCE_MODEL


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[CortexOps]')

session = TruSession()

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history", output_key="output")

prompt = ChatPromptTemplate.from_messages([
    ("system", RECOMMEND_INCIDENT_RESOLUTION_OPENAI_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("user", RECOMMEND_INCIDENT_RESOLUTION_OPENAI_USER_PROMPT),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent_tools = [is_query_valid, search_incidents, search_kb]

incidents_listener = None

@cl.on_app_startup
async def on_app_start():
    load_dotenv()
    run_dashboard(session, port=8003)

@cl.on_app_shutdown
async def on_app_shutdown():
    global incidents_listener
    
    stop_dashboard(session)

    if incidents_listener:
        logger.info("Stopping incidents listener...")
        incidents_listener.cancel()

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
    global incidents_listener

    if incidents_listener:
        try:
            incidents_listener.cancel()
        except Exception as e:
            logger.error("Error stopping incidents listener: %s", e)

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

    incidents_listener = asyncio.create_task(listen_for_incidents())

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
    processing_msg = cl.Message("🔎 Analyzing incident")
    await processing_msg.send()

    try:
        animation_task = asyncio.create_task(animate_processing(processing_msg))
        
        cb = AsyncIteratorCallbackHandler()

        incident = action.payload
        query = f"Short Description: {incident.get('short_description')}\nDescription: {incident.get('description')}"

        llm = ChatOpenAI(
            temperature=0.0,
            model=APP_INFERENCE_MODEL,
            callbacks=[cb],
            streaming=True,
        )
        agent = create_openai_functions_agent(tools=agent_tools, llm=llm, prompt=prompt)
        agent_executor = AgentExecutor(agent=agent, tools=agent_tools, memory=memory, verbose=True)

        msg = cl.Message(author="assistant", content="")

        def safe_serialize(obj):
            try:
                json.dumps(obj)
            except TypeError:
                return None


        async for chunk in agent_executor.astream(
            {"input": query},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            str = safe_serialize(chunk)
            if str and "Used ChatOpenAI" not in str:
                await msg.stream_token(str)

        await msg.send()
    finally:
        animation_task.cancel()  # Stop animated loading
        try:
            await animation_task  # Needed to suppress cancellation warning
        except asyncio.CancelledError:
            pass