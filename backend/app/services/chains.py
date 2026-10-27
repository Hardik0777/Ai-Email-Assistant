"""LangChain LCEL chains: PromptTemplate | RunnableLambda(LLM) | StrOutputParser."""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable, RunnableLambda

from app.services import llm, prompt_templates


async def _run_llm(prompt: PromptValue) -> str:
    # Looked up at call time, so tests can swap in a fake LLM.
    return await llm.call_gemini(prompt.to_string())


def build_chain(template) -> Runnable:
    return template | RunnableLambda(_run_llm) | StrOutputParser()


summarize_chain = build_chain(prompt_templates.SUMMARIZE)
reply_chain = build_chain(prompt_templates.REPLY)
tasks_chain = build_chain(prompt_templates.TASKS)
classify_chain = build_chain(prompt_templates.CLASSIFY)
