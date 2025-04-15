import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Painel de Monitoramento", page_icon="📊", layout="wide")

st.markdown("## 📊 Painel de Monitoramento - AMA 2025 (Power BI)")

# Link do Power BI (deixando responsivo e centralizado)
url_powerbi = "https://app.powerbi.com/view?r=eyJrIjoiZDE2YWVhY2EtZDZhZC00YjEwLTg0MzgtMTAzN2U0OWE2NGNlIiwidCI6IjZiOTZhMTUxLWY1MWUtNDdlNi04ZTRiLTRkZThhYTcyNTYwNSJ9"

# Iframe com layout ampliado
components.iframe(src=url_powerbi, width=1200, height=800, scrolling=True)
