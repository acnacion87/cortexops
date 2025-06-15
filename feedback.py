import numpy as np

from trulens.core import Feedback
from trulens.apps.langchain import TruChain
from trulens.providers.openai import OpenAI

from tru_app_meta import APP_FEEDBACK_MODEL, APP_METADATA, APP_VERSION


def create_tru_chain(agent):
    feedback_functions = create_feedback_functions()
    return TruChain(
        agent,
        app_name="CortexOps",
        app_version=APP_VERSION,
        metadata=APP_METADATA,
        feedbacks=feedback_functions,
    )

def create_feedback_functions(provider = None):
    provider = provider or OpenAI(model_engine=APP_FEEDBACK_MODEL)

    # Question/answer relevance between overall question and answer.
    f_answer_relevance = Feedback(
        provider.relevance_with_cot_reasons, name="Answer Relevance"
    ).on_input_output()

    # Context relevance between question and each context chunk.
    f_context_relevance = (
        Feedback(
            provider.context_relevance_with_cot_reasons, name="Context Relevance"
        )
        .on_input()
        .on_output()
        .aggregate(np.mean)
    )

    # Define a groundedness feedback function
    f_groundedness = (
        Feedback(
            provider.groundedness_measure_with_cot_reasons, name="Groundedness",
        )
        .on_input_output()
    )

    return [f_answer_relevance, f_context_relevance, f_groundedness]