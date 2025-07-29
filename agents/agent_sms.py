from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tools.sms.send_sms_tool import send_sms_tool
from config import API_KEY

# 🔁 Modèle Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    google_api_key=API_KEY,
    temperature=0.3
)

# 🧰 Tool
tools = [send_sms_tool]
memory = MemorySaver()

# Agent sms
agent_executor = create_react_agent(
    llm,
    tools,
    checkpointer=memory
)


# 🚀 Fonction agent SMS
def run_sms(nom_audio: str, transcription: str):
    print("🧠 Agent SMS lancé...")
    
    try:
        messages = [
            HumanMessage(content=f"""
Tu es un assistant Orange Maroc.

Voici la transcription complète de l'appel lié au fichier audio **{nom_audio}** :

\"\"\"{transcription}\"\"\"

Ta mission est la suivante :

1. **Déduis si un SMS doit être envoyé ou non.**  
   - Si l’appel est simplement une demande d'information (ex: adresse d’agence, horaires, question sur un produit), **n’envoie pas de SMS**.
   - Si l’appel concerne un problème technique, une plainte, une activation, un service ou une action faite par l’agent, **alors génère un SMS clair et professionnel**.

2. Si un SMS est nécessaire, appelle le tool `send_sms_tool` avec ces deux champs :
   - `nom_audio`: "{nom_audio}"
   - `sms_text`: le SMS que tu veux envoyer (1-2 phrases max, ton professionnel).

3. Si aucun SMS n’est nécessaire, réponds simplement :  
```json
{{ "sms": "non_envoye" }}


""")
        ]
        
        

        print(f"📤 Tentative d'envoi SMS pour {nom_audio}...")
        result = agent_executor.invoke({
    "messages": messages,
    "configurable": {
        "thread_id": f"sms_{nom_audio}"
    }
})

        
        print(f"✅ Agent SMS terminé pour {nom_audio}")
        print(f"🔍 Résultat: {result}")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Erreur dans l'agent SMS pour {nom_audio}: {str(e)}"
        print(error_msg)
        return {"error": str(e)}