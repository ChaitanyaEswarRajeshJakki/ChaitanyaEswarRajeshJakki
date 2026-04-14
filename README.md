<h1 align="center">👋 Hi, I'm Jakki Chaitanya Eswar Rajesh</h1>

<p align="center">
  <b>AI Engineer · Azure Data Engineer (DP-203) · Python Developer</b><br/>
  <i>Building production multi-agent LLM systems, RAG pipelines, and cloud-scale ETL solutions</i>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/chaitanyaeswarrajesh/">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
  </a>
  <a href="https://github.com/ChaituRajSagar">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/>
  </a>
  <a href="mailto:chaitanyaeswar.rajesh@gmail.com">
    <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white"/>
  </a>
</p>

<p align="center">
  <a href="https://chaiturajsagar.github.io/interactive-resume-infographic/infographic.html">
    <img src="https://img.shields.io/badge/🚀%20Interactive%20Career%20Infographic-View%20Now-2E75B6?style=for-the-badge"/>
  </a>
</p>

---

## 🧠 Who I Am

- 🏆 **Microsoft Certified Azure Data Engineer Associate (DP-203)**
- 🤖 **3+ years** building production Generative AI systems — multi-agent platforms, RAG pipelines, LLM orchestration
- ☁️ **7+ years** backend engineering — Azure Data Factory, ETL pipelines, cloud migration
- 🏛️ Delivered data engineering solutions for **U.S. government clients** — Contra Costa County, LA County, California State Agencies
- 🌐 Open to **AI Engineer** and **Azure Data Engineer** roles — Remote or Hyderabad

---

## 🚀 What I'm Building Right Now

### 🔷 AppNova AI — Enterprise Multi-Agent Code Modernisation Platform

> 11 specialized AI agents analyse legacy codebases in parallel and generate full modernisation reports

- **Agents:** Architecture · Security · Code Generation · DevOps · Testing · Migration Planning · Documentation · UI/UX · Business Rules · Integration · Data Migration
- **Backend:** FastAPI + LangGraph + asyncio + SSE streaming
- **LLM Cascade:** Claude → Gemini → Groq (LLaMA 3) → Ollama with automatic key rotation across 25+ API keys and zero-downtime provider fallback
- **RAG:** ChromaDB with AST-based file summaries, corpus deduplication, content fingerprinting
- **Features:** Real-time Spectator Mode, DOCX/MD export, self-correcting agents, batch context ingestion via Gemini's 1M-token window

