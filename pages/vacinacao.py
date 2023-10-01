## BIBLIOTECAS
from st_pages import add_page_title
from pandas import json_normalize
from bs4 import BeautifulSoup
from io import BytesIO

import urllib.request, json
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import pyautogui
import requests
import urllib
import re


add_page_title(layout="wide")

# CACHEAR OS DADOS AO ABRIR A PAQUINA
# @st.cache_data

# DADOS
## LATITUDE E LONGITUDE DOS ESTADOS BRASILEIROS
dados = [
        ["AC","-8.77","-70.55"],
        ["AL","-9.62","-36.82"],
        ["AM","-3.47","-65.10"],
        ["AP","1.41","-51.77"],
        ["BA","-13.29","-41.71"],
        ["CE","-5.20","-39.53"],
        ["DF","-15.83","-47.86"],
        ["ES","-19.19","-40.34"],
        ["GO","-15.98","-49.86"],
        ["MA","-5.42","-45.44"],
        ["MT","-12.64","-55.42"],
        ["MS","-20.51","-54.54"],
        ["MG","-18.10","-44.38"],
        ["PA","-3.79","-52.48"],
        ["PB","-7.28","-36.72"],
        ["PR","-24.89","-51.55"],
        ["PE","-8.38","-37.86"],
        ["PI","-6.60","-42.28"],
        ["RJ","-22.25","-42.66"],
        ["RN","-5.81","-36.59"],
        ["RO","-10.83","-63.34"],
        ["RS","-30.17","-53.50"],
        ["RR","1.99","-61.33"],
        ["SC","-27.45","-50.95"],
        ["SE","-10.57","-37.45"],
        ["SP","-22.19","-48.79"],
        ["TO","-9.46","-48.26"]
]

cols = ["uf","latitude","longitude"]

df_lat_long = pd.DataFrame(data=dados, columns=cols)

## ACESSO API VACINACAO COVID
url = "https://imunizacao-es.saude.gov.br/_search?scroll=10m"

