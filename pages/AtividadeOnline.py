import streamlit as st
import pandas as pd
import unicodedata
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ⚙️ Configuração inicial da página (deve ser a primeira chamada)
st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")

st.title("💡 Atividade Online - AMA 2025")

# --- Dados do aluno ---
st.subheader("Preencha seus dados abaixo:")
nome_aluno = st.text_input("Nome do Aluno:")
escola = st.text_input("Escola:")
turma = st.text_input("Turma:")

st.subheader("Digite abaixo o código fornecido pelo(a) professor(a):")
codigo_atividade = st.text_input("Código da atividade (ex: ABC123):")

# --- Geração de identificador único ---
def gerar_id_unico(nome, escola, turma, codigo):
    def normalizar(txt):
        txt = txt.lower().strip()
        txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
        return ''.join(c for c in txt if c.isalnum())
    return f"{normalizar(nome)}_{normalizar(escola)}_{normalizar(turma)}_{normalizar(codigo)}"

id_unico = gerar_id_unico(nome_aluno, escola, turma, codigo_atividade)

# --- Armazenar IDs bloqueados ---
if "ids_enviados" not in st.session_state:
    st.session_state.ids_enviados = set()

# --- Carregamento de dados da API do Google Sheets ---
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

        df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.upper()
        df["ATIVIDADE"] = df["ATIVIDADE"].astype(str).str.strip()
        return df[["CODIGO", "ATIVIDADE"]]
    except Exception as e:
        st.error(f"❌ Erro ao acessar a API do Google Sheets: {e}")
        return pd.DataFrame()

dados = carregar_atividades_api()

# --- Geração da atividade ---
if st.button("📥 Gerar Atividade"):
    if not all([nome_aluno.strip(), escola.strip(), turma.strip(), codigo_atividade.strip()]):
        st.warning("⚠️ Por favor, preencha todos os campos antes de visualizar a atividade.")
        st.stop()

    if id_unico in st.session_state.ids_enviados:
        st.warning("❌ Você já fez essa atividade.")
        st.stop()

    st.session_state.codigo_confirmado = codigo_atividade.strip().upper()
    st.session_state.id_unico_atual = id_unico

# --- Exibir questões após confirmação ---
if "codigo_confirmado" in st.session_state:
    codigo_atividade = st.session_state.get("codigo_confirmado")
id_unico = st.session_state.get("id_unico_atual")

if not all([codigo_atividade, id_unico]):
    st.warning("❌ Algo deu errado ao recuperar os dados da atividade.")
    st.stop()


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
    st.subheader("Responda cada questão com atenção, marcando uma das alternativas (você só tem uma tentativa):")

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
        if not all([nome_aluno.strip(), escola.strip(), turma.strip()]):
            st.warning("Por favor, preencha todos os campos antes de enviar.")
            st.stop()

        if any(r is None for r in respostas.values()):
            st.warning("⚠️ Existe alguma questão não respondida!")
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

            st.session_state.ids_enviados.add(id_unico)
            st.success("✅ Respostas enviadas com sucesso! Obrigado por participar.")

            # Limpa a seção para evitar novo envio
            for key in list(st.session_state.keys()):
                if key not in ["ids_enviados"]:
                    del st.session_state[key]

            st.stop()

        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")
