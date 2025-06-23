"""
============================:: FINANCE_GOBIS ::============================
==========================:: FUNDOS IMOBILIÁRIOS ::=========================
Essa é a aplicação principal (app.py) que integra os fundos imobiliários monitorados pela skill Finance_Gobis da Alexa.
A aplicação é um servidor Flask que recebe uma solicitação POST de um webhook e responde com um JSON.
O JSON contém as informações de atualização dos fundos imobiliários monitorados pela skill.
A aplicação ainda não é capaz de lidar com solicitações de eventos de usuário da Alexa com eficiencia,
mas ao tocar em um botão, a skill é encerrada.
"""
# ::== AJUDA ==::
# PARA CADA FII QUE DESEJA MONITORAR:
# NÃO SE ESQUEÇA DE CRIAR UM ARQUIVO apl_nome_do_fii.json (pasta raiz)
# IMPORTAR FUNÇÕES get_xxxx DOS FUNDOS ADICIONADOS EM app.py
# DUPLICAR UM ARQUIVO DE FUNDO: nome-do-fii.py (pasta raiz)
# ALTERAR O NOME DA FUNÇÃO get_xxxx E TODAS AS VARIÁVEIS DO ARQUIVO nome-do-fundo.py
# ADICIONAR OS INICIALIZADORES DE HANDLERS: show_xxxxx_screen_handler = ShowXxxxxScreenHandler()
# ADICIONAR OS HANDLERS AO SkillBuilder: sb.add_request_handler(show_xxxxx_screen_handler)

# import locale
import time
from datetime import datetime
import pytz
import re  # Regex substituir ultimos caracteres numéricos
import os
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import (
    is_request_type, get_supported_interfaces, is_intent_name,  get_slot_value)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SendEventCommand, SetValueCommand)
from ask_sdk_model.dialog.dynamic_entities_directive import DynamicEntitiesDirective
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model import SessionEndedRequest, IntentRequest
# from typing import Dict, Any

#from infofii import get_dadosfii
from logtail import LogtailHandler
from log_utils import LogtailSafeHandler  # se estiver num arquivo separado
from utils import state_asset_mapping
from can_handle_base import APLUserEventHandler
from alert_service import tratar_alerta
from scraper import web_scrape
import grava_historico
# ============================================================================================

# LEMBRE-SE DE IMPORTAR AS FUNÇÕES get_xxxx DOS FUNDOS ADICIONADOS
# LEMBRE-SE DE CARREGAR OS DOCUMENTOS APL JSON ACIMA.
# ADICIONAR UM NOVO BLOCO (3 LINHAS) PARA ALTERAR DOCUMENTO APL DO FUNDO ADICIONADO: TROCAR apl_document_xxxx E AS OUTRAS 3 VARIÁVEIS
# DEVE-SE ADICIONAR UMA NOVA LINHA DEFININDO O CARD DO FUNDO: TROCAR voz_xxxxxx e card_xxxxxx PELO NOME DO FUNDO.

# ==========:: CONFIGURAÇÃO DO LOGGER ::==========

# =================================================

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
import logging
from log_utils import log_debug, log_info, log_warning, log_error, log_intent_event, log_session_state

# Para uso dos logs já configurados como root: logging.info("")
"""if not DEBUG_MODE:
    logging.basicConfig(level=logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")

    if LOG_LOGTAIL_KEY:
        root_handler = LogtailSafeHandler(source_token=LOG_LOGTAIL_KEY)
        root_handler.setFormatter(formatter)
        root_logger.addHandler(root_handler)

"""
# ============================================================================

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

time.sleep(1)

app = Flask(__name__)

log_debug("✅ APLICATIVO DA CARTEIRA FINANCEIRA INICIADO COM SUCESSO!")

# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

# Mapeamento de Estados e Fundos
"""state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()
logging.info(f"\n O Mapa é: {state_asset_mapping}")"""

# time.sleep(5)
# logging.info(f"\n A lista é: {lista_ativos}")

# Dicionário para letras em extenso (português)
letras_extenso = {
    "a": "a",
    "b": "bê",
    "c": "cê",
    "d": "dê",
    "e": "é",
    "f": "éfe",
    "g": "gê",
    "h": "agá",
    "i": "i",
    "j": "jóta",
    "k": "cá",
    "l": "éle",
    "m": "ême",
    "n": "êne",
    "o": "ó",
    "p": "pê",
    "q": "quê",
    "r": "érre",
    "s": "ésse",
    "t": "tê",
    "u": "u",
    "v": "vê",
    "w": "dáblio",
    "x": "xis",
    "y": "ípsilon",
    "z": "zê"
}

ativos_favoritos = [1, 2, 3, 4]

"""def remover_sufixo_numerico(codigo):
    # Remove qualquer sequência de dígitos no final do código
    return re.sub(r'\d+$', '', codigo, flags=re.IGNORECASE)"""

def limpar_fund_name(raw):
    if not raw:
        return None
    raw = str(raw).lower()
    raw = re.sub(r'\s|\.', '', raw)     # Remove espaços e pontos
    raw = re.sub(r'\d+$', '', raw)      # Remove números no final
    return raw

def gerar_sinonimos(fundo):
    # normaliza tudo em minúsculas
    base = fundo.strip().lower()
    letras = list(base)
    # 1) Sigla contínua
    contigua = base
    # 2) Sigla separada por espaço: "k n c r"
    separado = " ".join(letras)
    # 3) Sigla com pontos: "k.n.c.r"
    pontuada = ". ".join(letras)
    # 4) Sigla com pontos em maiúsculas: "K.N.C.R"
    pontuada_upper = pontuada.upper()
    # 5) Sigla com pontos em minusculas: 'k. n. c. r.'
    pontuada_literal = ". ".join(letras) + "."
    # 6) Letras por extenso: "kê ene cê erre"
    extenso = " ".join([letras_extenso.get(l, l) for l in letras])
    # Monta um set pra evitar duplicatas e retorna como lista
    return list({contigua, separado, pontuada, pontuada_upper, pontuada_literal, extenso})

