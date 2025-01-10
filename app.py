"""
============================:: FINANCE_GOBIS ::============================
==========================:: FUNDOS IMOBILIÁRIOS ::=========================
Essa é a aplicação principal (app.py) que integra os fundos imobiliários monitorados pela skill Finance_Gobis da Alexa.
A aplicação é um servidor Flask que recebe uma solicitação POST de um webhook e responde com um JSON.
O JSON contém as informações de atualização dos fundos imobiliários monitorados pela skill.
A aplicação ainda não é capaz de lidar com solicitações de eventos de usuário da Alexa com eficiencia,
mas ao tocar em um botão, a skill é encerrada.
"""
# PARA CADA FII QUE DESEJA MONITORAR:
# NÃO SE ESQUEÇA DE CRIAR UM ARQUIVO apl_nome_do_fii.json (pasta raiz)
# IMPORTAR FUNÇÕES get_xxxx DOS FUNDOS ADICIONADOS EM app.py
# DUPLICAR UM ARQUIVO DE FUNDO: nome-do-fii.py (pasta raiz)
# ALTERAR O NOME DA FUNÇÃO get_xxxx E TODAS AS VARIÁVEIS DO ARQUIVO nome-do-fundo.py
# ADICIONAR OS INICIALIZADORES DE HANDLERS: show_xxxxx_screen_handler = ShowXxxxxScreenHandler()
# ADICIONAR OS HANDLERS AO SkillBuilder: sb.add_request_handler(show_xxxxx_screen_handler)

# import locale
import os
import signal
import time
import json
import logging
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import (
    is_request_type, get_supported_interfaces, is_intent_name)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SendEventCommand)
from typing import Dict, Any

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

logging.basicConfig(level=logging.INFO)

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
    
# LEMBRE-SE DE IMPORTAR AS FUNÇÕES get_xxxx DOS FUNDOS ADICIONADOS
# AQUI, ADICIONAR UMA NOVA LINHA PARA CADA VARIÁVEL (alterar 4) RECEBER O VALOR REPASSADO PELA TUPLA DA FUNÇÃO get_xxxx    
card_xpml11, variac_xpml11, hist_text_xpml = get_xpml(requests, BeautifulSoup) # ,_ significa que a variável variac_xpml11 não será utilizada
card_mxrf11, variac_mxrf11, hist_text_mxrf = get_mxrf(requests, BeautifulSoup)
card_xplg11, variac_xplg11, hist_text_xplg = get_xplg(requests, BeautifulSoup)
card_btlg11, variac_btlg11, hist_text_btlg = get_btlg(requests, BeautifulSoup)
card_kncr11, variac_kncr11, hist_text_kncr = get_kncr(requests, BeautifulSoup)
card_knri11, variac_knri11, hist_text_knri = get_knri(requests, BeautifulSoup) # Último fundo a ser chamado na alexa

# AQUI FAZER O CARREGAMENTO DO DOC APL JSON PARA VARIÁVEL apl_document_xxxx. (adicionar 2 linhas e alterar 4 senteças)
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

# AQUI, ADICIONAR UM NOVO BLOCO (3 LINHAS) PARA ALTERAR DOCUMENTO APL DO FUNDO ADICIONADO: TROCAR apl_document_xxxx E AS OUTRAS 3 VARIÁVEIS 
apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_xpml11
#apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['text'] = card_xpml11
apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_xpml11
apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_xpml
#apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_xpml

