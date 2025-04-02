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

# --- DADOS DAS ATIVIDADES ---
URL_ATIVIDADES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=1069213106&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_atividades():
    try:
        response = requests.get(URL_ATIVIDADES, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=",")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar atividades: {e}")
        return pd.DataFrame()

dados = carregar_atividades()

# --- CÓDIGO DO PROFESSOR ---
st.subheader("Código da atividade")
codigo_atividade = st.text_input("Cole o código fornecido pelo professor:")

if st.button("📥 Gerar Atividade"):
    if not codigo_atividade:
        st.warning("Por favor, cole o código da atividade.")
        st.stop()

    if dados.empty or "CODIGO" not in dados.columns or "ATIVIDADE" not in dados.columns:
        st.error("A planilha de atividades está incompleta ou mal formatada.")
        st.stop()

    dados_filtrados = dados[dados["CODIGO"].str.upper() == codigo_atividade.strip().upper()]

    if dados_filtrados.empty:
        st.warning("Código inválido ou sem atividades associadas.")
        st.stop()

    # --- EXIBIÇÃO DAS QUESTÕES ---
    st.markdown("---")
    st.subheader("Responda cada questão marcando uma das alternativas:")

    respostas = {}
    for idx, row in dados_filtrados.iterrows():
        atividade = row["ATIVIDADE"]
        url = f"https://questoesama.pages.dev/{atividade}.jpg"
        st.image(url, caption=f"Atividade {idx + 1}", use_container_width=True)
        resposta = st.radio(
            label="",  # Remove o texto "Escolha a alternativa..."
            options=["A", "B", "C", "D", "E"],
            key=f"resposta_{idx}",
            index=None
        )
        respostas[atividade] = resposta

    # --- ENVIO DAS RESPOSTAS ---
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

            linhas = []
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for atividade, resposta in respostas.items():
                linhas.append([
                    timestamp,
                    codigo_atividade,
                    nome_aluno,
                    escola,
                    serie,
                    atividade,
                    resposta
                ])

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
