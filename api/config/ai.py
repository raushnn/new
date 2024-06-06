from __future__ import annotations

from os import environ

import openai
from httpx import Client
from langchain.llms import OpenAI
from langchain.vectorstores import Qdrant

# German proxy
openai.proxy = {
    "http": "http://EN51X2TRnhgICus:YumWPpcW37GoVTD@185.173.26.133:42046",
    "https://": "http://EN51X2TRnhgICus:YumWPpcW37GoVTD@185.173.26.133:42046",
}

# DEFAULT_OPENAI_API_KEY = environ["DEFAULT_OPENAI_API_KEY"]
DEFAULT_OPENAI_API_KEY = 'sk-proj-BF3N2NaJkmlbsi0wr04iT3BlbkFJIrXqmhKmVfGotopoq46g'

# QDRANT_CONNECTION_STRING = environ["QDRANT_CONNECTION_STRING"]
QDRANT_CONNECTION_STRING = 'http://localhost:6333'  # Qdrant default URL

VECTOR_STORE = Qdrant(
    url=QDRANT_CONNECTION_STRING,
    collection_name="main",
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
