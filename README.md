# 🤖 AI Chatbot

An AI-powered chatbot web application that allows users to interact with an AI assistant, manage their accounts securely, store chat history, and analyze resumes using AI.

## 🚀 Features

* 🔐 User Registration and Login
* 🔑 JWT-based Authentication
* 🤖 AI-powered Chatbot
* 💬 Real-time conversational interaction
* 📝 Chat History Storage
* 📄 AI Resume Analysis
* 📊 Resume feedback and improvement suggestions
* 🔒 Password hashing using bcrypt
* 🗄️ MySQL database integration
* 🌐 REST APIs using FastAPI
* 🎨 Responsive frontend interface

## 🛠️ Technologies Used

### Backend

* Python
* FastAPI
* SQLAlchemy
* PyMySQL
* JWT
* Bcrypt
* Google Gemini API

### Frontend

* HTML
* CSS
* JavaScript

### Database

* MySQL

### Tools

* Git
* GitHub
* VS Code
* Postman

## 📁 Project Structure

```text
AI_Chatbot/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── resume_service.py
│   └── .env
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── .gitignore
└── README.md
```

> **Note:** The `.env` file contains sensitive information such as API keys and database credentials and should never be uploaded to GitHub.

## ⚙️ Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/AishwaryaC-2004/AI_Chatbot.git
```

Navigate into the project:

```bash
cd AI_Chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install fastapi uvicorn sqlalchemy pymysql python-dotenv bcrypt python-jose google-genai
```

### 4. Configure environment variables

Create:

```text
backend/.env
```

Add your own configuration:

```env
GOOGLE_API_KEY=your_api_key
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

Do not upload this file to GitHub.

## 🗄️ Database Setup

Create a MySQL database for the application.

Update the database configuration in your environment variables according to your local MySQL setup.

The application uses the database to store:

* User information
* Chat messages
* Resume analysis information
* Other application data

## ▶️ Run the Backend

Navigate to the backend folder:

```powershell
cd backend
```

Start the FastAPI server:

```powershell
python -m uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 🌐 Run the Frontend

Open:

```text
frontend/index.html
```

in your browser, or use the VS Code Live Server extension.

Make sure the FastAPI backend is running before using the chatbot.

## 🔐 Authentication

The application uses JWT authentication to protect user-specific APIs.

The authentication flow is:

```text
User
  ↓
Regi
```
