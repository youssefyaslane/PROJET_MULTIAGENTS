from langchain_core.tools import tool
from pymongo import MongoClient

@tool
def list_audio_not_transcribed(_=None) -> dict:
    """
    Liste les fichiers audio non encore transcrits dans la base MongoDB.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        
        # Récupérer les noms des fichiers audio
        fs_files = client["audioClient"]["audioClient.files"]
        audio_files = []
        for doc in fs_files.find({"filename": {"$exists": True}}):
            if doc.get("filename"):
                audio_files.append(doc["filename"])
        
        # Récupérer les noms des fichiers déjà transcrits
        transcripts = client["audioTranscripts"]["audioTranscripts"]
        transcribed_files = []
        for doc in transcripts.find():
            # Vérifier les deux champs possibles
            filename = doc.get("filename") or doc.get("nom_audio")
            if filename:
                transcribed_files.append(filename)
        
        # Trouver les non transcrits
        not_transcribed = [f for f in audio_files if f not in transcribed_files]
        
        if not_transcribed:
            return {"audios_non_transcrits": not_transcribed}
        else:
            return {"message": "Tous les fichiers audio sont déjà transcrits."}
            
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}