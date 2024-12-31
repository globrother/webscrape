"""
===== ::: CONSTRUINDO RESPOSTA PARA ALEXA ::: ========================================
"""


def alexa_xpml11(get_element, request, requests, BeautifulSoup):
    
    data = request.get_json()
    session = data.get('session', {})
    attributes = session.get('attributes', {})

    if attributes.get('follow_up', False):
        # Enviar a segunda resposta
        return send_follow_up_response()
    
    xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16 = get_element(requests, BeautifulSoup)

    voz_xpml11 = f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>" \
        f"• Dividend Yield: {dyxpml11_3}%\n<break time='500ms'/>" \
        f"• P/VP: {pvpxpml11_6}\n<break time='500ms'/>" \
        f"• Último rendimento: R$ {divpcxmpl11_16}<break time='500ms'/>"
            
    card_xpml11 = f"• Valor atual da cota: R$ {xpml11_0}\n" \
        f"• Dividend Yield: {dyxpml11_3}%\n" \
        f"• P/VP: {pvpxpml11_6}\n" \
        f"• Último rendimento: R$ {divpcxmpl11_16}"

    response = {
        "version": "1.0",
        "response": {
        "outputSpeech": {
            "type": "SSML",
            "ssml": f"<speak> Atualizações do Fundo XPML onze \n{voz_xpml11}</speak>",
            "type": "PlainText",
            "text": f"Atualizações do Fundo X P M L onze\n{voz_xpml11}"
                    },
            "card": {
                "type": "Simple",
                "title": "Obtendo de Status Invest",
                "content": f"Atualizações do Fundo XPML11:\n{card_xpml11}"
            },
            "shouldEndSession": False # deixa a sessão aberta
        }
    }
    return response

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