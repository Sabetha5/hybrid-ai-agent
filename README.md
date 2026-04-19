# 🤖 Smart AI Agent (RAG + Web Scraping)

A full-stack AI application that combines LLMs, Retrieval-Augmented Generation (RAG), and web scraping to answer user queries intelligently in real time.

---

## 🚀 Features

* 🌐 Scrape and summarize websites dynamically
* 📄 Chat with PDF documents using RAG
* 🧠 Intent classification (SCRAPE / GENERAL / SEARCH)
* 🤖 LLM-powered responses (Groq - LLaMA 3)
* ⚡ FastAPI backend
* 🎨 Streamlit frontend
* 🐳 Dockerized for deployment

---

## 🏗️ Architecture

User → Streamlit UI → FastAPI → AI Agent → Tools (Firecrawl / RAG)

---

## 🧰 Tech Stack

* **LLM:** Groq (LLaMA 3)
* **Backend:** FastAPI
* **Frontend:** Streamlit
* **RAG:** FAISS + HuggingFace Embeddings
* **Tools:** MCP, Firecrawl
* **Deployment:** Docker + Render

---

## ⚙️ Setup (Local)

### 1. Clone repository

git clone https://github.com/Sabetha5/hybrid-ai-agent.git
cd hybrid-ai-agent

---

### 2. Create virtual environment

python -m venv .venv
.venv\Scripts\activate

---

### 3. Install dependencies

pip install uv
uv sync

---

### 4. Add environment variables

Create a `.env` file:

GROQ_API_KEY=your_key
FIRECRAWL_API_KEY=your_key

---

### 5. Run backend

uvicorn app:app --reload

---

### 6. Run frontend

streamlit run ui.py

---

## 🐳 Docker

docker build -t ai-agent .
docker run -p 8000:8000 ai-agent

---

## 🌍 Deployment

* Backend deployed using Render (Docker)
* Frontend deployed using Streamlit

---

## 🔐 Security

* API keys stored securely using environment variables
* `.env` file excluded via `.gitignore`

---

## 📌 Future Improvements

* Authentication system
* Chat history storage (database)
* Monitoring with Prometheus & Grafana
* Kubernetes deployment

---

## 👩‍💻 Author

Sabetha Sheenu
AI/ML Engineer | GenAI Enthusiast 🚀