def get_dynamic_entities_directive():
    fundos = [limpar_fund_name(v) for v in state_asset_mapping.values()]
    entities = [
        {
            "id": fundo,
            "name": {"value": fundo},
            "synonyms": gerar_sinonimos(fundo)
        } for fundo in fundos
    ]
    return DynamicEntitiesDirective(
        update_behavior="REPLACE",
        types=[
            {
                "name": "FUNDO_TYPES_xxxx",
                "values": entities
            }
        ]
    )

# Carrega documentos APL da pasta principal
def _load_apl_document(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # print(f"Content of {file_path}: {content}")
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

voz_xpml11 = voz_mxrf11 = voz_xplg11 = voz_btlg11 = voz_kncr11 = voz_knri11 = None

# ============================================================================================
"""# Faz a comparação do valor da cota com o valor para o alerta de preço.
def comparador(historico, cota_atual, voz_fundo):
    # Verificar se o histórico é válido e contém pelo menos um registro
    if historico and isinstance(historico, list) and len(historico) >= 1:
        alert_value = historico[0].get("valor", "").replace("R$ ", "")
        logging.info(f"Valor do Alerta: {alert_value}")
        logging.info(f"Valor Atual da Cota: {cota_atual}")

        # Verificar se o valor do alerta é válido
        if alert_value:
            try:
                alert_value_float = float(alert_value.replace(',', '.'))
                cota_atual_float = float(cota_atual.replace(',', '.'))
                #logging.info(f"Valor de alert_value_float: {alert_value_float}")
                #logging.info(f"Valor de cota_atual_float: {cota_atual_float} \n")

                # Comparar os valores e adicionar aviso de fala se necessário
                if cota_atual_float <= alert_value_float:
                    voz_fundo += f"\n<break time='900ms'/>Aviso!<break time='500ms'/> Alerta de preço da cota atingido em ({cota_atual})!<break time='500ms'/> Repito, Alerta de preço atingido."
            except ValueError as e:
                logging.error(f"Erro ao converter valores para float: {e}")
    else:
        logging.info("\n Histórico está vazio ou não é uma lista válida \n")

    return voz_fundo
"""
# ===============::::: SESSÃO WEBSCRAPE :::::===============
"""def web_scrape(fundo):
    # extrai os caracteres numéricos de fundo
    fundo_fii = limpar_fund_name(fundo)
    doc_apl = "apl_fii.json"  # f"apl_{fundo_fii}.json"
    # Carregar APL padrão de exibiçaõ dos fundos
    apl_document = _load_apl_document(doc_apl)
    # Adiciona a geração do texto do histórico de alertas
    sufixo = f"alert_value_{fundo_fii}"
    historico = grava_historico.ler_historico(sufixo)
    aux = "alert"
    hist_alert = grava_historico.gerar_texto_historico(historico, aux)
    # logging.info(f"\n Recuperando hist_alert_xpml da sessão: {hist_alert} \n")

    fii = fundo
    #logging.info(f"valor de fii: {fii}")
    
    # 🔹 Obtendo Url do Gráfico
    url_grafico = obter_grafico.requisitando_chart(fii)
    timestamp = int(time.time() // 3600)  # 🔹 Atualiza a cada hora
    url_grafico = f"{url_grafico}&v={timestamp}" if "?" in url_grafico else f"{url_grafico}?v={timestamp}" # verifica se já tem ? e atribui
    #logging.info(f"URL do Gráfico: {url_grafico}")

    # Lista de links de imagens de planos de fundo
    background_images = [
        "https://lh5.googleusercontent.com/d/1-A_3cMBv-0E1o4RAzMjf8j31q2IKj3e5",
        "https://lh5.googleusercontent.com/d/1-9P8D-AJCsH6-S2ZSmSURlT8aGDGcgV4",
        "https://lh5.googleusercontent.com/d/1-Eeo6Kr7MQQ1MTAtFnrYynkaqaDrU_LW",
        "https://lh5.googleusercontent.com/d/1-8MRaljDqQKt6IlhTtlcKcEsFKO6psqF",
        "https://lh5.googleusercontent.com/d/1-Eeo6Kr7MQQ1MTAtFnrYynkaqaDrU_LW",
        "https://lh5.googleusercontent.com/d/1-CUhhgJDaGaTMJL6Ss0hdFENPb07F1FU"
    ]

    # Determina o índice do fundo atual com base no ID do estado
    fundo_index = next(
        (key for key, value in state_asset_mapping.items() if value == fundo), None)

    if fundo_index is not None:
        logging.info(f"Índice do fundo '{fundo}': {fundo_index}")
    else:
        logging.error(f"Fundo '{fundo}' não encontrado no mapeamento de estados.")
        # Define um índice padrão (primeiro fundo) ou tome outra ação apropriada
        fundo_index = 1
        logging.info(f"Usando índice padrão: {fundo_index}")

    # Seleciona a imagem de fundo correspondente ao índice
    background_image = background_images[(
        fundo_index - 1) % len(background_images)]
    # logger.info(f"O link da imagem de fundo é: {background_image}")

    # ,_ significa que a variável variac_xpml11 não será utilizada
    cota_fii, card_fii, variac_fii, hist_text_fii, logo_url_atv = get_dadosfii(fii)

    voz = card_fii.replace('<br>', '\n<break time="500ms"/>')

    cota_atual = cota_fii
    voz_fundo = voz
    voz = comparador(historico, cota_atual, voz_fundo)

    # DIVIDE O HISTÓRICO EM DUAS COLUNAS
    #logging.info(f"hist_text_FII é: {hist_text_fii}")
    meio = len(hist_text_fii) // 2  # Divide a lista ao meio
    hist_text_ativo_col1 = hist_text_fii[:meio]  # Primeira metade da lista
    hist_text_ativo_col2 = hist_text_fii[meio:]   # Segunda metade da lista
    #logging.info(f"COl2 é: {hist_text_ativo_col2}")

    dados_info = {
        "card_ativo": card_fii,
        "variac_ativo": variac_fii,
        "hist_text_ativo_col1": hist_text_ativo_col1,
        "hist_text_ativo_col2": hist_text_ativo_col2,
        "hist_alert": hist_alert,
        "background_image": background_image,
        "logo_url_atv": logo_url_atv,
        "url_grafico": url_grafico
    }

    return dados_info, card_fii, variac_fii, hist_text_fii, apl_document, voz
"""
# ============================================================================================

# ====================::::: CLASSES E INTENTS DA SKILL ALEXA :::::====================

# HANDLER INICIAL DA SKILL, EXIBE PRIMEIRO ATIVO
class LaunchRequestHandler(AbstractRequestHandler):
    # ::::: 1 :::::
    log_info("Iniciando a skill")
    log_debug("Agora no Handler LaunchRequest")
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.add_directive(get_dynamic_entities_directive())
        session_attr = handler_input.attributes_manager.session_attributes

        # Defina os intervalos em que os favoritos devem ser exibidos
        intervalos_favoritos = [
            (8, 10),   # das 9h às 10h (inclusive 9, exclusivo 10)
            (12, 13),  # exemplo: das 13h às 14h
            (15, 16),
            (17, 18),
            (19, 21),
            (21, 24),
            (00, 8)
            # adicione outros intervalos conforme desejar
        ]

        # Exemplo: exibir só favoritos durante o dia
        # hora = datetime.now().hour
        hora = int(datetime.now(brt_tz).strftime("%H"))

        # Função para verificar se a hora está em algum intervalo
        def intervalos_exibe(hora, intervalos):
            return any(inicio <= hora < fim for inicio, fim in intervalos)

        if intervalos_exibe(hora, intervalos_favoritos):
            ativos_ids = ativos_favoritos[:]
            session_attr["exibir_favoritos"] = True
        else:
            ativos_ids = sorted(state_asset_mapping.keys())
            session_attr["exibir_favoritos"] = False

        session_attr["ativos_ids"] = ativos_ids

        log_debug("=== LaunchRequestHandler.handle ===")
        #log_info(f"Hora: {hora}")
        log_info(f"intervalos_favoritos: {intervalos_favoritos}")
        log_info(f"ativos_ids definidos: {ativos_ids}")

        # Exibe o primeiro ativo
        session_attr["state"] = ativos_ids[0]
        log_info(f"state inicial: {session_attr['state']}")
        fundo = state_asset_mapping[ativos_ids[0]]
        dados_info, _, _, _, apl_document, voz = web_scrape(fundo)

        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="mainScreenToken",
                document=apl_document,
                datasources={
                    "dados_update": {
                        **dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                    }
                }
            )
        )

        # Só fala se não for favoritos
        if not session_attr.get("exibir_favoritos"):
            handler_input.response_builder.speak(
                f"<break time='1s'/>Aqui estão as atualizações financeiras:<break time='1s'/>\n{voz}"
            )

        # **Avance o estado para o próximo fundo antes de agendar autoNavigate**
        session_attr["state"] = ativos_ids[1] if len(ativos_ids) > 1 else None

        # Agende navegação automática
        handler_input.response_builder.add_directive(
            ExecuteCommandsDirective(
                token="mainScreenToken",
                commands=[
                    SendEventCommand(
                        arguments=["autoNavigate"], delay=10000
                    )
                ]
            )
        )

        return handler_input.response_builder.set_should_end_session(False).response
