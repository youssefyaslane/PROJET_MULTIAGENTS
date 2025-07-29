import os
from pymongo import MongoClient
import gridfs

# === Connexion à MongoDB ===
client = MongoClient("mongodb://localhost:27017/")
db = client["audioClientBase"]
fs = gridfs.GridFS(db)

# === Dossier racine à parcourir ===
root_dir = r"C:\Users\HP\Desktop\speech_to_text\data\mbu_10_08_24 16_47_00"

# === Parcours récursif ===
for dirpath, dirnames, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith(".mp3"):
            full_path = os.path.join(dirpath, file)
            relative_path = os.path.relpath(full_path, root_dir)

            with open(full_path, "rb") as f:
                # Vérifie si le fichier est déjà stocké (évite les doublons)
                if not fs.exists({"filename": relative_path}):
                    fs.put(
                        f,
                        filename=relative_path,
                        metadata={
                            "dossier_parent": os.path.basename(os.path.dirname(full_path)),
                            "nom_fichier": file
                        }
                    )
                    print(f"[✅] Fichier stocké : {relative_path}")
                else:
                    print(f"[⚠️] Fichier déjà existant : {relative_path}")
