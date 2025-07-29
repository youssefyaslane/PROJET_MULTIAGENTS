from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pymongo import MongoClient
from typing import List

class SaveAnalysisInput(BaseModel):
    nom_audio: str = Field(..., description="Nom du fichier audio analysé")
    client_type: str
    client_anciennete: str
    client_ville: str
    categorie_appel: str
    description_appel: str
    equipement_concerne: str
    urgence_perçue: str
    intention_desabonnement: str
    type_intervention_support: List[str]
    résolution_statut_support: str
    commentaire_support: str
    motif_principal: str
    niveau_risque_churn: str
    opportunite_commerciale: str
    résumé: str

@tool(args_schema=SaveAnalysisInput)
def save_analysis_tool(**kwargs) -> dict:
    """
    Enregistre directement l’analyse complète en base MongoDB (collection analyseAppels).
    Empêche les doublons basés sur nom_audio.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        collection = client["analyseAppels"]["analyseAppels"]

        nom_audio = kwargs.get("nom_audio")
        if collection.find_one({"nom_audio": nom_audio}):
            return {
                "status": "skip",
                "message": f"⏭️ Analyse déjà existante pour : {nom_audio}"
            }

        collection.insert_one(kwargs)
        return {
            "status": "ok",
            "message": f"✅ Analyse sauvegardée avec succès pour : {nom_audio}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Erreur MongoDB : {str(e)}"
        }
