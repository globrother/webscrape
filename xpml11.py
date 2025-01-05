"""
===== ::: OBTENDO DADOS WEB DO FII XPML11 ::: ========================================
"""
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')


def get_xpml(requests, BeautifulSoup):
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/xpml11'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['value']

            xpml11_0 = dyxpml11_3 = pvpxpml11_6 = divpcxpml11_16 = None

            for div in container_divs:
                for tag in tags:
                    elements = div.find_all(class_=tag)
                    if len(elements) > 4:
                        xpml11_0 = elements[0].text
                        dyxpml11_3 = elements[3].text
                        pvpxpml11_6 = elements[6].text
                        divpcxpml11_16 = str(
                            round((float((elements[15].text).replace(',', '.'))), 2)).replace('.', ',')

                        break

            if not all([xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxpml11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {
                response.status_code}")

        """
        voz_xpml11 = (
            f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>"
            f"• Dividend Yield: {dyxpml11_3}%\n<break time='500ms'/>"
            f"• P/VP: {pvpxpml11_6}\n<break time='500ms'/>"
            f"• Último rendimento: R$ {divpcxpml11_16}<break time='1s'/>"
        )
        """

        card_xpml11 = (
            "Atualizações do Fundo XPML11:<br><br>"
            f"• Valor atual da cota: R$ {xpml11_0}<br>"
            f"• Dividend Yield: {dyxpml11_3}%<br>"
            f"• P/VP: {pvpxpml11_6}<br>"
            f"• Último rendimento: R$ {divpcxpml11_16}"
        )
        return card_xpml11

    except Exception as e:
        return {"error": str(e)}, 500
