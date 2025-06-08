from langchain.callbacks.base import BaseCallbackHandler

class RagChainLogger(BaseCallbackHandler):

    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        print(f"[CHAIN Start] Run Id: {run_id} - {serialized}")
        print(f"[Input]: {inputs}.")

    def on_chain_end(self, outputs, *, run_id, parent_run_id = None, **kwargs):
        print(f"[CHAIN End] Run Id: {run_id} - {outputs}.")

    def on_retriever_start(self, serialized, query, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        print(f"[RETRIEVER Start] Query: {query}.")

    def on_retriever_end(self, documents, *, run_id, parent_run_id = None, **kwargs):
        print(f"[RETRIEVER End] Retrieved {len(documents)} documents.")

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        print(f"[LLM Start] Prompt: {prompts}")
    
    def on_llm_end(self, response, *, run_id, parent_run_id = None, **kwargs):
        print(f"[LLM End] Response: {response.generations[0][0].text}")