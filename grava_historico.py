import datetime
import pytz
import os
from parse_rest.connection import register
from parse_rest.datatypes import Object
from parse_rest.query import QueryResourceDoesNotExist

# Definir a variável de ambiente PARSE_API_ROOT
os.environ["PARSE_API_ROOT"] = "https://parseapi.back4app.com/"

# Configurar a conexão com o Back4App
APPLICATION_ID = os.getenv("APPLICATION_ID")
REST_API_KEY = os.getenv("CLIENT_KEY")
#MASTER_KEY = os.getenv("MASTER_KEY")  # Opcional, use se necessário

register(
    APPLICATION_ID,
    REST_API_KEY,
    #master_key=MASTER_KEY
)

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

# Função para criar uma nova classe dinamicamente
def create_dynamic_class(class_name):
    return type(class_name, (Object,), {})

def obter_nome_classe(sufixo):
    # Exemplo de função para gerar o nome da classe
    return f"Classe_{sufixo}"

def gravar_historico(sufixo, valor, limite_registros=250):
    nome_classe = obter_nome_classe(sufixo)
    ClasseDinamica = create_dynamic_class(nome_classe)
    
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    data_hora_atual = f"{data_atual}\u2003{hora_atual}"
    print(hora_atual)
    novo_registro = {
        "data": data_hora_atual,
        "valor": valor  # Valor já formatado como string
    }

    # Verifica se o último valor é igual ao novo valor
    query = ClasseDinamica.Query.order_by("-createdAt")
    try:
        resultados = query.limit(1).all()
    except QueryResourceDoesNotExist:
        resultados = []

    if resultados and resultados[0].valor == valor:
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return

    # Adiciona o novo registro no Parse
    historico_obj = ClasseDinamica(**novo_registro)
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
    ClasseDinamica = create_dynamic_class(nome_classe)
    
    query = ClasseDinamica.Query.order_by("-createdAt")
    try:
        resultados = query.all()
    except QueryResourceDoesNotExist:
        resultados = []
    historico = [{"data": resultado.data, "valor": resultado.valor} for resultado in resultados]
    return historico

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003{registro["valor"]}' for registro in historico]
    return "<br>".join(linhas)

