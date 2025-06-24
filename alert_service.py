# alerta_service.py
from ask_sdk_model import IntentRequest
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective,
    ExecuteCommandsDirective,
    SendEventCommand
)
from utils import limpar_asset_name, state_asset_mapping, _load_apl_document
from scraper import web_scrape
import grava_historico
from flask import request

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
from log_utils import log_debug, log_info, log_warning, log_error
# =====================================================================

def tratar_alerta(session_attr: dict, slots: dict) -> dict:
    """
    Resultado:
      action:  "ask_value" | "ask_fund" | "show_apl" | "create" | "error"
      speech: texto a ser falado
      reprompt: opcional, texto para reprompt
      directives: opcional, lista de directives APL/Commands
    """
    # Bloqueia alerta de preço se seleção estiver ativo
    if isinstance(request, IntentRequest):
        asset_name = request.intent.slots.get("fundName").value if request.intent.slots.get("fundName") else None
        if session_attr.get("select_in_progress") and not asset_name:
            log_warning("🛑 Seleção em andamento, fundName ausente. Bloqueando CreatePriceAlertIntent.")
            return False

    # -------------------------------------------------------
    # 0) Se não estivermos já no meio de um alerta, limpe tudo
    # -------------------------------------------------------
    # isso garante que SIGLA e ALERTVALUE não fiquem “pendurados”
    if not session_attr.get("alert_in_progress", False):
        session_attr.pop("sigla_alerta", None)
        session_attr.pop("AlertValue", None)

    # -----------------------------------
    # 1) lê os slots de voz
    # -----------------------------------
    alert_value = slots.get("alertValue")
    alert_value = alert_value.value if alert_value else None

    alert_value_cents = slots.get("alertValueCents")
    alert_value_cents = alert_value_cents.value if alert_value_cents else None

    slot_asset = slots.get("fundName")
    slot_asset = slot_asset.value if slot_asset else None

    # -----------------------------------
    # 2) se slot de ativo veio, já salve
    # -----------------------------------
    if slot_asset:
        session_attr["sigla_alerta"] = limpar_asset_name(slot_asset)
        log_info(f"[Service] Slot fundName salvo em sessão: {session_attr['sigla_alerta']}")

    # -----------------------------------
    # 3) recupere a sigla da sessão
    # -----------------------------------
    asset_name = session_attr.get("sigla_alerta")
    # se ainda não tiver, tente APL
    if not asset_name:
        cid   = session_attr.get("current_asset_id")
        cname = session_attr.get("current_asset_name")
        if cid and cname:
            asset_name = limpar_asset_name(cname)
            session_attr["sigla_alerta"] = asset_name
            log_info(f"[Service] Usando ativo atual: {asset_name}")
        else:
            session_attr["alert_in_progress"] = True
            return {
                "action": "ask_fund",
                "speech": "Para qual ativo você quer criar o alerta?",
                "reprompt": "Por favor, diga o nome do ativo."
            }

    # -----------------------------------
    # 4) normalize e valide a sigla
    sigla = asset_name
    ativos_permitidos = [limpar_asset_name(n) for n in state_asset_mapping.values()]
    asset_full, asset_state_id = next(
        ((n, sid)
         for sid, n in state_asset_mapping.items()
         if limpar_asset_name(n) == sigla),
        (None, None)
    )

    # -----------------------------------
    # 5) pergunta/monte o valor
    if "AlertValue" not in session_attr or session_attr["AlertValue"] is None:
        # sem slot de valor
        if not alert_value and not alert_value_cents:
            session_attr["alert_in_progress"] = True
            return {
                "action": "ask_value",
                "speech": "Qual é o valor do alerta em reais e centavos?",
                "reprompt": "Por favor, diga o valor em reais e centavos."
            }

        # monta AlertValue
        if alert_value and alert_value_cents:
            session_attr["AlertValue"] = f"{alert_value},{alert_value_cents}"
        elif alert_value:
            session_attr["AlertValue"] = f"{alert_value},00"
        else:
            session_attr["AlertValue"] = f"0,{alert_value_cents}"

        log_info(f"[Service] AlertValue montado: {session_attr['AlertValue']}")

    # -----------------------------------
    # 6) se sigla inválida, mostra APL
    if sigla not in ativos_permitidos or not asset_full:
        session_attr["alert_in_progress"] = True
        session_attr["manual_selection"]  = True
        apl = _load_apl_document("apl_add_alerta.json")
        return {
            "action": "show_apl",
            "speech": "Não consegui identificar o cadastro desse ativo. Digite manualmente na tela.",
            "directives": [
                RenderDocumentDirective(token="inputScreenToken", document=apl)
            ]
        }

    # -----------------------------------
    # 7) tudo OK, CRIA o alerta
    alert_value = session_attr["AlertValue"]
    key = f"alert_value_{sigla}"
    session_attr[key] = alert_value
    log_info(f"[Service] Salvando alerta: {sigla} → {alert_value}")

    # grava histórico
    valor_formatado = f"R$ {alert_value}"
    grava_historico.gravar_historico(key, valor_formatado)
    historico = grava_historico.ler_historico(key)
    texto_hist = grava_historico.gerar_texto_historico(historico, "alert")
    log_info(f"[Service] Histórico gerado: {texto_hist}")

    # prepara directives de retorno (tela inicial + navegação)
    first_asset = state_asset_mapping[1]
    dados_info, _, _, _, apl_doc, _ = web_scrape(first_asset)
    directives = [
        RenderDocumentDirective(
            token="mainScreenToken",
            document=apl_doc,
            datasources={"dados_update": {**dados_info}}
        ),
        ExecuteCommandsDirective(
            token="mainScreenToken",
            commands=[SendEventCommand(arguments=["autoNavigate"], delay=5000)]
        )
    ]

    # limpa o estado do alerta (incluindo indicador de progresso)
    session_attr["AlertValue"]       = None
    session_attr["alert_in_progress"] = False
    session_attr["manual_selection"]  = False
    session_attr["state"]             = 2

    speech = f"Alerta de preço de {alert_value} criado para o fundo {asset_full}. Voltando à tela inicial."
    return {
        "action":     "create",
        "speech":     speech,
        "directives": directives
    }