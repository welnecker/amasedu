import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# --- IDENTIFICAÇÃO DO ALUNO ---
st.subheader("Identificação do aluno")
nome_aluno = st.text_input("Nome do Aluno:")
escola = st.text_input("Escola:")
turma = st.text_input("Turma:")

# --- CARREGAR ATIVIDADES COM API ---
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

        header = [col.strip().upper() for col in values[0]]
        rows = [row + [None] * (len(header) - len(row)) for row in values[1:]]
        df = pd.DataFrame(rows, columns=header)

        if not {"CODIGO", "ATIVIDADE", "TIMESTAMP"}.issubset(df.columns):
            st.error("A planilha precisa conter as colunas: CODIGO, ATIVIDADE, TIMESTAMP.")
            return pd.DataFrame()

        df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.upper()
        df["ATIVIDADE"] = df["ATIVIDADE"].astype(str).str.strip()
        df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], errors="coerce")

        return df[["CODIGO", "ATIVIDADE", "TIMESTAMP"]]
    except Exception as e:
        st.error(f"❌ Erro ao acessar a API do Google Sheets: {e}")
        return pd.DataFrame()

dados = carregar_atividades_api()

# --- CÓDIGO DO PROFESSOR ---
st.subheader("Código fornecido pelo professor")
codigo_atividade = st.text_input("Digite o código da atividade (ex: ABC123):")

# Validação dos dados do aluno antes de mostrar atividades
if st.button("📥 Gerar Atividade"):
    if not all([nome_aluno.strip(), escola.strip(), turma.strip(), codigo_atividade.strip()]):
        st.warning("⚠️ Por favor, preencha todos os campos antes de visualizar a atividade.")
        st.stop()

    st.session_state.codigo_confirmado = codigo_atividade.strip().upper()

# Após confirmação
if "codigo_confirmado" in st.session_state:
    codigo_atividade = st.session_state.codigo_confirmado

    if "CODIGO" not in dados.columns or "ATIVIDADE" not in dados.columns:
        st.error("A planilha está sem as colunas necessárias (CODIGO, ATIVIDADE).")
        st.stop()

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
        if not nome_aluno or escola.strip() == "" or turma.strip() == "":
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
                [timestamp, codigo_atividade, nome_aluno, escola, turma, atividade, resposta]
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
