
def web_scrape(fundo):
    doc_apl = f"apl_{fundo}.json"
    apl_document = _load_apl_document(doc_apl)
    # Adiciona a geração do texto do histórico de alertas
    sufixo = f"alert_value_{fundo}"
    historico = grava_historico.ler_historico(sufixo)
    aux = "alert"
    hist_alert = grava_historico.gerar_texto_historico(historico, aux)
    logging.info(f"\n Recuperando hist_alert_xpml da sessão: {hist_alert} \n")
    
    fii = fundo
    cota_fii, card_fii, variac_fii, hist_text_fii = get_dadosfii(fii) # ,_ significa que a variável variac_xpml11 não será utilizada
    apl_document['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['items'][0]['items'][0]['text'] = card_fii
    apl_document['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_fii
    apl_document['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['item'][0]['text'] = hist_text_fii
    apl_document['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['items'][0]['items'][2]['items'][1]['text'] = hist_alert
    voz = card_fii.replace('<br>', '\n<break time="500ms"/>')
    
    cota_atual = cota_fii
    voz_fundo = voz
    voz = comparador(historico, cota_atual, voz_fundo)
    
    return card_fii, variac_fii, hist_text_fii, apl_document, voz





 _, _, _, apl_document, voz = web_scrape("xpml11")
 
 
 {
    "version": "2024.3",
    "session": {
        "new": true,
        "sessionId": "SessionId.random-session-id",
        "application": {
            "applicationId": "amzn1.ask.skill.random-skill-id"
        },
        "attributes": {},
        "user": {
            "userId": "amzn1.ask.account.random-user-id"
        }
    },
    "request": {
        "type": "LaunchRequestHandler",
        "requestId": "RequestId.random-request-id",
        "timestamp": "2025-04-04T22:14:00Z",
        "locale": "pt-BR",
        "intent": {
            "name": "LaunchRequestHandler",
            "confirmationStatus": "NONE",
            "slots": {}
        }
    }
}