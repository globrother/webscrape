"""
===== ::: OBTENDO DADOS WEB DO FII KNRI11 ::: ========================================
"""
import grava_historico

def get_knri(requests, BeautifulSoup):
            
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/knri11'
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

            knri11_0 = varknri11 = dyknri11_3 = pvpknri11_6 = divpcknri11_16 = None

            for div in container_divs:
                # Encontra todos os elementos que têm as classes 'v-align-middle' ou 'value'
                """
                função de critério que está sendo passada para find_all.
                Esta função anônima (lambda) verifica se a tag atual (tag)
                possui a classe v-align-middle ou value em seu atributo class.
                """
                # elements = div.find_all(lambda tag: 'v-align-middle' in tag.get('class', []) or 'value' in tag.get('class', [])) #sem o uso de tags
                elements = div.find_all(lambda tag: any(t in tag.get('class', []) for t in tags)) #com o uso do dicionário tags.
                # print(f"Elements: {elements}")
                if len(elements) > 4:
                    knri11_0 = elements[0].text # Valor atual da cota
                    varknri11 = elements[1].text # Variação da cota dia anterior
                    dyknri11_3 = elements[4].text # Dividend Yield
                    pvpknri11_6 = elements[26].text # P/VP
                    divpcknri11_16 = str(
                                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota
                    
                break
            print(knri11_0)
            if not all([knri11_0, dyknri11_3, pvpknri11_6, divpcknri11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
                
        arrow_knri = ""
        aux_knri = ""
        
        if varknri11[0] == "-":
            arrow_knri = "&#x2B07;"
            aux_knri = "queda"
        else:
            arrow_knri = "&#x2B06;"
            aux_knri = "alta"
                
        variac_knri11 = (f"Houve {aux_knri} de <b>{varknri11}  {arrow_knri}</b> na cota do FII KNRI11 (hoje X ontem).")
        #variac_knri11_aux = (f"<b>{varknri11}  {arrow_knri}</b>")
        
        card_knri11 = (
            f"Atualizações do Fundo KNRI11:<br><br>"
            f"• Houve {aux_knri} de {varknri11} na cota<br>"
            f"• Valor atual da cota: R$ {knri11_0}<br>"
            f"• Dividend Yield: {dyknri11_3}%<br>"
            f"• P/VP: {pvpknri11_6}<br>"
            f"• Último rendimento: R$ {divpcknri11_16}"
        )
        
        grava_historico.gravar_historico("historico_knri.json", f"R$ {knri11_0}")
        historico = grava_historico.ler_historico("historico_knri.json")
        hist_text_knri = grava_historico.gerar_texto_historico(historico)
        
        return card_knri11, variac_knri11, hist_text_knri

    except Exception as e:
        return ({"error": str(e)}), 500
