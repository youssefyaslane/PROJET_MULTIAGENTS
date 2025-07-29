from langchain_core.tools import tool

@tool
def send_email_alert_tool(message: str) -> str:
    """Envoie un email d’alerte à l’équipe si une situation critique est détectée."""
    print(f"📧 ALERTE EMAIL envoyée : {message}")
    # Ici tu peux brancher un vrai envoi SMTP ou SendGrid, ou Twilio SendGrid API
    return "Email d’alerte envoyé"