payload = json.dumps({
  "size": 10000
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Basic aW11bml6YWNhb19wdWJsaWM6cWx0bzV0JjdyX0ArI1Rsc3RpZ2k='
}

response = requests.request("GET", url, headers=headers, data=payload)

info = json.loads(response.content)

vl_scroll_id = info['_scroll_id']
vl_took = info['took']
vl_shards_total = info['_shards']['total']
vl_successful = info['_shards']['successful']
vl_total_value = info['hits']['total']['value']
vl_max_score = info['hits']['max_score']

dados = json.loads(response.text)

items = dados['hits']['hits']

df_api_vaci_covid = json_normalize(data=items)

df_api_vaci_covid = df_api_vaci_covid.rename(columns={
                                                        '_source.paciente_endereco_nmMunicipio':'municipio_paciente',
                                                        '_source.paciente_dataNascimento':'data_nascimento',
                                                        '_source.estabelecimento_razaoSocial':'razao_social',
                                                        '_source.estabelecimento_uf':'uf_estabelecimento',
                                                        '_source.paciente_endereco_uf':'uf_endereco_paciente',
                                                        '_source.estalecimento_noFantasia':'nome_estabelecimento',
                                                        '_source.vacina_descricao_dose':'descricao_vacina',
                                                        '_source.vacina_numDose':'num_dose',
                                                        '_source.paciente_enumSexoBiologico':'sexo_biologico_paciente',
                                                        '_source.paciente_idade':'idade_paciente',
                                                        '_source.vacina_nome':'nome_vacina',
                                                        '_source.paciente_racaCor_valor':'cor_paciente',
                                                        '_source.paciente_endereco_nmPais':'pais_paciente'})

li = [
    'municipio_paciente',
    'data_nascimento',
    'razao_social',
    'uf_estabelecimento',
    'uf_endereco_paciente',
    'nome_estabelecimento',
    'descricao_vacina',
    'num_dose',
    'sexo_biologico_paciente',
    'idade_paciente',
    'nome_vacina',
    'cor_paciente',
    'pais_paciente'
]

df_api_vaci_covid = df_api_vaci_covid[li]

# CRIA O MENU LATERAL DE FILTROS
st.sidebar.title('Filtros')

# LIMPAR FILTROS
if st.sidebar.button("Limpar Filtros"):
    pyautogui.hotkey("ctrl","F5")

## CRIAR FILTRO DE NOME DO PRODUTO    
with st.sidebar.expander('Estados'):
    uf_endereco_paciente = st.multiselect('Selecione os estados', 
                             options=df_api_vaci_covid['uf_endereco_paciente'].unique(),
                             default=df_api_vaci_covid['uf_endereco_paciente'].unique())

## VALIDAR SE TODOS OS ESTADOS ESTAO SELECIONADOS
if len(uf_endereco_paciente) > 0:
    uf_endereco_paciente = uf_endereco_paciente 
else:
    uf_endereco_paciente = df_api_vaci_covid['uf_endereco_paciente'].unique()

# APLICANDO OS FILTROS 
## CRIA A QUERY PARA OS FILTROS
query = '''
    uf_endereco_paciente in @uf_endereco_paciente
'''

query2 = '''
    uf in @uf_endereco_paciente
'''

## APLICA OS FILTROS DA QUERY
df_api_vaci_covid = df_api_vaci_covid.query(query)
df_lat_long = df_lat_long.query(query2)

vacinacao_estados = df_api_vaci_covid.groupby('uf_endereco_paciente')[['municipio_paciente']].size().reset_index(name="count")

vacinacao_estados = pd.merge(vacinacao_estados,
                             df_lat_long,
                             how='inner',
                             left_on=['uf_endereco_paciente'],
                             right_on=['uf']).drop(columns=['uf'])

vacinacao_estados = vacinacao_estados.drop_duplicates(subset='uf_endereco_paciente')[['uf_endereco_paciente','latitude','longitude','count']].sort_values('count', ascending=False)

l = [
    ''
]
vacinacao_municipio = df_api_vaci_covid.groupby(['municipio_paciente'])['num_dose'].count().reset_index(name="Total")
vacinacao_municipio = vacinacao_municipio[~vacinacao_municipio['municipio_paciente'].isin(l)].sort_values('Total', ascending=False)
vacinacao_municipio = vacinacao_municipio.head(10).sort_values('Total', ascending=True)
vacinacao_municipio.set_index('municipio_paciente', inplace=True)

l = [
    '',
    'XX'
]
vacinacao_dose_estado = df_api_vaci_covid.groupby(['uf_endereco_paciente','descricao_vacina'])['num_dose'].count().reset_index(name="Total")
vacinacao_dose_estado = vacinacao_dose_estado[~vacinacao_dose_estado['uf_endereco_paciente'].isin(l)].sort_values('Total', ascending=False)

# GRAFICOS
## API VACINACAO COVID-19
fig_mapa_vacinacao_estados = px.scatter_geo(
                                            vacinacao_estados,
                                            lat='latitude',
                                            lon='longitude',
                                            scope='south america',
                                            size='count',
                                            template='seaborn',
                                            hover_name='uf_endereco_paciente',
                                            hover_data={'latitude':False, 'longitude':False},
                                            title='Vacinacao por Estado')

fig_mapa_vacinacao_estados.update_layout(yaxis_title='')
fig_mapa_vacinacao_estados.update_traces(marker_color='rgb(34, 186, 187)')

# fig_mapa_vacinacao_estados.update_layout(width=1000, height=500)

fig_municipios_vacinacao_estados = px.bar(
                                            vacinacao_municipio,
                                            x=vacinacao_municipio.Total,
                                            y=vacinacao_municipio.index,
                                            text=vacinacao_municipio.Total,
                                            title='Vacinacao por Municipio',
                                            )

fig_municipios_vacinacao_estados.update_layout(yaxis_title='')
fig_municipios_vacinacao_estados.update_layout(xaxis_title='')
fig_municipios_vacinacao_estados.update_traces(marker_color='rgb(158, 248, 238)')

fig_vacinacao_dose_estado = px.bar(vacinacao_dose_estado, 
                                   x="uf_endereco_paciente", 
                                   y="Total", 
                                   color="descricao_vacina", 
                                   title='Vacinacao por Dose')

fig_vacinacao_dose_estado.update_layout(yaxis_title='')
fig_vacinacao_dose_estado.update_layout(xaxis_title='')

# VISUALIZACAO STREAMLIT
coluna1, coluna2 = st.columns(2)
with coluna1:
      st.plotly_chart(fig_mapa_vacinacao_estados, use_container_width=True)
with coluna2:
      st.plotly_chart(fig_municipios_vacinacao_estados, use_container_width=True)

st.plotly_chart(fig_vacinacao_dose_estado, use_container_width=True)