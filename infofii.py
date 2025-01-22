# =====::: FUNÇÃO UNICA PARA WEBSCRAPING DOS FIIs :::===== #
import requests
from bs4 import BeautifulSoup
import logging
import grava_historico

def get_dadosfii(fii):
    
    try:
        fii = "xpml11" # apagar depois
        url = "https://statusinvest.com.br/fundos-imobiliarios/" & fii
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
        # Lista de proxies HTTPS de serviços gratuitos ou pagos
        proxies = {
        'http': 'http://67.43.227.226:2053',
        'https': 'http://183.234.215.11:8443', # Certifique-se de usar um proxy que suporte HTTPS
        }
        
        response = requests.get(url, headers=headers) # iserir: proxies=proxies se necessário
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['v-align-middle', 'value']
            
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
                    cota_fii = elements[0].text # Valor atual da cota
                    var_fii = elements[1].text # Variação da cota dia anterior
                    dy_fii = elements[4].text # Dividend Yield
                    pvp_fii = elements[26].text # P/VP
                    divpc_fii = str(
                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota
                    
                    break
                
            if not all([xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxpml11_16]):
                raise ValueError("Impossível obter todos os elementos requeridos.")
            
        else:
            logging.info(f"Erro ao acessar o site: {response.status_code}")
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
        
        arrow_fii = ""
        aux_fii = ""
        
        if var_fii[0] == "-":
            arrow_fii = "&#x2B07;"
            aux_fii = "queda"
        else:
            arrow_fii = "&#x2B06;"
            aux_fii = "alta"

        variac_fii = (f"Houve {aux_fii} de <b>{var_fii}  {arrow_fii}</b> na cota do FII XPML11 (hoje X ontem).")
        
        card_fii = (
            f"Atualizações do Fundo {fii}:<br>"
            f"• Houve {aux_fii} de {var_fii} na cota<br>"
            f"• Valor atual da cota: R$ {cota_fii}<br>"
            f"• Dividend Yield: {dy_fii}%<br>"
            f"• P/VP: {pvp_fii}<br>"
            f"• Último rendimento: R$ {divpc_fii}"
        )
        
        # Com caminho absoluto, parece não ser necessário: os.path.join(os.path.dirname(__file__)
        #nome_do_arquivo = os.path.join(os.path.dirname(__file__), 'historico_xpml.json') # com caminho absoluto
        nome_arquivo = "historico_" & fii & ".json"
        grava_historico.gravar_historico(nome_arquivo, f"R$ {cota_fii}")  
        meu_historico = grava_historico.ler_historico(nome_arquivo)
        hist_text_fii = grava_historico.gerar_texto_historico(meu_historico)
        
        return card_fii, variac_fii, hist_text_fii
    
    except Exception as e:
        return {"error": str(e)}, 500