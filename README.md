# 🤖 FAQBot — AI-Powered FAQ Chatbot

> A full-stack **Streamlit** application that delivers domain-specific AI chat support,
> powered by **Groq**'s ultra-fast LLM inference, with user accounts, persistent chat
> history, prompt engineering, FAQ generation, and Dark / Light themes.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLM-orange?logo=groq)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🎓 **College FAQs** | Admissions, courses, exams, scholarships, campus life |
| 🏢 **HR Support** | Leave, payroll, benefits, policies, onboarding |
| 🛒 **Customer Support** | Orders, returns, shipping, billing, complaints |
| 🛠️ **Product Assistance** | Setup, troubleshoot, integrations, APIs |
| 💬 **General Assistant** | Open-ended, versatile conversations |
| 🔐 **Auth System** | Register + Login with bcrypt-hashed passwords |
| 💾 **Chat History** | All sessions persisted in SQLite, shown in sidebar |
| 📋 **FAQ Generator** | One-click generation of domain-specific FAQs |
| ⚡ **Streaming** | Real-time token streaming via Groq |
| 🧠 **Model Choice** | Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B, Gemma 2 9B |
| 🌗 **Dark / Light Theme** | Toggleable per user, persisted in DB |

---

## 🏗️ Architecture & Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                      │
│                                                             │
│  ┌─────────────┐   ┌──────────────────────────────────┐   │
│  │   Sidebar   │   │           Main Chat Panel         │   │
│  │             │   │                                   │   │
│  │ • Domain    │   │  ┌──────────────────────────┐    │   │
│  │   Selector  │   │  │    Chat Messages Feed     │    │   │
│  │ • Model     │   │  │  (user ↔ assistant turns) │    │   │
│  │   Selector  │   │  └──────────────────────────┘    │   │
│  │ • Theme     │   │  ┌──────────────────────────┐    │   │
│  │   Toggle    │   │  │     Chat Input Box        │    │   │
│  │ • Chat      │   │  └──────────────────────────┘    │   │
│  │   History   │   │  ┌──────────────────────────┐    │   │
│  │ • New Chat  │   │  │   FAQ Generator Panel     │    │   │
│  │ • Logout    │   │  └──────────────────────────┘    │   │
│  └─────────────┘   └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
            │                       │
            ▼                       ▼
  ┌──────────────────┐   ┌─────────────────────────────┐
  │   auth.py        │   │        groq_client.py        │
  │  (bcrypt hash,   │   │  stream_chat() — yields      │
  │   login, logout) │   │  chunks from Groq API        │
  └──────────────────┘   └─────────────────────────────┘
            │                       │
            ▼                       ▼
  ┌──────────────────────────────────────────────────────┐
  │                    database.py                        │
  │  SQLite tables: users · chat_sessions · messages     │
  └──────────────────────────────────────────────────────┘
            │
            ▼
  ┌──────────────────────────────────────────────────────┐
  │                    prompts.py                         │
  │  Domain system prompts + FAQ generation prompt       │
  │  build_messages() → full context for Groq API        │
  └──────────────────────────────────────────────────────┘
```

### Data Flow for Each Message
```
User types message
      │
      ▼
app.py: _send_message()
      │
      ├─► database.add_message(session_id, "user", text)
      │
      ├─► prompts.build_messages(domain, history, new_text)
      │       ↓
      │   [system_prompt] + [past turns] + [new user msg]
      │
      ├─► groq_client.stream_chat(messages, model)
      │       ↓
      │   Groq API → streaming chunks
      │       ↓
      │   st.write_stream() renders tokens in real-time
      │
      └─► database.add_message(session_id, "assistant", full_reply)
```

---

## 🗂️ File Structure

```
chatbot_faq/
├── app.py               # Main Streamlit app — UI routing, chat logic
├── database.py          # SQLite CRUD — users, sessions, messages
├── auth.py              # bcrypt auth — register, login, session helpers
├── groq_client.py       # Groq SDK wrapper — streaming + blocking chat
├── prompts.py           # Prompt engineering — 5 domain prompts + FAQ generator
├── styles.py            # Dark/Light CSS injection via st.markdown
├── .streamlit/
│   └── config.toml      # Default Streamlit dark theme config
├── requirements.txt     # Python dependencies
├── .env.example         # Template for .env (copy → fill → don't commit)
├── .gitignore           # Ignores .env, *.db, __pycache__, venv, etc.
└── README.md            # This file
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/faqbot.git
cd faqbot
```

### 2. Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
# Copy the example env file
cp .env.example .env   # Windows: copy .env.example .env

# Open .env and paste your Groq API key
# Get a free key at: https://console.groq.com/keys
```

Your `.env` should look like:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📋 Prompt Engineering Strategy

Each domain uses a **role-based system prompt** with:

| Technique | Purpose |
|-----------|---------|
| **Persona framing** | `You are EduBot, a knowledgeable College FAQ Assistant…` |
| **Explicit expertise scope** | Lists all sub-topics the bot knows about |
| **Behaviour rules** | Numbered rules: clarify first, structure answers, empathise |
| **Tone specification** | Warm / formal / technical depending on domain |
| **Chain-of-thought cues** | "Always structure long answers with headers and bullet points" |
| **Guardrails** | "When you don't know, say so and redirect to the right contact" |

### FAQ Generation Prompt
The FAQ generator uses a **structured output prompt** that enforces:
- Exactly N questions
- Consistent `Q1. / A:` format for easy parsing
- Mixed difficulty (beginner → advanced)
- Coverage of different sub-topics

---

## 🌗 Theme System

Themes are driven by CSS variable injection into Streamlit's DOM:

- **Dark** (default): `#0f1117` background, `#7c6af7` violet accent
- **Light**: `#f5f7fa` background, `#5c4ed4` purple accent

Theme preference is stored per user in the SQLite `users` table and restored on login.

---

## 🗃️ Database Schema

```sql
users (
    id, username, email, password_hash, full_name, theme, created_at
)

chat_sessions (
    id, user_id, title, domain, created_at, updated_at
)

messages (
    id, session_id, role, content, timestamp
)
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT © 2025 — see [LICENSE](LICENSE) for details.
