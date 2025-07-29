# tools/transcription/save_transcription_tool.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pymongo import MongoClient
from config import MONGO_URI

class SaveTranscriptionInput(BaseModel):
    filename: str = Field(..., description="Nom du fichier audio, ex: 3.wav")
    transcription: str = Field(..., description="Texte transcrit depuis l'audio")

@tool(args_schema=SaveTranscriptionInput)
def save_transcription_tool(filename: str, transcription: str) -> str:
    """
    Sauvegarde une transcription dans MongoDB (collection audioTranscripts).
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client["audioTranscripts"]
        collection = db["audioTranscripts"]

        # Vérifier si une transcription existe déjà
        existing = collection.find_one({
            "$or": [
                {"filename": filename},
                {"nom_audio": filename}
            ]
        })
        
        if existing:
            return f"❌ Transcription déjà existante pour {filename}."

        # Sauvegarder avec les deux champs pour compatibilité
        doc = {
            "filename": filename,
            "nom_audio": filename,  # Pour compatibilité
            "transcription": transcription
        }
        
        collection.insert_one(doc)
        return f"✅ Transcription sauvegardée pour {filename}."
        
    except Exception as e:
        return f"❌ Erreur lors de la sauvegarde de {filename}: {str(e)}"