# can_handle_base.py

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type
import logging
    
class APLUserEventHandler(AbstractRequestHandler):
    comandos_validos = set()

    def extra_conditions(self, handler_input) -> bool:
        return True  # padrão: não filtra nada extra

    def can_handle(self, handler_input):
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            args = handler_input.request_envelope.request.arguments
            if args and args[0] in self.comandos_validos:
                return self.extra_conditions(handler_input)
        return False
