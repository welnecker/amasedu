from concurrent.futures import ThreadPoolExecutor
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

# Caminhos dos JSONs das contas de serviço (ajuste se estiverem em outra pasta)
CREDENCIAIS = [
    "teste_carga/cred1.json",
    "teste_carga/cred2.json",
    "teste_carga/cred3.json"
]

PLANILHA_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
ABA_DESTINO = "ATIVIDADES"
BLOCO = 500

def enviar_bloco(respostas, cred_path, id_thread):
    try:
        creds = Credentials.from_service_account_file(cred_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        service = build("sheets", "v4", credentials=creds)

        start = time.time()
        service.spreadsheets().values().append(
            spreadsheetId=PLANILHA_ID,
            range=f"{ABA_DESTINO}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": respostas}
        ).execute()
        duracao = time.time() - start
        print(f"✅ [{cred_path}] Bloco enviado por thread {id_thread} ({len(respostas)} linhas) em {duracao:.2f}s")
    except Exception as e:
        print(f"❌ Erro com {cred_path}: {e}")

def enviar_respostas_em_blocos(respostas_total):
    blocos = [respostas_total[i:i + BLOCO] for i in range(0, len(respostas_total), BLOCO)]

    print(f"🔁 Enviando {len(respostas_total)} respostas em {len(blocos)} blocos usando múltiplas contas...")

    with ThreadPoolExecutor(max_workers=len(CREDENCIAIS)) as executor:
        for i, bloco in enumerate(blocos):
            cred_usada = CREDENCIAIS[i % len(CREDENCIAIS)]
            executor.submit(enviar_bloco, bloco, cred_usada, i + 1)
