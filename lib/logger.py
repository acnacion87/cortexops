import logging

from langchain.callbacks.base import BaseCallbackHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[RAG]')

class RagChainLogger(BaseCallbackHandler):

    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        logger.info("[Chain Start] Run Id: %s - %s", run_id, serialized)
        logger.info("[Input]: %s.", inputs)

    def on_chain_end(self, outputs, *, run_id, parent_run_id = None, **kwargs):
        logger.info("[Chain End] Run Id: %s - %s", run_id, outputs)

    def on_retriever_start(self, serialized, query, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        logger.info("[Retriever Start] Query: %s.", query)

    def on_retriever_end(self, documents, *, run_id, parent_run_id = None, **kwargs):
        logger.info("[Retriever End] Retrieved %d documents.", len(documents))

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        logger.info("[LLM Start] Prompt: %s", prompts)
    
    def on_llm_end(self, response, *, run_id, parent_run_id = None, **kwargs):
        logger.info("[LLM End] Response: %s", response.generations[0][0].text)