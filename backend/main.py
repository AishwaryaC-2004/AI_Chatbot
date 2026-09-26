import os
from pathlib import Path

import bcrypt

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    UploadFile,
    File
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from sqlalchemy.orm import Session

from jose import jwt, JWTError

from google import genai

from database import SessionLocal

from models import (
    User,
    ChatMessage,
    ResumeAnalysis,
    MockInterview,
    create_tables
)

from resume_service import extract_text_from_pdf


# =========================================================
# ENVIRONMENT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# =========================================================
# CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-this-secret-key"
)

ALGORITHM = "HS256"


if not GEMINI_API_KEY:

    raise RuntimeError(
        f"GEMINI_API_KEY is missing.\n"
        f"Check: {ENV_FILE}"
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="AI Career Assistant",
    description="AI-powered career assistant",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

@app.on_event("startup")
def startup():

    create_tables()

    print("========================================")
    print("AI CAREER ASSISTANT STARTED")
    print("========================================")
    print("Database tables ready")
    print("Gemini model:", GEMINI_MODEL)
    print("========================================")


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterRequest(BaseModel):

    name: str

    email: str

    password: str


class LoginRequest(BaseModel):

    email: str

    password: str


class ChatRequest(BaseModel):

    message: str


class MockInterviewRequest(BaseModel):

    role: str


class EvaluateInterviewRequest(BaseModel):

    interview_id: int

    answer: str


# =========================================================
# DATABASE
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials =
    Depends(security)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get(
            "user_id"
        )

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message":
            "AI Career Assistant API is running",
        "status":
            "success"
    }


# =========================================================
# REGISTER
# =========================================================

@app.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    name = request.name.strip()

    email = request.email.strip().lower()

    password = request.password


    if not name:

        raise HTTPException(
            status_code=400,
            detail="Name is required"
        )


    if len(password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters"
        )


    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


    user = User(
        name=name,
        email=email,
        password=hashed_password
    )


    db.add(user)

    db.commit()

    db.refresh(user)


    return {

        "message":
            "User registered successfully",

        "user_id":
            user.id,

        "name":
            user.name,

        "email":
            user.email
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    email = request.email.strip().lower()


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    password_correct = bcrypt.checkpw(

        request.password.encode("utf-8"),

        user.password.encode("utf-8")
    )


    if not password_correct:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    token_data = {

        "user_id":
            user.id,

        "email":
            user.email
    }


    access_token = jwt.encode(

        token_data,

        JWT_SECRET,

        algorithm=ALGORITHM
    )


    return {

        "message":
            "Login successful",

        "access_token":
            access_token,

        "user_id":
            user.id,

        "name":
            user.name,

        "email":
            user.email
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/api/chat")
def chat(

    request: ChatRequest,

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    message_text = request.message.strip()


    if not message_text:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )


    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    # Save user message

    user_message = ChatMessage(

        user_id=user_id,

        role="user",

        message=message_text
    )


    db.add(user_message)

    db.commit()


    # Get history

    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == user_id
        )
        .order_by(
            ChatMessage.id
        )
        .all()
    )


    conversation = ""


    for message in messages:

        if message.role == "user":

            conversation += (
                f"User: {message.message}\n"
            )

        else:

            conversation += (
                f"Assistant: {message.message}\n"
            )


    system_instruction = """
You are an AI Career Assistant.

You help students and job seekers with:

- Data Structures and Algorithms
- Java
- Python
- C
- C++
- SQL
- OOP
- DBMS
- Operating Systems
- Computer Networks
- Resume preparation
- Technical interviews
- HR interviews
- Coding interviews
- Career guidance
- Mock interviews

Rules:

1. Explain concepts clearly.

2. Use beginner-friendly language.

3. Explain the approach before code.

4. Give code when requested.

5. Mention time and space complexity
   for algorithmic problems.

6. Give examples when useful.

7. Remember the conversation context.

8. Keep answers relevant.

9. Prefer Java unless the user
   requests another language.

10. For DSA questions, explain the
    pattern and step-by-step approach.
"""


    try:

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=conversation,

            config={
                "system_instruction":
                    system_instruction
            }
        )


        ai_response = (
            response.text
            if response.text
            else
            "I could not generate a response."
        )


    except Exception as e:

        print("Gemini chat error:", e)

        raise HTTPException(

            status_code=500,

            detail="AI service is currently unavailable."
        )


    # Save AI response

    assistant_message = ChatMessage(

        user_id=user_id,

        role="assistant",

        message=ai_response
    )


    db.add(assistant_message)

    db.commit()


    return {

        "response":
            ai_response,

        "user_id":
            user_id
    }