# ============================================================================================

# ADICIONANDO NOVO ATIVO AO MAPEAMENTO map_ativo
class NovoAtivoUserEventHandler(APLUserEventHandler):
    comandos_validos = {
        "siglaAtivo",
        "nomeAtivo",
        "confirmarCadastro",
        "cancelarCadastro"
    }
    log_debug("Agora no Handler LaunchRequest")

    """def can_handle(self, handler_input):
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            arguments = handler_input.request_envelope.request.arguments
            return arguments and (
                arguments[0] == "siglaAtivo" or
                arguments[0] == "nomeAtivo" or
                arguments[0] == "confirmarCadastro" or
                arguments[0] == "cancelarCadastro"
            )
        return False
"""
    def handle(self, handler_input):
        global state_asset_mapping, lista_ativos
        session_attr = handler_input.attributes_manager.session_attributes
        arguments = handler_input.request_envelope.request.arguments

        if arguments[0] == "siglaAtivo":
            session_attr["novo_ativo_sigla"] = arguments[1].strip().lower()
            speech_text = "Agora, digite o nome completo do ativo."
            handler_input.response_builder.speak(speech_text).ask(
                speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "nomeAtivo":
            session_attr["novo_ativo_nome"] = arguments[1].strip()
            speech_text = "Se os dados estiverem corretos, toque em Cadastrar para finalizar."
            handler_input.response_builder.speak(speech_text).ask(
                speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "cancelarCadastro":
            session_attr.pop("novo_ativo_sigla", None)
            session_attr.pop("novo_ativo_nome", None)
            session_attr["manual_selection"] = True
            session_attr["state"] = 2  # ou o state que desejar voltar

            # Volta para o primeiro fundo, ou outro desejado
            fundo = state_asset_mapping[1]
            dados_info, _, _, _, apl_document, voz = web_scrape(fundo)
            handler_input.response_builder.speak(
                "Cadastro cancelado. Voltando para a tela inicial. <break time='700ms'/>" + voz
            ).add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={
                        "dados_update": {
                            **dados_info  # 🔹 Agora o APL pode acessar esse valor (** expande o dicionário)
                        }
                    }
                )
            ).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "confirmarCadastro":
            sigla = session_attr.get("novo_ativo_sigla")
            nome = session_attr.get("novo_ativo_nome")
            if not sigla or not nome:
                handler_input.response_builder.speak("Erro ao cadastrar Ativo. Tente novamente.").ask(
                    "Por favor, digite novamente.").set_should_end_session(False)
                return handler_input.response_builder.response

            # Validação: sigla já existe?
            _, lista_ativos = grava_historico.carregar_ativos()
            siglas_existentes = [f['codigo'].lower() for f in lista_ativos]
            if sigla in siglas_existentes:
                handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} já está cadastrado!").set_should_end_session(False)
                return handler_input.response_builder.response

            # Gerar novo state_id
            state_ids = [f['state_id'] for f in lista_ativos]
            novo_state_id = max(state_ids) + 1 if state_ids else 1

            novo_ativo = {
                "state_id": novo_state_id,
                "codigo": sigla,
                "nome": nome,
                "apelido": limpar_fund_name(sigla).upper(),
                "ativo": True
            }
        grava_historico.adicionar_ativo(novo_ativo)

        # Limpar cache de ativos
        grava_historico._ativos_cache = None
        grava_historico._ativos_cache_time = 0

        # Recarregue o mapeamento após adicionar o novo ativo
        state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()

        # Feedback imediato e avanço de tela
        fundo = state_asset_mapping[novo_state_id]
        dados_info, _, _, _, apl_document, voz = web_scrape(fundo)
        log_info(json.dumps(apl_document, indent=2, ensure_ascii=False))

        session_attr["manual_selection"] = True # Desativa a navegaçaõ automática
        session_attr["state"] = 1 # Estado da Sessão para primeira página

        handler_input.response_builder.speak(
            f"O ativo {sigla.upper()} foi cadastrado com sucesso! Agora exibindo o fundo {fundo}. <break time='1s'/>{voz}"
        ).add_directive(
            RenderDocumentDirective(
                token="mainScreenToken",  # token para exibição de fundos
                document=apl_document,
                datasources={
                    "dados_update":
                        dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                }
            )
        ).set_should_end_session(False)
        return handler_input.response_builder.response
