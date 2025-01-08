import datetime
import json
import os

def gravar_historico(nome_arquivo, valor, limite_registros=100):
    #data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    data_hora_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    novo_registro = {
        "data": data_hora_atual,
        "valor": valor  # Valor já formatado como string
    }

    # Verifica se o arquivo já existe
    if os.path.exists(nome_arquivo):
        try:
            # Lê o conteúdo existente do arquivo JSON
            with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read()
                if conteudo.strip() == "":
                    historico = []
                else:
                    historico = json.loads(conteudo)
        except json.JSONDecodeError:
            historico = []
    else:
        historico = []

    # Verifica se o último valor é igual ao novo valor
    if historico and historico[0]["valor"] == valor:
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return

    # Adiciona o novo registro no início da lista
    historico.insert(0, novo_registro)

    # Mantém apenas os registros mais recentes até o limite especificado
    historico = historico[:limite_registros]

    # Grava a lista atualizada de volta no arquivo JSON
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=4)

# gerando string para o documento APL alexa:

def ler_historico(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
           historico = json.load(arquivo)
        return historico
    else:
        return []

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003 {registro["valor"]}' for registro in historico]
    return "<br>".join(linhas)
