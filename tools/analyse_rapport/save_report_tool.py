from langchain_core.tools import tool
from pymongo import MongoClient
from datetime import datetime

@tool
def save_report_tool(content: str) -> str:
    """
    Sauvegarde un rapport Markdown dans MongoDB une seul fois.
    Stocke aussi la date et le nombre de lignes dans le contenu.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["analyseAppels"]
        collection = db["rapportsExploratoires"]

        nb_lignes = content.count("\n")
        document = {
            "date": datetime.utcnow().isoformat(),
            "rapport_markdown": content,
        }

        collection.insert_one(document)
        return "✅ Rapport exploratoire sauvegardé dans MongoDB."

    except Exception as e:
        return f"❌ Erreur lors de l'enregistrement dans MongoDB : {str(e)}"
