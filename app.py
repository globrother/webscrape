"""
============================:: FINANCE_GOBIS ::============================
==========================:: FUNDOS IMOBILIÁRIOS ::=========================
Essa é a aplicação principal (app.py) que integra os fundos imobiliários monitorados pela skill Finance_Gobis da Alexa.
A aplicação é um servidor Flask que recebe uma solicitação POST de um webhook e responde com um JSON.
O JSON contém as informações de atualização dos fundos imobiliários monitorados pela skill.
A aplicação ainda não é capaz de lidar com solicitações de eventos de usuário da Alexa com eficiencia.
"""
# ::== AJUDA ==::
# ADICIONAR OS INICIALIZADORES DE HANDLERS: show_xxxxx_screen_handler = ShowXxxxxScreenHandler()
# ADICIONAR OS HANDLERS AO SkillBuilder: sb.add_request_handler(show_xxxxx_screen_handler)

# import locale
from dotenv import load_dotenv
load_dotenv()
import time
from datetime import datetime
import pytz
import os
import json
import sqlite3
import threading
#import requests
#from bs4 import BeautifulSoup
from flask import Flask, request, send_from_directory, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import (
    is_request_type, get_supported_interfaces, is_intent_name,  get_slot_value)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
#from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SendEventCommand, SetFocusCommand, SetValueCommand)
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model import SessionEndedRequest, IntentRequest
from handlers import register_handlers
# from typing import Dict, Any

from utils import (
    state_asset_mapping,
    limpar_asset_name,
    get_dynamic_entities_directive,
    _load_apl_document,
    iniciar_processamento,
    gerar_todos_os_graficos,
    ativos_favoritos
)
from handlers.can_handle_base import APLUserEventHandler
from alert_service import tratar_alerta
from scraper import web_scrape
import grava_historico
# ============================================================================================

# ====================:: CONFIGURAÇÃO DO LOG ::====================
from log_utils import log_debug, log_info, log_warning, log_error, log_intent_event, log_session_state
# =====================================================================

# ====================:: CONFIGURAÇÕES TOKENS ::=======================
SECRET_TOKEN = os.getenv("API_KEY")
# =====================================================================

# Diretório para servir imagem do gráfico
OUTPUT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cache")
log_info(f"OUTPUT_DIR:{OUTPUT_DIR}")

#criando conexão com o banco SQLite
def conectar_sqlite():
    caminho = os.path.abspath("/home/ubuntu/webscrape/finance.db")
    return sqlite3.connect(caminho)
#def conectar_sqlite():
    #return sqlite3.connect("finance.db")


# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

time.sleep(1)

app = Flask(__name__, static_folder=None) # static_folder=None, desativa a pasta padrão para usar a pasta personalizada /static/

log_info("✅ APLICATIVO DA CARTEIRA FINANCEIRA INICIADO COM SUCESSO!")
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

# log_info(f"\n A lista é: {lista_ativos}")

#ativos_favoritos = [1, 2, 3, 4]

#voz_xpml11 = voz_mxrf11 = voz_xplg11 = voz_btlg11 = voz_kncr11 = voz_knri11 = None

# ====================::::: CLASSES E INTENTS DA SKILL ALEXA :::::====================
"""
    log_info("🔄 Iniciando geração de gráficos em segundo plano...")
    try:
        # 🔹 Consulta os ativos do banco
        conn = conectar_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo FROM ativos WHERE status = True")
        ativos = [row[0] for row in cursor.fetchall()]
        conn.close()

        # 🔹 Gera os gráficos
        graficos_gerados = []
        for ticker in ativos:
            url = requisitando_chart(ticker)
            if url:
                graficos_gerados.append((ticker, url))
                
            log_info(f"✅ Gráfico gerado para {ticker}")
    except Exception as e:
        log_error(f"❌ Erro ao gerar gráficos em segundo plano: {e}")
"""


# HANDLER INICIAL DA SKILL, EXIBE PRIMEIRO ATIVO
class LaunchRequestHandler(AbstractRequestHandler):
    # ::::: 1 :::::
    log_info("Iniciando a skill")
    log_debug("Agora no Handler LaunchRequest")
    
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False
        
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """
        # BLOCO PARA ATUALIZAR GRÁFICOS NA PARTIDA
        # (não é mais necessário, pois foi implementado >
        # > atualizar_graficos_periodicamente() no flask )
        try:
            # 🔹 Consulta os ativos do banco
            conn = conectar_sqlite()
            cursor = conn.cursor()
            cursor.execute("SELECT codigo FROM ativos WHERE status = True")
            ativos = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            log_debug(f"Usando banco em: {os.path.abspath('finance.db')}")
            
            session_attr = handler_input.attributes_manager.session_attributes
            if not session_attr.get("graficos_em_progresso", False):
                session_attr["graficos_em_progresso"] = True
                # 🔹 Dispara a geração de gráficos em segundo plano
                threading.Thread(target=gerar_todos_os_graficos, args=(ativos,)).start()
                
        except Exception as e:
            log_error(f"Erro ao iniciar geração de gráficos em segundo plano: {e}")
         """ 
           
        try:    
            log_info("PASSOU AQUI")
            start_time = time.time()
            
            # Verifica se a sessão está ativa antes de acessar session_attributes
            if not handler_input.request_envelope.session or not handler_input.request_envelope.session.session_id:
                log_warning("Requisição sem sessão ativa! Retornando mensagem amigável.")
                return handler_input.response_builder.speak(
                    "A sessão não está mais ativa. Por favor, inicie novamente."
                ).set_should_end_session(True).response
            
            #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
            #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
            handler_input.response_builder.add_directive(get_dynamic_entities_directive())
            session_attr = handler_input.attributes_manager.session_attributes

            # Defina os intervalos em que os favoritos devem ser exibidos
            intervalos_favoritos = [
                (8, 10),   # das 9h às 10h (inclusive 9, exclusivo 10)
                (11, 12),  # exemplo: das 11h às 12h
                (13, 14),  # exemplo: das 13h às 14h
                (15, 16),
                (17, 18),
                (21, 24),
                (00, 8)
                # adicione outros intervalos conforme desejar
            ]

            # Exemplo: exibir só favoritos durante o dia 1
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
            
            if not ativos_ids:
                log_error("ativos_ids está vazio — não há ativos disponíveis para exibição.")
                return handler_input.response_builder.speak(
                    "Não encontrei ativos disponíveis no momento. Tente novamente mais tarde."
                ).set_should_end_session(True).response
                
            # Garante que IDs realmente existem no state_asset_mapping
            #log_debug(f"ativos_ids antes do filtro: {ativos_ids}")
            #log_debug(f"state_asset_mapping.keys(): {list(state_asset_mapping.keys())}")

            log_debug(f"ativos_ids: {ativos_ids}")
            ativos_ids = [i for i in ativos_ids if i in state_asset_mapping]
            
            log_debug(f"ativos_ids após filtro: {ativos_ids}")

            session_attr["ativos_ids"] = ativos_ids

            #log_debug(f"intervalos_favoritos: {intervalos_favoritos}")
            #log_debug(f"ativos_ids definidos: {ativos_ids}")
            
            # Defina o delay com base em favoritos
            exibir_favoritos = session_attr.get("exibir_favoritos", False)
            if exibir_favoritos:
                delay_ms = 10000  # Favoritos:(10s)
            else:
                delay_ms = 1000  # Regulares:(2s)

            # Exibe o primeiro ativo
            session_attr["state"] = ativos_ids[0]
            log_debug(f"state inicial: {session_attr['state']}")
            fundo = state_asset_mapping[ativos_ids[0]]["codigo"]
            dados_info, _, _, _, apl_document, voz, timeout = web_scrape(fundo)
            
            #log_debug(f"[web_scrape] fundo: {fundo}, apl_document: {apl_document}")
            
            """
            if not apl_document or not isinstance(apl_document, dict) or not apl_document.get("mainTemplate"):
                log_error(f"❌ apl_document inválido ou vazio para fundo {fundo}. Pulando renderização.")
                return handler_input.response_builder.speak(
                    f"O fundo {fundo.upper()} está indisponível no momento. Tente novamente mais tarde."
                ).set_should_end_session(False).response
            """
            
            # GARANTE QUE O TEMPO TOTAL NÃO EXCEDE O TEMPO DA ALEXA DE ~9s
            tempo_processamento = time.time() - start_time
            log_info(f"Tempo de processamento do ativo {fundo}: {tempo_processamento:.2f}s")
            
            # Limite de segurança (ex: 7.5 segundos)
            LIMITE_TIMEOUT = 8.5
            
            # Recupera ou inicializa o contador de tentativas
            tentativas = session_attr.get("tentativas_timeout", 0)
            
            if (timeout or tempo_processamento > LIMITE_TIMEOUT):
                tentativas += 1
                session_attr["tentativas_timeout"] = tentativas
                
                if tentativas >= 5:
                    log_warning("Limite de tentativas de timeout atingido. Encerrando skill.")
                    handler_input.response_builder.speak(
                        "Ocorreu um atraso repetido na atualização dos ativos. Encerrando a skill por agora. Tente novamente mais tarde."
                    )
                    return handler_input.response_builder.set_should_end_session(True).response
                
                # Resposta rápida para evitar timeout
                handler_input.response_builder.speak(
                    f"Estou buscando as informações do ativo {fundo.upper()}, aguarde um momento..."
                )
                # Agende o próximo fundo para manter a navegação automática
                handler_input.response_builder.add_directive(
                    ExecuteCommandsDirective(
                        token="mainScreenToken",
                        commands=[
                            SendEventCommand(arguments=["autoNavigate"], delay=1000)
                        ]
                    )
                )
                return handler_input.response_builder.set_should_end_session(False).response
            else:
                # Zera o contador se processamento foi rápido
                session_attr["tentativas_timeout"] = 0

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
                            arguments=["autoNavigate"], delay=delay_ms
                        )
                    ]
                )
            )

            return handler_input.response_builder.set_should_end_session(False).response
        except Exception as e:
            import traceback
            log_error(f"Erro inesperado no LaunchRequestHandler: {e}")
            print(traceback.format_exc())
            handler_input.response_builder.speak(
                "Ocorreu um erro interno. Encerrando a skill."
            )
            return handler_input.response_builder.set_should_end_session(True).response
