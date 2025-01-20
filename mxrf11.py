"""
===== ::: OBTENDO DADOS WEB DO FII MXRF11 ::: ========================================
"""
import grava_historico
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

def get_mxrf(requests, BeautifulSoup):
        
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/mxrf11'
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

            mxrf11_0 = varmxrf11 = dymxrf11_3 = pvpmxrf11_6 = divpcmxrf11_16 = None

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
                    mxrf11_0 = elements[0].text # Valor atual da cota
                    varmxrf11 = elements[1].text # Variação da cota dia anterior
                    dymxrf11_3 = elements[4].text # Dividend Yield
                    pvpmxrf11_6 = elements[26].text # P/VP
                    divpcmxrf11_16 = str(
                                        round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',') # Dividendo por cota
                    # print(f"resultado: {mxrf11_0}; {varmxrf11}; {dymxrf11_3}; {pvpmxrf11_6}; {divpcmxrf11_16}")
                    
                    break
            print(mxrf11_0)
            if not all([mxrf11_0, dymxrf11_3, pvpmxrf11_6, divpcmxrf11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")
        
        arrow_mxrf = ""
        aux_mxrf = ""
        
        if varmxrf11[0] == "-":
            arrow_mxrf = "&#x2B07;"
            aux_mxrf = "queda"
        else:
            arrow_mxrf = "&#x2B06;"
            aux_mxrf = "alta"
                
        variac_mxrf11 = (f"Houve {aux_mxrf} de <b>{varmxrf11}  {arrow_mxrf}</b> na cota do FII MXRF11 (hoje X ontem).")
        #variac_mxrf11_aux = (f"<b>VAR {varmxrf11}  {arrow_mxrf}</b>")
        
        card_mxrf11 = (
            f"Atualizações do Fundo MXRF11:<br><br>"
            f"• Houve {aux_mxrf} de {varmxrf11} na cota<br>"
            f"• Valor atual da cota: R$ {mxrf11_0}<br>"
            f"• Dividend Yield: {dymxrf11_3}%<br>"
            f"• P/VP: {pvpmxrf11_6}<br>"
            f"• Último rendimento: R$ {divpcmxrf11_16}"
        )
        
        grava_historico.gravar_historico("historico_mxrf.json", f"R$ {mxrf11_0}")
        historico = grava_historico.ler_historico("historico_mxrf.json")
        hist_text_mxrf = grava_historico.gerar_texto_historico(historico)

        return card_mxrf11, variac_mxrf11, hist_text_mxrf

    except Exception as e:
        return {"error": str(e)}, 500
