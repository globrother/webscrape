from .monitor_refresh import MonitorRefreshHandler
from .monitor_stop import MonitorStopHandler
# Adicione aqui outros handlers personalizados
# from .select_fund import SelectFundIntentHandler
# from .alert_price import CreatePriceAlertIntentHandler

def register_handlers(sb):
    """
    Registra todos os handlers da pasta handlers no SkillBuilder.
    """
    sb.add_request_handler(MonitorRefreshHandler())
    sb.add_request_handler(MonitorStopHandler())
    # Adicione aqui os outros
