import plotly.express as px

fig = px.line(x=[1, 2, 3], y=[10, 20, 30])
print("chamando fig.write_image")
fig.write_image("teste.png")
print("finalizando")