# ============================================================================================

# HANDLER PARA ABRIR SKILL DIRETAMENTE EM ALGUM ATIVO
class LaunchIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug("Agora no Handler LaunchIntent")
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False
        
        return is_intent_name("LaunchIntent")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        slots = handler_input.request_envelope.request.intent.slots
        fund_name = slots.get("fundName").value if slots.get("fundName") else None
        #session_attr["contexto_atual"] = "select_in_progress"
        #session_attr["select_in_progress"] = True

        if fund_name:
            log_debug(f"[LaunchIntent] fundo recebido na invocação: {fund_name}")
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr["contexto_atual"] = "select_in_progress"
            session_attr["select_in_progress"] = True
            session_attr["sigla_alerta"] = fund_name
            return SelectFundIntentHandler().handle(handler_input)

        return LaunchRequestHandler().handle(handler_input)
# ============================================================================================
class WakeUpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("WakeUpIntent")(handler_input)

    def handle(self, handler_input):
        # Lógica para acordar o servidor ou atualizar o tempo para a próxima hibernação
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["server_status"] = True
        
        """
        # 🔹 Consulta os ativos do banco
        conn = conectar_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo FROM ativos WHERE status = True")
        ativos = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        log_debug(f"Usando banco em: {os.path.abspath('finance.db')}")
        
        # 🔹 Dispara a geração de gráficos em segundo plano
        threading.Thread(target=gerar_todos_os_graficos, args=(ativos,)).start()
        #hreading.Thread(target=gerar_todos_os_graficos).start()

        # 🔹 Resposta rápida para Alexa
        speech_text = (
            "<speak><prosody volume='x-soft'>O servidor foi acordado. "
            "Os gráficos estão sendo preparados agora em segundo plano.</prosody></speak>"
        )
        """
        
        # Verifica se o servidor está hibernado
        if session_attr.get("server_status"):
            session_attr["server_status"] = "awake"
            # Aqui você pode adicionar lógica para acordar o servidor, se necessário
            speech_text = "<speak><prosody volume='x-soft'>O servidor já estava acordado.</prosody></speak>"
            log_info("O servidor já estava acordado. O tempo para a próxima hibernação foi atualizado")
        else:
            # Atualiza o tempo para a próxima hibernação
            speech_text = "<speak><prosody volume='x-soft'>O servidor foi acordado.</prosody></speak>"

        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response
# ============================================================================================
    
# EXIBIR ATIVO NO MODO MONITOR
class MonitorIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora em MonitorIntentHandler")
        #if not is_intent_name("MonitorIntent")(handler_input):
        #    return False  # corta logo se não é a intent certa
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False
        
        return is_intent_name("MonitorIntent")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        slots = handler_input.request_envelope.request.intent.slots
        fund_name = slots.get("fundName").value if slots.get("fundName") else None
        #session_attr["contexto_atual"] = "select_in_progress"
        #session_attr["select_in_progress"] = True

        if fund_name:
            log_debug(f"[MonitorIntent] fundo recebido na invocação: {fund_name}")
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr["contexto_atual"] = "monitor_in_progress"
            session_attr["select_in_progress"] = True
            session_attr["sigla_alerta"] = fund_name
            return SelectFundIntentHandler().handle(handler_input)

        return LaunchRequestHandler().handle(handler_input)
# ============================================================================================

