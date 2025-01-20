"""
===== ::: OBTENDO DADOS WEB DO FII XPLG11 ::: ========================================
"""
# NÃO SE ESQUEÇA DE CRIAR UM ARQUIVO apl_(nome_do_fii).py PARA CADA FII QUE DESEJA MONITORAR

import grava_historico
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

def get_xplg(requests, BeautifulSoup):
    
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/xplg11'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        proxies = {
        'http': 'http://89.117.22.218:8080',
        'https': 'http://101.255.150.254:3128', # Certifique-se de usar um proxy que suporte HTTPS
        }

        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['v-align-middle', 'value']

            xplg11_0 = varxplg11 = dyxplg11_3 = pvpxplg11_6 = divpcxplg11_16 = None

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
                    xplg11_0 = elements[0].text # Valor atual da cota
                    varxplg11 = elements[1].text # Variação da cota dia anterior
                    dyxplg11_3 = elements[4].text # Dividend Yield
                    pvpxplg11_6 = elements[26].text # P/VP
                    divpcxplg11_16 = str(
                                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota
                    
                    break
            #print(xplg11_0)
            if not all([xplg11_0, dyxplg11_3, pvpxplg11_6, divpcxplg11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
        
        arrow_xplg = ""
        aux_xplg = ""
        
        if varxplg11[0] == "-":
            arrow_xplg = "&#x2B07;"
            aux_xplg = "queda"
        else:
            arrow_xplg = "&#x2B06;"
            aux_xplg = "alta"
                
        variac_xplg11 = (f"Houve {aux_xplg} de <b>{varxplg11}  {arrow_xplg}</b> na cota do FII XPLG11 (hoje X ontem).")
        
        card_xplg11 = (
            f"Atualizações do Fundo XPLG11:<br><br>"
            f"• Houve {aux_xplg} de {varxplg11} na cota<br>"
            f"• Valor atual da cota: R$ {xplg11_0}<br>"
            f"• Dividend Yield: {dyxplg11_3}%<br>"
            f"• P/VP: {pvpxplg11_6}<br>"
            f"• Último rendimento: R$ {divpcxplg11_16}"
        )
        
        grava_historico.gravar_historico("historico_xplg.json", f"R$ {xplg11_0}")   
        historico = grava_historico.ler_historico("historico_xplg.json")
        hist_text_xplg = grava_historico.gerar_texto_historico(historico)

        return card_xplg11, variac_xplg11, hist_text_xplg

    except Exception as e:
        return {"error": str(e)}, 500