# ============================================================================================

# HANDLER PARA ADICIONAR NOVO ATIVO (carregando página de entrata de dados)
class AddAtivoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler AddAtivoIntent")
        return is_intent_name("AddAtivoIntent")(handler_input)

    def handle(self, handler_input):
        apl_document = _load_apl_document("apl_add_ativo.json")
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="addAtivoToken",
                document=apl_document
            )
        ).speak("Digite a sigla e o nome completo do novo ativo.").ask("Por favor, digite a sigla do novo ativo.").set_should_end_session(False)
        return handler_input.response_builder.response
# ============================================================================================

# HANDLER PARA CRIAR UM ALERTA DE PREÇO.
class CreatePriceAlertIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler CreatePriceAlertIntent")
        if not is_intent_name("CreatePriceAlertIntent")(handler_input):
            return False  # corta logo se não é a intent certa
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request

        # Bloqueia alerta de preço se seleção estiver ativo
        if isinstance(request, IntentRequest):
            asset_name = request.intent.slots.get("fundName").value if request.intent.slots.get("fundName") else None
            if session_attr.get("select_in_progress") and not asset_name:
                log_warning("🛑 Seleção em andamento, fundName ausente. Bloqueando CreatePriceAlertIntent.")
                return False

        return is_intent_name("CreatePriceAlertIntent")(handler_input)
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["contexto_atual"] = "alerta_preco"
        slots = handler_input.request_envelope.request.intent.slots

        result = tratar_alerta(session_attr, slots)

        builder = handler_input.response_builder
        # Tratar cada ação
        if result["action"] == "ask_fund":
            return builder.speak(result["speech"]).ask(result["reprompt"]).response

        if result["action"] == "ask_value":
            return builder.speak(result["speech"]).ask(result["reprompt"]).response

        if result["action"] == "show_apl":
            for d in result.get("directives", []):
                builder.add_directive(d)
            return builder.speak(result["speech"]).response

        if result["action"] == "create":
            for d in result.get("directives", []):
                builder.add_directive(d)
            return builder.speak(result["speech"]).set_should_end_session(False).response

        # fallback seguro
        speech = "Desculpe, não entendi. Pode tentar novamente?"
        return builder.speak(speech).ask(speech).response
# ============================================================================================

# HANDLER PARA TRATAR ENTRADA DE DADOS DO ALERTA DE PREÇOS
class AlertaInputHandler(APLUserEventHandler):
    # verifique comandos_validos em can_handle_base.py para mais detalhes 
    comandos_validos = {
        "siglaAlerta",
        "valorAlerta",
        "confirmarAlerta",
        "cancelarAlerta"
    }

    log_debug("Agora no Handler AlertaInput")

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        arguments = handler_input.request_envelope.request.arguments

        if arguments[0] == "siglaAlerta":
            session_attr["sigla_alerta"] = arguments[1].strip().lower()
            speech_text = "Agora, digite o valor ."
            handler_input.response_builder.speak(speech_text).ask(
                speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "valorAlerta":
            session_attr["AlertValue"] = arguments[1]
            valor = session_attr.get("AlertValue")
            log_info(f"O valor é: {valor}")
            speech_text = "Se os dados estiverem corretos, toque em Cadastrar para finalizar."
            handler_input.response_builder.speak(speech_text).ask(
                speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "cancelarAlerta":
            session_attr.pop("sigla_alerta", None)
            session_attr.pop("AlertValue", None)
            session_attr["alert_in_progress"] = False
            session_attr["manual_selection"] = True
            session_attr["state"] = 2  # ou o state que desejar voltar

            # Volta para o primeiro fundo, ou outro desejado
            fundo = state_asset_mapping[1]
            dados_info, _, _, _, apl_document, voz = web_scrape(fundo)
            handler_input.response_builder.speak(
                "Cadastro cancelado. Voltando para a tela inicial. <break time='700ms'/>"
            ).add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={
                        "dados_update": {
                            **dados_info  # 🔹 Agora o APL pode acessar esse valor (** expande o dicionário)
                        }
                    }
                )
            ).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "confirmarAlerta":
            sigla = session_attr.get("sigla_alerta")
            valor = session_attr.get("AlertValue")
            log_info(f"O valor de Sigla e Valor são: {sigla}::{valor}")
            if not sigla or not valor:
                log_info("Erro ao cadastrar Ativo")
                handler_input.response_builder.speak("Erro ao cadastrar Ativo. Tente novamente.").ask(
                    "Por favor, digite novamente.").set_should_end_session(False)
                return handler_input.response_builder.response

            # Validação: sigla já existe?
            allowed_funds = [limpar_fund_name(v) for v in state_asset_mapping.values()]
            sigla_normalizada = limpar_fund_name(sigla)

            if sigla_normalizada not in allowed_funds:
                handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} não está cadastrado! Tente outro ativo").set_should_end_session(False)
                return handler_input.response_builder.response
            
            else:
                log_info("Direcionando para Processar Cadastro...")
                return CreatePriceAlertIntentHandler().processar_cadastro(handler_input)  # Reutiliza a lógica de gravação
