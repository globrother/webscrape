import datetime

nome_arquivo = "historico_xpml.txt"
nome_variavel = "xpml11_0"
xpml11_0 = 101.00
valor = xpml11_0


def gravar_historico(nome_arquivo, valor):
    # Obtém a data atual no formato dd/mm/aaaa
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # Formata a linha a ser gravada no arquivo
    linha = f"{data_atual}:\u2003 R$ {valor:,.2f}\n"
    
    # Abre o arquivo em modo de adição ('a') e escreve a linha
    with open(nome_arquivo, "a", encoding="utf-8") as arquivo:
        arquivo.write(linha)

gravar_historico(nome_arquivo, valor)