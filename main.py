import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from database.save_context import salvar_contexto, recuperar_ultimo_contexto, recuperar_mensagens_do_contexto
import os

# Configuração do modelo com streaming
# model = OllamaLLM(model="cogito", streaming=True)
model = OllamaLLM(model="cogito", base_url=os.getenv("OLLAMA_URL"), streaming=True)

# Template do prompt
template = """
Você é um assistente de programação altamente qualificado, capaz de explicar conceitos, corrigir códigos, sugerir boas práticas e resolver dúvidas sobre qualquer linguagem ou tecnologia de desenvolvimento de software.

Você sempre responde de forma didática, técnica e, quando necessário, apresenta exemplos de código claros e funcionais.

Aqui está o histórico da nossa conversa até agora: {context}

Pergunta do usuário: {question}

Sua resposta:
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Configuração da página Streamlit
st.set_page_config(page_title="Yoda AI ChatBot", page_icon="🛸")
st.title("🛸 Yoda AI ChatBot")
contexto = recuperar_ultimo_contexto("padawan")
# Inicializa o estado da aplicação
if "messages" not in st.session_state:
    st.session_state.messages = recuperar_mensagens_do_contexto(contexto)
if "context" not in st.session_state:
    st.session_state.context = contexto or ""

# Exibe o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Campo de entrada do usuário
if prompt := st.chat_input("Digite sua pergunta..."):
    # Adiciona pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        streamed_response = ""

        for chunk in chain.stream({"context": st.session_state.context, "question": prompt}):
            streamed_response += chunk
            response_placeholder.markdown(streamed_response + "▌")

        response_placeholder.markdown(streamed_response)
        st.session_state.messages.append({"role": "assistant", "content": streamed_response})

        # Atualiza contexto
        st.session_state.context += f"\nUser: {prompt}\nAI: {streamed_response}"
        salvar_contexto("padawan", st.session_state.context)
