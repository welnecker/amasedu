import random
import time
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ======= CONFIGURAÇÃO =======
PLANILHA_ID = "17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8"
ABA_DESTINO = "ATIVIDADES"
ABA_CODIGOS = "ATIVIDADES_GERADAS"
BLOCO = 500
TOTAL = 50000  # Ajuste para 50.000 respostas

TURMAS = ["6º ANO", "7º ANO", "8º ANO", "9º ANO"]
ESCOLAS = [f"ESCOLA {chr(65+i)}" for i in range(10)]
RESPOSTAS_POSSIVEIS = ["A", "B", "C", "D"]

# ======= AUTENTICAÇÃO =======
creds1 = Credentials.from_service_account_file(
    "C:/Users/jdwelnecker/Python_Janio/AMA2025/teste_carga/cred1.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

creds2 = Credentials.from_service_account_file(
    "C:/Users/jdwelnecker/Python_Janio/AMA2025/teste_carga/cred2.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

creds3 = Credentials.from_service_account_file(
    "C:/Users/jdwelnecker/Python_Janio/AMA2025/teste_carga/cred3.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service1 = build("sheets", "v4", credentials=creds1)
service2 = build("sheets", "v4", credentials=creds2)
service3 = build("sheets", "v4", credentials=creds3)

# ======= BUSCAR CÓDIGOS EXISTENTES =======
def carregar_codigos_existentes():
    result = service1.spreadsheets().values().get(
        spreadsheetId=PLANILHA_ID,
        range=f"{ABA_CODIGOS}!A2:E"
    ).execute()
    valores = result.get("values", [])
    return [linha for linha in valores if len(linha) >= 5]  # codigo, data, SRE, escola, turma

codigos_atividade = carregar_codigos_existentes()
if not codigos_atividade:
    print("❌ Nenhum código de atividade encontrado na aba ATIVIDADES_GERADAS.")
    exit()

# ======= GERADOR DE RESPOSTAS =======
def gerar_resposta():
    codigo_info = random.choice(codigos_atividade)
    codigo = codigo_info[0]
    escola = codigo_info[3]
    turma = codigo_info[4]
    serie = turma
    nome_aluno = f"Aluno {random.randint(1000, 9999)}"
    respostas = random.choices(RESPOSTAS_POSSIVEIS, k=10)
    gabarito = random.choices(RESPOSTAS_POSSIVEIS, k=10)
    acertos = sum(1 for r, g in zip(respostas, gabarito) if r == g)

    return [codigo, nome_aluno, escola, turma, serie, *respostas, *gabarito, f"{acertos} certas"]

# ======= EXECUÇÃO EM BLOCOS =======
print("\n🕒 Iniciando simulação de respostas com gabarito...")
start_geral = time.time()
linhas_total = []

# Função para rotacionar as credenciais
def escolher_credencial_aleatoria():
    return random.choice([service1, service2, service3])

for i in range(TOTAL):
    linhas_total.append(gerar_resposta())

    if len(linhas_total) == BLOCO or i == TOTAL - 1:
        bloco_inicio = time.time()
        inicio_i = i + 1 - len(linhas_total) + 1
        fim_i = i + 1
        print(f"Enviando bloco {inicio_i} a {fim_i}...")

        try:
            service = escolher_credencial_aleatoria()

            service.spreadsheets().values().append(
                spreadsheetId=PLANILHA_ID,
                range=f"{ABA_DESTINO}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": linhas_total}
            ).execute()
            bloco_fim = time.time()
            duracao = bloco_fim - bloco_inicio
            print(f"✅ Bloco enviado em {duracao:.2f}s ({len(linhas_total)/duracao:.1f} reg/s)")
        except Exception as e:
            print(f"❌ Erro ao enviar bloco: {e}")

        linhas_total = []
        time.sleep(1)

fim_geral = time.time()
print(f"\n🕰️ Teste de respostas finalizado em {fim_geral - start_geral:.2f} segundos.")
