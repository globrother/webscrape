"""
===== ::: CONSTRUINDO RESPOSTA PARA ALEXA ::: ========================================
"""
from flask import jsonify
import time
#from xpml11 import get_element

def alexa_xpml11(get_element, request, requests, BeautifulSoup):
    try:
        data = request.get_json()
        
        xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16 = get_element(requests, BeautifulSoup)
        
        voz_xpml11 = f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>" \
             f"• Dividend Yield: {dyxpml11_3}%\n<break time='500ms'/>" \
             f"• P/VP: {pvpxpml11_6}\n<break time='500ms'/>" \
             f"• Último rendimento: R$ {divpcxmpl11_16}"
        
        card_xpml11 = f"• Valor atual da cota: R$ {xpml11_0}\n" \
             f"• Dividend Yield: {dyxpml11_3}%\n" \
             f"• P/VP: {pvpxpml11_6}\n" \
             f"• Último rendimento: R$ {divpcxmpl11_16}"

        response = {
            "version": "1.0",
            "sessionAttributes":{
                 "follow_up": True },
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": f"<speak> Atualizações do Fundo XPML onze \n{voz_xpml11}</speak>"
                },
                "card": {
                    "type": "Simple",
                    "title": "Obtendo de Status Invest",
                    "content": f"Atualizações do Fundo XPML11:\n\n{card_xpml11}"
                },
                "shouldEndSession": False
            }
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_follow_up_response():
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Aqui está a próxima atualização."
            },
            "card": {
                "type": "Simple",
                "title": "Mais Informações do Fundo XPML11",
                "content": "Informações adicionais aqui."
            },
            "shouldEndSession": True  # Fecha a sessão após a resposta
        }
    }
    return response

"""
def send_follow_up_response():
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Aqui está a próxima atualização."
            },
            "card": {
                "type": "Simple",
                "title": "Mais Informações do Fundo XPML11",
                "content": "Informações adicionais aqui."
            },
            "shouldEndSession": True  # Fecha a sessão após a resposta
        }
    }
    return jsonify(response)
"""