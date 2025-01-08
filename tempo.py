import datetime

# Obtém a data e hora atual
#data_hora_atual = datetime.now()

# Formata a hora atual
#hora_atual = data_hora_atual.strftime("%H:%M:%S")
data_hora_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

print("Hora Atual:", data_hora_atual)
#print("Hora Atual:", hora_atual)
