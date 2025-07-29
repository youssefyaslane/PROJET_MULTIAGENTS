from langchain_core.tools import tool
from pydantic import BaseModel, Field
from twilio.rest import Client
from pymongo import MongoClient
from config import TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM

# ✅ Initialisation des clients au niveau module (une seule fois)
try:
    twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
    client_mongo = MongoClient("mongodb://localhost:27017/")
    col_audio_infos = client_mongo["audioClient"]["audioInfos"]
    print("✅ Clients Twilio et MongoDB initialisés avec succès")
except Exception as e:
    print(f"❌ Erreur initialisation clients: {e}")

# ✅ Définition du schéma d'entrée
class SendSMSInput(BaseModel):
    nom_audio: str = Field(..., description="Nom du fichier audio traité")
    sms_text: str = Field(..., description="Texte du SMS à envoyer au client")

@tool(args_schema=SendSMSInput)
def send_sms_tool(nom_audio: str, sms_text: str) -> str:
    """
    Envoie un SMS via Twilio et met à jour MongoDB avec le statut 'sms': 'done'.
    Le numéro du client est récupéré depuis MongoDB à partir du nom du fichier audio.
    """
    try:
        print(f"🔍 Recherche du document pour: {nom_audio}")
        
        # 📄 Recherche du document
        doc = col_audio_infos.find_one({"nom_audio": nom_audio})
        if not doc:
            error_msg = f"❌ Aucun document trouvé avec nom_audio = {nom_audio}"
            print(error_msg)
            return error_msg

        num = doc.get("num")
        if not num:
            error_msg = f"❌ Numéro de téléphone manquant pour {nom_audio}"
            print(error_msg)
            return error_msg

        # ✅ Vérification si SMS déjà envoyé
        if doc.get("sms") == "done":
            warning_msg = f"⚠️ SMS déjà envoyé pour {nom_audio}."
            print(warning_msg)
            return warning_msg

        print(f"📲 Tentative d'envoi SMS à {num}")
        print(f"📝 Contenu: {sms_text}")

        # 📲 Envoi du SMS
        message = twilio_client.messages.create(
            body=sms_text,
            from_=TWILIO_FROM,
            to=num
        )

        print(f"✅ SMS envoyé avec succès, SID: {message.sid}")

        # 💾 Mise à jour MongoDB
        update_result = col_audio_infos.update_one(
            {"nom_audio": nom_audio},
            {"$set": {
                "sms": "done",
                "sms_text": sms_text,
                "sms_sid": message.sid
            }}
        )

        if update_result.modified_count > 0:
            success_msg = f"✅ SMS envoyé à {num} pour {nom_audio} et base mise à jour."
            print(success_msg)
            return success_msg
        else:
            warning_msg = f"⚠️ SMS envoyé mais erreur mise à jour base pour {nom_audio}"
            print(warning_msg)
            return warning_msg

    except Exception as e:
        error_msg = f"❌ Erreur lors de l'envoi du SMS : {str(e)}"
        print(error_msg)
        return error_msg