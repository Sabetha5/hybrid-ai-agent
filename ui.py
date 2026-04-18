import streamlit as st
import requests
from pypdf import PdfReader

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

st.set_page_config(page_title="AI Agent Chat", layout="centered")

st.title("🤖 AI Chat Agent")

uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])

if uploaded_file:
    pdf_text = read_pdf(uploaded_file)
    st.session_state["pdf_text"] = pdf_text
    st.success("✅ PDF uploaded and processed")

# 🔥 Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔥 Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 🔥 Chat input
user_input = st.chat_input("Ask something...")

if user_input:

    # 👉 Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 👉 Show user message instantly
    with st.chat_message("user"):
        st.write(user_input)

    # 👉 Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                if "pdf_text" in st.session_state:
                    response = requests.post(
                        "http://127.0.0.1:8000/chat",
                    json={
                        "message": user_input,
                         "pdf_text": st.session_state["pdf_text"]
         }
    )
                else:
                 response = requests.post(
                     "http://127.0.0.1:8000/chat",
                    json={"message": user_input}
    )
               
                data = response.json()

                if "response" in data:
                    ai_reply = data["response"]
                else:
                    ai_reply = data.get("error", "Something went wrong")

            except Exception as e:
                ai_reply = f"Error: {e}"

        # 👉 Show response
        st.write(ai_reply)

    # 👉 Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_reply
    })