# AtividadeOnline.py (Geração de formulário interativo com imagens)
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import qrcode
from PIL import Image
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import base64
from io import BytesIO

st.set_page_config(page_title="Atividade Online AMA 2025", page_icon="💡")
st.title("💡 Atividade Online - AMA 2025")

st.subheader("Acesse a atividade gerada pelo professor")

# URL da própria página
URL_ATIVIDADE_ONLINE = "https://amasedu.streamlit.app/AtividadeOnline"

# Gerar QR Code
qr = qrcode.make(URL_ATIVIDADE_ONLINE)
buffer = BytesIO()
qr.save(buffer, format="PNG")
buffer.seek(0)

# Exibir QR Code e link
st.image(buffer, caption="Escaneie o QR Code para acessar esta atividade", use_column_width=True)
st.markdown(f"Ou acesse diretamente: [Clique aqui para abrir a atividade]({URL_ATIVIDADE_ONLINE})")

# Encerrar a execução da página aqui
st.stop()
