from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from email.message import EmailMessage
import smtplib

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/email", tags=["Email"])

# --- SMTP CONFIG ---
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "mullasameera66@gmail.com"
SMTP_PASSWORD = "your_app_password_here"   # Gmail App Password Only (not login password)

# --- Constant Mentor Email ---
MENTOR_EMAIL = "mentor.inbox@example.com"   # replace with your fixed mentor email


@router.post("/send")
def send_email_to_mentor(body: schemas.EmailToMentor, db: Session = Depends(get_db)):
    """
    Sends an email to a constant mentor email.
    Visible sender & reply-to fields will show student's email.
    """

    student = db.query(models.Student).filter(models.Student.id == body.student_id).first()
    alumni = db.query(models.Alumni).filter(models.Alumni.id == body.alumni_id).first()

    if not student or not alumni:
        raise HTTPException(status_code=404, detail="Student or Alumni not found")

    # Build the email
    msg = EmailMessage()
    msg["Subject"] = body.subject

    # Visible sender → student email (DYNAMIC)
    msg["From"] = f"{student.name} <{student.email}>"

    # Mentor replies → student (DYNAMIC)
    msg["Reply-To"] = student.email

    # Actual target inbox → mentor (STATIC)
    msg["To"] = MENTOR_EMAIL

    # Email content
    msg.set_content(
        f"Hello Mentor,\n\n"
        f"You received a new message from a student via MentorBridge.\n\n"
        f"--- Student Details ---\n"
        f"Name : {student.name}\n"
        f"Email: {student.email}\n"
        f"ID   : {student.id}\n\n"
        f"--- Selected Alumni (Context) ---\n"
        f"{alumni.name}  (ID: {alumni.id})\n\n"
        f"--- Student Message ---\n"
        f"{body.message}\n\n"
        f"------------------------\n"
        f"Sent via MentorBridge Alumni Recommendation System"
    )

    # Send email
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("Email error:", e)
        raise HTTPException(status_code=500, detail="Failed to send email.")

    return {
        "success": True,
        "sent_to": MENTOR_EMAIL,
        "reply_to": student.email
    }
