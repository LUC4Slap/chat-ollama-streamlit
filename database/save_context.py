from pymongo import MongoClient
from datetime import datetime
import os

# Conectando ao MongoDB (ajuste a string conforme seu ambiente)
client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017/"))
db = client["chatbot_db"]
conversas = db["conversas"]

# Função para salvar o contexto
def salvar_contexto(usuario, contexto):
    registro = {
        "usuario": usuario,
        "contexto": contexto,
        "data": datetime.utcnow()
    }
    conversas.insert_one(registro)
    print("Contexto salvo no MongoDB com sucesso!")

def recuperar_ultimo_contexto(usuario):
    registro = conversas.find_one({"usuario": usuario}, sort=[("data", -1)])
    if registro:
        return registro["contexto"]
    return ""

# def recuperar_mensagens_do_contexto(contexto):
#     mensagens = []
#     linhas = contexto.strip().split("\n")
#     for linha in linhas:
#         if linha.startswith("User:"):
#             mensagens.append({"role": "user", "content": linha.replace("User:", "").strip()})
#         elif linha.startswith("AI:"):
#             mensagens.append({"role": "assistant", "content": linha.replace("AI:", "").strip()})
#     print(mensagens)
#     return mensagens

def recuperar_mensagens_do_contexto(contexto):
    mensagens = []
    linhas = contexto.strip().split("\n")

    mensagem_atual = None
    conteudo_atual = []

    for linha in linhas:
        if linha.startswith("User:"):
            # Salva a mensagem anterior se existir
            if mensagem_atual:
                mensagens.append({"role": mensagem_atual, "content": "\n".join(conteudo_atual).strip()})
            mensagem_atual = "user"
            conteudo_atual = [linha.replace("User:", "").strip()]
        elif linha.startswith("AI:"):
            if mensagem_atual:
                mensagens.append({"role": mensagem_atual, "content": "\n".join(conteudo_atual).strip()})
            mensagem_atual = "assistant"
            conteudo_atual = [linha.replace("AI:", "").strip()]
        else:
            conteudo_atual.append(linha)

    # Salva a última mensagem
    if mensagem_atual and conteudo_atual:
        mensagens.append({"role": mensagem_atual, "content": "\n".join(conteudo_atual).strip()})

    return mensagens
