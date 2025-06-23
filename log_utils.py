import logging
import datetime
import requests
import os

DEBUG_MODE = False  # Defina como False para ocultar logs de debug

class LogtailSafeHandler(logging.Handler):
    def __init__(self, source_token, endpoint=None):
        super().__init__()
        self.source_token = source_token
        self.endpoint = endpoint or "https://s1357375.eu-nbg-2.betterstackdata.com"  # seu endpoint
        self.session = requests.Session()

    def emit(self, record):
        try:
            msg = self.format(record)
            payload = {
                "dt": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "message": msg
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.source_token}"
            }
            self.session.post(self.endpoint, json=payload, headers=headers, timeout=2)
        except Exception as e:
            print("⚠️ Falha ao enviar log para Logtail:", e)

# logger global embutido
LOG_LOGTAIL_KEY = os.getenv("LOG_LOGTAIL_KEY")
logger = logging.getLogger("skill")
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

formatter = logging.Formatter("[%(levelname)s] — %(name)s: %(message)s")#, %(asctime)s - "%Y-%m-%d %H:%M:%S")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if LOG_LOGTAIL_KEY:
    logtail_handler = LogtailSafeHandler(source_token=LOG_LOGTAIL_KEY)
    logtail_handler.setFormatter(formatter)
    logger.addHandler(logtail_handler)
    logger.info("✅ Logtail ativado com sucesso!")
else:
    logger.warning("⚠️ LOG_LOGTAIL_KEY ausente — sem envio externo de logs.")

# 🎯 Configura também o logger raiz (root logger) para capturar logging.info()
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

# Console handler para o root logger
root_console_handler = logging.StreamHandler()
root_console_handler.setFormatter(formatter)
root_logger.addHandler(root_console_handler)

# Logtail handler para o root logger
if LOG_LOGTAIL_KEY:
    root_logtail_handler = LogtailSafeHandler(source_token=LOG_LOGTAIL_KEY)
    root_logtail_handler.setFormatter(formatter)
    root_logger.addHandler(root_logtail_handler)
    logging.info("✅ Root logger conectado ao Logtail com sucesso!")
else:
    logging.warning("⚠️ Root logger sem Logtail — apenas saída local")

# funções utilitárias

def log_debug(msg):
    if DEBUG_MODE:
        logger.debug(f"🧪 {msg}")

def log_info(msg):
    logger.info(f"ℹ️ {msg}")

def log_warning(msg):
    logger.warning(f"⚠️ {msg}")

def log_error(msg):
    logger.error(f"🛑 {msg}")

def log_intent_event(handler_input, detalhe=""):
    try:
        intent = handler_input.request_envelope.request.intent.name
        user_id = handler_input.request_envelope.context.system.user.user_id
        logger.info(f"🧠 Intent: {intent} | Usuário: {user_id} | {detalhe}")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao logar evento de intent: {e}")