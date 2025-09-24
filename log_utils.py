import os
import time
import json
import logging
import datetime
import requests
import threading


from collections import deque
from logging.handlers import RotatingFileHandler


DEBUG_MODE = True  # Defina como False para ocultar logs de debug

fila_prioritaria = deque()
fila_normal = deque()

# Adiciona mensagem na fila apropriada
def adicionar_na_fila(mensagem, nivel="DEBUG"):
    if nivel in ["ERROR", "CRITICAL"]:
        fila_prioritaria.append(mensagem)
    else:
        fila_normal.append(mensagem)
        
# Worker que processa a fila e envia mensagens ao Telegram
def worker_envio_telegram():
    while True:
        if fila_prioritaria:
            msg = fila_prioritaria.popleft()
        elif fila_normal:
            msg = fila_normal.popleft()
        else:
            time.sleep(2)
            continue

        try:
            enviar_para_telegram(msg, chat_id=os.getenv("TELEGRAM_LOG_ID"))
            time.sleep(1)  # respeita limite de 1 msg/s
        except Exception as e:
            log_error(f"Erro no envio da fila: {e}")
            time.sleep(5)


# Enviar Alertas de Cota para o Telegram
def enviar_para_telegram(mensagem, chat_id=None):
    TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
    TELEGRAM_ALERT_ID = os.getenv("TELEGRAM_ALERT_ID")
    TELEGRAM_LOG_ID = os.getenv("TELEGRAM_LOG_ID")

    if not TELEGRAM_KEY:
        logger.warning("⚠️ Bot do Telegram não configurado")
        return

    # Define o destino: se não for passado, usa LOG_ID por padrão
    destino = chat_id or TELEGRAM_LOG_ID

    if not destino:
        logger.warning("⚠️ Nenhum chat_id definido para envio")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage"
    payload = {
        "chat_id": destino,
        "text": mensagem,
        #"parse_mode": "MarkdownV2" #"HTML"
    }

    try:
        resp = requests.post(url, json=payload, timeout=3)
        #logger.info(f"Status Telegram: {resp.status_code}")
        if resp.status_code != 200:
            logger.error(f"❌ Falha Telegram: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"Erro ao enviar para Telegram: {e}")

class TelegramSelectiveHandler(logging.Handler):
    def emit(self, record):
        try:
            if record.levelno != logging.INFO:
                mensagem = self.format(record)
                nivel = record.levelname
                adicionar_na_fila(f"📡 {nivel}: {mensagem}", nivel=nivel)
        except Exception as e:
            log_error(f"Erro no TelegramSelectiveHandler: {e}")

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

# Para salvar LOG em arquivo app.log
LOG_PATH = "/home/ubuntu/app.log"
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5*1024*1024, backupCount=1)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler customizado para enviar logs específicos ao Telegram
telegram_handler = TelegramSelectiveHandler()
telegram_handler.setFormatter(formatter)
logger.addHandler(telegram_handler)

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

# Worker para envio assíncrono de mensagens do Telegram
threading.Thread(target=worker_envio_telegram, daemon=True).start()
