API_KEY = ""
OPENAI_API_KEY = ""
TWILIO_SID = "AC411769da93506f4c9dad43c07589aa71"
TWILIO_TOKEN = "91b1a06088a0589adfd5e1e29a4d2d7d"
TWILIO_FROM = ""
MONGO_URI = "mongodb://localhost:27017"


LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="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"
LANGSMITH_PROJECT="orange-agent"

import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = ""  # ← ta clé LangSmith ici
os.environ["LANGCHAIN_PROJECT"] = "orange-agent"
