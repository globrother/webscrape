import http.client
import json

# Configurações das chaves
APPLICATION_ID = "m8jLEFk7pcs3PHm8MZmZFGtHKKUqpJLqjMtLF6Hz"
REST_API_KEY = "FGGS3m6YvCktVe0ezRFJReQrIu9vEw3Vb9Zk0c0V"

# Conexão ao servidor Back4App
connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
connection.connect()

# Requisição GET para recuperar objetos da classe GameScore
connection.request('GET', '/classes/GameScore', '', {
    "X-Parse-Application-Id": APPLICATION_ID,
    "X-Parse-REST-API-Key": REST_API_KEY
})

# Processar a resposta e imprimir os resultados
result = json.loads(connection.getresponse().read())
print(result)