# ADICIONANDO NOVO ATIVO AO MAPEAMENTO map_ativo
class GerenciarAtivoInputHandler(APLUserEventHandler):
    log_debug("Agora no Handler LaunchRequest")
    comandos_validos = {
        "siglaAtivo",
        "nomeAtivo",
        "confirmarCadastro",
        "cancelarCadastro",
        "excluirAtivo",
        "ativarAtivo",
        "desativarAtivo",
        "executarCadastro",
        "toggleFavorito"
    }
   
    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        global state_asset_mapping, lista_ativos
        session_attr = handler_input.attributes_manager.session_attributes
        arguments = handler_input.request_envelope.request.arguments
        session_attr["contexto_atual"] = "gerenciar_ativo"
        log_debug(f"Argumentos recebidos: {arguments}")
        
        if is_request_type("SessionEndedRequest")(handler_input):
            log_warning("⚠️ Ignorando SessionEndedRequest no GerenciarAtivoInputHandler.")
            return handler_input.response_builder.set_should_end_session(True).response

        # Limpar cache de ativos
        grava_historico._ativos_cache = None
        grava_historico._ativos_cache_time = 0
        
        # -----------------------------------------------
        if arguments[0] == "siglaAtivo":
            session_attr["novo_ativo_sigla"] = arguments[1].strip().lower()
            log_debug(f" Novo ativo sigla: {session_attr['novo_ativo_sigla']}")
            
            # Carrega lista atual e tenta localizar o ativo
            sigla = session_attr.get("novo_ativo_sigla")
            sigla_normalizada = limpar_asset_name(sigla)
            nome = session_attr.get("novo_ativo_nome")
            tipo_acao = session_attr.get("tipo_acao", None)
            log_warning(f"valor de sigla em siglaAtivo: {sigla}")
            
            if not sigla:
                return handler_input.response_builder.speak(
                    "Nenhum ativo preenchido, digite no campo por favor"
                ).set_should_end_session(False).response
            
            _, lista_ativos = grava_historico.carregar_ativos()
            #ativo = next((a for a in lista_ativos if a['codigo'].lower() == sigla), None)
            
            asset_state_id, asset_dict = next(
                (
                    (state_id, dados)
                    for state_id, dados in state_asset_mapping.items()
                    if limpar_asset_name(dados.get("codigo", "")) == sigla_normalizada
                ),
                (None, None)
            )
            session_attr['state'] = asset_state_id
            
            # Esse bloco trata quando o ativo não existe no banco de dados (no cadastro por exemplo)
            fala = ""
            if asset_dict is None:
                status_ativo = False  # ou True, conforme o que faz mais sentido para o seu fluxo
                favorito = False
                
                if tipo_acao == "excluir":
                    fala = f"Ativo {sigla.upper()} excluído com sucesso."
                    sigla = None
                    nome = None
                    session_attr.pop("novo_ativo_sigla", None)
                    session_attr.pop("novo_ativo_nome", None)
                    session_attr.pop("tipo_acao", None)
                else:
                    fala = f"O ativo {sigla.upper()} não foi encontrado. Se preferir, toque em cadastrar para incluir o ativo em sua lista."
            else:
                status_ativo = asset_dict.get("status", True)
                favorito = asset_dict.get("favorite", False)
            
            #status_ativo = ativo.get("status", True)  # True = ativo, False = inativo
            #favorito = ativo.get("favorite", False)
            
            apl_document = _load_apl_document("apl_gerenciar_ativo.json")
            dados_update = {
                "statusAtivo": "ATIVO" if status_ativo else "INATIVO",
                "desativarAtivoDisabled": not status_ativo,   # Desativa botão se já estiver inativo
                "ativarAtivoDisabled": status_ativo,          # Desativa botão se já estiver ativo
                "corBotaoAtivar": "gray" if status_ativo else "#009d52", # Ativar só fica verde se está inativo
                "corBotaoDesativar": "#ff692e" if status_ativo else "gray",  # Desativar só fica verde se está ativo
                "corTextoAtivar": "#717171" if status_ativo else "#ffffff", # Ativar só fica verde se está inativo
                "corTextoDesativar": "#ffffff" if status_ativo else "#717171",  # Desativar só fica verde se está ativo
                "iconeFavorito": "https://lh5.googleusercontent.com/d/1u6F9Xo6ZmbnvB6i4HUwwRHo7PnhWF75A" if favorito else "https://lh5.googleusercontent.com/d/1VdPwoILeWcirEuvmmt-pkvkmfRqYNA0F",
                "corFavorito": "gold" if favorito else "gray",
                "acaoFavorito": "removerFavorito" if favorito else "adicionarFavorito",
                "siglaAtivo": sigla,
                "nomeAtivo": nome
            }
            
            if not asset_dict:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="GerenciarAtivoToken",
                        document=apl_document,
                        datasources={
                            "dados_update": dados_update
                        }
                    )
                ).speak(fala).set_should_end_session(False)
                return handler_input.response_builder.response

            favorito_atual = asset_dict.get("favorite", False)
            fala_favorito = (
                "adicionado aos favoritos" if favorito_atual else "removido dos favoritos"
            )
            
            novo_status = asset_dict.get("status", False)
            #novo_status = True if arguments[0] == "ativarAtivo" else False
            log_debug(f"🔁 Novo status: {novo_status}")
            fala_status = "ativado" if novo_status else "desativado"
            
            session_attr = handler_input.attributes_manager.session_attributes
            #session_attr["manual_selection"] = True
            #apl_document = _load_apl_document("apl_gerenciar_ativo.json")
            # Recupera o tipo de ação da sessão
            log_debug(f"Valor de session_attr['tipo_acao']: {session_attr.get('tipo_acao')}")
            # Define o texto de fala conforme o tipo de ação
            if tipo_acao == "status":
                fala = f"O ativo {sigla.upper()} foi {fala_status} com sucesso."
            elif tipo_acao == "favorite":
                fala = f"O ativo {sigla.upper()} foi {fala_favorito} com sucesso."
            #elif tipo_acao == "excluir":
                #fala = f"O ativo {sigla.upper()} foi excluído com sucesso."
            else:
                fala = "Ao finalizar escolha uma opção."
            
            session_attr.update({"tipo_acao": None})
            #session_attr["tipo_acao"] = None

            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="GerenciarAtivoToken",
                    document=apl_document,
                    datasources={
                        "dados_update": dados_update
                    }
                )
            ).speak(fala).set_should_end_session(False)
            return handler_input.response_builder.response

        # -----------------------------------------------
        if arguments[0] in ["ativarAtivo", "desativarAtivo"]:
            session_attr["acao_status"] = True if arguments[0] == "ativarAtivo" else False
            session_attr["tipo_acao"] = "status"
            
            sigla = session_attr.get("novo_ativo_sigla")

            if not sigla:
                return handler_input.response_builder.speak(
                    "Nenhum ativo selecionado para alteração de status."
                ).set_should_end_session(False).response

            _, lista_ativos = grava_historico.carregar_ativos()
            ativo = next((a for a in lista_ativos if a['codigo'].lower() == sigla), None)

            if not ativo:
                return handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} não foi encontrado."
                ).set_should_end_session(False).response

            state_id = ativo.get("state_id")
            novo_status = session_attr.get("acao_status")

            if novo_status is None:
                log_warning("O status do ativo não foi especificado.")
                return handler_input.response_builder.speak(
                    "O status do ativo não foi especificado."
                ).set_should_end_session(False).response

            log_debug(f"🔁 Estado de Status: {sigla.upper()}: {novo_status}")
            sucesso = grava_historico.atualizar_status_ativo(state_id, novo_status)

            if sucesso:
                grava_historico._ativos_cache = None
                grava_historico._ativos_cache_time = 0
                log_debug(f"🔁 Status de {sigla} agora é: {novo_status}")
                return iniciar_processamento(handler_input, "siglaAtivo", [sigla])
            else:
                log_warning("Erro ao atualizar status.")
                return handler_input.response_builder.speak("Erro ao atualizar status.").response

        # -----------------------------------------------
        if arguments[0] == "toggleFavorito":
            log_debug("Entrou no toggleFavorito")
            sigla = session_attr.get("novo_ativo_sigla")
            session_attr["tipo_acao"] = "favorite"
            
            if not sigla:
                return handler_input.response_builder.speak(
                    "Nenhum ativo está selecionado para favoritamento."
                ).set_should_end_session(False).response

            _, lista_ativos = grava_historico.carregar_ativos()
            ativo = next((a for a in lista_ativos if a['codigo'].lower() == sigla), None)

            if not ativo:
                return handler_input.response_builder.speak(
                    f"Não encontrei o ativo {sigla.upper()} para incluir aos favoritos."
                ).set_should_end_session(False).response

            state_id = ativo.get("state_id")
            favorito_atual = ativo.get("favorite", 0)
            novo_favorito = not session_attr.get("favorito_atual", bool(favorito_atual))

            sucesso = grava_historico.atualizar_favorito(state_id, novo_favorito)

            if sucesso:
                grava_historico._ativos_cache = None
                grava_historico._ativos_cache_time = 0
                session_attr["favorito_atual"] = novo_favorito
                log_debug(f"🔁 Favorite de {sigla} agora é: {novo_favorito}")
                return iniciar_processamento(handler_input, "siglaAtivo", [sigla])
            else:
                log_warning("Erro ao atualizar favoritos.")
                return handler_input.response_builder.speak("Erro ao atualizar favorito.").response


        # -----------------------------------------------
        if arguments[0] == "nomeAtivo":
            session_attr["tipo_acao"] = "nome_ativo"
            session_attr["novo_ativo_nome"] = arguments[1].strip()
            # Resposta silenciosa
            return handler_input.response_builder.set_should_end_session(False).response
            
        # -----------------------------------------------
        if arguments[0] == "cancelarCadastro":
            session_attr.pop("novo_ativo_sigla", None)
            session_attr.pop("novo_ativo_nome", None)
            session_attr["manual_selection"] = True
            state_id = session_attr.get("state", 1)

            # Volta para o primeiro fundo, ou outro desejado
            fundo = state_asset_mapping[state_id]["codigo"]
            dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)
            handler_input.response_builder.speak(
                "Cadastro cancelado. Mostrando ativo. <break time='700ms'/>" + voz
            ).add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={
                        "dados_update": dados_info  # 🔹 Agora o APL acessa esse valor (** expande o dicionário)
                    }
                )
            ).set_should_end_session(False)
            return handler_input.response_builder.response
        # -----------------------------------------------
        if arguments[0] == "excluirAtivo":
            session_attr["tipo_acao"] = "excluir"
            sigla = session_attr.get("novo_ativo_sigla")
            log_debug(f"O valor de Sigla é: {sigla}")

            if not sigla:
                return handler_input.response_builder.speak(
                    "Nenhum ativo selecionado para exclusão."
                ).set_should_end_session(False).response

            # Recarrega lista e encontra o ativo pelo código
            _, lista_ativos = grava_historico.carregar_ativos()
            ativo_encontrado = next((a for a in lista_ativos if a['codigo'].lower() == sigla), None)

            if not ativo_encontrado:
                return handler_input.response_builder.speak(
                    f"Não encontrei o ativo {sigla.upper()} para excluir."
                ).set_should_end_session(False).response

            # Usa state_id em vez de objectId
            state_id = ativo_encontrado.get("state_id")
            if state_id:
                sucesso = grava_historico.excluir_ativo(state_id)

                if sucesso:
                    # Limpa o cache
                    grava_historico._ativos_cache = None
                    grava_historico._ativos_cache_time = 0
                    state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()
                    return iniciar_processamento(handler_input, "siglaAtivo", [sigla])
                else:
                    return handler_input.response_builder.speak(
                        f"Não foi possível excluir o ativo {sigla.upper()}."
                    ).set_should_end_session(False).response
        # -----------------------------------------------
        
        if arguments[0] == "confirmarCadastro":
            sigla = session_attr.get("novo_ativo_sigla")
            nome = session_attr.get("novo_ativo_nome")
            log_warning(f"Sigla e Nome: {sigla} e {nome}")
            if not sigla or not nome:
                log_warning(f"Erro ao cadastrar Ativo: {sigla} e {nome}")
                handler_input.response_builder.speak("Erro ao cadastrar Ativo. Preencha todos os campos.").ask(
                    "Por favor, digite novamente.").set_should_end_session(False)
                return handler_input.response_builder.response

            # Validação: sigla já existe?
            _, lista_ativos = grava_historico.carregar_ativos()
            siglas_existentes = [f['codigo'].lower() for f in lista_ativos]
            if sigla in siglas_existentes:
                handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} já está cadastrado!").set_should_end_session(False)
                return handler_input.response_builder.response
            
            # Gerar um novo state id que aloca o menor id vazio da lista
            state_ids = sorted([f['state_id'] for f in lista_ativos])
            novo_state_id = 1
            for id_atual in state_ids:
                if id_atual == novo_state_id:
                    novo_state_id += 1
                else:
                    break

            novo_ativo = {
                "state_id": novo_state_id,
                "codigo": sigla,
                "nome": nome,
                "apelido": limpar_asset_name(sigla).upper(),
                "status": True,
                "favorite": False  # Novo ativo não é favorito por padrão
            }
            
            if novo_ativo:
                sucesso = grava_historico.adicionar_ativo(novo_ativo)
                if sucesso:
                    # Limpa cache e recarrega ativos
                    grava_historico._ativos_cache = None
                    grava_historico._ativos_cache_time = 0
                    state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()
                    # Chama a tela de loading e dispara o próximo passo
                    return iniciar_processamento(handler_input, "executarCadastro", [sigla])
                else:
                    handler_input.response_builder.speak(
                        f"Não foi possível cadastrar o ativo {sigla.upper()}."
                ).set_should_end_session(False)
                return handler_input.response_builder.response
        
        # -----------------------------------------------
        if arguments[0] == "executarCadastro":
            # Recupera a sigla do argumento
            sigla = arguments[1] if len(arguments) > 1 else None
            if not sigla:
                return handler_input.response_builder.speak(
                    "Erro ao finalizar cadastro. Sigla não informada."
                ).set_should_end_session(False).response

            # Recarregue o mapeamento após adicionar o novo ativo
            state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()

            # Busca o novo state_id pelo código
            sigla_normalizada = limpar_asset_name(sigla) # Normaliza a sigla       
            novo_state_id, asset_full = next(
                (
                    (state_id, ativo.get("codigo"))
                    for state_id, ativo in state_asset_mapping.items()
                    if limpar_asset_name(ativo.get("codigo", "")) == sigla_normalizada
                ),
                (None, None)
            )
            
            if not novo_state_id:
                return handler_input.response_builder.speak(
                    f"Erro ao localizar o ativo {sigla.upper()} após cadastro."
                ).set_should_end_session(False).response

            # Feedback imediato e avanço de tela
            dados_info, _, _, _, apl_document, voz, _ = web_scrape(asset_full)
            #log_info(json.dumps(apl_document, indent=2, ensure_ascii=False))

            session_attr["manual_selection"] = True # Desativa a navegaçaõ automática
            session_attr["state"] = 1 # Estado da Sessão para primeira página

            handler_input.response_builder.speak(
                f"O ativo {sigla.upper()} foi cadastrado com sucesso! Agora exibindo o ativo {asset_full.upper()}. <break time='1s'/>{voz}"
            ).add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",  # token para exibição de fundos
                    document=apl_document,
                    datasources={
                        "dados_update": dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                    }
                )
            ).set_should_end_session(False)
            return handler_input.response_builder.response
