import random
import string
import time
from datetime import datetime
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ======= CONFIGURAÇÃO =======
PLANILHA_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
ABA = "ATIVIDADES_GERADAS"
BLOCO = 500
TOTAL = 10000

# Simular dados fixos
SRES = ["SRE I", "SRE II", "SRE III", "SRE IV", "SRE V"]
ESCOLAS = [f"ESCOLA {chr(65+i)}" for i in range(10)]
TURMAS = ["6º ANO", "7º ANO", "8º ANO", "9º ANO"]
ATIVIDADES = [f"M{str(i).zfill(3)}" for i in range(1, 641)]  # 640 imagens

# ======= AUTENTICAÇÃO =======
creds = Credentials.from_service_account_file(
    "apt-memento-450610-v4-8291f78192e8.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
service = build("sheets", "v4", credentials=creds)

# ======= GERADOR =======
def gerar_codigo(tamanho=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=tamanho))

def gerar_linha():
    return [
        gerar_codigo(),
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        random.choice(SRES),
        random.choice(ESCOLAS),
        random.choice(TURMAS),
        *random.sample(ATIVIDADES, 10)
    ]

# ======= EXECUÇÃO EM BLOCOS COM TEMPO =======
print("\n⏱️ Iniciando simulação com tempo...")
start_geral = time.time()
linhas_total = []

for i in range(TOTAL):
    linhas_total.append(gerar_linha())

    if len(linhas_total) == BLOCO or i == TOTAL - 1:
        bloco_inicio = time.time()
        inicio_i = i + 1 - len(linhas_total) + 1
        fim_i = i + 1
        print(f"Enviando bloco {inicio_i} a {fim_i}...")

        try:
            service.spreadsheets().values().append(
                spreadsheetId=PLANILHA_ID,
                range=f"{ABA}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": linhas_total}
            ).execute()
            bloco_fim = time.time()
            duracao = bloco_fim - bloco_inicio
            print(f"✅ Bloco enviado com sucesso em {duracao:.2f}s ({len(linhas_total)/duracao:.1f} reg/s)")
        except Exception as e:
            print(f"❌ Erro ao enviar bloco: {e}")

        linhas_total = []
        time.sleep(1)

fim_geral = time.time()
print(f"\n⏰️ Teste de carga finalizado em {fim_geral - start_geral:.2f} segundos totais.")