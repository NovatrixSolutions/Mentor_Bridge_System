from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from ..database import get_db
from .. import models, schemas

# Groq imports
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq API configured successfully")
else:
    print("⚠️ GROQ_API_KEY not found in .env file")
    client = None

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# -----------------------------
# GROQ-POWERED ANSWER
# -----------------------------
def llm_answer(db: Session, student_id: int, alumni_id: int, user_message: str) -> str:
    """
    Uses Groq API with Llama 3.3 to generate smart replies
    with context from previous messages in DB.
    """
    
    if not client:
        return (
            "⚠️ AI service is not configured. "
            "Please contact the administrator to set up GROQ_API_KEY."
        )
    
    # ✅ GET ALUMNI INFO FROM DATABASE
    alumni = db.query(models.Alumni).filter(models.Alumni.id == alumni_id).first()
    
    if not alumni:
        alumni_name = "Alumni Mentor"
        alumni_role = "Experienced Professional"
        alumni_company = ""
    else:
        alumni_name = alumni.name
        alumni_role = alumni.current_role or "Experienced Professional"
        alumni_company = f" at {alumni.company}" if alumni.company else ""
    
    # Load last 10 messages for context
    history_msgs = (
        db.query(models.Message)
        .filter(
            ((models.Message.sender_id == student_id) & (models.Message.receiver_id == alumni_id)) |
            ((models.Message.sender_id == alumni_id) & (models.Message.receiver_id == student_id))
        )
        .order_by(models.Message.created_at.asc())
        .all()
    )
    
    # ✅ BUILD SYSTEM PROMPT WITH REAL ALUMNI INFO
    messages = [
        {
            "role": "system",
            "content": (
                f"You are {alumni_name}, a {alumni_role}{alumni_company}. "
                f"You are an experienced, friendly alumni mentor helping a student with "
                f"career guidance, skills development, internships, projects, and interview "
                f"preparation. Answer clearly, practically, and encouragingly as {alumni_name}. "
                f"Use short paragraphs. Don't provide code unless specifically asked. "
                f"Stay in character as {alumni_name} throughout the conversation."
            )
        }
    ]
    
    # Add conversation history
    for msg in history_msgs[-10:]:  # last 10 for context
        role = "user" if msg.sender_type == "student" else "assistant"
        messages.append({"role": role, "content": msg.content})
    
    # Add current question
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.95
        )
        
        answer = response.choices[0].message.content.strip()
        
        if not answer:
            return "I couldn't generate a response. Please rephrase your question."
        
        return answer
        
    except Exception as e:
        print(f"❌ Groq API error: {type(e).__name__}: {str(e)}")
        
        # Better error messages
        if "rate_limit" in str(e).lower():
            return "⚠️ Too many requests. Please wait a moment and try again."
        elif "quota" in str(e).lower():
            return "⚠️ Daily quota reached. Service will reset soon."
        elif "authentication" in str(e).lower():
            return "🔒 API authentication error. Please contact administrator."
        else:
            return f"⚠️ AI service error: {str(e)[:100]}"


# -----------------------------
# SEND MESSAGE ENDPOINT
# -----------------------------
@router.post("/send", response_model=schemas.ChatReply)
def send_message(
    body: schemas.ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """
    Student sends a message to AI alumni mentor.
    We store the conversation in 'messages' and return an AI reply.
    """
    
    # Validate student & alumni exist
    student = db.query(models.Student).filter(models.Student.id == body.student_id).first()
    alumni = db.query(models.Alumni).filter(models.Alumni.id == body.alumni_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")
    
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Store student's message
    msg_user = models.Message(
        sender_id=body.student_id,
        receiver_id=body.alumni_id,
        sender_type="student",
        receiver_type="alumni_ai",
        content=body.message,
    )
    db.add(msg_user)
    
    # Generate AI reply via Groq
    ai_text = llm_answer(db, body.student_id, body.alumni_id, body.message)
    
    # Store AI's reply
    msg_bot = models.Message(
        sender_id=body.alumni_id,
        receiver_id=body.student_id,
        sender_type="alumni_ai",
        receiver_type="student",
        content=ai_text,
    )
    db.add(msg_bot)
    
    db.commit()
    
    return schemas.ChatReply(reply=ai_text)

# -----------------------------
# CHAT HISTORY ENDPOINT
# -----------------------------
@router.get("/history", response_model=List[schemas.ChatMessageOut])
def get_chat_history(
    student_id: int,
    alumni_id: int,
    db: Session = Depends(get_db)
):
    """
    Return full chat history between this student and this AI alumni.
    """
    msgs = (
        db.query(models.Message)
        .filter(
            ((models.Message.sender_id == student_id) & (models.Message.receiver_id == alumni_id)) |
            ((models.Message.sender_id == alumni_id) & (models.Message.receiver_id == student_id))
        )
        .order_by(models.Message.created_at.asc())
        .all()
    )
    
    return msgs

# -----------------------------
# CLEAR CHAT ENDPOINT
# -----------------------------
@router.delete("/clear", status_code=200)
def clear_chat(student_id: int, alumni_id: int, db: Session = Depends(get_db)):
    """
    Deletes full chat history between this student and this AI alumni.
    """
    
    deleted = (
        db.query(models.Message)
        .filter(
            ((models.Message.sender_id == student_id) & (models.Message.receiver_id == alumni_id)) |
            ((models.Message.sender_id == alumni_id) & (models.Message.receiver_id == student_id))
        )
        .delete(synchronize_session=False)
    )
    
    db.commit()
    return {"success": True, "deleted_messages": deleted}
