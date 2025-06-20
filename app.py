import os
from dotenv import load_dotenv
import chainlit as cl
from lib.embeddings import get_embedding_model, get_retriever
from shared.state import pop_item
import asyncio
import itertools


from lib.prompts import RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_SYSTEM_PROMPT, RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_USER_PROMPT

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate

from trulens.core import TruSession
from trulens.apps.app import TruApp
from trulens.dashboard import run_dashboard, stop_dashboard

from rag import IncidentRAGApp
from feedback import create_feedback_functions

load_dotenv()
INDEX_PATH = os.getenv("INDEX_PATH")

embedding_model = get_embedding_model()
retriever = get_retriever(INDEX_PATH)

system_prompt = SystemMessagePromptTemplate.from_template(RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_SYSTEM_PROMPT)
user_prompt = HumanMessagePromptTemplate.from_template(RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_USER_PROMPT)

prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

session = TruSession()
    
llm = ChatOllama(
    temperature=0.7,
    model="phi3:mini",
    num_thread=4,
    streaming=True,
)

combine_docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
incident_rag_app = IncidentRAGApp(retriever, combine_docs_chain)

feedback_functions = create_feedback_functions()
tru_recorder = TruApp(
    app=incident_rag_app,
    app_name="CortexOps",
    app_version="1.0.0",
    metadata={
        "type": "RAG",
        "retriever": "faiss",
        "embedding_model": "hkunlp/instructor-base",
        "index_style": "single-index",
        "rag_chain": "stuff_documents_chain",
        "prompt_style": "Zero-shot",
        "inference_model": "Ollama/phi3:mini",
        "feedback_model": "OpenAI/gpt-4o-mini"
    },
    feedbacks=feedback_functions,
)

async def animate_processing(msg: cl.Message, base_text="🔎 Analyzing incident", delay=0.5):
    """Animate a loading message by updating its content with dots."""
    for dots in itertools.cycle(["", ".", "..", "..."]):
        msg.content = f"{base_text}{dots}"
        await msg.update()
        await asyncio.sleep(delay)

async def process_incident(res):
    processing_msg = cl.Message("🔎 Analyzing incident")
    await processing_msg.send()

    try:
        animation_task = asyncio.create_task(animate_processing(processing_msg))
        
        cb = AsyncIteratorCallbackHandler()
        llm.callbacks = [cb]

        incident = res.get("payload")
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

        async with tru_recorder as recorder:
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

@cl.on_app_startup
async def on_app_start():
    run_dashboard(session, port=8003)

@cl.on_app_shutdown
async def on_app_shutdown():
    stop_dashboard(session)

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(author="assistant", content="⏳ Waiting for a new incident...").send()

    while True:
        item = pop_item()
        if item:
            content = f"⚠️ A new incident ticket was raised.\n\n**{item['number']}** - {item['short_description']}\n**Description**\n{item['description']}"
            payload = {
                "short_description": item["short_description"],
                "description": item["description"]
            }
            res = await cl.AskActionMessage(
                raise_on_timeout=True,
                content=content,
                actions=[
                    cl.Action(name="analyze", payload=payload, label="🧠 Analyze"),
                    cl.Action(name="ignore", payload=payload, label="❌ Ignore")
                ]).send()
            if (res.get("name") == "ignore"):
                await cl.Message(author="assistant", content=f"⚠️ Issue {res.get('payload').get('short_description')} was ignored...").send()
                continue
            else:
                await cl.Message(author="assistant", content=f"**{item['number']}** - {item['short_description']}\n\n{item['description']}").send()
                await process_incident(res)
                
                await cl.Message(author="assistant", content="⏳ Waiting for a new incident...").send()
                continue
        else:
            await asyncio.sleep(1)  # Wait before polling again
