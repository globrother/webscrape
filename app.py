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
import os
import json
import logging
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
    RenderDocumentDirective, ExecuteCommandsDirective, SendEventCommand)
#from typing import Dict, Any

# NÃO SE ESQUEÇA DE CRIAR UM ARQUIVO apl_nome_do_fii.json PARA CADA FII QUE DESEJA MONITORAR

# IMPORTAR FUNÇÕES get_xxxx DOS FUNDOS ADICIONADOS
# Não se esqueça de duplicar um arquivo nome-do-fundo.py ...
# ... e alterar o nome da função get_xxxx e todas as variáveis.
from xpml11 import get_xpml
from mxrf11 import get_mxrf
from xplg11 import get_xplg
from btlg11 import get_btlg
from kncr11 import get_kncr
from knri11 import get_knri
import grava_historico
# ============================================================================================

# LEMBRE-SE DE IMPORTAR AS FUNÇÕES get_xxxx DOS FUNDOS ADICIONADOS
# LEMBRE-SE DE CARREGAR OS DOCUMENTOS APL JSON ACIMA.
# ADICIONAR UM NOVO BLOCO (3 LINHAS) PARA ALTERAR DOCUMENTO APL DO FUNDO ADICIONADO: TROCAR apl_document_xxxx E AS OUTRAS 3 VARIÁVEIS 
# DEVE-SE ADICIONAR UMA NOVA LINHA DEFININDO O CARD DO FUNDO: TROCAR voz_xxxxxx e card_xxxxxx PELO NOME DO FUNDO.

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

time.sleep(1)

app = Flask(__name__)

# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

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

apl_document_xpml = apl_document_mxrf = apl_document_xplg = apl_document_btlg = apl_document_kncr = apl_document_knri = None
voz_xpml11 = voz_mxrf11 = voz_xplg11 = voz_btlg11 = voz_kncr11 = voz_knri11 = None

# =====::::: CARREGAMENTO DO DOC APL JSON :::::=====
   
# Fazer o carregamento do Doc APL json para variável apl_document_xxxx.
# Adicionar 2 linhas e fazer 4 alterações.
doc_apl_xpml = "apl_xpml.json"
apl_document_xpml = _load_apl_document(doc_apl_xpml)

doc_apl_mxrf = "apl_mxrf.json"
apl_document_mxrf = _load_apl_document(doc_apl_mxrf)

doc_apl_xplg = "apl_xplg.json"
apl_document_xplg = _load_apl_document(doc_apl_xplg)

doc_apl_btlg = "apl_btlg.json"
apl_document_btlg = _load_apl_document(doc_apl_btlg)

doc_apl_kncr = "apl_kncr.json"
apl_document_kncr = _load_apl_document(doc_apl_kncr)

doc_apl_knri = "apl_knri.json"
apl_document_knri = _load_apl_document(doc_apl_knri) # Último fundo a ser chamado na alexa
# ============================================================================================

# =====::::: SESSÃO WEBSCRAPE: ADICIONE UM NOVO FUNDO AQUI :::::=====

# Receber o valor repassado pela tupla da função get_xxxx (alterar 4 var);
# Criar uma nova função "web_scrape_xxxx" para cada novo fundo e definir as variáveis do fundo;
# Ao todo são 18 alterações incluindo a função scrape e get.
def web_scrape_xpml():
    card_xpml11, variac_xpml11, hist_text_xpml = get_xpml(requests, BeautifulSoup) # ,_ significa que a variável variac_xpml11 não será utilizada
    apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_xpml11
    apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_xpml11
    apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_xpml
    voz_xpml11 = card_xpml11.replace('<br>', '\n<break time="500ms"/>')
    
    return card_xpml11, variac_xpml11, hist_text_xpml, apl_document_xpml, voz_xpml11
    
