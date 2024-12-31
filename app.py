from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

app = Flask(__name__)

import xpml11

@app.route('/webscrape', methods=['POST'])
def alexa():
    try:
        data = request.get_json()
        xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16 = get_element()

        marcadores_voz = f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>" \
             f"• Dividend Yield: {dyxpml11_3}%\n<break time='500ms'/>" \
             f"• P/VP: {pvpxpml11_6}\n<break time='500ms'/>" \
             f"• Último rendimento: R$ {divpcxmpl11_16}<break time='500ms'/>"
        
        marcadores_card = f"• Valor atual da cota: R$ {xpml11_0}\n" \
             f"• Dividend Yield: {dyxpml11_3}%\n" \
             f"• P/VP: {pvpxpml11_6}\n" \
             f"• Último rendimento: R$ {divpcxmpl11_16}"

        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": f"<speak> Atualizações do Fundo XPML onze \n{marcadores_voz}</speak>",
                    "type": "PlainText",
                    "text": f"Atualizações do Fundo X P M L onze\n{marcadores_voz}"
                },
                "card": {
                    "type": "Simple",
                    "title": "Obtendo de Status Invest",
                    "content": f"Atualizações do Fundo XPML11:\n{marcadores_card}"
                },
                "shouldEndSession": True
            }
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
