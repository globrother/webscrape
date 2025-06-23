import logging
import datetime
import requests
import os

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
