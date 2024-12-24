from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)
sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        logger.info("POST request to the root URL")
        return jsonify({"message": "POST request received"})
    return "Skill Alexa Webscrape está funcionando!"

@app.route("/webscrape", methods=["GET"])
def webscrape():
    try:
        url = "https://www.weather-forecast.com/locations/Tokyo/forecasts/latest"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        weather = soup.find("span", class_="phrase").text
        logger.info(f"Weather fetched: {weather}")

        weather = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": weather
            },
            "shouldEndSession": True
        }
        }

        return jsonify({"weather": weather})
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return jsonify({"error": "Erro ao buscar a previsão do tempo"}), 500

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.info("LaunchRequestHandler can_handle invoked")
        return handler_input.request_envelope.request.type == "LaunchRequest"

    def handle(self, handler_input):
        logger.info("LaunchRequestHandler handle invoked")
        speech_text = "Bem-vindo à skill de previsão do tempo. Pergunte-me sobre o tempo."
        response = handler_input.response_builder.speak(speech_text).set_should_end_session(False).response
        logger.info(f"LaunchRequestHandler response: {response}")
        
        response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech_text
            },
            "shouldEndSession": True
        }
        }
        return response

class WeatherIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.info("WeatherIntentHandler can_handle invoked")
        return (handler_input.request_envelope.request.type == "IntentRequest" and
                handler_input.request_envelope.request.intent.name == "WeatherIntent")

    def handle(self, handler_input):
        logger.info("WeatherIntentHandler handle invoked")
        try:
            response = requests.get("https://alexawebscrape.onrender.com/webscrape")
            weather = response.json().get('weather', 'não disponível')
            logger.info(f"Weather fetched: {weather}")
            speech_text = f"A previsão do tempo é: {weather}"
            response = handler_input.response_builder.speak(speech_text).set_should_end_session(True).response
            logger.info(f"WeatherIntentHandler response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error in WeatherIntentHandler: {e}")
            speech_text = "Desculpe, ocorreu um erro ao obter a previsão do tempo."
            response = handler_input.response_builder.speak(speech_text).set_should_end_session(True).response
            logger.info(f"WeatherIntentHandler error response: {response}")
            return response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(WeatherIntentHandler())

lambda_handler = sb.lambda_handler()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