def web_scrape_mxrf():
    card_mxrf11, variac_mxrf11, hist_text_mxrf = get_mxrf(requests, BeautifulSoup)
    apl_document_mxrf['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_mxrf11
    apl_document_mxrf['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_mxrf11
    apl_document_mxrf['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_mxrf
    voz_mxrf11 = card_mxrf11.replace('<br>', '\n<break time="500ms"/>')
    #logger.info(f"\nDOCUMENTO APL:\n{apl_document_mxrf}\n")
     
    return card_mxrf11, variac_mxrf11, hist_text_mxrf, apl_document_mxrf, voz_mxrf11   
    
def web_scrape_xplg():
    card_xplg11, variac_xplg11, hist_text_xplg = get_xplg(requests, BeautifulSoup)
    apl_document_xplg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_xplg11
    apl_document_xplg['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_xplg11
    apl_document_xplg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_xplg
    voz_xplg11 = card_xplg11.replace('<br>', '\n<break time="500ms"/>')
    #logger.info(f"\nDOCUMENTO APL:\n{apl_document_xplg}\n")
    
    return card_xplg11, variac_xplg11, hist_text_xplg, apl_document_xplg, voz_xplg11
    
def web_scrape_btlg():
    card_btlg11, variac_btlg11, hist_text_btlg = get_btlg(requests, BeautifulSoup)
    apl_document_btlg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_btlg11
    apl_document_btlg['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_btlg11
    apl_document_btlg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_btlg
    voz_btlg11 = card_btlg11.replace('<br>', '\n<break time="500ms"/>')
    #logger.info(f"\nDOCUMENTO APL:\n{apl_document_btlg}\n")
    
    return card_btlg11, variac_btlg11, hist_text_btlg, apl_document_btlg, voz_btlg11
    
def web_scrape_kncr():
    card_kncr11, variac_kncr11, hist_text_kncr = get_kncr(requests, BeautifulSoup)
    apl_document_kncr['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_kncr11
    apl_document_kncr['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_kncr11
    apl_document_kncr['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_kncr
    voz_kncr11 = card_kncr11.replace('<br>', '\n<break time="500ms"/>')
    #logger.info(f"\nDOCUMENTO APL:\n{apl_document_kncr}\n")
    
    return card_kncr11, variac_kncr11, hist_text_kncr, apl_document_kncr, voz_kncr11
    
def web_scrape_knri():
    card_knri11, variac_knri11, hist_text_knri = get_knri(requests, BeautifulSoup) # Último fundo a ser chamado na alexa
    apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_knri11
    apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_knri11
    apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_knri
    voz_knri11 = card_knri11.replace(
        '<br>', '\n<break time="500ms"/>').replace('KNRI11', 'K N R I onze')
    
    return card_knri11, variac_knri11, hist_text_knri, apl_document_knri, voz_knri11
# ============================================================================================

# =====::::: CLASSE E INTENTS DA SKILL ALEXA :::::=====

class LaunchRequestHandler(AbstractRequestHandler):
    # ::::: 1 :::::
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # logging.debug(f"Handling LaunchRequest with card_xpml11: {self.card_xpml11}")
        _, _, _, apl_document_xpml, voz_xpml11 = web_scrape_xpml()
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "firstScreen"
        
        handler_input.response_builder.speak(f"<break time='1s'/>Aqui estão as atualizações dos fundos:<break time='1s'/>\n{voz_xpml11}").add_directive(
            RenderDocumentDirective(
                token="textDisplayToken1",
                document=apl_document_xpml
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="textDisplayToken1",
                commands=[
                    SendEventCommand(
                        arguments=["showSecondScreen"], delay=1)
                ]
            )
        )
        
        return handler_input.response_builder.set_should_end_session(False).response

# ============================================================================================

class ShowSecondScreenHandler(AbstractRequestHandler):
    # ::::: 2 :::::
    """
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showSecondScreen"]
    """
    def can_handle(self, handler_input):
        #time.sleep(5)
        #return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            #"showSecondScreen" in handler_input.request_envelope.request.arguments
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showSecondScreen"]
        
    def handle(self, handler_input):
        _, _, _, apl_document_mxrf, voz_mxrf11 = web_scrape_mxrf()        
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not session_attr.get("userInteracted"):
                session_attr["state"] = "secondScreen" # Atualiza o estado para "secondScreen"
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="textDisplayToken2",
                        document=apl_document_mxrf
                    )
                    
                ).speak(f"<break time='1s'/>\n{voz_mxrf11}<break time='500ms'/>").add_directive(
                    ExecuteCommandsDirective(
                        token="textDisplayToken2",
                        commands=[
                            SendEventCommand(
                                arguments=["showThirdScreen"], delay=1)
                        ]
                    )
                )
        return handler_input.response_builder.set_should_end_session(False).response
# ============================================================================================

class ShowThirdScreenHandler(AbstractRequestHandler):
    # ::::: 3 :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            "showThirdScreen" in handler_input.request_envelope.request.arguments

    def handle(self, handler_input):
        _, _, _, apl_document_xplg, voz_xplg11 = web_scrape_xplg()
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not session_attr.get("userInteracted"):
            session_attr["state"] = "thirdScreen" # Atualiza o estado para "thirdScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken3",
                    document=apl_document_xplg
                )  
            ).speak(f"<break time='1s'/>\n{voz_xplg11}").add_directive(
                ExecuteCommandsDirective(
                    token="textDisplayToken3",
                    commands=[
                        SendEventCommand(
                            arguments=["showFourthScreen"], delay=1)
                    ]
                )
            )
        #time.sleep(3)
        return handler_input.response_builder.set_should_end_session(False).response
# ============================================================================================

class ShowFourthScreenHandler(AbstractRequestHandler):
    # ::::: 4 :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showFourthScreen"]

    def handle(self, handler_input):
        
        _, _, _, apl_document_btlg, voz_btlg11 = web_scrape_btlg()
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "fourthScreen" # Atualiza o estado para "fourthScreen"
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="textDisplayToken4",
                document=apl_document_btlg
            )
        ).speak(f"<break time='1s'/>\n{voz_btlg11}").add_directive(
            ExecuteCommandsDirective(
                token="textDisplayToken4",
                commands=[
                    SendEventCommand(
                        arguments=["showFifthScreen"], delay=1) # Atraso em ms
                ]
            )
        )
        #time.sleep(3)
        return handler_input.response_builder.set_should_end_session(False).response
# ============================================================================================

# AQUI DEVE MUDAR DUAS VARIÁVEIS: apl_document_xxxxxx e voz_xxxxxx, AO ADICIONAR UM NOVO FUNDO
# MUDAR TAMBÉM O NOME DA CLASSE: ShowXxxxxscreenHandler. ARGUMENT: showXxxxxScreen(2x). TOKEN: textDisplayTokenx.
class ShowFifthScreenHandler(AbstractRequestHandler):
    # ::::: 5 :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showFifthScreen"]

    def handle(self, handler_input):
        
        _, _, _, apl_document_kncr, voz_kncr11 = web_scrape_kncr()
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "fifthScreen" # Atualiza o estado para "fifthScreen"
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="textDisplayToken5",
                document=apl_document_kncr
            )
        ).speak(f"<break time='1s'/>\n{voz_kncr11}").add_directive(
            ExecuteCommandsDirective(
                token="textDisplayToken5",
                commands=[
                    SendEventCommand(
                        arguments=["showEndedScreen"], delay=1)
                ]
            )
        )
        #time.sleep(3)
        return handler_input.response_builder.set_should_end_session(False).response
