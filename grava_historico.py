import datetime
import pytz
import json
#import parse
import os

#application_id = os.getenv("APPLICATION_ID")
#client_key = os.getenv("CLIENT_KEY")

from parse_rest.connection import register
from parse_rest.datatypes import Object
#from parse_rest.query import Query

# Configurar a conexão com o Back4App
register(
    app_id=os.getenv("APPLICATION_ID"),
    rest_key=os.getenv("CLIENT_KEY"),
    #master_key=os.getenv("MASTER_KEY")  # Opcional, use se necessário
)

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

def obter_nome_classe(sufixo):
    # Exemplo de função para gerar o nome da classe
    return f"historico_{sufixo}"

def gravar_historico(sufixo, valor, limite_registros=250):
    nome_classe = obter_nome_classe(sufixo)
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    data_hora_atual = f"{data_atual}\u2003{hora_atual}"
    print(hora_atual)
    novo_registro = {
        "data": data_hora_atual,
        "valor": valor  # Valor já formatado como string
    }

    # Verifica se o último valor é igual ao novo valor
    query = parse.Query(nome_classe)
    query.descending("createdAt")
    resultados = query.limit(1).find()

    if resultados and resultados[0].get("valor") == valor:
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return

    # Adiciona o novo registro no Parse
    historico_obj = parse.Object(nome_classe)
    historico_obj.set("data", data_hora_atual)
    historico_obj.set("valor", valor)
    historico_obj.save()
    print("\nHistórico gravado com sucesso.\n")

    # Verificar o limite de registros e remover os mais antigos se necessário
    total_registros = query.count()
    if total_registros > limite_registros:
        registros_antigos = query.skip(limite_registros).find()
        for registro in registros_antigos:
            registro.delete()

def ler_historico(sufixo):
    nome_classe = obter_nome_classe(sufixo)
    query = parse.Query(nome_classe)
    query.descending("createdAt")
    resultados = query.find()
    historico = []
    for resultado in resultados:
        registro = {
            "data": resultado.get("data"),
            "valor": resultado.get("valor")
        }
        historico.append(registro)
    return historico

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003{registro["valor"]}' for registro in historico]
    return "<br>".join(linhas)