# ============================================================================================

# HANDLER DE NAVEGAÇÃO AUTOMÁTICA PELOS ATIVOS
class DynamicScreenHandler(AbstractRequestHandler):
    def __init__(self, state_asset_mapping):
        self.state_asset_mapping = state_asset_mapping

    def can_handle(self, handler_input):
        log_debug("Agora no Handler DynamicScreen")
        session_attr = handler_input.attributes_manager.session_attributes
        log_session_state(handler_input, "session_attr no início")
        request_type = handler_input.request_envelope.request.object_type
        log_debug(f"DynamicScreenHandler: Tipo de solicitação recebido: {request_type}")

        # Bloqueia IntentRequests (evita que outros intents sejam processados incorretamente)
        if is_request_type("IntentRequest")(handler_input):
            log_info("DynamicScreenHandler: Rejeitando IntentRequest!")
            return False

        # Bloqueia navegação se alerta de preço estiver ativo
        if session_attr.get("alert_in_progress") or session_attr.get("manual_selection"):
            log_info("DynamicScreenHandler: Alertas ativos. Pausando navegação automática.")
            return False

        # Permite apenas eventos de auto-navegação
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            arguments = handler_input.request_envelope.request.arguments
            if arguments and arguments[0] == "autoNavigate":
                log_warning("DynamicScreenHandler acionado para evento autoNavigate.")
                return True

        log_warning("DynamicScreenHandler ignorado para eventos de toque ou intent errado.")
        return False

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        ativos_ids = session_attr.get(
            "ativos_ids", sorted(self.state_asset_mapping.keys()))
        exibir_favoritos = session_attr.get("exibir_favoritos", False)
        current_state = session_attr.get(
            "state", ativos_ids[0])  # Estado inicial padrão é 1

        log_info("=== DynamicScreenHandler.handle ===")
        log_info(f"ativos_ids: {ativos_ids}")
        #log_info(f"exibir_favoritos: {exibir_favoritos}")
        log_info(f"current_state: {current_state}")
        log_session_state(handler_input, "Atributos da sessão")

        # Garante que tipos são iguais (tudo int ou tudo str)
        ativos_ids = [int(a) for a in ativos_ids]
        try:
            current_state = int(current_state)
        except Exception:
            current_state = ativos_ids[0]

        try:
            idx = ativos_ids.index(current_state)
        except ValueError:
            idx = 0

        log_info(f"ativos_ids: {ativos_ids}")
        log_info(f"current_state: {current_state}")
        log_info(f"idx: {idx}")
        log_info(f"idx (posição do fundo atual): {idx}")
        fundo = self.state_asset_mapping[ativos_ids[idx]]
        log_info(f"Fundo selecionado: {fundo}")

        # Obtenha o fundo atual do mapeamento
        fundo = self.state_asset_mapping[ativos_ids[idx]]
        # Chame a função web_scrape para obter os dados do fundo
        dados_info, _, _, _, apl_document, voz = web_scrape(fundo)

        # Calcula o próximo estado
        next_idx = idx + 1 if idx + 1 < len(ativos_ids) else None
        if next_idx is not None:
            session_attr["state"] = ativos_ids[next_idx]
            log_info(f"Avançando para o próximo state: {session_attr['state']}")
        else:
            session_attr["state"] = None
            log_info("Último ativo exibido, encerrando ciclo.")
            log_info(f"Novo state definido: {session_attr['state']}")

        # Construa a resposta
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="mainScreenToken",
                document=apl_document,
                datasources={
                    "dados_update": {
                        **dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                    }
                }
            )
        )

        # Só fala se não for favoritos
        if not exibir_favoritos:
            handler_input.response_builder.speak(f"<break time='1s'/>\n{voz}")

        # Se houver um próximo estado, agende a navegação automática.
        session_attr.pop("manual_selection", None)
        if next_idx is not None:
            log_info("Agendando próximo autoNavigate.")
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="mainScreenToken",
                    commands=[
                        SendEventCommand(
                            # Aguarda 10 segundos antes de navegar
                            arguments=["autoNavigate"], delay=10000
                        )
                    ]
                )
            )

            return handler_input.response_builder.set_should_end_session(False).response
        else:
            # Último ativo: encerre a skill de forma amigável
            log_info("Encerrando skill após o último ativo.")
            if not exibir_favoritos:
                handler_input.response_builder.speak(
                    f"<break time='1s'/>{voz}<break time='10s'/>Encerrando a skill. Até a próxima!"
                )
            # Se for favoritos, não fala nada!
            return handler_input.response_builder.set_should_end_session(True).response
# ============================================================================================

