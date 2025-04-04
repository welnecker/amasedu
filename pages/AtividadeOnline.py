import streamlit as st
import pandas as pd
from datetime import datetime
import unicodedata
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")

st.subheader("Preencha seus dados abaixo:")
nome_aluno = st.text_input("Nome do Aluno:")
escola = st.text_input("Escola:")
turma = st.text_input("Turma:")
st.subheader("Digite abaixo o código fornecido pelo(a) professor(a):")
codigo_atividade = st.text_input("Código da atividade (ex: ABC123):")

def normalizar_texto(txt):
    txt = txt.lower().strip()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return ''.join(c for c in txt if c.isalnum())

def gerar_id_unico(nome, escola, turma, codigo):
    return f"{normalizar_texto(nome)}_{normalizar_texto(escola)}_{normalizar_texto(turma)}_{normalizar_texto(codigo)}"

@st.cache_data(show_spinner=False)
def carregar_atividades():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
            range="ATIVIDADES_GERADAS!A1:Z"
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return pd.DataFrame(columns=["CODIGO"])
        header = [col.strip().upper() for col in values[0]]
        rows = [row + [None] * (len(header) - len(row)) for row in values[1:]]
        df = pd.DataFrame(rows, columns=header)
        df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar atividades: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def carregar_gabarito():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
            range="MATEMATICA!A1:N"
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return pd.DataFrame(columns=["ATIVIDADE", "GABARITO"])
        header = [col.strip().upper() for col in values[0]]
        rows = [row + [None] * (len(header) - len(row)) for row in values[1:]]
        df = pd.DataFrame(rows, columns=header)
        df["ATIVIDADE"] = df["ATIVIDADE"].astype(str).str.strip()
        df["GABARITO"] = df["GABARITO"].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar gabarito: {e}")
        return pd.DataFrame()

if "respostas_enviadas" not in st.session_state:
    st.session_state.respostas_enviadas = set()

if "respostas_salvas" not in st.session_state:
    st.session_state.respostas_salvas = {}

dados = carregar_atividades()

id_unico = gerar_id_unico(nome_aluno, escola, turma, codigo_atividade)
codigo_valido = bool(dados[dados["CODIGO"] == codigo_atividade.upper()].shape[0])

if id_unico in st.session_state.respostas_enviadas:
    st.warning("❌ Você já fez a atividade com esse código.")
else:
    if st.button("📥 Gerar Atividade") and not st.session_state.get("atividades_em_exibicao"):
        if not all([nome_aluno.strip(), escola.strip(), turma.strip(), codigo_atividade.strip()]):
            st.warning("⚠️ Por favor, preencha todos os campos.")
            st.stop()
        if not codigo_valido:
            st.warning("⚠️ Código da atividade inválido.")
            st.stop()
        st.session_state["atividades_em_exibicao"] = True
        st.rerun()

if st.session_state.get("atividades_em_exibicao"):
    linha = dados[dados["CODIGO"] == codigo_atividade.upper()]
    atividades = [linha[col].values[0] for col in linha.columns if col.startswith("ATIVIDADE") and linha[col].values[0]]

    st.markdown("---")
    st.subheader("Responda cada questão marcando uma alternativa:")
    respostas = {}
    for idx, atividade in enumerate(atividades):
        url = f"https://questoesama.pages.dev/{atividade}.jpg"
        st.image(url, caption=f"Atividade {idx + 1}", use_container_width=True)
        resposta = st.radio("Escolha a alternativa:", ["A", "B", "C", "D", "E"], key=f"resp_{idx}", index=None)
        respostas[atividade] = resposta

    if st.button("📤 Enviar Respostas"):
        if any(r is None for r in respostas.values()):
            st.warning("⚠️ Há questões não respondidas.")
            st.stop()

        try:
            gabarito_df = carregar_gabarito()
            acertos = 0
            acertos_detalhe = {}
            for atividade, resposta in respostas.items():
                linha_gabarito = gabarito_df[gabarito_df["ATIVIDADE"] == atividade]
                correto = False
                if not linha_gabarito.empty and linha_gabarito["GABARITO"].values[0] == resposta.upper():
                    acertos += 1
                    correto = True
                acertos_detalhe[atividade] = correto

            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            service = build("sheets", "v4", credentials=creds)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            linha_envio = [timestamp, codigo_atividade, nome_aluno, escola, turma]
            for atividade, resposta in respostas.items():
                linha_envio.extend([atividade, resposta])
            service.spreadsheets().values().append(
                spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                range="ATIVIDADES!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [linha_envio]}
            ).execute()

            st.session_state.respostas_enviadas.add(id_unico)
            st.session_state.respostas_salvas[id_unico] = acertos_detalhe
            st.success(f"✅ Respostas enviadas! Você acertou {acertos}/{len(respostas)}.")
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")

    if id_unico in st.session_state.respostas_salvas:
        acertos_detalhe = st.session_state.respostas_salvas[id_unico]
        st.markdown("---")
        for idx, atividade in enumerate(atividades):
            resposta_certa = acertos_detalhe.get(atividade, False)
            cor = "✅" if resposta_certa else "❌"
            st.markdown(f"**Atividade {idx+1}:** {cor}")

        st.markdown("---")
        if st.button("🔄 Limpar Atividade"):
            del st.session_state["atividades_em_exibicao"]
            st.rerun()