import datetime
import pytz
import json
import os
from parse_rest.connection import register
from parse_rest.datatypes import Object
from parse_rest.query import Query

# Configurar a conexão com o Back4App
register(
    app_id=os.getenv("APPLICATION_ID"),
    rest_key=os.getenv("CLIENT_KEY"),
    master_key=os.getenv("MASTER_KEY")  # Opcional, use se necessário
)

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

class Historico(Object):
    pass

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
    query = Query(Historico).filter(nome_classe=nome_classe).order_by("-createdAt")
    resultados = query.limit(1).all()

    if resultados and resultados[0].valor == valor:
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return

    # Adiciona o novo registro no Parse
    historico_obj = Historico(nome_classe=nome_classe, **novo_registro)
    historico_obj.save()
    print("\nHistórico gravado com sucesso.\n")

    # Verificar o limite de registros e remover os mais antigos se necessário
    total_registros = query.count()
    if total_registros > limite_registros:
        registros_antigos = query.skip(limite_registros).all()
        for registro in registros_antigos:
            registro.delete()

def ler_historico(sufixo):
    nome_classe = obter_nome_classe(sufixo)
    query = Query(Historico).filter(nome_classe=nome_classe).order_by("-createdAt")
    resultados = query.all()
    historico = [{"data": resultado.data, "valor": resultado.valor} for resultado in resultados]
    return historico

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003{registro["valor"]}' for registro in historico]
    return "<br>".join(linhas)

# Exemplo de uso
sufixo = "xpml"
valor = "Novo valor de exemplo"
gravar_historico(sufixo, valor)
historico = ler_historico(sufixo)
texto_historico = gerar_texto_historico(historico)
print(texto_historico)
