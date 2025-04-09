from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

PLANILHA_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
CREDENCIAIS_JSONS = ["cred1.json", "cred2.json", "cred3.json"]

print("\n🔍 Verificando acesso das contas de serviço...")

for cred_file in CREDENCIAIS_JSONS:
    try:
        creds = Credentials.from_service_account_file(
            cred_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)

        # Testa uma leitura básica
        result = service.spreadsheets().get(spreadsheetId=PLANILHA_ID).execute()
        nome = result.get("properties", {}).get("title", "[Sem nome]")
        print(f"✅ {cred_file} tem acesso ao documento: '{nome}'")

    except Exception as e:
        print(f"❌ {cred_file} NÃO tem acesso. Erro: {e}")

print("\n✅ Verificação concluída.")
