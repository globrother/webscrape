import datetime
import pytz
import os
from parse_rest.datatypes import Function, Object, GeoPoint
from parse_rest.connection import register
from parse_rest.query import QueryResourceDoesNotExist, Queryset
from parse_rest.connection import ParseBatcher
from parse_rest.core import ResourceRequestBadRequest, ParseError

import logging

# Usar o logger para registrar mensagens
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info('Função Gravar iniciada')

# Definir a variável de ambiente PARSE_API_ROOT
os.environ["PARSE_API_ROOT"] = "https://parseapi.back4app.com/"

# Configurar a conexão com o Back4App
APPLICATION_ID = os.getenv("APPLICATION_ID")
REST_API_KEY = os.getenv("CLIENT_KEY")
#MASTER_KEY = os.getenv("MASTER_KEY")

register(
    APPLICATION_ID,
    REST_API_KEY,
    master_key=None
)

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

# Função para criar uma nova classe dinamicamente
def create_dynamic_class(class_name):
    return Object.factory(class_name)

def obter_nome_classe(sufixo):
    # Exemplo de função para gerar o nome da classe
    return f"historico_{sufixo}"

def gravar_historico(sufixo, valor, limite_registros=250):
    nome_classe = obter_nome_classe(sufixo)
    ClasseDinamica = create_dynamic_class(nome_classe)
    
    logger.info(f"Função Gravar iniciada: {nome_classe}")
    
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    data_hora_atual = f"{data_atual}\u2003{hora_atual}"
    print(hora_atual)
    novo_registro = {
        "data": data_hora_atual,
        "valor": valor  # Valor já formatado como string
    }

    # Verifica se o último valor é igual ao novo valor
    try:
        resultados = ClasseDinamica.Query.filter(data=data_hora_atual).order_by("-createdAt").limit(1).all()
        logger.info(f"#### O novo registro é: {novo_registro}")
        logger.info(f"Resultado se valor igual: {resultados}")
    except QueryResourceDoesNotExist:
        resultados = []

    if resultados and resultados[0].valor == valor:
        logger.info(f"Valor na tabela: {valor}")
        logger.info(f"Valor zero da tabela: {resultados[0].valor}")
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return

    # Adiciona o novo registro no Parse
    historico_obj = ClasseDinamica(**novo_registro)
    historico_obj.save()
    print("\nHistórico gravado com sucesso.\n")

    # Verificar o limite de registros e remover os mais antigos se necessário
    total_registros = ClasseDinamica.Query.all().count()
    if total_registros > limite_registros:
        registros_antigos = ClasseDinamica.Query.all().order_by("-createdAt").skip(limite_registros).all()
        for registro in registros_antigos:
            registro.delete()

def ler_historico(sufixo):
    nome_classe = obter_nome_classe(sufixo)
    ClasseDinamica = create_dynamic_class(nome_classe)
    
    try:
        query = ClasseDinamica.Query.all().order_by("-createdAt")
        resultados = query.all()
    except QueryResourceDoesNotExist:
        resultados = []
    historico = [{"data": resultado.data, "valor": resultado.valor} for resultado in resultados]
    return historico

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003{registro["valor"]}' for registro in historico]
    return "<br>".join(linhas)