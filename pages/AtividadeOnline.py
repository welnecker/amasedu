# AtividadeOnline.py (nova página substituindo Feedback)
import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="📝")
st.title("📝 Atividade Online")

st.markdown("""
Nesta página, o(a) aluno(a) poderá responder às atividades selecionadas.
As respostas serão registradas automaticamente.
""")

# Dados do cabeçalho
escola = st.text_input("Escola:")
professor = st.text_input("Nome do Professor(a):")
data = st.date_input("Data da Atividade:", value=datetime.today())

# Verifica se há atividades selecionadas
if "atividades_exibidas" not in st.session_state or not st.session_state.atividades_exibidas:
    st.warning("Nenhuma atividade selecionada. Volte e escolha as atividades na página inicial.")
    st.stop()

# Importa novamente os dados da planilha de questões
import pandas as pd
import requests
from io import StringIO

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhv1IMZCz0xYYNGiEIlrqzvsELrjozHr32CNYHdcHzVqYWwDUFolet_2XOxv4EX7Tu3vxOB4w-YUX9/pub?gid=2127889637&single=true&output=csv"

@st.cache_data

def carregar_dados():
    try:
        response = requests.get(URL_PLANILHA, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

dados = carregar_dados()
if dados is None:
    st.error("Erro ao carregar atividades. Tente novamente mais tarde.")
    st.stop()

# Formulário de respostas
respostas = {}
st.markdown("## Responda às atividades abaixo:")
for i, idx in enumerate(st.session_state.atividades_exibidas):
    nome = dados.loc[idx, "ATIVIDADE"]
    imagem_url = f"https://questoesama.pages.dev/{nome}.jpg"
    st.image(imagem_url, caption=f"Atividade {i+1}", use_column_width=True)
    respostas[nome] = st.text_area(f"Resposta para a atividade {i+1}", key=f"resposta_{i}")

# Função para salvar as respostas na aba "ATIVIDADES" do Google Sheets
def salvar_respostas(secrets, spreadsheet_id, dados):
    creds = Credentials.from_service_account_info(secrets, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)
    valores = []
    for atividade, resposta in dados["respostas"].items():
        valores.append([
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            dados["escola"],
            dados["professor"],
            dados["data"].strftime("%d/%m/%Y"),
            atividade,
            resposta
        ])

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="ATIVIDADES!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": valores}
    ).execute()

if st.button("📨 Enviar respostas"):
    if not escola or not professor:
        st.warning("Preencha todos os campos do cabeçalho.")
    else:
        try:
            salvar_respostas(
                st.secrets["gcp_service_account"],
                "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                {
                    "escola": escola,
                    "professor": professor,
                    "data": data,
                    "respostas": respostas
                }
            )
            st.success("Respostas enviadas com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")