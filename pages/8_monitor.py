import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

# Definindo senha para proteção
def autenticar_usuario():
    senha = st.text_input("Digite a senha:", type="password")
    if senha != "141267Jdw@":
        st.warning("Senha incorreta! Tente novamente.")
        st.stop()

# Função para carregar os dados da planilha
def carregar_dados_planilha():
    creds = Credentials.from_service_account_file(
        "apt-memento-450610-v4-8291f78192e8.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)
    
    # Carregar dados das atividades geradas
    result_atividades = service.spreadsheets().values().get(
        spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
        range="ATIVIDADES_GERADAS!A1:Z"
    ).execute()
    atividades_data = result_atividades.get("values", [])

    # Carregar dados das respostas
    result_respostas = service.spreadsheets().values().get(
        spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
        range="ATIVIDADES!A1:Z"
    ).execute()
    respostas_data = result_respostas.get("values", [])
    
    return atividades_data, respostas_data

# Função para exibir tabelas e gráficos
def exibir_tabelas_graficos(atividades_data, respostas_data):
    # Converter para DataFrame para manipulação
    df_atividades = pd.DataFrame(atividades_data[1:], columns=atividades_data[0])
    df_respostas = pd.DataFrame(respostas_data[1:], columns=respostas_data[0])

    # Exibir tabelas
    st.subheader("📋 Tabela de Atividades Geradas")
    st.dataframe(df_atividades)

    st.subheader("📋 Tabela de Respostas Enviadas")
    st.dataframe(df_respostas)

    # Exibir gráfico de respostas enviadas ao longo do tempo
    st.subheader("📊 Respostas Enviadas por Período")
    df_respostas["Data"] = pd.to_datetime(df_respostas["Data"])  # Supondo que a data esteja na coluna 'Data'
    respostas_por_data = df_respostas.groupby(df_respostas["Data"].dt.date).size()
    fig_respostas = px.bar(respostas_por_data, title="Respostas enviadas por data")
    st.plotly_chart(fig_respostas)

    # Exibir gráfico de acertos e erros
    st.subheader("📊 Acertos e Erros")
    acertos = df_respostas["Resultado"].value_counts()  # Supondo que a coluna 'Resultado' tenha 'Certo' ou 'Errado'
    fig_acertos = px.pie(acertos, names=acertos.index, values=acertos.values, title="Distribuição de Acertos e Erros")
    st.plotly_chart(fig_acertos)

# Início do aplicativo
st.set_page_config(page_title="Monitoramento", page_icon="🔍")
st.title("📊 Monitoramento de Atividades AMA 2025")

# Verificação de senha
autenticar_usuario()

# Carregar e exibir os dados em tempo real
atividades_data, respostas_data = carregar_dados_planilha()
exibir_tabelas_graficos(atividades_data, respostas_data)
