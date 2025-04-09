import random
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def escolher_credencial_aleatoria(lista_credenciais):
    """
    Retorna uma das credenciais fornecidas, de forma aleatória.
    """
    return random.choice(lista_credenciais)

def enviar_respostas_em_blocos(linhas, credencial):
    """
    Envia uma lista de respostas para o Google Sheets, utilizando a credencial informada.
    Cada item de `linhas` deve ser uma lista (linha na planilha).
    """
    try:
        creds = Credentials.from_service_account_info(
            credencial,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)

        spreadsheet_id = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
        range_destino = "ATIVIDADES!A1"

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_destino,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": linhas}
        ).execute()

    except Exception as e:
        raise RuntimeError(f"Erro ao enviar respostas em bloco: {e}")
