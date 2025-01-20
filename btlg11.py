"""
===== ::: OBTENDO DADOS WEB DO FII BTLG11 ::: ========================================
"""
# NÃO SE ESQUEÇA DE CRIAR UM ARQUIVO apl_(nome_do_fii).py PARA CADA FII QUE DESEJA MONITORAR

import grava_historico
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

def get_btlg(requests, BeautifulSoup):
        
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/btlg11'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        proxies = {
        'http': 'http://89.117.22.218:8080',
        'https': 'http://104.152.186.111:2019', # Certifique-se de usar um proxy que suporte HTTPS
        }

        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['v-align-middle', 'value']

            btlg11_0 = varbtlg11 = dybtlg11_3 = pvpbtlg11_6 = divpcbtlg11_16 = None

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
                    btlg11_0 = elements[0].text # Valor atual da cota
                    varbtlg11 = elements[1].text # Variação da cota dia anterior
                    dybtlg11_3 = elements[4].text # Dividend Yield
                    pvpbtlg11_6 = elements[26].text # P/VP
                    divpcbtlg11_16 = str(
                                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota
                    # print(f"resultado: {btlg11_0}; {varbtlg11}; {dybtlg11_3}; {pvpbtlg11_6}; {divpcbtlg11_16}")
                    
                break
            print(btlg11_0)
            if not all([btlg11_0, dybtlg11_3, pvpbtlg11_6, divpcbtlg11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
        
        arrow_btlg = ""
        aux_btlg = ""
        
        if varbtlg11[0] == "-":
            arrow_btlg = "&#x2B07;"
            aux_btlg = "queda"
        else:
            arrow_btlg = "&#x2B06;"
            aux_btlg = "alta"
                
        variac_btlg11 = (f"Houve {aux_btlg} de <b>{varbtlg11}  {arrow_btlg}</b> na cota do FII BTLG11 (hoje X ontem).")
        #variac_btlg11_aux = (f"<b>VAR {varbtlg11}  {arrow_btlg}</b>")
        
        card_btlg11 = (
            f"Atualizações do Fundo BTLG11:<br><br>"
            f"• Houve {aux_btlg} de {varbtlg11} na cota<br>"
            f"• Valor atual da cota: R$ {btlg11_0}<br>"
            f"• Dividend Yield: {dybtlg11_3}%<br>"
            f"• P/VP: {pvpbtlg11_6}<br>"
            f"• Último rendimento: R$ {divpcbtlg11_16}"
        )
        
        grava_historico.gravar_historico("historico_btlg.json", f"R$ {btlg11_0}")
        historico = grava_historico.ler_historico("historico_btlg.json")
        hist_text_btlg = grava_historico.gerar_texto_historico(historico)

        return card_btlg11, variac_btlg11, hist_text_btlg

    except Exception as e:
        return {"error": str(e)}, 500