# ============================================================================================

# HANDLER PARA ADICIONAR NOVO ATIVO (carregando página de entrata de dados)
class GerenciarAtivoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora no Handler GerenciarAtivoIntent")
        #log_intent_event(handler_input,"Verificar")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False
        
        return is_intent_name("GerenciarAtivoIntent")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["manual_selection"] = True
        session_attr["contexto_atual"] = "gerenciar_ativo"
        apl_document = _load_apl_document("apl_gerenciar_ativo.json")
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="GerenciarAtivoToken",
                document=apl_document
            )
        ).speak("Digite a sigla e o nome completo do novo ativo.").ask("Por favor, digite a sigla do novo ativo.").set_should_end_session(False)
        return handler_input.response_builder.response
# ============================================================================================

# HANDLER PARA CRIAR UM ALERTA DE PREÇO.
class CreatePriceAlertIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora no Handler CreatePriceAlertIntent")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False # Proteção para quando for APL.UserEvent
        
        if not is_intent_name("CreatePriceAlertIntent")(handler_input):
            return False  # corta logo se não é a intent certa
        
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        log_intent_event(handler_input, "Criando alerta")

        # Bloqueia alerta de preço se seleção estiver ativo
        if isinstance(request, IntentRequest):
            asset_name = request.intent.slots.get("fundName").value if request.intent.slots.get("fundName") else None
            if session_attr.get("select_in_progress") and not asset_name:
                log_warning("🛑 Seleção em andamento, fundName ausente. Bloqueando CreatePriceAlertIntent.")
                return False

        return is_intent_name("CreatePriceAlertIntent")(handler_input)
    
    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
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
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
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
            fundo = state_asset_mapping[1]["codigo"]
            dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)
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
            log_info("ConfirmarAlerta acionado via APL")
            #sigla = session_attr.get("sigla_alerta")
            #valor = session_attr.get("AlertValue")
            #log_info(f"O valor de Sigla e Valor são: {sigla}::{valor}")
            fake_slots = {}  # slots não são usados porque já temos os dados em session_attr

            resultado = tratar_alerta(session_attr, fake_slots)

            # Ação esperada: "create", "error", "show_apl", etc
            if resultado["action"] == "create":
                handler_input.response_builder.speak(resultado["speech"])

                for directive in resultado.get("directives", []):
                    handler_input.response_builder.add_directive(directive)

                return handler_input.response_builder.set_should_end_session(False).response

            if resultado["action"] == "show_apl":
                handler_input.response_builder.speak(resultado["speech"])

                for directive in resultado.get("directives", []):
                    handler_input.response_builder.add_directive(directive)

                return handler_input.response_builder.set_should_end_session(False).response

            if resultado["action"] == "error":
                handler_input.response_builder.speak(resultado["speech"]).ask(
                    resultado.get("reprompt", "")
                )
                return handler_input.response_builder.set_should_end_session(False).response

            # Fallback genérico
            handler_input.response_builder.speak("Houve um erro ao tentar cadastrar o alerta.").set_should_end_session(False)
            return handler_input.response_builder.response

            """# Validação: sigla já existe?
            allowed_funds = [limpar_asset_name(v.get("codigo", "")) for v in state_asset_mapping.values()]
            sigla_normalizada = limpar_asset_name(sigla)

            if sigla_normalizada not in allowed_funds:
                handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} não está cadastrado! Tente outro ativo").set_should_end_session(False)
                return handler_input.response_builder.response"""
