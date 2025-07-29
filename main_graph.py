# main_graph.py

from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from typing import TypedDict
from agents.agent_analyse import run_analysis
from agents.agent_exploratoire import run_exploratory_agent
from agents.agent_sms import run_sms
from langsmith.client import Client
import uuid
import os


# 📦 État partagé
class AgentState(TypedDict, total=False):
    nom_audio: str
    transcription: str
    analyse: dict
    sms: str
    rapport: dict

# 🎙️ Transcription Agent
class TranscriptionAgent(Runnable):
    def invoke(self, state: AgentState, config=None) -> AgentState:
        from agents.agent_transcription import run_transcription_for_one
        print("🎙️ Transcription - récupération du prochain audio...")
        result = run_transcription_for_one()

        if not result or "nom_audio" not in result:
            print("✅ Aucun fichier à transcrire.")
            return {}

        return {
            "nom_audio": result["nom_audio"],
            "transcription": result["transcription"]
        }

# 🧠 Analyse Agent
class AnalyseAgent(Runnable):
    def invoke(self, state: AgentState, config=None) -> AgentState:
        if "nom_audio" not in state or "transcription" not in state:
            return {}
        print(f"🧠 Analyse pour {state['nom_audio']}")
        return {"analyse": run_analysis(state["nom_audio"], state["transcription"])}
    
# 📊 Rapport exploratoire (markdown + alerte si besoin)
class RapportAgent(Runnable):
    def invoke(self, state: AgentState, config=None) -> AgentState:
        if "nom_audio" not in state:  # 👈 Ignore si aucune transcription
            print("📊 Aucun audio traité → pas de rapport exploratoire.")
            return {}
        print("📊 Rapport exploratoire déclenché...")
        rapport_result = run_exploratory_agent()
        return {"rapport": rapport_result}

# 📩 SMS Agent
class SmsAgent(Runnable):
    def invoke(self, state: AgentState, config=None) -> AgentState:
        if "nom_audio" not in state or "transcription" not in state:
            return {}
        print(f"📩 SMS pour {state['nom_audio']}")
        run_sms(state["nom_audio"], state["transcription"])
        return {"sms": "done"}

# 🧠 Construction du graphe
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("transcription_node", TranscriptionAgent())
    graph.add_node("analyse_node", AnalyseAgent())
    graph.add_node("rapport_node", RapportAgent())
    graph.add_node("sms_node", SmsAgent())

    graph.set_entry_point("transcription_node")

    # Ordre des étapes
    graph.add_edge("transcription_node", "analyse_node")
    graph.add_edge("analyse_node", "rapport_node")
    graph.add_edge("rapport_node", "sms_node")
    graph.add_edge("sms_node", END)

    return graph.compile()

# ▶️ Exécution avec boucle intelligente
if __name__ == "__main__":
    print("🚀 Pipeline LangGraph multi-agents")
    run_id = str(uuid.uuid4())
    os.environ["LANGCHAIN_SESSION"] = f"run-{run_id}"
    print(f"🔍 Run ID LangSmith : {run_id}")
    app = build_graph()
    while True:
        state = app.invoke({})
        if not state or "nom_audio" not in state:
            print("✅ Tous les fichiers audio ont été traités.")
            break
