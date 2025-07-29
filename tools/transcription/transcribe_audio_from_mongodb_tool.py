from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pymongo import MongoClient
import gridfs
import tempfile
import os
import google.generativeai as genai
from config import MONGO_URI, API_KEY

# Configuration Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")


class TranscribeAudioInput(BaseModel):
    nom_audio: str = Field(..., description="Nom du fichier audio à transcrire depuis MongoDB (ex: 3.wav)")


@tool(args_schema=TranscribeAudioInput)
def transcribe_audio_from_mongodb(nom_audio: str) -> dict:
    """
    Récupère un fichier audio depuis MongoDB, le transcrit avec Gemini, puis retourne la transcription.
    """
    try:
        # Connexion Mongo + GridFS
        client = MongoClient(MONGO_URI)
        db = client["audioClient"]
        fs = gridfs.GridFS(db, collection="audioClient")

        file_doc = db["audioClient.files"].find_one({"filename": nom_audio})
        if not file_doc:
            return {"error": f"❌ Fichier '{nom_audio}' introuvable dans MongoDB."}

        file_data = fs.get(file_doc["_id"]).read()

        # Créer fichier temporaire WAV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        # Upload + Prompt transcription
        uploaded_file = genai.upload_file(path=temp_path)
        prompt = [
            uploaded_file,
            "Transcris fidèlement cet enregistrement audio entre un client et un agent Orange Maroc. Utilise les balises 'Client:' et 'Agent:' uniquement si possible."
        ]

        response = model.generate_content(prompt)

        # Supprimer le fichier temporaire
        os.remove(temp_path)

        return {
            "nom_audio": nom_audio,
            "transcription": response.text.strip()
        }

    except Exception as e:
        return {"error": f"❌ Erreur Gemini : {str(e)}"}
