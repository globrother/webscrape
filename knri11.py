"""
===== ::: OBTENDO DADOS WEB DO FII KNRI11 ::: ========================================
"""
from flask import jsonify


def get_knri(requests, BeautifulSoup):
    try:
        url = 'https://statusinvest.com.br/fundos-imobiliarios/knri11'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container_divs = soup.find_all('div', class_='container pb-7')
            tags = ['value']

            knri11_0 = dyknri11_3 = pvpknri11_6 = divpcknri11_16 = None

            for div in container_divs:
                for tag in tags:
                    elements = div.find_all(class_=tag)
                    if len(elements) > 4:
                        knri11_0 = elements[0].text
                        dyknri11_3 = elements[3].text
                        pvpknri11_6 = elements[6].text
                        divpcknri11_16 = str(
                            round((float((elements[15].text).replace(',', '.'))), 2)).replace('.', ',')

                        break

            if not all([knri11_0, dyknri11_3, pvpknri11_6, divpcknri11_16]):
                raise ValueError("Unable to scrape all required elements.")
        else:
            raise ConnectionError(f"Erro ao acessar o site: Status Code {
                response.status_code}")

        card_knri11 = (
            "Atualizações do Fundo KNRI11:<br><br>"
            f"• Valor atual da cota: R$ {knri11_0}<br>"
            f"• Dividend Yield: {dyknri11_3}%<br>"
            f"• P/VP: {pvpknri11_6}<br>"
            f"• Último rendimento: R$ {divpcknri11_16}"
        )
        return card_knri11

    except Exception as e:
        return jsonify({"error": str(e)}), 500