# HANDLER PARA MOSTRAR FUNDO SOLICITADO
class SelectFundIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler SelectFundInput")
        return is_intent_name("SelectFundIntent")(handler_input) or \
               is_intent_name("AMAZON.NextIntent")(handler_input)

    def handle(self, handler_input):
        #handler_input.response_builder.add_directive(get_dynamic_entities_directive())
        session_attr = handler_input.attributes_manager.session_attributes
        intent_name = handler_input.request_envelope.request.intent.name
        session_attr["contexto_atual"] = "selecao_ativo"
        session_attr["select_in_progress"] = True
        log_info(f"Intent recebido: {intent_name}")

        intent = handler_input.request_envelope.request.intent
        slots = intent.slots
        fund_name = slots.get("fundName").value #if slots.get("fundName") else None
        log_intent_event(handler_input, f"🧠 Slot raw: {slots['fundName'].value}")
        log_info(f"🎙️ fund_name captado: {repr(fund_name)}")
        log_intent_event(handler_input, f"SelectFundIntentHandler acionado. Slots recebidos: {slots}")

        resolutions = slots["fundName"].resolutions
        if resolutions and resolutions.resolutions_per_authority:
           for authority in resolutions.resolutions_per_authority:
                if authority.status.code == "ER_SUCCESS_MATCH" and authority.values:
                    for value in authority.values:
                        resolved_id = value.value.id
                        log_info(f"🎯 Resolvido como ID: {resolved_id}")

        allowed_funds = [limpar_fund_name(v) for v in state_asset_mapping.values()]

        #directive = get_dynamic_entities_directive()
        #log_info(f"/n 📦 Entidades dinâmicas carregadas: {json.dumps(directive.to_dict(), ensure_ascii=False, indent=2)}/n")
        #handler_input.response_builder.add_directive(directive)

        if intent_name == "AMAZON.NextIntent":
            session_attr.pop("manual_selection", None)
            speech_text = "Continuando a navegação pelos ativos."
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="mainScreenToken",
                    commands=[
                        SendEventCommand(arguments=["autoNavigate"], delay=0)
                    ]
                )
            ).speak(speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        # Tentativa de reconhecimento por voz
        tentativas = session_attr.get("tentativas_fundo", 0)

        if not fund_name:
            session_attr["tentativas_fundo"] = tentativas + 1
            if tentativas < 2:
                speech = "Desculpe, não entendi o nome do ativo. Tente falar: mostrar ativo segido do nome do ativo sem o número?"
                return handler_input.response_builder.speak(speech).ask(speech).set_should_end_session(False).response
            else:
                session_attr["tentativas_fundo"] = 0
                session_attr["select_in_progress"] = True
                apl_doc = _load_apl_document("apl_select_ativo.json")
                handler_input.response_builder.add_directive(RenderDocumentDirective(
                    token="inputScreenToken", document=apl_doc))
                speech = "Não consegui entender. Por favor, digite o nome do fundo na tela."
                return handler_input.response_builder.speak(speech).set_should_end_session(False).response
        
        sigla_normalizada = limpar_fund_name(fund_name)

        if sigla_normalizada in allowed_funds:
            fundo_full, fundo_state_id = next(
                ((nome, state_id) for state_id, nome in state_asset_mapping.items()
                if limpar_fund_name(nome) == sigla_normalizada),
                (None, None)
            )

            log_info(f"fundo full é: {fundo_full}")

            if not fundo_full:
                return handler_input.response_builder.speak(
                    f"Não consegui localizar o ativo {fund_name.upper()}."
                ).set_should_end_session(False).response

            session_attr.update({
                "state": fundo_state_id,
                "manual_selection": None,
                "current_asset_id": fundo_state_id, # para uso em Alerta de Preço
                "current_asset_name": fundo_full, # para uso em Alerta de Preço
                "select_in_progress": False,
                "manual_selection": False
            })

            try:
                dados_info, _, _, _, apl_doc, voz = web_scrape(fundo_full)
            except Exception as e:
                logging.error(f"Erro no web_scrape para {fundo_full}: {e}")
                return handler_input.response_builder.speak("Ocorreu um erro ao recuperar as informações do ativo."
                ).set_should_end_session(False).response

            speech = f"Mostrando o ativo {fund_name.upper()}."
            handler_input.response_builder.add_directive(RenderDocumentDirective(
                token="mainScreenToken",
                document=apl_doc,
                datasources={
                    "dados_update": dados_info
                }
            )).speak(f"{speech}<break time='500ms'/>{voz}").set_should_end_session(False)
            return handler_input.response_builder.response

        # O ativo não é válido, redireciona para entrada manual
        apl_doc = _load_apl_document("apl_select_ativo.json")
        session_attr["alert_in_progress"] = True
        handler_input.response_builder.add_directive(RenderDocumentDirective(
            token="inputScreenToken", document=apl_doc))
        speech = "Não reconheci esse ativo. Por favor, digite o nome na tela."
        return handler_input.response_builder.speak(speech).set_should_end_session(False).response
# ============================================================================================

# HANDLER PARA TRATAR ENTRADA DE DADOS PARA MOSTRAR FUNDO
class SelectInputHandler(APLUserEventHandler):
    # verifique comandos_validos em can_handle_base.py para mais detalhes 
    comandos_validos = {
        "siglaSelectAtivo",
        "confirmarSelect",
        "cancelarSelect"
    }
    
    log_debug("Agora no Handler SelectInput")

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        arguments = handler_input.request_envelope.request.arguments

        if arguments[0] == "siglaSelectAtivo":
            session_attr["sigla_select_ativo"] = arguments[1].strip().lower()
            speech_text = "Se os dados estiverem corretos, toque em Confirmar para finalizar."
            handler_input.response_builder.speak(speech_text).ask(
                "Você pode confirmar ou corrigir o nome do ativo.").set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "cancelarSelect":
            session_attr.pop("sigla_select_ativo", None)
            session_attr["alert_in_progress"] = False
            session_attr["manual_selection"] = True
            session_attr["state"] = 2  # ou o state que desejar voltar

            # Volta para o primeiro fundo, ou outro desejado
            fundo = state_asset_mapping[1]
            dados_info, _, _, _, apl_document, voz = web_scrape(fundo)
            handler_input.response_builder.speak(
                "Cadastro cancelado. Voltando para a tela inicial. <break time='700ms'/>"
            ).add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={
                        "dados_update": dados_info  # Agora o APL acessa esse valor 
                    } # (o uso de ** expande o dicionário, ex: **{dados_info})
                )
            ).set_should_end_session(False)
            return handler_input.response_builder.response

        if arguments[0] == "confirmarSelect":
            sigla = session_attr.get("sigla_select_ativo")
            log_info(f"O valor de Sigla é: {sigla}")
            
            if not sigla:
                log_warning("Erro ao Mostrar Ativo")
                handler_input.response_builder.speak("Erro ao Mostrar Ativo. Tente novamente.").ask(
                    "Por favor, digite novamente.").set_should_end_session(False)
                return handler_input.response_builder.response

            # Validação: sigla já existe?
            allowed_funds = [limpar_fund_name(v) for v in state_asset_mapping.values()]
            sigla_normalizada = limpar_fund_name(sigla)

            if sigla_normalizada not in allowed_funds:
                handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} não está cadastrado! Tente outro ativo").set_should_end_session(False)
                return handler_input.response_builder.response
            
            # Encontrar fundo completo e ID
            fundo_key = sigla.lower()
            fundo_full = None
            fundo_state_id = None
            for state_id, nome in state_asset_mapping.items():
                if limpar_fund_name(nome) == sigla_normalizada:
                    fundo_full = nome
                    fundo_state_id = state_id
                    break

            if not fundo_full:
                handler_input.response_builder.speak(
                    "Ativo não encontrado. Por favor, tente novamente."
                ).set_should_end_session(False)
                return handler_input.response_builder.response

            # Atualiza sessão
            session_attr.update({
                "state": fundo_state_id,
                "manual_selection": None,
                "current_fund_id": fundo_state_id, # para uso em Alerta de Preço
                "current_fund_name": fundo_full, # para uso em Alerta de Preço
                "select_in_progress": False,
                "manual_selection": False
            })

            dados_info, _, _, _, apl_document, voz = web_scrape(fundo_full)
            speech_text = f"Mostrando o ativo {sigla.upper()}."

            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={
                        "dados_update": dados_info
                    }
                )
            ).speak(f"{speech_text}<break time='500ms'/>{voz}").set_should_end_session(False)

            return handler_input.response_builder.response
