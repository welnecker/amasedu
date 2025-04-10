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
    try:
        # Carregar credenciais do secrets.toml
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        service = build("sheets", "v4", credentials=creds)
        
        # Carregar dados das atividades geradas
        result_atividades = service.spreadsheets().values().get(
            spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
            range="ATIVIDADES_GERADAS!A1:Z"
        ).execute()
        atividades_data = result_atividades.get("values", [])
        
        return atividades_data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return []

# Função para exibir gráficos
def exibir_grafico_atividades_por_disciplina(atividades_data):
    # Converter para DataFrame para manipulação
    df_atividades = pd.DataFrame(atividades_data[1:], columns=atividades_data[0])

    # Contar as ocorrências de cada valor na coluna 'DISCIPLINA'
    if "DISCIPLINA" in df_atividades.columns:
        atividades_por_disciplina = df_atividades["DISCIPLINA"].value_counts()
        
        # Exibir gráfico de colunas
        fig = px.bar(atividades_por_disciplina, title="Quantidade de Atividades Geradas por Disciplina", labels={'index': 'Disciplina', 'value': 'Quantidade'})
        st.plotly_chart(fig)
    else:
        st.warning("A coluna 'DISCIPLINA' não foi encontrada nos dados.")

# Início do aplicativo
st.set_page_config(page_title="Monitoramento", page_icon="🔍")
st.title("📊 Monitoramento de Atividades AMA 2025")

# Verificação de senha
autenticar_usuario()

# Carregar os dados e gerar gráfico
atividades_data = carregar_dados_planilha()
exibir_grafico_atividades_por_disciplina(atividades_data)