# ============================================================================================

# HANDLER DE NAVEGAÇÃO AUTOMÁTICA PELOS ATIVOS
class DynamicScreenHandler(AbstractRequestHandler):
    """def __init__(self, state_asset_mapping):
        self.state_asset_mapping = state_asset_mapping"""
        
    def __init__(self, state_asset_mapping):
        # Filtra apenas ativos com status True (ativos visíveis)
        self.state_asset_mapping = {
            k: v for k, v in state_asset_mapping.items()
            if v.get("status", True)  # se não tiver chave, assume ativo por padrão
        }

    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
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
        
        # Protege contra UserEvent após encerramento
        if handler_input.request_envelope.request.object_type == "Alexa.Presentation.APL.UserEvent" and session_attr.get("state") is None:
            log_warning("UserEvent recebido após encerramento. Ignorando.")
            return handler_input.response_builder.response

        # Permite apenas eventos de auto-navegação
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            arguments = handler_input.request_envelope.request.arguments
            log_info(f"UserEvent recebido: argumentos={arguments}, contexto={session_attr.get('contexto_atual')}")
            if arguments and arguments[0] == "autoNavigate":
                log_debug("DynamicScreenHandler acionado para evento autoNavigate.")
                return True

        log_warning("DynamicScreenHandler ignorado para eventos de toque ou intent errado.")
        return False

    def handle(self, handler_input):
        start_time = time.time()
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["contexto_atual"] = "auto_navegacao"
        ativos_ids = session_attr.get("ativos_ids", sorted(self.state_asset_mapping.keys()))
        exibir_favoritos = session_attr.get("exibir_favoritos", False)
        current_state = session_attr.get("state", ativos_ids[0])  # Estado inicial padrão é 1
        token_apl = "mainScreenToken"

        log_info("=== DynamicScreenHandler.handle ===")
        #log_info(f"ativos_ids: {ativos_ids}")
        #log_info(f"exibir_favoritos: {exibir_favoritos}")
        #log_info(f"current_state: {current_state}")
        log_session_state(handler_input, "Atributos da sessão")

        # Garante que tipos são iguais (tudo int ou tudo str)
        ativos_ids = [int(a) for a in ativos_ids]
        try:
            current_state = int(current_state)
        except Exception:
            current_state = ativos_ids[0]

        try:
            idx = ativos_ids.index(current_state)
            next_idx = idx + 1 if idx + 1 < len(ativos_ids) else None
        except ValueError:
            idx = 0

        try:
            log_info(f"ativos_ids: {ativos_ids}")
            log_info(f"current_state: {current_state}")
            log_info(f"idx: {idx}")
            log_info(f"idx (posição do fundo atual): {idx}")
            fundo = self.state_asset_mapping[ativos_ids[idx]]["codigo"]
            log_info(f"Fundo selecionado: {fundo}")

            # Obtenha o fundo atual do mapeamento
            fundo = self.state_asset_mapping[ativos_ids[idx]]["codigo"]
            session_attr['asset_full'] = fundo
            
            # Chame a função web_scrape para obter os dados do fundo
            dados_info, _, _, _, apl_document, voz, timeout = web_scrape(fundo)
            
            tempo_processamento = time.time() - start_time
            log_info(f"Tempo de processamento do ativo {fundo}: {tempo_processamento:.2f}s")
            
            # Limite de segurança (ex: 7.5 segundos)
            LIMITE_TIMEOUT = 8.5
            
            # Recupera ou inicializa o contador de tentativas
            tentativas = session_attr.get("tentativas_timeout", 0)
            
            if (timeout or tempo_processamento > LIMITE_TIMEOUT):
                tentativas += 1
                session_attr["tentativas_timeout"] = tentativas
                
                if tentativas >= 5:
                    log_warning("Limite de tentativas de timeout atingido. Encerrando skill.")
                    handler_input.response_builder.speak(
                        "Ocorreu um atraso repetido na atualização dos ativos. Encerrando a skill por agora. Tente novamente mais tarde."
                    )
                    return handler_input.response_builder.set_should_end_session(True).response
                
                # Resposta rápida para evitar timeout
                handler_input.response_builder.speak(
                    f"Estou buscando as informações do ativo {fundo.upper()}, aguarde um momento..."
                )
                # Agende o próximo fundo para manter a navegação automática
                handler_input.response_builder.add_directive(
                    ExecuteCommandsDirective(
                        token="mainScreenToken",
                        commands=[
                            SendEventCommand(arguments=["autoNavigate"], delay=1000)
                        ]
                    )
                )
                return handler_input.response_builder.set_should_end_session(False).response
            else:
                # Zera o contador se processamento foi rápido
                session_attr["tentativas_timeout"] = 0
            
            #import json
            #log_debug(f"[APL] Dados enviados: {json.dumps(dados_info, ensure_ascii=False)}")
            #log_debug(f"[APL] Tamanho do datasource: {len(json.dumps(dados_info))} bytes")
            log_debug(f"[APL] Tamanho datasource: {len(json.dumps(dados_info, ensure_ascii=False))} bytes")
            
            # Verificando dados_info
            if not isinstance(dados_info, dict) or not dados_info:
                log_error(f"❌ dados_info inválido para fundo {fundo}. Ignorando entrada.")
                handler_input.response_builder.speak(
                    f"O fundo {fundo.upper()} está indisponível no momento. Pulando para o próximo."
                ).set_should_end_session(False)
                
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="mainScreenToken",
                        document=apl_document,
                        datasources={
                            "dados_update": dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                        }
                    )
                )
                # Força o avanço automático
                session_attr["state"] = ativos_ids[next_idx] if next_idx is not None else None
                handler_input.response_builder.add_directive(
                    ExecuteCommandsDirective(
                        token=token_apl,
                        commands=[
                            SendEventCommand(arguments=["autoNavigate"], delay=1500)
                        ]
                    )
                )
                return handler_input.response_builder.response

            # Calcula o próximo estado
            if next_idx is not None:
                session_attr["state"] = ativos_ids[next_idx]
                log_info(f"Avançando para o próximo state: {session_attr['state']}")
            else:
                session_attr["state"] = None
                log_info("Último ativo exibido, encerrando ciclo.")
                log_info(f"Novo state definido: {session_attr['state']}")
                
            # Defina o delay com base em favoritos
            if exibir_favoritos:
                delay_ms = 10000  # Favoritos:(10s)
            else:
                delay_ms = 1000  # Regulares:(2s)

            # Construa a resposta
            """token_apl = "mainScreenToken"
            log_debug(f"[APL] Adicionando RenderDocumentDirective com token: {token_apl}")
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={
                        "dados_update": dados_info  # Agora o APL acessa esse valor (** expande o dicionário)
                    }
                )
            )"""

            # Só fala se não for favoritos
            if not exibir_favoritos:
                handler_input.response_builder.speak(f"<break time='1s'/>\n{voz}")

            # Se houver um próximo estado, agende a navegação automática.
            log_debug(f"🧪 Renderizando fundo: {fundo}")
            #log_debug(f"Dados enviados: {json.dumps(dados_info, ensure_ascii=False)}")
            session_attr.pop("manual_selection", None)
            
            if next_idx is not None:
                log_info("Agendando próximo autoNavigate.")
                # Reenvie o documento APL antes do comando automático
                #token_apl = "mainScreenToken"
                #log_debug(f"[APL] Adicionando RenderDocumentDirective com token: {token_apl}")
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token=token_apl,
                        document=apl_document,
                        datasources={
                            "dados_update": dados_info
                        }
                    )
                )
                
                #log_debug(f"[APL] Adicionando ExecuteCommandsDirective com token: {token_apl}")
                handler_input.response_builder.add_directive(
                    ExecuteCommandsDirective(
                        token=token_apl,
                        commands=[
                            SendEventCommand(
                                arguments=["autoNavigate"], delay=delay_ms
                            )
                        ]
                    )
                )
                log_info(f"Tempo total Processamento:{fundo}: {time.time() - start_time:.2f}s")
                return handler_input.response_builder.set_should_end_session(False).response
            else:
                # Último ativo: encerre a skill de forma amigável após 10 segundos
                log_info("Encerrando skill após o último ativo.")
                session_attr["state"] = None
                
                #token_apl = "mainScreenToken"
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token=token_apl,
                        document=apl_document,
                        datasources={
                            "dados_update": dados_info
                        }
                    )
                )
                
                if not exibir_favoritos:
                    handler_input.response_builder.speak(
                        f"<break time='1s'/>{voz}<break time='10s'/>Encerrando a skill. Até a próxima!"
                    )
                # Se for favoritos, não fala nada!
                return handler_input.response_builder.set_should_end_session(True).response
        
        except Exception as e:
            log_error(f"Erro inesperado no handler: {e}")
            handler_input.response_builder.speak(
                "Ocorreu um erro interno. Encerrando a skill."
            )
            return handler_input.response_builder.set_should_end_session(True).response
