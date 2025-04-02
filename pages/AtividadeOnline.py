import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configuração da página
st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

# Cabeçalho do aluno
st.subheader("Identificação do aluno")
nome_aluno = st.text_input("Nome do Aluno:")
escola = st.text_input("Escola:")
serie = st.selectbox("Série:", ["Escolha..."] + [f"{i}º ano" for i in range(1, 10)])

# Campo para o código da atividade
st.subheader("Código da atividade")
codigo_atividade = st.text_input("Cole o código fornecido pelo professor:")

# Botão para gerar atividades
if st.button("📥 Gerar Atividade"):
    if not codigo_atividade:
        st.warning("Por favor, cole o código da atividade.")
        st.stop()

    codigo_atividade = codigo_atividade.strip().upper()

    # Conectar via API ao Google Sheets
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=creds)

        sheet_id = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
        range_name = "ATIVIDADES_GERADAS!A:C"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

        values = result.get("values", [])
        if not values:
            st.warning("Planilha de atividades vazia.")
            st.stop()

        header = values[0]
        df = pd.DataFrame(values[1:], columns=header)
        df.columns = df.columns.str.strip().str.upper()

        if "CODIGO" not in df.columns or "ATIVIDADE" not in df.columns:
            st.error("A planilha está sem as colunas necessárias (CODIGO, ATIVIDADE).")
            st.stop()

        df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.upper()
        df["ATIVIDADE"] = df["ATIVIDADE"].astype(str).str.strip()

        dados_filtrados = df[
            (df["CODIGO"] == codigo_atividade) &
            (df["ATIVIDADE"].notna()) &
            (df["ATIVIDADE"] != "")
        ]

        if dados_filtrados.empty:
            st.warning("Código inválido ou sem atividades associadas.")
            st.stop()

        # Exibir atividades
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

        # Enviar respostas
        if st.button("📤 Enviar respostas"):
            if not nome_aluno or not escola or serie == "Escolha...":
                st.warning("Por favor, preencha todos os campos antes de enviar.")
                st.stop()

            try:
                envio_creds = Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=["https://www.googleapis.com/auth/spreadsheets"]
                )
                envio_service = build("sheets", "v4", credentials=envio_creds)

                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                linhas = [
                    [timestamp, codigo_atividade, nome_aluno, escola, serie, atividade, resposta]
                    for atividade, resposta in respostas.items()
                ]

                envio_service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range="ATIVIDADES!A1",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": linhas}
                ).execute()

                st.success("✅ Respostas enviadas com sucesso! Obrigado por participar.")
            except Exception as e:
                st.error(f"❌ Erro ao enviar respostas: {e}")

    except Exception as e:
        st.error(f"❌ Erro ao acessar as atividades: {e}")
