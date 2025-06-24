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

def recuperar_mensagens_do_contexto(contexto):
    mensagens = []
    linhas = contexto.strip().split("\n")
    for linha in linhas:
        if linha.startswith("User:"):
            mensagens.append({"role": "user", "content": linha.replace("User:", "").strip()})
        elif linha.startswith("AI:"):
            mensagens.append({"role": "assistant", "content": linha.replace("AI:", "").strip()})
    return mensagens
