
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# --- IDENTIFICAÇÃO DO ALUNO ---
st.subheader("Identificação do aluno")
nome_aluno = st.text_input("Nome do Aluno:")
escola = st.text_input("Escola:")
serie = st.selectbox("Série:", ["Escolha..."] + [f"{i}º ano" for i in range(1, 10)])

# --- URL DA PLANILHA COM ATIVIDADES GERADAS ---
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

@st.cache_data(show_spinner=False)
def carregar_atividades_api():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
            range="ATIVIDADES_GERADAS!A:C"
        ).execute()

        values = result.get("values", [])
        if not values or len(values) < 2:
            return pd.DataFrame(columns=["CODIGO", "ATIVIDADE", "TIMESTAMP"])

        df = pd.DataFrame(values[1:], columns=values[0])
        df.columns = df.columns.str.strip().str.upper()

        # Verificação das colunas essenciais
        if not {"CODIGO", "ATIVIDADE"}.issubset(df.columns):
            st.error("A planilha está sem as colunas necessárias (CODIGO, ATIVIDADE).")
            return pd.DataFrame()

        df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.upper()
        df["ATIVIDADE"] = df["ATIVIDADE"].astype(str).str.strip()

        return df[["CODIGO", "ATIVIDADE"]]
    
    except Exception as e:
        st.error(f"❌ Erro ao acessar a API do Google Sheets: {e}")
        return pd.DataFrame()

# Carrega as atividades via API agora
dados = carregar_atividades_api()


# --- CÓDIGO DO PROFESSOR ---
st.subheader("Código da atividade")
codigo_atividade = st.text_input("Cole o código fornecido pelo professor:")

if st.button("📥 Gerar Atividade"):
    if not codigo_atividade.strip():
        st.warning("Por favor, cole o código da atividade.")
        st.stop()
    st.session_state.codigo_confirmado = codigo_atividade.strip().upper()

# Após clique, continua com a lógica mesmo após o reload
if "codigo_confirmado" in st.session_state:
    codigo_atividade = st.session_state.codigo_confirmado

    if "CODIGO" not in dados.columns or "ATIVIDADE" not in dados.columns:
        st.error("A planilha está sem as colunas necessárias (CODIGO, ATIVIDADE).")
        st.stop()

    dados["CODIGO"] = dados["CODIGO"].astype(str).str.strip().str.upper()
    dados["ATIVIDADE"] = dados["ATIVIDADE"].astype(str).str.strip()

    dados_filtrados = dados[
        (dados["CODIGO"] == codigo_atividade) &
        (dados["ATIVIDADE"].notna()) &
        (dados["ATIVIDADE"] != "")
    ]

    if dados_filtrados.empty:
        st.warning("Código inválido ou sem atividades associadas.")
        st.stop()

    st.markdown("---")
    st.subheader("Responda cada questão marcando uma das alternativas:")

    respostas = {}
    for idx, row in dados_filtrados.iterrows():
        atividade = row["ATIVIDADE"]
        url = f"https://questoesama.pages.dev/{atividade}.jpg"
        st.image(url, caption=f"Atividade {idx + 1}", use_container_width=True)
        resposta = st.radio(
            label="",
            options=["A", "B", "C", "D", "E"],
            key=f"resposta_{idx}",
            index=None
        )
        respostas[atividade] = resposta

    if st.button("📤 Enviar respostas"):
        if not nome_aluno or escola.strip() == "" or serie == "Escolha...":
            st.warning("Por favor, preencha todos os campos antes de enviar.")
            st.stop()

        try:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            service = build("sheets", "v4", credentials=creds)

            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            linhas = [
                [timestamp, codigo_atividade, nome_aluno, escola, serie, atividade, resposta]
                for atividade, resposta in respostas.items()
            ]

            service.spreadsheets().values().append(
                spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                range="ATIVIDADES!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": linhas}
            ).execute()

            st.success("Respostas enviadas com sucesso! Obrigado por participar.")
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")