[![AppNova Repo](https://img.shields.io/badge/GitHub-AppNova%20AI-2E75B6?style=flat-square&logo=github)](https://github.com/ChaituRajSagar/AppNova)

---

## 🛠️ Featured Projects

### 🟢 GovGenie — AI-Powered RFP Response Generator
> RAG system that drafts government bid responses by retrieving past proposal language — cutting prep time by ~70%

- **Stack:** FastAPI · LangChain · Ollama (LLaMA 3.1) · ChromaDB · HuggingFace Embeddings · React
- Conversational chat interface with `ConversationBufferMemory` for follow-up RFP clause queries
- Per-stage token tracking via `tiktoken` for cost visibility
- Reduced bid writing from **5+ days → under 24 hours**

---

### 🟢 ReferenceFiller — Automated DOCX Template Population
> Upload a resume → LLM extracts structured data → fills DOCX template automatically

- **Stack:** FastAPI · Ollama · ChromaDB · python-docx · mammoth · Jinja2
- Session-based UUID stores with chunk-based text splitting
- ChromaDB semantic search matches extracted skills to template fields
- Replaced a **45-minute manual HR task with a 2-minute automated workflow**

---

### 🟢 Video to Narrative — Surveillance Video AI Summariser
> Turns dashcam/bodycam footage into structured law-enforcement incident reports

- **Stack:** Flask · OpenCV · Whisper · ViT-GPT2 · Groq (llama3-8b-8192)
- Frame extraction → ViT-GPT2 captions → Whisper audio transcript → Groq LLM synthesis
- Two output modes: general summary + formal law-enforcement narrative
- Structured JSON output with timestamps, transcript, and multi-perspective summaries

[![video_to_narrative](https://img.shields.io/badge/GitHub-video__to__narrative-2E75B6?style=flat-square&logo=github)](https://github.com/ChaituRajSagar/video_to_narrative)

---

### 🟢 Skill Matrix App — HR Skill Extraction via RAG
> Auto-extracts skills from DOCX/PDF resumes and populates HR skill matrix templates

- **Stack:** Flask · ChromaDB · Ollama (Mistral) · Sentence Transformers · python-docx
- Fully local — no data sent to external APIs
- RAG pipeline reduces hallucination to near zero vs baseline LLM-only approaches

[![Skill_Matrix_App](https://img.shields.io/badge/GitHub-Skill__Matrix__App-2E75B6?style=flat-square&logo=github)](https://github.com/ChaituRajSagar/Skill_Matrix_App)

---

### 🟢 Gemini YouTube Automation Bot — Autonomous AI Video Publisher
> Zero human input — AI generates, produces, and publishes YouTube videos end-to-end

- **Stack:** Python · Google Gemini · MoviePy · gTTS · GitHub Actions · YouTube Data API
- Gemini generates SEO-optimised scripts → gTTS voiceover → MoviePy video composition → auto-publish
- Custom thumbnail generation, dynamic TextClip overlays
- Entire pipeline runs on **GitHub Actions cron schedule** — no server required

[![gemini-youtube-automation](https://img.shields.io/badge/GitHub-gemini--youtube--automation-2E75B6?style=flat-square&logo=github)](https://github.com/ChaituRajSagar/gemini-youtube-automation)

---

### 🟢 Video Frame Extractor
> Batch-extracts and organises frames from multiple video files

- **Stack:** Python · OpenCV · python-dotenv · MoviePy
- Configurable frame rate, input/output paths via `.env`
- Creates separate subfolders per video for organised output

[![video_to_frames](https://img.shields.io/badge/GitHub-video__to__frames-2E75B6?style=flat-square&logo=github)](https://github.com/ChaituRajSagar/video_to_frames)

---

## ☁️ Azure Data Engineering Work

> 30+ production ADF pipelines for U.S. government agencies

| What | Detail |
|---|---|
| **Pipelines** | 30+ ADF pipelines — person, address, offense, narrative, gang, property records |
| **Performance** | 50% faster data processing via optimised Mapping Data Flows |
| **Migration** | ARIES cloud migration — 40+ tables, on-prem SQL Server → Azure Cloud, zero data loss |
| **Automation** | ADF validation + deduplication logic — 40% less manual review effort |
| **Infrastructure** | Azure VMs · Elastic Pools · Azure SQL · Data Lake Gen2 · Key Vault |
| **Clients** | Contra Costa County · LA County · California State Agencies |

---

## 🧰 Tech Stack

<p>
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white"/>
<img src="https://img.shields.io/badge/LangGraph-FF6B35?style=flat-square&logoColor=white"/>
<img src="https://img.shields.io/badge/ChromaDB-FF6B35?style=flat-square&logoColor=white"/>
<img src="https://img.shields.io/badge/Claude-D97706?style=flat-square&logoColor=white"/>
<img src="https://img.shields.io/badge/Gemini-4285F4?style=flat-square&logo=google&logoColor=white"/>
<img src="https://img.shields.io/badge/Groq-F55036?style=flat-square&logoColor=white"/>
<img src="https://img.shields.io/badge/Ollama-000000?style=flat-square&logoColor=white"/>
<img src="https://img.shields.io/badge/Azure%20Data%20Factory-0078D4?style=flat-square&logo=microsoftazure&logoColor=white"/>
<img src="https://img.shields.io/badge/Azure%20SQL-0078D4?style=flat-square&logo=microsoftazure&logoColor=white"/>
<img src="https://img.shields.io/badge/Azure%20Data%20Lake-0078D4?style=flat-square&logo=microsoftazure&logoColor=white"/>
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white"/>
<img src="https://img.shields.io/badge/Whisper-412991?style=flat-square&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black"/>
<img src="https://img.shields.io/badge/RAG-2E75B6?style=flat-square&logoColor=white"/>
<img src="https://img.shields.io/badge/SQL-4479A1?style=flat-square&logo=mysql&logoColor=white"/>
</p>

---

## 📊 GitHub Stats

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=ChaituRajSagar&show_icons=true&theme=tokyonight&hide_border=true" height="150"/>
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=ChaituRajSagar&layout=compact&theme=tokyonight&hide_border=true" height="150"/>
</p>

---

## 🎯 Interactive Career Infographic

<p align="center">
  <a href="https://chaiturajsagar.github.io/interactive-resume-infographic/infographic.html">
    <img src="https://img.shields.io/badge/🚀%20Explore%20My%20Interactive%20Profile-Click%20Here-2E75B6?style=for-the-badge"/>
  </a>
</p>

---

<p align="center">
  <i>📫 chaitanyaeswar.rajesh@gmail.com · +91 9908856899 · Hyderabad, India</i><br/>
  <i>Open to AI Engineer and Azure Data Engineer roles — Remote or Hyderabad</i>
</p>
