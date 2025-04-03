
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

def gerar_id_unico(nome, escola, turma, codigo):
    def normalizar(txt):
        txt = txt.lower().strip()
        txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
        return ''.join(c for c in txt if c.isalnum())
    return f"{normalizar(nome)}_{normalizar(escola)}_{normalizar(turma)}_{normalizar(codigo)}"

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
            range="ATIVIDADES_GERADAS!A:Z"
        ).execute()
        values = result.get("values", [])
        header = [col.strip().upper() for col in values[0]]
        rows = [row + [None] * (len(header) - len(row)) for row in values[1:]]
        df = pd.DataFrame(rows, columns=header)
        df["CODIGO"] = df["CODIGO"].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao acessar a API do Google Sheets: {e}")
        return pd.DataFrame()

dados = carregar_atividades_api()

if "ids_realizados" not in st.session_state:
    st.session_state.ids_realizados = set()

if st.button("📥 Gerar Atividade"):
    if not all([nome_aluno.strip(), escola.strip(), turma.strip(), codigo_atividade.strip()]):
        st.warning("⚠️ Por favor, preencha todos os campos antes de visualizar a atividade.")
        st.stop()

    id_unico = gerar_id_unico(nome_aluno, escola, turma, codigo_atividade)
    if id_unico in st.session_state.ids_realizados:
        st.warning("❌ Você já fez essa atividade.")
        st.stop()

    st.session_state.codigo_confirmado = codigo_atividade.strip().upper()
    st.session_state.id_unico_atual = id_unico
    st.rerun()

if "codigo_confirmado" in st.session_state:
    codigo_atividade = st.session_state.codigo_confirmado
    id_unico = st.session_state.id_unico_atual
    linha = dados[dados["CODIGO"] == codigo_atividade]

    if linha.empty:
        st.warning("Código inválido ou sem atividades associadas.")
        st.stop()

    atividades = [linha[col].values[0] for col in linha.columns if col.startswith("ATIVIDADE") and linha[col].values[0]]

    st.markdown("---")
    st.subheader("Responda cada questão com atenção, marcando uma das alternativas (você só tem uma tentativa):")

    respostas = {}
    for idx, atividade in enumerate(atividades):
        url = f"https://questoesama.pages.dev/{atividade}.jpg"
        st.image(url, caption=f"Atividade {idx + 1}", use_container_width=True)
        resposta = st.radio("", ["A", "B", "C", "D", "E"], key=f"resposta_{idx}", index=None)
        respostas[atividade] = resposta

    if st.button("📤 Enviar respostas"):
        if any(r is None for r in respostas.values()):
            st.warning("⚠️ Existe alguma questão não respondida!")
            st.stop()

        try:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            service = build("sheets", "v4", credentials=creds)

            # Gabarito
            gabarito_result = service.spreadsheets().values().get(
                spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                range="MATEMATICA!A:B"
            ).execute()
            gabarito_data = gabarito_result.get("values", [])
            gabarito_df = pd.DataFrame(gabarito_data[1:], columns=gabarito_data[0])
            gabarito_df["QUESTAO"] = gabarito_df["QUESTAO"].astype(str).str.strip()
            gabarito_df["GABARITO"] = gabarito_df["GABARITO"].str.upper().str.strip()

            acertos = 0
            for atividade, resposta in respostas.items():
                nome = atividade.replace(".jpg", "")
                row = gabarito_df[gabarito_df["QUESTAO"] == nome]
                if not row.empty and resposta == row.iloc[0]["GABARITO"]:
                    acertos += 1
            total = len(respostas)

            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            linha_unica = [timestamp, codigo_atividade, nome_aluno, escola, turma, f"{acertos}/{total}"]
            for atividade, resposta in respostas.items():
                linha_unica.extend([atividade, resposta])

            service.spreadsheets().values().append(
                spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                range="ATIVIDADES!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [linha_unica]}
            ).execute()

            st.session_state["resultado_final"] = f"{acertos}/{total}"
            st.session_state.ids_realizados.add(id_unico)
            st.session_state.codigo_confirmado = None

            st.success(f"✅ Respostas enviadas com sucesso! Você acertou {acertos} de {total} questões.")

        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")

if "resultado_final" in st.session_state:
    st.success(f"✅ Você acertou {st.session_state['resultado_final']} questões.")
