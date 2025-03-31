# .\venv\Scripts\activate
# streamlit run dashboard.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = "wide")

def formata_numero(valor, prefixo = ""):
    for unidade in ["", "mil"]:
        if valor < 1000:
            return f"{prefixo} {valor:.2f} {unidade}"
        valor /= 1000
    return f"{prefixo} {valor:.2f} milhões"

st.title("DASHBOARD DE VENDAS :shopping_trolley:")

## DataFrame
url = "https://labdados.com/produtos"
regioes = ["Brasil", "Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"]

st.sidebar.title("Filtros")
regiao = st.sidebar.selectbox("Região", regioes)

if regiao == "Brasil":
    regiao = ""

todos_anos = st.sidebar.checkbox("Dados de todo o período", value = True)
if todos_anos:
    ano = ""
else:
    ano = st.sidebar.slider("Ano", 2020, 2023)

query_string = {"regiao": regiao.lower(), "ano": ano}

response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados["Data da Compra"] = pd.to_datetime(dados["Data da Compra"], format = "%d/%m/%Y")

filtro_vendedores = st.sidebar.multiselect("Vendedores", dados["Vendedor"].unique())
if filtro_vendedores:
    dados = dados[dados["Vendedor"].isin(filtro_vendedores)]

## Tabelas
### Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index("Data da Compra").groupby(pd.Grouper(freq = "M"))["Preço"].sum().reset_index()
receita_mensal["Ano"] = receita_mensal["Data da Compra"].dt.year
receita_mensal["Mes"] = receita_mensal["Data da Compra"].dt.month_name()

receita_categorias = dados.groupby("Categoria do Produto")[["Preço"]].sum().sort_values("Preço", ascending = False)

### Tabelas de quantidades de Vendas
quantidade_vedas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
quantidade_vedas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(quantidade_vedas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

quantidade_vendas_mensal = dados.set_index("Data da Compra").groupby(pd.Grouper(freq = "M"))["Preço"].count().reset_index()
quantidade_vendas_mensal["Ano"] = quantidade_vendas_mensal["Data da Compra"].dt.year
quantidade_vendas_mensal["Mes"] = quantidade_vendas_mensal["Data da Compra"].dt.month_name()

quantidade_vendas_categorias = dados.groupby("Categoria do Produto")[["Preço"]].count().sort_values("Preço", ascending = False)

### Tabelas Vendedores
vendedores = pd.DataFrame(dados.groupby("Vendedor")["Preço"].agg(["sum","count"]))

## Gráficos
### Grrafico Receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = "Mes",
                             y = "Preço",
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = "Ano",
                             line_dash = "Ano",
                             title = "Receita Mensal")
fig_receita_mensal.update_layout(yaxis_title = "Receita")

fig_receita_estados = px.bar(receita_estados.head(),
                             x = "Local da compra",
                             y = "Preço",
                             text_auto = True,
                             title = "Top Estados (Receita)")
fig_receita_estados.update_layout(yaxis_title = "Receita")

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = "Receita por Categorias",)
fig_receita_categorias.update_layout(yaxis_title = "Receita")

###Gráficos Quantidade de Vendas
fig_mapa_quantidade_venda = px.scatter_geo(quantidade_vedas_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Quantidade de Vendas por Estado')

fig_quantidade_vendas_estados = px.bar(quantidade_vedas_estados.head(),
                             x = "Local da compra",
                             y = "Preço",
                             text_auto = True,
                             title = "Top Estados (Quantidade de Vendas)")
fig_quantidade_vendas_estados.update_layout(yaxis_title = "Quantidade de Vendas")

fig_quantidade_venda_mensal = px.line(quantidade_vendas_mensal,
                             x = "Mes",
                             y = "Preço",
                             markers = True,
                             range_y = (0, quantidade_vendas_mensal.max()),
                             color = "Ano",
                             line_dash = "Ano",
                             title = "Quantidade de Venda Mensal")
fig_quantidade_venda_mensal.update_layout(yaxis_title = "Quantidade")

fig_quantidade_vedas_categorias = px.bar(quantidade_vendas_categorias,
                                text_auto = True,
                                title = "Quantidade de Vendas por Categorias",)
fig_quantidade_vedas_categorias.update_layout(yaxis_title = "Quantidade")


###Graficos Vendedores
qtd_vendedores = st.number_input("Quantidade de vendedores", 2, 10, 5)

fig_receita_vendedores = px.bar(vendedores[["sum"]].sort_values("sum", ascending = True).head(qtd_vendedores),
                                        x = "sum",
                                        y = vendedores[["sum"]].sort_values("sum", ascending = True).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f"Top {qtd_vendedores} vendedores (receita).")

fig_vendas_vendedores = px.bar(vendedores[["count"]].sort_values("count", ascending = True).head(qtd_vendedores),
                                        x = "count",
                                        y = vendedores[["count"]].sort_values("count",ascending = True).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f"Top {qtd_vendedores} vendedores (quantidade de vendas).")

# Visualizacao Streamlit
aba1, aba2, aba3 = st.tabs(["Receita", "Quantidade de Vendas", "Vendedores"])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_quantidade_venda, use_container_width = True)
        st.plotly_chart(fig_quantidade_vendas_estados, use_container_width = True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_quantidade_venda_mensal, use_container_width = True)
        st.plotly_chart(fig_quantidade_vedas_categorias, use_container_width = True)

with aba3:  
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_vendedores)


st.dataframe(dados)