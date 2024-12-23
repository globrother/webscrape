from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
sb = SkillBuilder()

@app.route("/", methods=["GET"])
def index():
    return "Skill Alexa Webscrape está funcionando!"

@app.route("/webscrape", methods=["GET"])
def webscrape():
    url = "https://www.weather-forecast.com/locations/Tokyo/forecasts/latest"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    weather = soup.find("span", class_="phrase").text
    return jsonify({"weather": weather})

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "LaunchRequest"

    def handle(self, handler_input):
        speech_text = "Bem-vindo à skill de previsão do tempo. Pergunte-me sobre o tempo."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class WeatherIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.type == "IntentRequest" and
                handler_input.request_envelope.request.intent.name == "WeatherIntent")

    def handle(self, handler_input):
        response = requests.get("https://alexawebscrape.onrender.com/webscrape")
        weather = response.json().get('weather', 'não disponível')
        speech_text = f"A previsão do tempo é: {weather}"
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(WeatherIntentHandler())

lambda_handler = sb.lambda_handler()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
