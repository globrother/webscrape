from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective, ExecuteCommandsDirective, SendEventCommand
from log_utils import log_info, log_debug, log_warning
from scraper import web_scrape
from datetime import datetime, timedelta

from handlers.can_handle_base import APLUserEventHandler  # <– sua base compartilhada
# ou apenas: from .apl_user_event_base import APLUserEventHandler

class MonitorRefreshHandler(APLUserEventHandler):
    comandos_validos = {"monitorRefresh"}

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes

        # Verifica se o tempo de monitoramento excedeu
        start_str = session_attr.get("monitor_start")
        if start_str:
            start = datetime.fromisoformat(start_str)
            if datetime.now() - start > timedelta(minutes=2):
                session_attr["monitor_loop"] = False
                session_attr["contexto_atual"] = None
                return handler_input.response_builder.speak(
                    "Tempo de monitoramento encerrado."
                ).set_should_end_session(True).response

        # Caso esteja desativado, apenas retorna silenciosamente
        if not session_attr.get("monitor_loop"):
            return handler_input.response_builder.response

        asset_full = session_attr.get("asset_full")
        if not asset_full:
            return handler_input.response_builder.response

        log_info(f"[MonitorRefresh] Recarregando dados para {asset_full}")
        dados_info, _, _, _, apl_document, _ = web_scrape(asset_full)

        handler_input.response_builder.add_directive(RenderDocumentDirective(
            token="mainScreenToken",
            document=apl_document,
            datasources={"dados_update": dados_info}
        ))

        handler_input.response_builder.add_directive(ExecuteCommandsDirective(
            token="mainScreenToken",
            commands=[SendEventCommand(arguments=["monitorRefresh"], delay=60000)]
        ))

        return handler_input.response_builder.set_should_end_session(False).response
