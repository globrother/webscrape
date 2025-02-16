"""
===== ::: OBTENDO DADOS WEB DO FII KNCR11 ::: ========================================
"""
# NÃO SE ESQUEÇA DE CRIAR UM ARQUIVO apl_(nome_do_fii).py PARA CADA FII QUE DESEJA MONITORAR

import grava_historico
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

import logging

# Usar o logger para registrar mensagens
logger = logging.getLogger(__name__)
logger.info('Função iniciada')

def get_kncr(requests, BeautifulSoup):
        
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/kncr11'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        proxies = {
        'http': 'http://89.117.22.218:8080',
        'https': 'http://101.255.150.254:3128', # Certifique-se de usar um proxy que suporte HTTPS
        }

        response = requests.get(url, headers=headers)
        logger.info(f"\n Status Code: {response.status_code}\n")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['v-align-middle', 'value']
            
            kncr11_0 = varkncr11 = dykncr11_3 = pvpkncr11_6 = divpckncr11_16 = None

            for div in container_divs:
                # Encontra todos os elementos que têm as classes 'v-align-middle' ou 'value'
                """
                função de critério que está sendo passada para find_all.
                Esta função anônima (lambda) verifica se a tag atual (tag)
                possui a classe v-align-middle ou value em seu atributo class.
                """
                # elements = div.find_all(lambda tag: 'v-align-middle' in tag.get('class', []) or 'value' in tag.get('class', [])) #sem o uso de tags
                elements = div.find_all(lambda tag: any(t in tag.get('class', []) for t in tags)) #com o uso do dicionário tags.
                #print(f"Elements: {elements}")
                if len(elements) > 4:
                    kncr11_0 = elements[0].text # Valor atual da cota
                    varkncr11 = elements[1].text # Variação da cota dia anterior
                    dykncr11_3 = elements[4].text # Dividend Yield
                    pvpkncr11_6 = elements[26].text # P/VP
                    divpckncr11_16 = str(
                                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota
                    
                break

            if not all([kncr11_0, dykncr11_3, pvpkncr11_6, divpckncr11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
        
        arrow_kncr = ""
        aux_kncr = ""
        
        if varkncr11[0] == "-":
            arrow_kncr = "&#x2B07;"
            aux_kncr = "queda"
        else:
            arrow_kncr = "&#x2B06;"
            aux_kncr = "alta"
                
        variac_kncr11 = (f"Houve {aux_kncr} de <b>{varkncr11}  {arrow_kncr}</b> na cota do FII KNCR11 (hoje X ontem).")
        #variac_kncr11_aux = (f"<b>VAR {varkncr11}  {arrow_kncr}</b>")
        
        card_kncr11 = (
            f"Atualizações do Fundo KNCR11:<br><br>"
            f"• Houve {aux_kncr} de {varkncr11} na cota<br>"
            f"• Valor atual da cota: R$ {kncr11_0}<br>"
            f"• Dividend Yield: {dykncr11_3}%<br>"
            f"• P/VP: {pvpkncr11_6}<br>"
            f"• Último rendimento: R$ {divpckncr11_16}"
        )
        
        sufixo = "kncr"
        valor = f"R$ {kncr11_0}"
        aux = "fund"
        grava_historico.gravar_historico(sufixo, valor)
        historico = grava_historico.ler_historico(sufixo)
        hist_text_kncr = grava_historico.gerar_texto_historico(historico, aux)

        return kncr11_0, card_kncr11, variac_kncr11, hist_text_kncr

    except Exception as e:
        logging.info(f"Ocorreu um erro em {sufixo}: {e}")
        return {"error": str(e)}, 500
