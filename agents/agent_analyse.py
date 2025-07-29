from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from config import API_KEY

# 🔧 Tool personnalisé
from tools.analyse.save_analysis_tool import save_analysis_tool
from langsmith.run_helpers import traceable


# 🔁 Modèle Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    google_api_key=API_KEY,
    temperature=0.3
)

# 🧰 Liste des tools
tools = [save_analysis_tool]

# 💾 Mémoire interne
memory = MemorySaver()

# agent analyse
agent_executor = create_react_agent(
    llm,
    tools,
    checkpointer=memory
)

# 🚀 Lancer l’analyse pour un fichier précis
@traceable(name="AgentAnalyseOrange", tags=["analyse", "orange"])
def run_analysis(nom_audio: str, transcription: str):
    print("🧠 Agent Analyse lancé...")

    messages = [
        HumanMessage(content=f"""
Tu es un assistant d’analyse d’appel client pour Orange Maroc.

Voici la transcription du fichier audio "{nom_audio}" :

\"\"\"{transcription}\"\"\"

Génère un JSON structuré comme suit :

{{
  "nom_audio": nom du fichier audio (ex: "2.wav"),  // très important pour le suivi

  "client_type": "particulier" si le client parle de ses services personnels (mobile, internet maison, etc.), 
                 "professionnel" si l’appel concerne une entreprise ou une activité pro,
                 sinon "inconnu" s’il n’y a pas assez d’indices,

  "client_anciennete": "<6mois" si le client mentionne être nouveau, 
                       "6mois-2ans" s’il indique une durée modérée, 
                       ">2ans" s’il dit être client de longue date, 
                       sinon "inconnu",

  "client_ville": choisir parmi "Casablanca", "Rabat", "Marrakech", "Agadir" si explicitement mentionnée, 
                  sinon "autre" pour une autre ville, ou "non mentionnée" si rien n’est dit,

  "categorie_appel": catégorise selon le motif principal de l’appel :
                     - "technique" pour problèmes de connexion, réseau, panne, débit
                     - "facturation_paiement" pour montants, retards, prélèvements, facture incomprise
                     - "forfaits_offres" pour demandes sur les prix, promotions, changement de forfait
                     - "information" si le client cherche juste des infos générales
                     - "réclamation" si le ton est insatisfait ou le client exprime une plainte
                     - "résiliation" si le client parle d’annuler un service ou quitter Orange
                     - "service_mobile" pour activation, portabilité, problèmes SIM, recharge
                     - "autre" si aucun des cas précédents ne s’applique clairement

  "description_appel": une phrase courte résumant l’appel (1 à 2 phrases max, ton neutre),

  "equipement_concerne": déduire à partir de l’appel : "routeur", "mobile", "ligne_fixe", "carte_sim", 
                         sinon "aucun" s’il n’est pas question de matériel, ou "inconnu" si incertain,

  "urgence_perçue": 
                    - "haute" si le client est agacé, en détresse ou demande une action rapide
                    - "moyenne" si l’appel est sérieux mais sans signe de colère
                    - "basse" si le client est calme, veut juste des infos ou une simple explication,

  "intention_desabonnement": 
                    - "oui" si le client évoque quitter Orange, résilier ou aller vers un concurrent,
                    - "non" s’il ne montre aucun signe de rupture,
                    - "incertain" s’il hésite ou évoque des insatisfactions sans décision claire,

  "type_intervention_support": liste des actions faites ou promises pendant l’appel :
                    ["explication", "transfert_technique", "diagnostic", "activation_service", 
                    "désactivation_service", "confirmation", "ticket_créé", "aucune"],
                    Sélectionner toutes les actions pertinentes,

  "résolution_statut_support": 
                    - "résolu" si le problème est traité avec satisfaction,
                    - "en_attente" si une action future est prévue ou un ticket ouvert,
                    - "non_résolu" si le client reste insatisfait ou sans solution,

  "commentaire_support": résumer objectivement la réaction et l’attitude du support, sans émotion,

  "motif_principal": formuler clairement en une phrase le besoin ou le problème exprimé par le client,

  "niveau_risque_churn": 
                    - "élevé" si le client est en colère, exprime des menaces de départ,
                    - "modéré" s’il est insatisfait mais encore ouvert à discussion,
                    - "faible" si l’appel est purement informatif ou que le client est satisfait,

  "opportunite_commerciale": 
                    - "oui" si le client demande à changer de forfait, ajoute un service, 
                      ou manifeste un intérêt pour des offres,
                    - "non" sinon,

  "résumé": phrase finale résumant tout l’appel (1 phrase synthétique).
}}

Envoie ensuite ce JSON au tool `save_analysis_tool` pour l’enregistrer en base MongoDB.
Important : tu dois absolument utiliser le tool `save_analysis_tool` avec le JSON généré, sinon ton travail ne sera pas pris en compte.

""")
    ]



    result = agent_executor.invoke({
    "messages": messages,
    "configurable": {
        "thread_id": f"analyse_{nom_audio}"
    },
    "recursion_limit": 100
})


    print(f"✅ Résultat de l'agent Analyse pour {nom_audio} :\n{result}")
    return result