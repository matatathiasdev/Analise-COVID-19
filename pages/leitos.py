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
## WEB SCRAPING CSV LEITOS HOSPITALARES COVID
url="https://opendatasus.saude.gov.br/dataset/registro-de-ocupacao-hospitalar-covid-19"

req = requests.get(url)
soup = BeautifulSoup(req.text, features="html.parser")

li = [i.split(" ")[0].replace('"',"") for i in str(soup.find_all(href=re.compile('LeitoOcupacao'))).replace('[<a class="resource-url-analytics" ','').split("href=")]
li.pop(0)

l = []
for i in li:
    df = pd.read_csv(BytesIO(requests.get(i).content),
                 encoding='UTF-8',
                 delimiter=',',
                 header=0,
                 decimal='.')
    l.append(df)

df_leitos_hosp_covid = pd.concat(l, axis=0, ignore_index=True)

df_leitos_hosp_covid = df_leitos_hosp_covid.rename(columns={
                                                            'ocupacaoSuspeitoCli':'ocupacao_suspeito_cli',
                                                            'ocupacaoSuspeitoUti':'ocupacao_suspeito_uti',
                                                            'ocupacaoConfirmadoCli':'ocupacao_confirmado_cli',
                                                            'ocupacaoConfirmadoUti':'ocupacao_confirmado_uti',
                                                            'ocupacaoCovidUti':'ocupacao_covid_uti',
                                                            'ocupacaoCovidCli':'ocupacao_covid_cli',
                                                            'ocupacaoHospitalarUti':'ocupacao_hospitalar_uti',
                                                            'ocupacaoHospitalarCli':'ocupacao_hospitalar_cli',
                                                            'saidaSuspeitaObitos':'saida_suspeita_obitos',
                                                            'saidaSuspeitaAltas':'saida_suspeita_altas',
                                                            'saidaConfirmadaObitos':'saida_confirmada_obitos',
                                                            'saidaConfirmadaAltas':'saida_confirmada_altas',
                                                            'estado':'estado',
                                                            'municipio':'municipio',
                                                            '_created_at':'data'})

li = [
        'ocupacao_suspeito_cli',
        'ocupacao_suspeito_uti',
        'ocupacao_confirmado_cli',
        'ocupacao_confirmado_uti',
        'ocupacao_covid_uti',
        'ocupacao_covid_cli',
        'ocupacao_hospitalar_uti',
        'ocupacao_hospitalar_cli',
        'saida_suspeita_obitos',
        'saida_suspeita_altas',
        'saida_confirmada_obitos',
        'saida_confirmada_altas',
        'estado',
        'municipio',
        'data']


df_leitos_hosp_covid = df_leitos_hosp_covid[li]

df_leitos_hosp_covid = df_leitos_hosp_covid.replace([np.inf, -np.inf, np.nan], 0)

df_leitos_hosp_covid['ocupacao_cli_total'] = (df_leitos_hosp_covid['ocupacao_suspeito_cli'] + 
                                              df_leitos_hosp_covid['ocupacao_confirmado_cli'] + 
                                              df_leitos_hosp_covid['ocupacao_covid_cli'] + 
                                              df_leitos_hosp_covid['ocupacao_hospitalar_cli'])

df_leitos_hosp_covid['ocupacao_uti_total'] = (df_leitos_hosp_covid['ocupacao_suspeito_uti'] + 
                                              df_leitos_hosp_covid['ocupacao_confirmado_uti'] + 
                                              df_leitos_hosp_covid['ocupacao_covid_uti'] + 
                                              df_leitos_hosp_covid['ocupacao_hospitalar_uti'])

l = [
    0,
    'GOIAS'
]
leitos_percentual = df_leitos_hosp_covid[~df_leitos_hosp_covid['estado'].isin(l)].groupby('estado')[['ocupacao_cli_total','ocupacao_uti_total','ocupacao_covid_uti','ocupacao_covid_cli']].sum().reset_index()

leitos_percentual['percentual_uti'] = leitos_percentual['ocupacao_covid_uti'] / leitos_percentual['ocupacao_uti_total']
leitos_percentual['percentual_cli'] = leitos_percentual['ocupacao_covid_cli'] / leitos_percentual['ocupacao_cli_total']

ap1 = leitos_percentual[['estado','percentual_uti']]
ap1 = ap1.rename(columns={'percentual_uti':'vl_percente'})
ap1['status'] = 'Percentual Ocupacao UTI por COVID-19'

ap2 = leitos_percentual[['estado','percentual_cli']]
ap2 = ap2.rename(columns={'percentual_cli':'vl_percente'})
ap2['status'] = 'Percentual Ocupacao Clinica por COVID-19'

leitos_percentual_geral_estados = pd.concat([ap1, ap2])

l = [
    0,
    'GOIAS'
]
leitos_percentual = df_leitos_hosp_covid[~df_leitos_hosp_covid['municipio'].isin(l)].groupby('municipio')[['ocupacao_cli_total','ocupacao_uti_total','ocupacao_covid_uti','ocupacao_covid_cli']].sum().reset_index()

leitos_percentual['percentual_uti'] = leitos_percentual['ocupacao_covid_uti'] / leitos_percentual['ocupacao_uti_total']
leitos_percentual['percentual_cli'] = leitos_percentual['ocupacao_covid_cli'] / leitos_percentual['ocupacao_cli_total']

ap1 = leitos_percentual[['municipio','percentual_uti']]
ap1 = ap1.rename(columns={'percentual_uti':'vl_percente'})
ap1['status'] = 'Percentual Ocupacao UTI por COVID-19'

ap2 = leitos_percentual[['municipio','percentual_cli']]
ap2 = ap2.rename(columns={'percentual_cli':'vl_percente'})
ap2['status'] = 'Percentual Ocupacao Clinica por COVID-19'

leitos_percentual_geral_municipios = pd.concat([ap1, ap2])

## LEITOS HOSPITALARES COVID
fig_leitos_estados = px.histogram(leitos_percentual_geral_estados, 
                                  x="estado", 
                                  y="vl_percente",
                                  color='status', 
                                  barmode='group',
                                  height=400,
                                  title='Leitos por Estados')

fig_leitos_estados.update_layout(yaxis_title='')
fig_leitos_estados.update_layout(xaxis_title='')

fig_leitos_municipios = px.histogram(leitos_percentual_geral_municipios, 
                                     y="municipio", 
                                     x="vl_percente",
                                     color='status', 
                                     barmode='group', 
                                     height=1000,
                                     title='Leitos por Municipios')

fig_leitos_municipios.update_layout(yaxis_title='')
fig_leitos_municipios.update_layout(xaxis_title='')

with aba3:
     tabela_ativa = 3
     st.plotly_chart(fig_leitos_estados, use_container_width=True)
     st.plotly_chart(fig_leitos_municipios, use_container_width=True)
             