# =========================================================
# CHAT HISTORY
# =========================================================

@app.get("/api/chat/history")
def chat_history(

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == user_id
        )
        .order_by(
            ChatMessage.id
        )
        .all()
    )


    return {

        "messages": [

            {

                "id":
                    message.id,

                "role":
                    message.role,

                "message":
                    message.message,

                "created_at":
                    (
                        message.created_at.isoformat()
                        if message.created_at
                        else None
                    )
            }

            for message in messages
        ]
    }


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.post("/api/resume/analyze")
async def analyze_resume(

    file: UploadFile = File(...),

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    allowed_types = {

        "application/pdf",

        "image/png",

        "image/jpeg"
    }


    if file.content_type not in allowed_types:

        raise HTTPException(

            status_code=400,

            detail=
                "Only PDF, PNG and JPG/JPEG files are allowed."
        )


    file_bytes = await file.read()


    max_size = 5 * 1024 * 1024


    if len(file_bytes) > max_size:

        raise HTTPException(

            status_code=400,

            detail="Resume must be smaller than 5 MB."
        )


    prompt = """
You are an expert resume analyzer and career assistant.

Analyze the uploaded resume carefully.

Return a detailed report using this structure:

# Resume Analysis

## 1. ATS Score
Give an ATS score out of 100.
Explain why.

## 2. Resume Summary
Summarize the candidate.

## 3. Technical Skills
List technical skills found.

## 4. Soft Skills
List soft skills found.

## 5. Education
List education details.

## 6. Projects
List important projects.

## 7. Experience
List work/internship experience if present.

## 8. Strengths
List strong points.

## 9. Weaknesses
List weaknesses.

## 10. Missing / Recommended Skills
Suggest useful skills.

## 11. ATS Optimization
Suggest improvements.

## 12. Overall Recommendations
Give practical suggestions.

Focus on software engineering,
technology jobs and fresher opportunities.

Do not invent information.
"""


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if file.content_type == "application/pdf":

        try:

            resume_text = extract_text_from_pdf(
                file_bytes
            )

        except Exception as e:

            print("PDF extraction error:", e)

            raise HTTPException(

                status_code=400,

                detail="Unable to read the PDF."
            )


        if not resume_text.strip():

            raise HTTPException(

                status_code=400,

                detail=(
                    "No text could be extracted "
                    "from this PDF."
                )
            )


        full_prompt = (

            prompt
            + "\n\nRESUME CONTENT:\n"
            + resume_text
        )


        try:

            response = client.models.generate_content(

                model=GEMINI_MODEL,

                contents=full_prompt
            )


            analysis = response.text


        except Exception as e:

            print(
                "Gemini resume error:",
                e
            )

            raise HTTPException(

                status_code=500,

                detail="Resume analysis failed."
            )


    # -----------------------------------------------------
    # IMAGE
    # -----------------------------------------------------

    else:

        try:

            response = client.models.generate_content(

                model=GEMINI_MODEL,

                contents=[

                    prompt,

                    {
                        "inline_data": {

                            "mime_type":
                                file.content_type,

                            "data":
                                file_bytes
                        }
                    }
                ]
            )


            analysis = response.text


        except Exception as e:

            print(
                "Gemini image error:",
                e
            )

            raise HTTPException(

                status_code=500,

                detail=
                    "Image resume analysis failed."
            )


    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    resume_record = ResumeAnalysis(

        user_id=user_id,

        filename=file.filename,

        analysis=analysis
    )


    db.add(resume_record)


    # Also save to chat

    chat_record = ChatMessage(

        user_id=user_id,

        role="assistant",

        message=(
            f"📄 Resume Analysis: "
            f"{file.filename}\n\n"
            f"{analysis}"
        )
    )


    db.add(chat_record)

    db.commit()


    return {

        "message":
            "Resume analyzed successfully",

        "filename":
            file.filename,

        "analysis":
            analysis,

        "user_id":
            user_id
    }


# =========================================================
# RESUME HISTORY
# =========================================================

@app.get("/api/resume/history")
def resume_history(

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    records = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == user_id
        )
        .order_by(
            ResumeAnalysis.id.desc()
        )
        .all()
    )


    return {

        "resumes": [

            {

                "id":
                    record.id,

                "filename":
                    record.filename,

                "analysis":
                    record.analysis,

                "created_at":
                    (
                        record.created_at.isoformat()
                        if record.created_at
                        else None
                    )
            }

            for record in records
        ]
    }