apl_document_mxrf['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_mxrf11
apl_document_mxrf['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_mxrf11
apl_document_mxrf['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_mxrf

apl_document_xplg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_xplg11
apl_document_xplg['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_xplg11
apl_document_xplg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_xplg

apl_document_btlg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_btlg11
apl_document_btlg['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_btlg11
apl_document_btlg['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_btlg

apl_document_kncr['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_kncr11
apl_document_kncr['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_kncr11
apl_document_kncr['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_kncr

apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['item']['text'] = card_knri11
apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_knri11
apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_knri

# AQUI DEVE-SE ADICIONAR UMA NOVA LINHA DEFININDO O CARD DO FUNDO: TROCAR voz_xxxxxx e card_xxxxxx PELO NOME DO FUNDO.
voz_xpml11 = card_xpml11.replace('<br>', '\n<break time="500ms"/>')
voz_mxrf11 = card_mxrf11.replace('<br>', '\n<break time="500ms"/>')
voz_xplg11 = card_xplg11.replace('<br>', '\n<break time="500ms"/>')
voz_btlg11 = card_btlg11.replace('<br>', '\n<break time="500ms"/>')
voz_kncr11 = card_kncr11.replace('<br>', '\n<break time="500ms"/>')
voz_knri11 = card_knri11.replace(
    '<br>', '\n<break time="500ms"/>').replace('KNRI11', 'K N R I onze')
# ============================================================================================

class LaunchRequestHandler(AbstractRequestHandler):
    # ::::: 1 :::::
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # logging.debug(f"Handling LaunchRequest with card_xpml11: {self.card_xpml11}")
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "firstScreen"
        
        handler_input.response_builder.speak(f"Aqui estão as atualizações dos fundos:<break time='1s'/>\n{voz_xpml11}").add_directive(
            RenderDocumentDirective(
                token="textDisplayToken1",
                document=apl_document_xpml
            )  
        ).add_directive(
            ExecuteCommandsDirective(
                token="textDisplayToken1",
                commands=[
                    SendEventCommand(
                        arguments=["showSecondScreen"], delay=0)
                ]
            )
        ).set_should_end_session(False)
        
        return handler_input.response_builder.response
# ============================================================================================

class ShowSecondScreenHandler(AbstractRequestHandler):
    # ::::: 2 :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showSecondScreen"]

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "secondScreen" # Atualiza o estado para "secondScreen"
        handler_input.response_builder.speak(f"<break time='1s'/>\n{voz_mxrf11}").add_directive(
            RenderDocumentDirective(
                token="textDisplayToken2",
                document=apl_document_mxrf
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="textDisplayToken2",
                commands=[
                    SendEventCommand(
                        arguments=["showThirdScreen"], delay=0)
                ]
            )
        ).set_should_end_session(False)
        
        return handler_input.response_builder.response
# ============================================================================================

# AQUI DEVE MUDAR DUAS VARIÁVEIS: apl_document_xxxxxx e voz_xxxxxx, AO ADICIONAR UM NOVO FUNDO
# MUDAR TAMBÉM O NOME DA CLASSE: ShowXxxxxscreenHandler. ARGUMENT: showXxxxxScreen(2x). TOKEN: textDisplayTokenx.
class ShowThirdScreenHandler(AbstractRequestHandler):
    # ::::: 3 :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showThirdScreen"]

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
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
                        arguments=["showFourthScreen"], delay=0)
                ]
            )
        ).set_should_end_session(False)
        
        return handler_input.response_builder.response
# ============================================================================================

# AQUI DEVE MUDAR DUAS VARIÁVEIS: apl_document_xxxxxx e voz_xxxxxx, AO ADICIONAR UM NOVO FUNDO
# MUDAR TAMBÉM O NOME DA CLASSE: ShowXxxxxscreenHandler. ARGUMENT: showXxxxxScreen(2x). TOKEN: textDisplayTokenx.
class ShowFourthScreenHandler(AbstractRequestHandler):
    # ::::: 4 :::::
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showFourthScreen"]

    def handle(self, handler_input):
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
                        arguments=["showFifthScreen"], delay=0)
                ]
            )
        ).set_should_end_session(False)
        
        return handler_input.response_builder.response
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
                        arguments=["showEndedScreen"], delay=0)
                ]
            )
        ).set_should_end_session(False)
        
        return handler_input.response_builder.response
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
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "endedScreen" # Atualiza o estado para "endedScreen"
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="textDisplayToken6",
                document=apl_document_knri
            )
        ).speak(f"<break time='1s'/>\n{voz_knri11}").set_should_end_session(False)
        #os._exit(0) # Finalizar servidor Flask
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

        # Continuação da lógica baseada no estado armazenado
        if "state" in session_attr and session_attr["state"] == "firstScreen":
            session_attr["state"] = "secondScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken2",
                    document=apl_document_mxrf
                )
            ).speak(f"Próximo:<break time='1s'/>\n{voz_mxrf11}")
            
        elif "state" in session_attr and session_attr["state"] == "secondScreen":
            session_attr["state"] = "thirdScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken3",
                    document=apl_document_xplg
                )
            ).speak(f"Próximo:<break time='1s'/>\n{voz_xplg11}")
            
        elif "state" in session_attr and session_attr["state"] == "thirdScreen":
            session_attr["state"] = "fourthScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken4",
                    document=apl_document_btlg
                )
            ).speak(f"Próximo:<break time='1s'/>\n{voz_btlg11}")
            
        elif "state" in session_attr and session_attr["state"] == "fourthScreen":
            session_attr["state"] = "fifthScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken5",
                    document=apl_document_kncr
                )
            ).speak(f"Próximo:<break time='1s'/>\n{voz_kncr11}")
            
        elif "state" in session_attr and session_attr["state"] == "fifthScreen":
            session_attr["state"] = "endedScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken6",
                    document=apl_document_knri
                )
            ).speak(f"Próximo:<break time='1s'/>\n{voz_knri11}")   
        else:
            session_attr["state"] = "firstScreen"
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="textDisplayToken1",
                    document=apl_document_xpml
                )
            ).speak(f"Recomeçando:<break time='1s'/>\n{voz_xpml11}")

        handler_input.attributes_manager.session_attributes = session_attr

        return handler_input.response_builder.set_should_end_session(False).response

class CatchAllRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return True

    def handle(self, handler_input):
        # Em vez de encerrar, vamos definir uma mensagem padrão
        handler_input.response_builder.speak("Encerrando a skill. Até a próxima!").set_should_end_session(True)
        logging.info("Encerrando o servidor Flask...")
        os.kill(os.getpid(), signal.SIGTERM)
        return handler_input.response_builder.response # Finalizar servidor Flask usando sinal

#class CatchAllRequestHandler(AbstractRequestHandler):
    #def can_handle(self, handler_input):
        #return True
    """Aqui eu peço o encerramento da skill caso nenhum handler seja capaz de lidar com a solicitação.
    dessa forma ao tocar sobre o botão de voltar, a skill será encerrada, pois não implementei nenhum
    método para essa solicitação."""

    #def handle(self, handler_input):
        # return handler_input.response_builder.speak("Desculpe, não consegui entender a solicitação.").response
        #return handler_input.response_builder.speak(
            #"Encerrando a skill. Até a próxima!").set_should_end_session(True).response
# ============================================================================================

@app.route('/webscrape', methods=['POST'])
def webhook():
    data = request.get_json()

    # Defina card_xpml11 aqui dentro do contexto da aplicação Flask (não está mais precisando)
    
    # Inicialize o SkillBuilder
    sb = SkillBuilder()

    # Inicialize os handlers com card_xpml11
    launch_request_handler = LaunchRequestHandler()
    show_second_screen_handler = ShowSecondScreenHandler()
    show_third_screen_handler = ShowThirdScreenHandler()
    show_fourth_screen_handler = ShowFourthScreenHandler()
    show_fifth_screen_handler = ShowFifthScreenHandler()
    show_ended_screen_handler = ShowEndedScreenHandler()

    touch_handler = TouchHandler()
    catch_all_request_handler = CatchAllRequestHandler()
    
    # go_back_handler = GoBackHandler()

    # Adicione os handlers ao SkillBuilder
    sb.add_request_handler(launch_request_handler)
    sb.add_request_handler(show_second_screen_handler)
    sb.add_request_handler(show_third_screen_handler)
    sb.add_request_handler(show_fourth_screen_handler)
    sb.add_request_handler(show_fifth_screen_handler)
    sb.add_request_handler(show_ended_screen_handler)
    
    sb.add_request_handler(touch_handler)
    sb.add_request_handler(catch_all_request_handler)
    
    # sb.add_request_handler(go_back_handler)

    # Gere a resposta
    response = sb.lambda_handler()(data, None)
    return jsonify(response)

if __name__ == '__main__':
    logging.info("Iniciando o servidor Flask...")
    # logging.basicConfig(level=logging.DEBUG) # Habilita debug logging
    app.run(debug=True, use_reloader=False, port=5000)
