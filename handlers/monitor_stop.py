from ask_sdk_core.dispatch_components import AbstractRequestHandler
from log_utils import log_info
from handlers.can_handle_base import APLUserEventHandler

class MonitorStopHandler(APLUserEventHandler):
    comandos_validos = {"monitorStop"}

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["monitor_loop"] = False
        session_attr["contexto_atual"] = None

        log_info("[MonitorStop] Encerrando monitoramento.")
        speech = "Monitoramento encerrado. Você pode me pedir outro ativo ou criar um alerta."

        return handler_input.response_builder.speak(speech).set_should_end_session(False).response
