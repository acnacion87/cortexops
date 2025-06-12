import numpy as np

from trulens.core import Feedback,Select

from trulens.providers.openai import OpenAI

def create_feedback_functions(provider = None):
    provider = provider or OpenAI(model_engine="gpt-4o-mini")

    # Question/answer relevance between overall question and answer.
    f_answer_relevance = Feedback(
        provider.relevance_with_cot_reasons, name="Answer Relevance"
    ).on_input().on(Select.RecordCalls.generate.rets)

    # Context relevance between question and each context chunk.
    f_context_relevance = (
        Feedback(
            provider.context_relevance_with_cot_reasons, name="Context Relevance"
        )
        .on(Select.Record.app.retrieve.args.query)
        .on(Select.RecordCalls.retrieve.rets[:])
        .aggregate(np.mean)
    )

    # Define a groundedness feedback function
    f_groundedness = (
        Feedback(
            provider.groundedness_measure_with_cot_reasons, name="Groundedness",
        )
        .on(Select.RecordCalls.retrieve.rets.collect())
        .on_output()
    )

    return [f_answer_relevance, f_context_relevance, f_groundedness]