# ============================================================================================
# ↓ ↓ ↓ ↓ ADICIONE NOVOS ↓ ↓ ↓ ↓ ↓ ↓ HANDLERS DE FUNDOS AQUI ↓ ↓ ↓ ↓
    
# ↑ ↑ ↑ ↑ ADICIONE NOVOS ↑ ↑ ↑ ↑ ↑ ↑ HANDLERS DE FUNDOS AQUI ↑ ↑ ↑ ↑
# ESSE É O ULTIMO HANDLER, NÃO PRECISA MUDAR NADA AQUI APENAS MANTER
class ShowEndedScreenHandler(AbstractRequestHandler):
    # ::::: FINAL :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showEndedScreen"]

    def handle(self, handler_input):
        
        _, _, _, apl_document_knri, voz_knri11 = web_scrape_knri()
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "endedScreen" # Atualiza o estado para "endedScreen"
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="textDisplayToken6",
                document=apl_document_knri
            )
        ).speak(f"<break time='1s'/>\n{voz_knri11}").set_should_end_session(False)
        #os._exit(0) # Finalizar servidor Flask
        return handler_input.response_builder.set_should_end_session(True).response
# ============================================================================================

class CreatePriceAlertIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CreatePriceAlertIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes
        
        # Primeira interação: perguntar o valor do alerta
        if "alertValue" not in session_attr:
            speech_text = "Qual é o valor do alerta?"
            reprompt = "Por favor, me diga o valor do alerta."
            handler_input.response_builder.speak(speech_text).ask(reprompt)
            return handler_input.response_builder.response
        
        # Segunda interação: perguntar o fundo FII
        elif "fundName" not in session_attr:
            alert_value = get_slot_value(handler_input, "alertValue")
            session_attr["alertValue"] = alert_value
            speech_text = "Qual é o nome do fundo FII?"
            reprompt = "Por favor, me diga o nome do fundo FII."
            handler_input.response_builder.speak(speech_text).ask(reprompt)
            return handler_input.response_builder.response
        
        # Terceira interação: armazenar os dados no banco de dados
        else:
            fund_name = get_slot_value(handler_input, "fundName")
            alert_value = session_attr["alertValue"]
            session_attr["fundName"] = fund_name
            
            # Armazenar no banco de dados Back4App
            logger.info('\n Começar a gravar\n')
            sufixo = f"alert_value_{fund_name.lower()}"
            valor = alert_value
            grava_historico.gravar_historico(sufixo, valor)
            
            speech_text = f"Alerta de preço de {alert_value} reais para o fundo {fund_name} criado com sucesso."
            return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

class SelectFundIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SelectFundIntent")(handler_input)

    def handle(self, handler_input):
        #fundo = handler_input.request_envelope.request.intent.slots["fundo"].value
        session_attr = handler_input.attributes_manager.session_attributes
        fundo = handler_input.request_envelope.request.intent.slots["fundo"].value

        # Inicializa variáveis
        response_text = ""
        document = None
        voice_prompt = ""
        # Marca que o usuário interagiu
        session_attr["userInteracted"] = True

        # Define o documento APL e a resposta de voz com base no fundo selecionado
        if fundo in ["XPML11", "XPML", "Xispê eme éle"]:
            time.sleep(1)
            _, _, _, apl_document_xpml, voz_xpml11 = web_scrape_xpml()
            response_text = f"Mostrando informações sobre o fundo {fundo}."
            voice_prompt = voz_xpml11
            document = apl_document_xpml
        elif fundo in ["MXRF11", "MXRF", "Eme xis erre efi"]:
            _, _, _, apl_document_mxrf, voz_mxrf11 = web_scrape_mxrf()
            document = apl_document_mxrf
            response_text = f"Mostrando informações sobre o fundo {fundo}."
            voice_prompt = voz_mxrf11
        elif fundo in ["XPLG11", "XPLG", "Xispê éle gê"]:
            _, _, _, apl_document_xplg, voz_xplg11 = web_scrape_xplg()
            document = apl_document_xplg
            response_text = f"Mostrando informações sobre o fundo {fundo}."
            voice_prompt = voz_xplg11
        elif fundo in ["BTLG11", "BTLG", "Bêtê éle gê"]:
            _, _, _, apl_document_btlg, voz_btlg11 = web_scrape_btlg()
            document = apl_document_btlg
            response_text = f"Mostrando informações sobre o fundo {fundo}."
            voice_prompt = voz_btlg11
        elif fundo in ["KNCR11","KNCR", "CA ene cê erre"]:
            _, _, _, apl_document_kncr, voz_kncr11 = web_scrape_kncr()
            document = apl_document_kncr
            response_text = f"Mostrando informações sobre o fundo {fundo}."
            voice_prompt = voz_kncr11
        elif fundo in ["KNRI11", "KNRI", "Ca ene erri i"]:
            _, _, _, apl_document_knri, voz_knri11 = web_scrape_knri()
            document = apl_document_knri
            response_text = f"Mostrando informações sobre o fundo {fundo}."
            voice_prompt = voz_knri11
        else:
            response_text = "Desculpe, não consegui encontrar o fundo solicitado."

        # Adiciona a resposta de fala e o documento APL, se aplicável
        if document:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken",
                    document=document
                )
            ).speak(f"{response_text}<break time='500ms'/>\n{voice_prompt}").set_should_end_session(False)
        else:
            handler_input.response_builder.speak(response_text).set_should_end_session(False)

        return handler_input.response_builder.response
