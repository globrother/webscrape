"""
===== ::: OBTENDO DADOS WEB DO FII XPML11 ::: ========================================
"""
import grava_historico
import os
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

import logging

# Usar o logger para registrar mensagens
logger = logging.getLogger(__name__)
logger.info('Função XPML iniciada')

def get_xpml(requests, BeautifulSoup):
    logging.info("ANTES DA REQUISIÇÃO GET_XPML VEJA<<<<<<<<")
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/xpml11'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Referer': 'https://statusinvest.com.br/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        logging.info("gobis Status Veja")
        proxies = {
        'http': 'http://89.117.22.218:8080',
        'https': 'http://183.234.215.11:8443', # Certifique-se de usar um proxy que suporte HTTPS
        }

        response = requests.get(url, headers=headers)
        logging.info(f"gobis Status Code Veja: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['v-align-middle', 'value']
            logging.info("Veja antes do for")   
            xpml11_0 = varxpml11 = dyxpml11_3 = pvpxpml11_6 = divpcxpml11_16 = None

            for div in container_divs:
                # Encontra todos os elementos que têm as classes 'v-align-middle' ou 'value'
                """
                função de critério que está sendo passada para find_all.
                Esta função anônima (lambda) verifica se a tag atual (tag)
                possui a classe v-align-middle ou value em seu atributo class.
                """
                # elements = div.find_all(lambda tag: 'v-align-middle' in tag.get('class', []) or 'value' in tag.get('class', [])) #sem o uso de tags
                elements = div.find_all(lambda tag: any(t in tag.get('class', []) for t in tags)) #com o uso do dicionário tags.
                if len(elements) > 4:
                    xpml11_0 = elements[0].text # Valor atual da cota
                    varxpml11 = elements[1].text # Variação da cota dia anterior
                    dyxpml11_3 = elements[4].text # Dividend Yield
                    pvpxpml11_6 = elements[26].text # P/VP
                    divpcxpml11_16 = str(
                                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota                    
                    logging.info("Veja dentro do for") 
                    break
            #print(xpml11_0)
            if not all([xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxpml11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
        
        arrow_xpml = ""
        aux_xpml = ""
        
        if varxpml11[0] == "-":
            arrow_xpml = "&#x2B07;"
            aux_xpml = "queda"
        else:
            arrow_xpml = "&#x2B06;"
            aux_xpml = "alta"
                
        variac_xpml11 = (f"Houve {aux_xpml} de <b>{varxpml11}  {arrow_xpml}</b> na cota do FII XPML11 (hoje X ontem).")
        #variac_xpml11_aux = (f"<b>VAR {varxpml11}  {arrow_xpml}</b>")
        
        card_xpml11 = (
            f"Atualizações do Fundo XPML11:<br><br>"
            f"• Houve {aux_xpml} de {varxpml11} na cota<br>"
            f"• Valor atual da cota: R$ {xpml11_0}<br>"
            f"• Dividend Yield: {dyxpml11_3}%<br>"
            f"• P/VP: {pvpxpml11_6}<br>"
            f"• Último rendimento: R$ {divpcxpml11_16}"
        )
        # Com caminho absoluto, parece não ser necessário: os.path.join(os.path.dirname(__file__)
        # nome_do_arquivo = os.path.join(os.path.dirname(__file__), 'historico_xpml.json') # com caminho absoluto
        # grava_historico.gravar_historico(nome_do_arquivo, f"R$ {xpml11_0}")  
        # meu_historico = grava_historico.ler_historico("historico_xpml.json")
        # hist_text_xpml = grava_historico.gerar_texto_historico(meu_historico)
        logging.info("começar a chamar função de gravar Veja") 
        sufixo = "xpml"
        valor = f"R$ {xpml11_0}"
        grava_historico.gravar_historico(sufixo, valor)
        historico = grava_historico.ler_historico(sufixo)
        hist_text_xpml = grava_historico.gerar_texto_historico(historico)
        print(hist_text_xpml)

        logging.info(f"Veja os valores:> {card_xpml11, variac_xpml11, hist_text_xpml}") 
        return card_xpml11, variac_xpml11, hist_text_xpml

    except Exception as e:
        return {"error": str(e)}, 500