# ============================================================================================

# HANDLER PARA MOSTRAR FUNDO SOLICITADO
class SelectFundIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora no Handler SelectFundInput")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False # Proteção para quando for APL.UserEvent
        
        return is_intent_name("SelectFundIntent")(handler_input) or \
               is_intent_name("AMAZON.NextIntent")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        #handler_input.response_builder.add_directive(get_dynamic_entities_directive())
        session_attr = handler_input.attributes_manager.session_attributes
        intent_name = handler_input.request_envelope.request.intent.name
        if session_attr.get("contexto_atual") == "monitor_in_progress":
            session_attr["contexto_atual"] = "monitor_in_progress"
        else:
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

        allowed_funds = [limpar_asset_name(v.get("codigo", "")) for v in state_asset_mapping.values()]
        log_warning(f"Fundos permitidos: {allowed_funds}")

        #directive = get_dynamic_entities_directive()
        #log_info(f"/n 📦 Entidades dinâmicas carregadas: {json.dumps(directive.to_dict(), ensure_ascii=False, indent=2)}/n")
        #handler_input.response_builder.add_directive(directive)

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
        
        sigla_normalizada = limpar_asset_name(fund_name)
        log_warning(f"Sigla Normalizada: {sigla_normalizada}")

        if intent_name == "AMAZON.NextIntent":
            session_attr.pop("manual_selection", None)
            speech_text = "Continuando a navegação pelos ativos."
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_doc,
                    datasources={
                        "dados_update": dados_info
                    }
                )
            )
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="mainScreenToken",
                    commands=[
                        SendEventCommand(arguments=["autoNavigate"], delay=2000)
                    ]
                )
            ).speak(speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        if sigla_normalizada in allowed_funds:
            log_warning("Entrou no IF de verificar sigla")
            fundo_state_id, fundo_full = next(
                (
                    (state_id, dados.get("codigo"))
                    for state_id, dados in state_asset_mapping.items()
                    if limpar_asset_name(dados.get("codigo", "")) == sigla_normalizada
                ),
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
                "manual_selection": False,
                "asset_full": fundo_full
            })

            try:
                dados_info, _, _, _, apl_doc, voz, _ = web_scrape(fundo_full)
            except Exception as e:
                log_error(f"Erro no web_scrape para {fundo_full}: {e}")
                return handler_input.response_builder.speak("Ocorreu um erro ao recuperar as informações do ativo."
                ).set_should_end_session(False).response

            log_info(f"Contexto da Sessão: {session_attr['contexto_atual']}")
            # BLOCO QUE TRATA O MONITOR DE ATIVO
            if session_attr.get("contexto_atual") == "monitor_in_progress":
                session_attr["monitor_loop"] = True
                session_attr["monitor_start"] = datetime.now().isoformat()
                log_info(f"Dentro do bloco Monitor {fundo_full}")

                # 1. Renderiza o documento primeiro!
                handler_input.response_builder.add_directive(RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_doc,
                    datasources={
                        "dados_update": dados_info
                    }
                ))

                # 2. Depois agenda o comando com delay (agora com tela já existente)
                handler_input.response_builder.add_directive(ExecuteCommandsDirective(
                    token="mainScreenToken",
                    commands=[
                        SendEventCommand(arguments=["monitorRefresh"], delay=30000)  # 60 segundos para teste
                    ]
                ))

                # 3. Fala algo ao usuário
                handler_input.response_builder.speak(f"Monitorando o fundo {fund_name.upper()} com atualizações automáticas.")
                return handler_input.response_builder.set_should_end_session(False).response

            log_info(f"Contexto da Sessão 3: {session_attr['contexto_atual']}")
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
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
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
            fundo = state_asset_mapping[1]["codigo"]
            dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)
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
            allowed_funds = [limpar_asset_name(v.get("codigo", "")) for v in state_asset_mapping.values()]
            sigla_normalizada = limpar_asset_name(sigla)

            if sigla_normalizada not in allowed_funds:
                handler_input.response_builder.speak(
                    f"O ativo {sigla.upper()} não está cadastrado! Tente outro ativo").set_should_end_session(False)
                return handler_input.response_builder.response
            
            # Encontrar fundo completo e ID
            fundo_key = sigla.lower()
            fundo_full = None
            fundo_state_id = None
            for state_id, nome in state_asset_mapping.items():
                if limpar_asset_name(nome) == sigla_normalizada:
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

            dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo_full)
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

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_info("TouchHandler: handle chamado.")
        # Recupera os atributos de sessão
        session_attr = handler_input.attributes_manager.session_attributes
        current_state = session_attr.get("state", 1)
        log_info(f"[TouchHandler] current_state: {current_state}")

        # Verifica se o estado atual está no mapeamento
        if current_state not in self.state_asset_mapping:
            log_warning(f"[TouchHandler] current_state {current_state} não encontrado no mapeamento. Reiniciando para 1.")
            # Se o estado não for encontrado, reinicia para o primeiro estado
            current_state = 1

        # Obtenha o fundo atual do mapeamento
        fundo = self.state_asset_mapping.get(current_state, {}).get("codigo")
        if not fundo:
            log_error(f"[TouchHandler] Fundo não encontrado para state {current_state}.")
            handler_input.response_builder.speak("Não foi possível exibir o ativo. Reiniciando a navegação.").set_should_end_session(False)
            session_attr["state"] = 1
            handler_input.attributes_manager.session_attributes = session_attr
            return handler_input.response_builder.response

        log_info(f"[TouchHandler] Fundo selecionado: {fundo}")

        """# Verifica se é o último estado
        if current_state == 1:
            voz_prefix = "Recomeçando!"
            # next_state = "firstScreen"  # Reinicia para o primeiro estado
        else:
            voz_prefix = "Próximo!"
        """

        # Chama a função web_scrape para obter os dados do fundo
        dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)

        # Calcula o próximo estado
        next_state = current_state + 1 if current_state + 1 in state_asset_mapping else None
        log_info(f"[TouchHandler] Próximo state: {next_state}")
        
        # Atualiza o estado para o próximo
        session_attr["state"] = next_state

        # Constrói a resposta
        voz_prefix = "Recomeçando!" if current_state == 1 else "Próximo!"
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
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora no Handler SessionEndedRequest")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False # Proteção para quando for APL.UserEvent
        
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        request = handler_input.request_envelope.request
        session_attr = handler_input.attributes_manager.session_attributes

        log_warning("SessionEndedRequestHandler acionado.")

        # Coleta motivo e detalhes do encerramento
        reason = getattr(request, "reason", "Motivo não informado")
        error = getattr(request, "error", None)
        if error:
            log_error(f"💥 Detalhes: {error}")
            # Tenta acessar campos específicos com segurança
            if hasattr(error, "type"):
                log_error(f"🔎 Tipo: {error.type}")
            if hasattr(error, "message"):
                log_error(f"📝 Mensagem: {error.message}")

        request = handler_input.request_envelope.request
        if hasattr(request, "reason"):
            log_warning(f"Motivo do fim da sessão: {request.reason}")

        log_info(f"📦 Atributos de sessão no encerramento: {session_attr}")

        # Você pode usar isso para métricas ou análises futuras
        if reason == "ERROR" and error:
            log_debug("🔧 Erro interno detectado. Pode ter sido uma exceção silenciosa em outro handler.")

        # Mantém a sessão como 'não finalizada', caso algo esteja escutando
        # handler_input.response_builder.set_should_end_session(False) # estava causando problemas com o comando "pare"
        return handler_input.response_builder.response

