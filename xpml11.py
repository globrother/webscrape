"""
===== ::: OBTENDO DADOS WEB DO FII XPML11 ::: ========================================
"""
def get_element(requests, BeautifulSoup):
    url = 'https://statusinvest.com.br/fundos-imobiliarios/xpml11'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        container_divs = soup.find_all('div', class_='container pb-7')
        tags = ['value']
        
        xpml11_0 = dyxpml11_3 = pvpxpml11_6 = divpcxmpl11_16 = None
        
        for div in container_divs:
            for tag in tags:
                elements = div.find_all(class_=tag)
                if len(elements) > 4:
                    xpml11_0 = elements[0].text
                    dyxpml11_3 = elements[3].text
                    pvpxpml11_6 = elements[6].text
                    divpcxmpl11_16 = elements[15].text
                    break
        
        if not all([xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16]):
            raise ValueError("Unable to scrape all required elements.")
    else:
        raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")

    return xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16