# ============================================================================================

class TouchHandler(APLUserEventHandler):
    comandos_validos = {"touch"}
    log_debug("Agora no Handler Touch de toque na tela")

    def __init__(self, state_asset_mapping):
        self.state_asset_mapping = state_asset_mapping

    """def can_handle(self, handler_input):

        #request_type = handler_input.request_envelope.request.object_type
        #log_info(f"TouchHandler: Tipo de solicitação recebido: {request_type}")

        #def can_handle(self, handler_input):
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            arguments = handler_input.request_envelope.request.arguments
            log_info(f"TouchHandler: Argumentos recebidos: {arguments}")
            
            # Filtrar apenas eventos de toque
            return arguments and len(arguments) > 0 and arguments[0] == "touch"
        
        return False"""

    def handle(self, handler_input):
        log_info("TouchHandler: handle chamado.")
        # Recupera os atributos de sessão
        session_attr = handler_input.attributes_manager.session_attributes
        current_state = session_attr.get("state", 1)

        # Verifica se o estado atual está no mapeamento
        if current_state not in self.state_asset_mapping:
            # Se o estado não for encontrado, reinicia para o primeiro estado
            current_state = 1

        # Obtenha o fundo atual do mapeamento
        fundo = self.state_asset_mapping[current_state]

        # Verifica se é o último estado
        if current_state == 1:
            voz_prefix = "Recomeçando!"
            # next_state = "firstScreen"  # Reinicia para o primeiro estado
        else:
            voz_prefix = "Próximo!"

        # Chama a função web_scrape para obter os dados do fundo
        dados_info, _, _, _, apl_document, voz = web_scrape(fundo)

        # Calcula o próximo estado
        next_state = current_state + 1 if current_state + 1 in state_asset_mapping else None

        # Atualiza o estado para o próximo
        session_attr["state"] = next_state

        # Constrói a resposta
        handler_input.response_builder.speak(f"{voz_prefix}<break time='1s'/>\n{voz}").add_directive(
            RenderDocumentDirective(
                token="mainScreenToken",
                document=apl_document,
                datasources={
                    "dados_update": dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                }
            )
        )

        # Define o próximo estado na sessão
        handler_input.attributes_manager.session_attributes = session_attr

        return handler_input.response_builder.set_should_end_session(False).response
# ============================================================================================

# ============================================================================================

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler SessionEndedRequest")
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        request = handler_input.request_envelope.request
        session_attr = handler_input.attributes_manager.session_attributes

        log_intent_event(handler_input, "📌 SessionEndedRequestHandler acionado.")

        # Coleta motivo e detalhes do encerramento
        reason = getattr(request, "reason", "Motivo não informado")
        error = getattr(request, "error", None)
        if error:
            logging.error(f"💥 Detalhes do erro: {error}")
            # Tenta acessar campos específicos com segurança
            if hasattr(error, "type"):
                logging.error(f"🔎 Tipo: {error.type}")
            if hasattr(error, "message"):
                logging.error(f"📝 Mensagem: {error.message}")

        request = handler_input.request_envelope.request
        if hasattr(request, "reason"):
            log_warning(f"Motivo do fim da sessão: {request.reason}")

        log_info(f"📦 Atributos de sessão no encerramento: {session_attr}")

        # Você pode usar isso para métricas ou análises futuras
        if reason == "ERROR" and error:
            logging.debug("🔧 Erro interno detectado. Pode ter sido uma exceção silenciosa em outro handler.")

        # Mantém a sessão como 'não finalizada', caso algo esteja escutando
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response
# ============================================================================================

