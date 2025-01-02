from bs4 import BeautifulSoup

html = """
<div class="container">
    <strong>Primeiro</strong>
    <strong>Segundo</strong>
    <strong>Terceiro</strong>
    <strong>Quarto</strong>
    <strong>Quinto</strong>
</div>
"""

soup = BeautifulSoup(html, 'html.parser')
div = soup.find('div', class_='container')
elements = div.find_all('strong')

# Acessando elementos específicos por índice
primeiro_elemento = elements[0].text
quarto_elemento = elements[3].text
quinto_elemento = elements[4].text

print(f"Primeiro elemento: {primeiro_elemento}")
print(f"Quarto elemento: {quarto_elemento}")
print(f"Quinto elemento: {quinto_elemento}")
