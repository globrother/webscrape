import datetime
import pytz
import json
import os

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

def gravar_historico(nome_arquivo, valor, limite_registros=100):
    #data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    #data_hora_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    data_hora_atual = f"{data_atual}\u2003{hora_atual}"
    print(hora_atual)
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
                   # print("\nArquivo histórico lido com sucesso.\n")
        except json.JSONDecodeError:
            print("Erro ao decodificar o arquivo JSON.")
            historico = []
    else:
        historico = []

    #print(f"/nHistórico atual: \n{historico}\n")
    
    # Verifica se o último valor é igual ao novo valor
    if historico and historico[0]["valor"] == valor:
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return # Se valor for igual a função se encerra aqui

    # Adiciona o novo registro no início da lista
    historico.insert(0, novo_registro)

    # Mantém apenas os registros mais recentes até o limite especificado
    historico = historico[:limite_registros]
    
    #print(f"\nHistórico atualizado: {historico}\n")

    # Grava a lista atualizada de volta no arquivo JSON
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=4)
        #print("\nHistórico gravado com sucesso.\n")

# gerando string para o documento APL alexa:

def ler_historico(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
           historico = json.load(arquivo)
           print("Passareis")
        return historico
    else:
        return []

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003{registro["valor"]}' for registro in historico]
    print("Passamos")
    return "<br>".join(linhas)
