from trulens.core.instruments import instrument
from lib.logger import RagChainLogger
from langchain_core.runnables import RunnableConfig

class IncidentRAGApp:
    QUERY_INSTRUCTION = (
        "Represent the new Merchant Onboarding System incident report "
        "to find the most relevant resolution steps and troubleshooting steps:")

    def __init__(self, retriever, combine_docs_chain):
        self.retriever = retriever
        self.combine_docs_chain = combine_docs_chain
        self.config = RunnableConfig(callbacks=[RagChainLogger()])

    @instrument
    async def retrieve(self, query):
        return await self.retriever.ainvoke(f"{IncidentRAGApp.QUERY_INSTRUCTION}{query}", config=self.config)
    
    @instrument
    async def generate(self, query, context):
        return await self.combine_docs_chain.ainvoke({"context": context, "input": query}, config=self.config)

    @instrument
    async def full_chain(self, query):
        context = await self.retrieve(query)
        answer = await self.generate(query, context)
        return {
            "context": context,
            "answer": answer["answer"] if isinstance(answer, dict) else answer
        }