# ============================================================================================

class TouchHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        print("Verificando evento de toque...")
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            print("Tipo de evento é UserEvent")
            if "touch" in handler_input.request_envelope.request.arguments:
                print("Evento de toque detectado")
                return True
        return False

    def handle(self, handler_input):
        print("Manejando evento de toque...")

        # Recupera os atributos de sessão
        session_attr = handler_input.attributes_manager.session_attributes
        if not session_attr:
            session_attr = {}
        
        print(f"Estado atual: {session_attr.get('state')}")
        #time.sleep(1)
        # Continuação da lógica baseada no estado armazenado
        if "state" in session_attr and session_attr["state"] == "firstScreen":
            session_attr["state"] = "secondScreen"
            handler_input.response_builder.speak("Ok")
            _, _, _, apl_document_mxrf, voz_mxrf11 = web_scrape_mxrf()
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken2",
                    document=apl_document_mxrf
                )
            ).speak(f"Próximo:<break time='500ms'/>\n{voz_mxrf11}").set_should_end_session(False)
            
        elif "state" in session_attr and session_attr["state"] == "secondScreen":
            session_attr["state"] = "thirdScreen"
            _, _, _, apl_document_xplg, voz_xplg11 = web_scrape_xplg()
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken3",
                    document=apl_document_xplg
                )
            ).speak(f"Próximo:<break time='500ms'/>\n{voz_xplg11}").set_should_end_session(False)
            
        elif "state" in session_attr and session_attr["state"] == "thirdScreen":
            session_attr["state"] = "fourthScreen"
            _, _, _, apl_document_xpml, voz_btlg11 = web_scrape_btlg()
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken4",
                    document=apl_document_btlg
                )
            ).speak(f"Próximo:<break time='500ms'/>\n{voz_btlg11}").set_should_end_session(False)
            
        elif "state" in session_attr and session_attr["state"] == "fourthScreen":
            session_attr["state"] = "fifthScreen"
            _, _, _, apl_document_kncr, voz_kncr11 = web_scrape_kncr()
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken5",
                    document=apl_document_kncr
                )
            ).speak(f"Próximo:<break time='500ms'/>\n{voz_kncr11}").set_should_end_session(False)
            
        elif "state" in session_attr and session_attr["state"] == "fifthScreen":
            session_attr["state"] = "endedScreen"
            _, _, _, apl_document_knri, voz_knri11 = web_scrape_knri()
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken6",
                    document=apl_document_knri
                )
            ).speak(f"Próximo:<break time='500ms'/>\n{voz_knri11}").set_should_end_session(False)  
        else:
            session_attr["state"] = "firstScreen"
            _, _, _, apl_document_xpml, voz_xpml11 = web_scrape_xpml()
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken1",
                    document=apl_document_xpml
                )
            ).speak(f"Recomeçando:<break time='500ms'/>\n{voz_xpml11}").set_should_end_session(False)

        handler_input.attributes_manager.session_attributes = session_attr
        return handler_input.response_builder.set_should_end_session(False).response    
