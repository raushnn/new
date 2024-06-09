from __future__ import annotations

from os import environ

import openai
from httpx import Client
from langchain_community.llms import OpenAI
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

# German proxy
openai.proxy = {
    "http": "http://EN51X2TRnhgICus:YumWPpcW37GoVTD@185.173.26.133:42046",
    "https://": "http://EN51X2TRnhgICus:YumWPpcW37GoVTD@185.173.26.133:42046",
}

DEFAULT_OPENAI_API_KEY = environ["DEFAULT_OPENAI_API_KEY"]

QDRANT_CONNECTION_STRING = environ["QDRANT_CONNECTION_STRING"]

VECTOR_STORE = QdrantClient(url=QDRANT_CONNECTION_STRING)

# Create a collection if it doesn't exist
VECTOR_STORE.create_collection(
    collection_name="main",
    vectors_config={"size": 100, "distance": "Cosine"},
)

LLM_HTTPX_CLIENT = Client(
    proxies={
        "http://": "http://EN51X2TRnhgICus:YumWPpcW37GoVTD@185.173.26.133:42046",
        "https://": "http://EN51X2TRnhgICus:YumWPpcW37GoVTD@185.173.26.133:42046",
    },
)

DEFAULT_LLM = OpenAI(
    api_key=DEFAULT_OPENAI_API_KEY,
    http_client=LLM_HTTPX_CLIENT,
)