# ============================================================================================

class ExceptionEncounteredHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        return handler_input.request_envelope.request.object_type == "System.ExceptionEncountered"

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        request = handler_input.request_envelope.request
        error = getattr(request, "error", {})
        log_warning("⚠️ System.ExceptionEncountered capturado!")
        log_error(f"📌 Code: {getattr(error, 'code', 'sem código')}")
        log_error(f"📄 Message: {getattr(error, 'message', 'sem mensagem')}")
        log_error(f"📎 current_token: {getattr(request, 'current_token', 'N/A')}")
        log_error(f"📎 token: {getattr(request, 'token', 'N/A')}")
        log_error(f"📎 presentationToken: {getattr(request, 'presentationToken', 'N/A')}")
        log_error(f"📎 error.token: {getattr(error, 'token', 'N/A')}")
        log_error(f"📌 Stack Trace: {getattr(error, 'stackTrace', '')}")
        log_error(f"🔎 Tipo da requisição: {getattr(request, 'object_type', 'sem tipo')}")
        log_error(f"🔎 Arguments: {getattr(request, 'arguments', 'sem argumentos')}")
        log_error(f"🔎 Session Attributes: {handler_input.attributes_manager.session_attributes}")
        
        # Tenta retomar a navegação automática
        session_attr = handler_input.attributes_manager.session_attributes
        ativos_ids = session_attr.get("ativos_ids")
        state = session_attr.get("state")
        fundo = session_attr.get("asset_full") or session_attr.get("last_fundo") or "xpml11"

        # Só tenta retomar se ainda há ativos para exibir
        if ativos_ids and state is not None:
            try:
                from utils import _load_apl_document
                from scraper import web_scrape
                dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="mainScreenToken",
                        document=apl_document,
                        datasources={"dados_update": dados_info}
                    )
                )
                handler_input.response_builder.add_directive(
                    ExecuteCommandsDirective(
                        token="mainScreenToken",
                        commands=[
                            SendEventCommand(arguments=["autoNavigate"], delay=3000)
                        ]
                    )
                )
                handler_input.response_builder.speak(
                    "Houve uma falha, mas estou retomando a navegação automática."
                )
                return handler_input.response_builder.set_should_end_session(False).response
            except Exception as e:
                log_error(f"Erro ao tentar retomar navegação automática: {e}")

        # Se não for possível retomar, encerra a sessão normalmente
        return handler_input.response_builder.speak(
            "Ocorreu um erro inesperado. Encerrando a skill."
        ).set_should_end_session(True).response
        
        #return handler_input.response_builder.set_should_end_session(True).response

# ============================================================================================

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora no Handler FallbackIntent")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False # Proteção para quando for APL.UserEvent
        
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_warning("FallbackIntent acionado. Redirecionando conforme o contexto.")

        if isinstance(request, SessionEndedRequest):
            log_warning(f"Motivo do fim da sessão: {request.reason}")

        apl_document = None
        session_attr = handler_input.attributes_manager.session_attributes
        contexto_atual = session_attr.get("contexto_atual", "desconhecido")

        if contexto_atual == "alerta_preco":
            log_warning("FallbackIntent: Contexto de Alerta de Preço")
            apl_document = _load_apl_document("apl_add_alerta.json")
            speech_text = "Desculpe não entendi o nome do fundo. Por favor,  digite manualmente na tela."

        elif contexto_atual == "selecao_ativo":
            log_warning("FallbackIntent: Contexto de Seleção de Ativo")
            apl_document = _load_apl_document("apl_select_ativo.json")
            speech_text = "Não consegui entender o nome do ativo. Digite manualmente na tela."
        
        elif contexto_atual == "gerenciar_ativo":
            log_warning("FallbackIntent: Contexto de Gerenciar Ativo")
            apl_document = _load_apl_document("apl_gerenciar_ativo.json")
            speech_text = "Não consegui entender o nome do ativo. Digite manualmente na tela."

        elif contexto_atual == "auto_navegacao":
            log_warning("FallbackIntent: Contexto de navegação automática.")
            speech_text = "Desculpe, não entendi. Diga 'próximo' para avançar ou 'favoritos' para ver seus ativos favoritos."
            fundo = session_attr.get("asset_full") or session_attr.get("last_fundo") or "xpml11"
            dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={"dados_update": dados_info}
                )
            )

            # Adiciona comando para retomar a navegação automática após o fallback
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="mainScreenToken",
                    commands=[
                        SendEventCommand(arguments=["autoNavigate"], delay=2000)  # 2 segundos de delay
                    ]
                )
            )
        
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
class StopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            return False # Proteção para quando for APL.UserEvent
        
        return is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        
        session_attr = handler_input.attributes_manager.session_attributes
        contexto = session_attr.get("contexto_atual", "desconhecido")
        
        if contexto == "gerenciar_ativo":
            mensagem = "Encerrando o gerenciamento de ativos. Até logo!"
        elif contexto == "selecao_ativo":
            mensagem = "Encerrando a seleção de ativos. Até logo!"
        elif contexto == "alerta_preco":
            mensagem = "Encerrando sessão de alerta de preço. Até logo!"
        elif contexto == "auto_navegacao":
            mensagem = "Encerrando a navegação automática. Até logo!"
        else:
            mensagem = "Tudo bem. Até mais!"
            
        log_info("🛑 AMAZON.StopIntent capturado.")
        return (
            handler_input.response_builder
            .speak(mensagem)
            .set_should_end_session(True)
            .response
        )

class CatchAllRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        log_debug("Agora no Handler CatchAllRequest")
        log_info("🔍 CatchAllRequestHandler: Verificando requisição não tratada.")
        
        request = handler_input.request_envelope.request
        if request.object_type == "Alexa.Presentation.APL.UserEvent":
            log_warning("[CatchAll] Ignorando UserEvent não tratado.")
            return False
        
        return True  # aceita qualquer solicitação que não casou com outros handlers

    def handle(self, handler_input):
        #log_debug(f"[{self.__class__.__name__}] can_handle chamado. Tipo de request: {handler_input.request_envelope.request.object_type}")
        #log_debug(f"[{self.__class__.__name__}] handle chamado. Session: {handler_input.attributes_manager.session_attributes}")
        request = handler_input.request_envelope.request
        session_attr = handler_input.attributes_manager.session_attributes
        contexto = session_attr.get("contexto_atual")
        apl_document = None

        log_warning(f"⚠️ Nenhum handler específico capturou esta requisição. Tipo: {request.object_type}")
        
        # 🔒 Tratamento especial para User Touch Event fantasma
        speech = "Desculpe, não entendi. Pode tentar de novo?" # Fala Padrão
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
            log_warning("CatchAll: Contexto de Alerta de Preço.")
            apl_document = _load_apl_document("apl_add_alerta.json")
            speech = "Desculpe, não entendi o nome do fundo. Por favor, digite na tela."

        elif contexto == "selecao_ativo":
            log_warning("CatchAll: Contexto de Seleção de Ativo.")
            apl_document = _load_apl_document("apl_select_ativo.json")
            speech = "Não consegui entender. Você pode falar: mostrar ativo seguido do nome do ativo sem o número, ou digitar na tela."

        elif contexto == "gerenciar_ativo":
            log_warning("CatchAll: Contexto de Cadastro de Ativo.")
            apl_document = _load_apl_document("apl_gerenciar_ativo.json")
            speech = "Não reconheci o ativo que você mencionou. Tente digitar manualmente."
        
        elif contexto == "auto_navegacao":
            log_warning("FallbackIntent: Contexto de navegação automática.")
            speech_text = "Desculpe, não entendi. Diga 'próximo' para avançar ou 'favoritos' para ver seus ativos favoritos."
            fundo = session_attr.get("asset_full") or session_attr.get("last_fundo") or "xpml11"
            dados_info, _, _, _, apl_document, voz, _ = web_scrape(fundo)
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="mainScreenToken",
                    document=apl_document,
                    datasources={"dados_update": dados_info}
                )
            )

            # Adiciona comando para retomar a navegação automática após o fallback
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="mainScreenToken",
                    commands=[
                        SendEventCommand(arguments=["autoNavigate"], delay=2000)  # 2 segundos de delay
                    ]
                )
            )
        else:
            speech = "Não consegui entender o que você quis dizer. Encerrando por agora, mas você pode me chamar de novo quando quiser."
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
    
    # Verifica se é um payload da Alexa
    if not data or "request" not in data or "type" not in data["request"]:
        log_warning("❌ Payload inválido recebido no webhook.")
        return jsonify({"error": "Payload inválido para Alexa Skills Kit"}), 400

    log_info("📡 Requisição recebida da Alexa. Inicializando SkillBuilder...")
    
    # Inicialize o SkillBuilder
    sb = SkillBuilder()

    # Inicialize os handlers com card_fii
    launch_request_handler = LaunchRequestHandler()
    launch_intent_handler = LaunchIntentHandler()
    wakeup_intent_handler = WakeUpIntentHandler()
    stop_intent_handler = StopIntentHandler()
    session_ended_request_handler = SessionEndedRequestHandler()
    exception_encountered_handler = ExceptionEncounteredHandler()
    monitor_intent_handler = MonitorIntentHandler()
    create_price_alert_intent_handler = CreatePriceAlertIntentHandler()
    alerta_input_handler = AlertaInputHandler()
    gerenciar_ativo_intent_handler = GerenciarAtivoIntentHandler()
    gerenciar_ativo_Input_handler = GerenciarAtivoInputHandler()
    dynamic_screen_handler = DynamicScreenHandler(state_asset_mapping)
    touch_handler = TouchHandler(state_asset_mapping)
    select_fund_intent_handler = SelectFundIntentHandler()
    select_input_handler = SelectInputHandler()
    fall_back_intent_handler = FallbackIntentHandler()
    catch_all_request_handler = CatchAllRequestHandler()

    # go_back_handler = GoBackHandler()

    # Adicione os handlers ao SkillBuilder
    sb.add_request_handler(launch_request_handler)
    sb.add_request_handler(launch_intent_handler)
    sb.add_request_handler(wakeup_intent_handler)
    sb.add_request_handler(stop_intent_handler)
    sb.add_request_handler(session_ended_request_handler)
    sb.add_request_handler(exception_encountered_handler)
    sb.add_request_handler(monitor_intent_handler)
    register_handlers(sb)
    sb.add_request_handler(create_price_alert_intent_handler)
    sb.add_request_handler(alerta_input_handler)
    sb.add_request_handler(gerenciar_ativo_intent_handler)
    sb.add_request_handler(gerenciar_ativo_Input_handler)
    sb.add_request_handler(dynamic_screen_handler)
    sb.add_request_handler(touch_handler)
    sb.add_request_handler(select_fund_intent_handler)
    sb.add_request_handler(select_input_handler)
    sb.add_request_handler(fall_back_intent_handler)
    sb.add_request_handler(catch_all_request_handler)

    # sb.add_request_handler(go_back_handler)

    # Gere a resposta
    response = sb.lambda_handler()(data, None)
    log_info("✅ Resposta gerada com sucesso para a Alexa.")
    return jsonify(response)

@app.route('/saude')
def saude():
    return "OK", 200

OUTPUT_DIR = "/home/ubuntu/webscrape/cache"

@app.route('/static/<path:filename>')
# 🔹 Verifica autenticação no header
def static_files(filename):
    
    token = request.args.get("token")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Não autorizado! Token inválido"}), 401
    
    full_path = os.path.join(OUTPUT_DIR, filename)
    print(f"Tentando servir: {full_path}")
    
     # 🔹 Verifica se o arquivo existe antes de tentar servir
    if not os.path.exists(full_path):
        return jsonify({"error": "Arquivo não encontrado"}), 404

    return send_from_directory(OUTPUT_DIR, filename, mimetype="image/png")

def atualizar_graficos_periodicamente():
    while True:
        try:
            log_info("⏰ Atualizando gráficos em background (agendado)...")
            # Consulta os ativos do banco
            conn = conectar_sqlite()
            cursor = conn.cursor()
            cursor.execute("SELECT codigo FROM ativos WHERE status = True")
            ativos = [row[0] for row in cursor.fetchall()]
            conn.close()
            # Gera os gráficos (chame sua função que gera todos)
            #gerar_todos_os_graficos(ativos)
            log_info("✅ Gráficos atualizados com sucesso.")
        except Exception as e:
            log_error(f"Erro ao atualizar gráficos agendados: {e}")
        # Aguarda 20 minutos (1200 segundos)
        time.sleep(1200)

# Inicia a thread de atualização automática ao iniciar o app
threading.Thread(target=atualizar_graficos_periodicamente, daemon=True).start()

if __name__ == '__main__':
    log_info("\n Iniciando o servidor Flask...\n")
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=True)  #use_reloader=False para evitar reinicializações duplicadas)
    #ssl_context=('/home/ubuntu/fullchain.pem', '/home/ubuntu/privkey.pem')