# =========================================================
# MOCK INTERVIEW
# =========================================================

@app.post("/api/mock-interview/start")
def start_mock_interview(

    request: MockInterviewRequest,

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    role = request.role.strip()


    if not role:

        raise HTTPException(

            status_code=400,

            detail="Role is required"
        )


    prompt = f"""
You are conducting a technical mock interview.

Candidate role:
{role}

Generate ONE interview question.

The question should be suitable for
a software engineering candidate.

Do not provide the answer.

Return only the question.
"""


    try:

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=prompt
        )


        question = response.text.strip()


    except Exception as e:

        print(
            "Mock interview error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail="Unable to generate interview question."
        )


    interview = MockInterview(

        user_id=user_id,

        role=role,

        question=question
    )


    db.add(interview)

    db.commit()

    db.refresh(interview)


    return {

        "interview_id":
            interview.id,

        "role":
            role,

        "question":
            question
    }


# =========================================================
# EVALUATE MOCK INTERVIEW
# =========================================================

@app.post("/api/mock-interview/evaluate")
def evaluate_mock_interview(

    request: EvaluateInterviewRequest,

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    interview = (
        db.query(MockInterview)
        .filter(
            MockInterview.id ==
            request.interview_id
        )
        .filter(
            MockInterview.user_id ==
            user_id
        )
        .first()
    )


    if not interview:

        raise HTTPException(

            status_code=404,

            detail="Interview question not found."
        )


    prompt = f"""
You are a technical interviewer.

Role:
{interview.role}

Question:
{interview.question}

Candidate answer:
{request.answer}

Evaluate the answer.

Return exactly:

Score: X/10

Feedback:
...

Strengths:
...

Weaknesses:
...

Better Answer:
...

Keep the feedback practical and
beginner-friendly.
"""


    try:

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=prompt
        )


        feedback = response.text


    except Exception as e:

        print(
            "Interview evaluation error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail="Unable to evaluate answer."
        )


    score = None


    try:

        first_line = feedback.split("\n")[0]

        score_text = (
            first_line
            .replace("Score:", "")
            .replace("/10", "")
            .strip()
        )

        score = int(score_text)

    except Exception:

        score = None


    interview.answer = request.answer

    interview.feedback = feedback

    interview.score = score


    db.commit()


    return {

        "interview_id":
            interview.id,

        "score":
            score,

        "feedback":
            feedback
    }


# =========================================================
# MOCK INTERVIEW HISTORY
# =========================================================

@app.get("/api/mock-interview/history")
def mock_interview_history(

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db)
):

    interviews = (
        db.query(MockInterview)
        .filter(
            MockInterview.user_id == user_id
        )
        .order_by(
            MockInterview.id.desc()
        )
        .all()
    )


    return {

        "interviews": [

            {

                "id":
                    interview.id,

                "role":
                    interview.role,

                "question":
                    interview.question,

                "answer":
                    interview.answer,

                "feedback":
                    interview.feedback,

                "score":
                    interview.score,

                "created_at":
                    (
                        interview.created_at.isoformat()
                        if interview.created_at
                        else None
                    )
            }

            for interview in interviews
        ]
    }