# ============================================================================================

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler FallbackIntent")
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        log_intent_event(handler_input, "FallbackIntent acionado. Redirecionando conforme o contexto.")

        if isinstance(request, SessionEndedRequest):
            log_warning(f"Motivo do fim da sessão: {request.reason}")

        apl_document = None
        session_attr = handler_input.attributes_manager.session_attributes
        contexto_atual = session_attr.get("contexto_atual", "desconhecido")

        if contexto_atual == "alerta_preco":
            apl_document = _load_apl_document("apl_add_alerta.json")
            speech_text = "Desculpe não entendi o nome do fundo. Por favor,  digite manualmente na tela."

        elif contexto_atual == "selecao_ativo":
            apl_document = _load_apl_document("apl_select_ativo.json")
            speech_text = "Não consegui entender o nome do ativo. Digite manualmente na tela."
        
        elif contexto_atual == "cadastro_ativo":
            apl_document = _load_apl_document("apl_add_ativo.json")
            speech_text = "Não consegui entender o nome do ativo. Digite manualmente na tela."

        elif contexto_atual == "auto_navegacao":
            speech_text = "Desculpe, não entendi. Diga 'próximo' para avançar ou 'favoritos' para ver seus ativos favoritos."
            apl_document = None  # 🔹 Não precisa abrir um APL específico

        else:
            speech_text = "Não consegui entender sua solicitação. Você pode tentar novamente ou encerrar a Skill."

        response_builder = handler_input.response_builder.speak(speech_text).set_should_end_session(False)

        if apl_document is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="inputScreenToken",
                    document=apl_document
                )
            )

        return response_builder.response
# ============================================================================================

"""
    Aqui eu peço o encerramento da skill caso nenhum handler seja capaz de lidar com a solicitação.
    dessa forma ao tocar sobre o botão de voltar, a skill será encerrada, pois não implementei nenhum
    método para essa solicitação.
"""
class CatchAllRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler CatchAllRequest")
        log_info("🔍 CatchAllRequestHandler: Verificando requisição não tratada.")
        return True  # aceita qualquer solicitação que não casou com outros handlers

    def handle(self, handler_input):
        request = handler_input.request_envelope.request
        session_attr = handler_input.attributes_manager.session_attributes
        contexto = session_attr.get("contexto_atual")
        apl_document = None

        log_warning(f"⚠️ Nenhum handler específico capturou esta requisição. Tipo: {request.object_type}")
        
        # 🔒 Tratamento especial para User Touch Event fantasma
        if request.object_type == "Alexa.Presentation.APL.UserEvent":
            arguments = getattr(request, "arguments", [])
            if arguments and arguments[0] == "touch":
                log_warning("[CatchAll] UserEvent de toque 'touch' ignorado como evento fantasma.")
                return handler_input.response_builder.response  # ignora silenciosamente
        
        if isinstance(request, IntentRequest):
            intent_name = request.intent.name
            log_warning(f"📌 Intent inesperada recebida: {intent_name}")
        else:
            log_warning("📌 Requisição não foi do tipo IntentRequest.")

        # Respostas contextuais
        if contexto == "alerta_preco":
            apl_document = _load_apl_document("apl_add_alerta.json")
            speech = "Desculpe, não entendi o nome do fundo. Por favor, digite na tela."

        elif contexto == "selecao_ativo":
            apl_document = _load_apl_document("apl_select_ativo.json")
            speech = "Não consegui entender. Você pode falar: mostrar ativo seguido do nome do ativo sem o número, ou digitar na tela."

        elif contexto == "cadastro_ativo":
            apl_document = _load_apl_document("apl_add_ativo.json")
            speech = "Não reconheci o ativo que você mencionou. Tente digitar manualmente."

        elif contexto == "auto_navegacao":
            speech = "Desculpe, não entendi. Diga 'próximo' para continuar ou 'favoritos' para ver sua lista."
            apl_document = None

        else:
            speech = "Hmm, não consegui entender o que você quis dizer. Encerrando por agora, mas você pode me chamar de novo quando quiser."
            log_warning("🚪 Encerrando sessão por ausência de contexto.")
            return handler_input.response_builder.speak(speech).set_should_end_session(True).response

        if apl_document:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(token="fallbackToken", document=apl_document)
            )

        log_info(f"🎤 Resposta de fallback gerada com contexto: {contexto}")
        return handler_input.response_builder.speak(speech).ask(speech).set_should_end_session(False).response

# ============================================================================================
# ============================================================================================

@app.route('/webscrape', methods=['POST'])
def webhook():
    data = request.get_json()

    # Inicialize o SkillBuilder
    sb = SkillBuilder()

    # Inicialize os handlers com card_fii
    launch_request_handler = LaunchRequestHandler()
    create_price_alert_intent_handler = CreatePriceAlertIntentHandler()
    alerta_input_handler = AlertaInputHandler()
    add_ativo_intent_handler = AddAtivoIntentHandler()
    novo_ativo_usesevent_handler = NovoAtivoUserEventHandler()
    dynamic_screen_handler = DynamicScreenHandler(state_asset_mapping)
    touch_handler = TouchHandler(state_asset_mapping)
    select_fund_intent_handler = SelectFundIntentHandler()
    select_input_handler = SelectInputHandler()
    session_ended_request_handler = SessionEndedRequestHandler()
    fall_back_intent_handler = FallbackIntentHandler()
    catch_all_request_handler = CatchAllRequestHandler()

    # go_back_handler = GoBackHandler()

    # Adicione os handlers ao SkillBuilder
    sb.add_request_handler(launch_request_handler)
    sb.add_request_handler(create_price_alert_intent_handler)
    sb.add_request_handler(alerta_input_handler)
    sb.add_request_handler(add_ativo_intent_handler)
    sb.add_request_handler(novo_ativo_usesevent_handler)
    sb.add_request_handler(dynamic_screen_handler)
    sb.add_request_handler(touch_handler)
    sb.add_request_handler(select_fund_intent_handler)
    sb.add_request_handler(select_input_handler)
    sb.add_request_handler(session_ended_request_handler)
    sb.add_request_handler(fall_back_intent_handler)
    sb.add_request_handler(catch_all_request_handler)

    # sb.add_request_handler(go_back_handler)

    # Gere a resposta
    response = sb.lambda_handler()(data, None)
    return jsonify(response)

if __name__ == '__main__':
    log_info("\n Iniciando o servidor Flask...\n")
    # logging.basicConfig(level=logging.DEBUG) # Habilita debug logging
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
