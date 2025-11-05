# 🤖 Frontdesk HITL (Human-in-the-Loop) AI Supervisor

This project simulates a **Human-in-the-Loop AI Supervisor System** for a virtual front desk agent.  
It uses **Firebase Firestore** as a backend database and **LiveKit Cloud** for real-time AI communication.

---

## 🧠 Overview

The AI agent connects to Firestore and LiveKit.  
It can:
1. **Search** a knowledge base for answers.
2. **Escalate** unknown questions to a human supervisor.
3. **Update** the knowledge base once the supervisor responds.

A simple **Supervisor UI** (`supervisor.html`) allows real-time monitoring and resolving of help requests.

---

## 🧩 Architecture

AI Agent (Python)
├── Connects to Firestore (Firebase)
├── Uses LiveKit Cloud for communication
├── Looks up known queries
├── Creates help requests if unknown
└── Updates Firestore with escalations

Supervisor UI (HTML + JS)
├── Listens to help_requests collection in real time
├── Lets supervisor resolve pending requests
└── Adds new entries to knowledge_base when resolved

yaml
Copy code

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
2. Create and activate a virtual environment
bash
Copy code
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
🔑 4. Add your environment variables
Create a .env file in the root directory and add:

env
Copy code
LIVEKIT_URL=wss://<your-project-id>.livekit.cloud
LIVEKIT_API_KEY=<your-api-key>
LIVEKIT_API_SECRET=<your-api-secret>
⚠️ Never commit this file to GitHub — it contains sensitive keys!

🔥 5. Add your Firebase credentials
Download your Firebase service account JSON from the Firebase Console:

Go to Project Settings → Service Accounts → Generate New Private Key

Rename it to:

pgsql
Copy code
serviceAccountKey.json
Place it in the same folder as agent.py.

🚀 Run the AI Agent
bash
Copy code
python agent.py
Expected output:

scss
Copy code
✅ Firebase connection successful.
🚀 [LiveKit] Starting worker...
✅ [LiveKit] Worker started. Waiting for calls (chat messages)...
🧑‍💼 Run the Supervisor Panel
Simply double-click supervisor.html to open it in your browser.
You’ll see live updates from Firestore:

Pending help requests

Resolved requests

Timeout requests

🧩 Project Structure
bash
Copy code
📦 frontdesk-hitl
├── agent.py                  # Main AI agent logic
├── supervisor.html           # Supervisor UI
├── requirements.txt          # Dependencies
├── serviceAccountKey.json    # Firebase key (excluded from Git)
├── .env                      # LiveKit credentials (excluded from Git)
└── README.md                 # This file
🛡️ Security Notes
.env and serviceAccountKey.json must not be pushed to GitHub.

Add the following to .gitignore:

bash
Copy code
venv/
__pycache__/
serviceAccountKey.json
.env
*.pyc
🧠 Future Improvements
Add voice support using LiveKit’s Voice AI API.

Implement webhook callbacks for customer notifications.

Introduce supervisor authentication for multi-user management.

🏗️ Credits
Developed by Muhammed Shahbas V S
B.Tech Information Technology, IIITA