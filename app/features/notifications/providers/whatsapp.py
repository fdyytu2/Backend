from app.core.logging import logger


def send_whatsapp_msg(target: str, message: str):
    # Nanti integrasikan dengan Fonnte/Wablas/mainsms di sini
    logger.info(f"WA SENT to {target}: {message}")
    return True
