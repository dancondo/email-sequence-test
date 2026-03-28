from openai import OpenAI

from app.modules.openai_llm.client import create_openai_client


def get_openai_client() -> OpenAI:
    return create_openai_client()
