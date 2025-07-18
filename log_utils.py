import logging
import datetime
import requests
import json
import os

DEBUG_MODE = True  # Defina como False para ocultar logs de debug

# Enviar Alertas de Cota para o Telegram
def enviar_para_telegram(mensagem):
    TELEGRAM_ALERT_KEY = os.getenv("TELEGRAM_ALERT_KEY")
    TELEGRAM_ALERT_ID = os.getenv("TELEGRAM_ALERT_ID")

    if not TELEGRAM_ALERT_KEY or not TELEGRAM_ALERT_ID:
        log_warning("⚠️ Telegram não configurado")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_ALERT_KEY}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_ALERT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
        
    try:
        resp = requests.post(url, json=payload, timeout=3)
        log_info(F"Status:{resp.status_code}")
        if resp.status_code != 200:
            log_error(f"❌ Falha Telegram: {resp.status_code} - {resp.text}")
    except Exception as e:
        log_error(f"Erro ao enviar para Telegram: {e}")

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
            # Envia log para o BetterStack (Logtail)
            self.session.post(self.endpoint, json=payload, headers=headers, timeout=2)
            
        except Exception as e:
            print("⚠️ Falha ao enviar log para Logtail:", e)

# logger global embutido
LOG_LOGTAIL_KEY = os.getenv("LOG_LOGTAIL_KEY")
logger = logging.getLogger("skill")
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

formatter = logging.Formatter("[%(levelname)s] %(module)s.%(funcName)s: %(message)s")#%(name)s:, %(asctime)s - "%Y-%m-%d %H:%M:%S")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

raw_formatter = logging.Formatter("%(message)s")
raw_handler = logging.StreamHandler()
raw_handler.setFormatter(raw_formatter)

logger_raw = logging.getLogger("telegram_raw")
logger_raw.setLevel(logging.INFO)
logger_raw.addHandler(raw_handler)
logger.propagate = False

if LOG_LOGTAIL_KEY:
    logtail_handler = LogtailSafeHandler(source_token=LOG_LOGTAIL_KEY)
    logtail_handler.setFormatter(formatter)
    logger.addHandler(logtail_handler)
    logger.info("✅ Logtail ativado com sucesso!")
else:
    logger.warning("⚠️ LOG_LOGTAIL_KEY ausente — sem envio externo de logs.")

# funções utilitárias
def log_debug(msg):
        logger.debug(f"🧪 {msg}", stacklevel=2) #stacklevel=2 para inserir localização do log

def log_info(msg):
    #logger.info(f"ℹ️ {msg}")
    logger.findCaller(stack_info=False)  # opcional
    logger.info(f"ℹ️ {msg}", stacklevel=2)

def log_warning(msg):
    logger.warning(f"⚠️ {msg}")

def log_error(msg):
    logger.error(f"🛑 {msg}", stacklevel=2)

def log_telegram(msg):
    logger_raw.info(f"{msg}")
    # Se contiver o marcador, envia para o Telegram
    if "Gobs-Finance" in msg and "TGAR" in msg or "BBAS" in msg or "PETR" in msg or "BEES" in msg:
        log_warning("⚠️ Enviando alerta financeiro para Telegram")
        enviar_para_telegram(f"🚨 {msg}")

def log_intent_event(handler_input, detalhe=""):
    try:
        intent = handler_input.request_envelope.request.intent.name
        user_id = handler_input.request_envelope.context.system.user.user_id
        logger.info(f"🧠 Intent: {intent} | {detalhe}") # | Usuário: {user_id}
    except Exception as e:
        logger.warning(f"⚠️ Erro ao logar evento de intent: {e}")

def log_session_state(handler_input, contexto=""):
    try:
        session_attr = handler_input.attributes_manager.session_attributes
        session_str = json.dumps(session_attr, ensure_ascii=False)
        logger.info(f"🗂️ Sessão atual {f'({contexto})' if contexto else ''}: {session_str}")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao registrar estado da sessão: {e}")
