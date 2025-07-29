from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from config import API_KEY

from tools.analyse_rapport.save_report_tool import save_report_tool
from tools.analyse_rapport.send_email_alert_tool import send_email_alert_tool

from pymongo import MongoClient
import pandas as pd

# 🔁 Initialisation LLM + outils
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    google_api_key=API_KEY,
    temperature=0.3
)

memory = MemorySaver()

tools = [save_report_tool, send_email_alert_tool]

agent_executor = create_react_agent(
    llm,
    tools,
)

# ▶️ Lancement de l’agent exploratoire autonome
def run_exploratory_agent():
    print("📊 Agent exploratoire (react_agent) lancé...")

    try:
        # 1. Charger les transcriptions déjà analysées
        collection = MongoClient()["audioTranscripts"]["audioTranscripts"]
        docs = list(collection.find({}, {"_id": 0}))
        df = pd.DataFrame(docs)

        if df.empty:
            print("❌ Aucun appel disponible pour analyse.")
            return {"rapport": "vide"}

        # 2. Construire le prompt
        prompt = f"""
Tu es un agent data analyst expert chez Orange Maroc.

Voici les transcriptions brutes des appels clients :

{df['transcription'].dropna().tolist()[:5]}

Ta mission :
1. Rédige un rapport d’analyse exploratoire en markdown clair et synthétique.
2. Appelle ensuite le tool pour sauvegarder ce rapport dans MongoDB qu’une seule fois 
juste après avoir rédigé le rapport..
3. Si tu détectes un problème critique (churn élevé, réclamation répétée,incidents graves...), envoye un mail 
avec un message clair d’alerte pour l’équipe.
"""

        result = agent_executor.invoke({
            "messages": [HumanMessage(content=prompt)],
            "configurable": {"thread_id": "rapport_exploratoire"},
        })

        print("✅ Rapport exploratoire généré + tools exécutés.")
        return result

    except Exception as e:
        print(f"❌ Erreur dans run_exploratory_agent : {str(e)}")
        return {"error": str(e)}
