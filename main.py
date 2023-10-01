## BIBLIOTECAS
from st_pages import Page, add_page_title, show_pages
from pandas import json_normalize
from bs4 import BeautifulSoup
from io import BytesIO

import urllib.request, json
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import requests
import urllib
import re

# LIMPAR O CASH DA PAGINA INICIAL
main = st.container()
body = main.container()
body.empty()  # +++
code_container = main.container()
code_container.empty()
state = main.container()

# ARRUMAR OS NOMES DAS ABAS
show_pages(
    [
        Page("main.py", "DASHBOARD COVID-19", ":hospital:"),
        Page("pages/leitos.py", "LEITOS", "🛏️"),
        Page("pages/vacinacao.py", "VACINAÇÃO", "💉")
    ]
)

# ADDICIONAR A PAGINA E AJUSTAR O SEU LAYOUT DA PAGINA
add_page_title(layout="wide")


# FUNCAO FORMATA NUMERO
def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.3f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.3f} milhões'

# shopping_trolley ADCIONAR UM EMOJI DE UM CARRINHO DE COMPRA 
# st.title('DASHBOARD COVID-19 :hospital:')

# DADOS
## ACESSAR DADOS DA API DO COVID POR ESTADO
url = 'https://covid19-brazil-api.now.sh/api/report/v1'
headers = {}

req = requests.request('GET', url,  headers=headers)

info = json.loads(req.text)
items = info['data']

df_api_covid = json_normalize(data=items,
                              meta =['uid','uf','state','cases','deaths','suspects','refuses','datetime'])

df_api_covid = df_api_covid.rename(columns={
                                            'state':'estado',
                                            'cases':'casos',
                                            'deaths':'mortes',
                                            'suspects':'suspeitas',
                                            'refuses':'recusas',
                                            'datetime':'data'})

# CRIA O MENU LATERAL DE FILTROS
st.sidebar.title('Filtros')

# # LIMPAR FILTROS
# if st.sidebar.button("Limpar Filtros"):
#     st.rerun()

## CRIAR FILTRO DE NOME DO PRODUTO    
with st.sidebar.expander('Estados'):
    estados = st.multiselect('Selecione os estados', 
                             options=df_api_covid['estado'].unique(),
                             default=df_api_covid['estado'].unique())

## VALIDAR SE TODOS OS ESTADOS ESTAO SELECIONADOS
if len(estados) > 0:
    estados = estados 
else:
    estados = df_api_covid['estado'].unique()

# APLICANDO OS FILTROS 
## CRIA A QUERY PARA OS FILTROS
query = '''
    estado in @estados
'''

## APLICA OS FILTROS DA QUERY
df_api_covid = df_api_covid.query(query)

### CASOS
qtd_casos = df_api_covid.groupby('estado')[['casos']].sum().sort_values('estado', ascending=True)
qtd_casos['vl_casos'] = qtd_casos['casos'].map("{:,.0f}".format)
qtd_casos['vl_casos'] = qtd_casos['vl_casos'] .apply(lambda x: str(x).replace(',','.'))

### RECUSAS
qtd_recusas = df_api_covid.groupby('estado')[['recusas']].sum().sort_values('estado', ascending=True)
qtd_recusas['vl_recusas'] = qtd_recusas['recusas'].map("{:,.0f}".format)
qtd_recusas['vl_recusas'] = qtd_recusas['vl_recusas'] .apply(lambda x: str(x).replace(',','.'))

### SUSPEITAS
qtd_suspeitas = df_api_covid.groupby('estado')[['suspeitas']].sum().sort_values('estado', ascending=True)
qtd_suspeitas['vl_suspeitas'] = qtd_suspeitas['suspeitas'].map("{:,.0f}".format)
qtd_suspeitas['vl_suspeitas'] = qtd_suspeitas['vl_suspeitas'] .apply(lambda x: str(x).replace(',','.'))

### MORTES
qtd_mortes = df_api_covid.groupby('estado')[['mortes']].sum().sort_values('estado', ascending=True)
qtd_mortes['vl_mortes'] = qtd_mortes['mortes'].map("{:,.0f}".format)
qtd_mortes['vl_mortes'] = qtd_mortes['vl_mortes'] .apply(lambda x: str(x).replace(',','.'))    

# GRAFICOS
## API COVID-19
### CASO
fig_qtd_casos = px.bar(
    qtd_casos,
    x=qtd_casos.index,
    y=qtd_casos.casos,
    text=qtd_casos.vl_casos,
    title='Quantidade de Casos',
    hover_data={'casos': False, 'vl_casos': True}
)

fig_qtd_casos.update_layout(yaxis_title='')
fig_qtd_casos.update_layout(xaxis_title='')
fig_qtd_casos.update_traces(marker_color='rgb(34, 186, 187)')

### RECUSAS
fig_qtd_recusas = px.bar(
    qtd_recusas,
    x=qtd_recusas.index,
    y=qtd_recusas.recusas,
    text=qtd_recusas.vl_recusas,
    title='Quantidade de Recusas',
    hover_data={'recusas': False, 'vl_recusas': True}
)

fig_qtd_recusas.update_layout(yaxis_title='')
fig_qtd_recusas.update_layout(xaxis_title='')
fig_qtd_recusas.update_traces(marker_color='rgb(158, 248, 238)')

### SUSPEITAS
fig_qtd_suspeitas = px.bar(
    qtd_suspeitas,
    x=qtd_suspeitas.index,
    y=qtd_suspeitas.suspeitas,
    text=qtd_suspeitas.vl_suspeitas,
    title='Quantidade de suspeitas',
    hover_data={'suspeitas': False, 'vl_suspeitas': True}
)

fig_qtd_suspeitas.update_layout(yaxis_title='')
fig_qtd_suspeitas.update_layout(xaxis_title='')
fig_qtd_suspeitas.update_traces(marker_color='rgb(250, 127, 8)')

### MORTES
fig_qtd_mortes = px.bar(
    qtd_mortes,
    x=qtd_mortes.index,
    y=qtd_mortes.mortes,
    text=qtd_mortes.vl_mortes,
    title='Quantidade de mortes',
    hover_data={'mortes': False, 'vl_mortes': True}
    )

fig_qtd_mortes.update_layout(yaxis_title='')
fig_qtd_mortes.update_layout(xaxis_title='')
fig_qtd_mortes.update_traces(marker_color='rgb(242, 68, 5)')

# VISUALIZACAO STREAMLIT
coluna1, coluna2 = st.columns(2)
with coluna1:
    st.metric('Caso', formata_numero(df_api_covid['casos'].sum()))
    st.plotly_chart(fig_qtd_casos, use_container_width=True)
    st.metric('Recusas', formata_numero(df_api_covid['recusas'].sum()))
    st.plotly_chart(fig_qtd_recusas, use_container_width=True)
with coluna2:
    st.metric('Mortes', formata_numero(df_api_covid['mortes'].sum()))
    st.plotly_chart(fig_qtd_mortes, use_container_width=True)
    st.metric('Suspeitas', formata_numero(df_api_covid['suspeitas'].sum()))
    st.plotly_chart(fig_qtd_suspeitas, use_container_width=True)

            
