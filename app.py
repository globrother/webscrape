from flask import Flask, jsonify, request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import logging

app = Flask(__name__)
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Launch Request."""
    speech_text = "Bem-vindo à sua Skill Alexa hospedada no Render!"
    reprompt_text = "Diga 'Olá' para me testar."
    return handler_input.response_builder.speak(speech_text).ask(reprompt_text).response

@sb.request_handler(can_handle_func=is_intent_name("HelloWorldIntent"))
def hello_world_intent_handler(handler_input):
    """Handler for Hello World Intent."""
    speech_text = "Olá do Render! Sua Skill está funcionando."
    return handler_input.response_builder.speak(speech_text).response

@sb.request_handler(can_handle_func=lambda input: True)
def fallback_handler(handler_input):
    """Handler for all other requests (fallback)."""
    speech_text = "Desculpe, não entendi. Pode repetir?"
    reprompt_text = "Por favor, tente novamente."
    return handler_input.response_builder.speak(speech_text).ask(reprompt_text).response

@app.route("/", methods=['POST'])
def alexa_endpoint():
    """Endpoint para receber as requisições da Alexa."""
    try:
        handler_input = HandlerInput(request.get_json(), None, None, None)
        response = sb.lambda_handler(handler_input)
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Erro ao processar a requisição: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080) # Use debug=False em produção