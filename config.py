API_KEY = "AIzaSyDw9wI1vkVGWJJShZTx6Y27Doc4Yzc0pUU"
OPENAI_API_KEY = "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"
TWILIO_SID = "AC411769da93506f4c9dad43c07589aa71"
TWILIO_TOKEN = "91b1a06088a0589adfd5e1e29a4d2d7d"
TWILIO_FROM = "+17407933067"
MONGO_URI = "mongodb://localhost:27017"


LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="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"
LANGSMITH_PROJECT="orange-agent"

import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"  # ← ta clé LangSmith ici
os.environ["LANGCHAIN_PROJECT"] = "orange-agent"
