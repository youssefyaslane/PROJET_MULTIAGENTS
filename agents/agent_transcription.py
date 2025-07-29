from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tools.transcription.list_audio_not_transcribed_tool import list_audio_not_transcribed
from tools.transcription.transcribe_audio_from_mongodb_tool import transcribe_audio_from_mongodb
from tools.transcription.save_transcription_tool import save_transcription_tool
from config import API_KEY
import json

# 🔁 Modèle Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    google_api_key=API_KEY,
    temperature=0.3
)

# 🧰 Tools utilisés
tools = [list_audio_not_transcribed, transcribe_audio_from_mongodb, save_transcription_tool]
memory = MemorySaver()

# Agent réactif
agent_executor = create_react_agent(
    llm,
    tools,
    checkpointer=memory
)

# 🔁 Fonction appelée par le TranscriptionAgent dans LangGraph
def run_transcription():
    print("📥 Lancement de l’agent de transcription...")

    messages = [
        HumanMessage(content="""
Transcris les fichiers audio non encore traités et enregistre les résultats.
""")
    ]

    result = agent_executor.invoke({
        "messages": messages,
        "configurable": {
            "thread_id": "transcription_thread"
        }
    })

    print("🧠 Résultat brut de l’agent :")
    print(result)

    # Analyse du résultat brut
    try:
        tool_messages = [msg for msg in result.get("messages", []) if msg.type == "tool"]
        for msg in tool_messages:
            content = msg.content
            if isinstance(content, str) and "nom_audio" in content and "transcription" in content:
                import json
                parsed = json.loads(content)
                return [(parsed["nom_audio"], parsed["transcription"])]
    except Exception as e:
        print("Erreur extraction ToolMessage :", str(e))

    return []
# 🔁 Fonction de transcription pour un seul fichier
def run_transcription_for_one():
    print("📥 Lancement de la transcription d’un fichier audio...")

    messages = [
        HumanMessage(content="""
Tu es un agent chargé de transcrire un appel client.

1. Liste les fichiers audio non encore transcrits.
2. Si aucun fichier n’est disponible, réponds clairement : "Aucun fichier à transcrire."
3. Sinon :
  - Transcris le prochain fichier.
  - Sauvegarde la transcription.
  - Renvoie uniquement ce JSON :
  {
    "nom_audio": "...",
    "transcription": "..."
  }
""")
    ]

    result = agent_executor.invoke({
        "messages": messages,
        "configurable": {
            "thread_id": "transcription_loop"
        }
    })

    print("🧠 Résultat brut de transcription :", result)

    # 🧠 Extraire la réponse du modèle
    try:
        for msg in result.get("messages", []):
            if msg.type == "tool":
                content = msg.content
                if isinstance(content, str) and "nom_audio" in content and "transcription" in content:
                    parsed = json.loads(content)
                    return {
                        "nom_audio": parsed["nom_audio"],
                        "transcription": parsed["transcription"]
                    }

        for msg in result.get("messages", []):
            if "aucun fichier" in msg.content.lower():
                return {}

    except Exception as e:
        print("❌ Erreur parsing transcription :", str(e))

    return {}