# ============================================================================================

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and \
               handler_input.request_envelope.request.intent.name == "AMAZON.FallbackIntent"
               
    def handle(self, handler_input):
        print("FallbackIntent acionado")
        # Cria uma instância de TouchHandler
        #touch_handler = TouchHandler()
                
        # Chama o método handle de TouchHandler
        #return touch_handler.handle(handler_input)
            
            
        # Não altere o estado e não forneça resposta audível
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response
# ============================================================================================

"""Aqui eu peço o encerramento da skill caso nenhum handler seja capaz de lidar com a solicitação.
    dessa forma ao tocar sobre o botão de voltar, a skill será encerrada, pois não implementei nenhum
    método para essa solicitação."""
class CatchAllRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return True

    def handle(self, handler_input):
        # Log para depuração
        print("CatchAllRequestHandler acionado")
        print(f"Tipo de Requisição: {handler_input.request_envelope.request}")
        
        # Verificar se é um FallbackIntent
        if handler_input.request_envelope.request.object_type == "IntentRequest" and \
            handler_input.request_envelope.request.intent.name == "AMAZON.FallbackIntent":
                print("FallbackIntent em CatchAllRequest detectado")
                # Cria uma instância de TouchHandler
                #touch_handler = TouchHandler()
                
                # Chama o método handle de TouchHandler
                #return touch_handler.handle(handler_input)
            
            
                # Não altere o estado e não forneça resposta audível
                handler_input.response_builder.set_should_end_session(False)
                return handler_input.response_builder.response
        
        # Mensagem padrão caso não seja um FallbackIntent
        handler_input.response_builder.speak(
            "Desculpe, não consegui entender sua solicitação. Diga sair para encerrar a sessão, ou tente novamente.").set_should_end_session(False)
        
        # Em vez de encerrar, vamos definir uma mensagem padrão
        handler_input.response_builder.speak("Encerrando a skill. Até a próxima!").set_should_end_session(True)
        logging.info("\n Encerrando Aplicativo...\n")
        #os.kill(os.getpid(), signal.SIGTERM) # Finalizar servidor Flask usando sinal
        return handler_input.response_builder.response
# ============================================================================================

@app.route('/webscrape', methods=['POST'])
def webhook():
    data = request.get_json()
        
    # Inicialize o SkillBuilder
    sb = SkillBuilder()

    # Inicialize os handlers com card_xpml11
    launch_request_handler = LaunchRequestHandler()
    show_second_screen_handler = ShowSecondScreenHandler()
    show_third_screen_handler = ShowThirdScreenHandler()
    show_fourth_screen_handler = ShowFourthScreenHandler()
    show_fifth_screen_handler = ShowFifthScreenHandler()
    show_ended_screen_handler = ShowEndedScreenHandler()
    select_fund_intent_handler = SelectFundIntentHandler()
    create_price_alert_intent_handler = CreatePriceAlertIntentHandler()
    
    touch_handler = TouchHandler()
    fall_back_intent_handler = FallbackIntentHandler()
    catch_all_request_handler = CatchAllRequestHandler()
    
    # go_back_handler = GoBackHandler()

    # Adicione os handlers ao SkillBuilder
    sb.add_request_handler(launch_request_handler)
    sb.add_request_handler(show_second_screen_handler)
    sb.add_request_handler(show_third_screen_handler)
    sb.add_request_handler(show_fourth_screen_handler)
    sb.add_request_handler(show_fifth_screen_handler)
    sb.add_request_handler(show_ended_screen_handler)
    sb.add_request_handler(select_fund_intent_handler)
    sb.add_request_handler(create_price_alert_intent_handler)
    
    sb.add_request_handler(touch_handler)
    sb.add_request_handler(fall_back_intent_handler)
    sb.add_request_handler(catch_all_request_handler)
    
    # sb.add_request_handler(go_back_handler)

    # Gere a resposta
    response = sb.lambda_handler()(data, None)
    return jsonify(response)
    
    
if __name__ == '__main__':
    logging.info("\n Iniciando o servidor Flask...\n")
    # logging.basicConfig(level=logging.DEBUG) # Habilita debug logging
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    