## BIBLIOTECAS
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

# CACHEAR OS DADOS AO ABRIR A PAQUINA
@st.cache_data

# DADOS
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
with aba2:
        tabela_ativa = 2
        coluna1, coluna2 = st.columns(2)
        with coluna1:
             st.plotly_chart(fig_mapa_vacinacao_estados, use_container_width=True)
        with coluna2:
             st.plotly_chart(fig_municipios_vacinacao_estados, use_container_width=True)
        
        st.plotly_chart(fig_vacinacao_dose_estado, use_container_width=True)