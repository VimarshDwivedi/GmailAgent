# 📬 GmailAgent

**GmailAgent** is an AI-powered assistant that automates tasks on Gmail using the Gmail API and Large Language Models (LLMs) like OpenAI’s GPT. This tool allows users to read, filter, compose, and manage emails with simple natural language commands.

---

## 🧠 Features

- 🔐 OAuth 2.0-based Gmail authentication
- 📥 Read and search emails based on filters (unread, sender, subject, etc.)
- ✉️ Draft and send emails using LLMs
- 🧹 Delete, archive, or label emails automatically
- 📝 Summarize long email threads
- 💬 Interact through a command line interface or Streamlit web app

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Google Gmail API**
- **OpenAI GPT (via API)**
- **Streamlit** *(optional frontend)*
- **LangChain** *(optional for LLM prompt structuring)*

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/VimarshDwivedi/GmailAgent.git
cd GmailAgent
2. Create a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Configure .env File
Create a .env file in the root directory and add your keys:

ini
Copy
Edit
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000
OPENAI_API_KEY=your_openai_api_key
🔑 Gmail API Setup
Go to the Google Cloud Console

Create a new project

Enable the Gmail API

Create OAuth 2.0 credentials (set redirect URI)

Download the credentials JSON file and rename it to credentials.json in the root folder

🚀 Run the App
Option 1: CLI Interface
bash
Copy
Edit
python main.py
Option 2: Streamlit App
bash
Copy
Edit
streamlit run app.py
💡 Example Prompts
“Summarize unread emails from today”

“Draft an email to Alice about project update”

“Archive all emails from noreply@example.com”

“Delete emails older than 7 days”
 

#📁 Project Structure
bash
Copy
Edit
📦 GmailAgent
├── app.py                  # Streamlit UI
├── main.py                 # CLI entrypoint
├── gmail_utils.py          # Gmail interaction logic
├── llm_utils.py            # LLM (OpenAI) prompt handling
├── requirements.txt
├── credentials.json        # Google API credentials
└── .env                    # Environment variables
🧪 #Testing
bash
Copy
Edit
pytest
🤝 Contributing
We welcome contributions! Please open issues or submit pull requests.



*🙋‍♂️ Author*
Vimarsh Dwivedi
GitHub • LinkedIn
