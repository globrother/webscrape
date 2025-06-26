# can_handle_base.py

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type
import logging
    
class APLUserEventHandler(AbstractRequestHandler):
    comandos_validos = set()

    def extra_conditions(self, handler_input) -> bool:
        # Pode sobrescrever nas subclasses
        return True

    def can_handle(self, handler_input):
        request = handler_input.request_envelope.request

        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            args = request.arguments
            logging.info(f"[APLUserEventHandler] UserEvent recebido: {args}")

            if not args:
                logging.info("[APLUserEventHandler] Ignorado: argumentos ausentes ou vazios.")
                return False

            if args[0] not in self.comandos_validos:
                logging.info(f"[APLUserEventHandler] Ignorado: '{args[0]}' não está em comandos_validos ({self.comandos_validos}).")
                return False

            if not self.extra_conditions(handler_input):
                logging.info("[APLUserEventHandler] Ignorado: falhou em extra_conditions().")
                return False

            logging.info(f"[APLUserEventHandler] Aceitando evento: {args[0]}")
            return True

        return False
