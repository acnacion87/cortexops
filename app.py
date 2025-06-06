import os
from dotenv import load_dotenv
import chainlit as cl
from shared.state import pop_item
import asyncio
import itertools

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.chat_models import ChatOllama

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate

load_dotenv()
INDEX_PATH = os.getenv("INDEX_PATH")

embedding_model = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-base",
    model_kwargs = {'device': 'cpu'},
    query_instruction="Represent the ServiceNow issue ticket:")

db = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={"k": 6})

prompt = PromptTemplate(
    input_variables=['context', 'input'],
    template="""
    You are an expert in resolving issues in a system based on previous incidents and confluence documentations.
    
    Documents:
    {context}

    Incident:
    {input}

    Think step-by-step:
    1. Understand the type of error and when it occurred.
    2. Check if similar incidents exist - metadata.source="ServiceNow"
    3. If match found, infer likely cause and steps taken.
    4. Check also for related documents - metadata.source="Confluence"
    5. If match found, list the references below under "References:"
    6. Else, specifically mention that you do not have info from past incidents and docs.

    Respond clearly and prioritize practical steps.

    📚 References:
    - Only include titles from source='Confluence' and link using 'url' metadata
    """)

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
        llm = ChatOllama(
            model="llama3.2:3b",
            streaming=True,
            callbacks=[cb],
            model_kwargs={"num_threads": 4, "temperature": 0.7}
        )

        combine_docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

        incident = res.get("payload")
        query = f"Title: {incident.get('title')}\nDescription: {incident.get('description')}"

        # Prepare streaming message
        first_token_received = False
        msg = cl.Message(content="")

        # Run chain and stream results
        async def consume():
            nonlocal first_token_received
            async for token in cb.aiter():
                if not first_token_received:
                    msg.content = "💡 Suggested investigation and resolution approach:\n\n" + token
                    await msg.send()
                    first_token_received = True
                else:
                    await msg.stream_token(token)
            if first_token_received:
                await msg.update()

        await asyncio.gather(
            retrieval_chain.ainvoke({"input": query}),
            consume()
        )
    finally:
        animation_task.cancel()  # Stop animated loading
        try:
            await animation_task  # Needed to suppress cancellation warning
        except asyncio.CancelledError:
            pass

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="⏳ Waiting for a new incident...").send()

    while True:
        item = pop_item()
        if item:
            content = f"⚠️ A new incident ticket was raised.\n\n{item['id']} - {item['title']}\nDescription: {item['description']}"
            payload = {
                "title": item["title"],
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
                await cl.Message(f"⚠️ Issue {res.get('payload').get('title')} was ignored...").send()
                continue
            else:
                await process_incident(res)
                
                await cl.Message(content="⏳ Waiting for a new incident...").send()
                continue
        else:
            await asyncio.sleep(1)  # Wait before polling again
