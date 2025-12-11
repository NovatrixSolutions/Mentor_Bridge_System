from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime



class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    department = Column(String, nullable=True)
    year = Column(Integer, nullable=True)

    skills = Column(String, nullable=True)        # comma-separated
    interests = Column(String, nullable=True)     # comma-separated
    career_goal = Column(String, nullable=True)

    # One student → many interactions
    interactions = relationship("Interaction", back_populates="student")


class Alumni(Base):
    __tablename__ = "alumni"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(String, unique=True, index=True, nullable=False)  # A001...
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)   # ✅ NEW


    graduation_year = Column(Integer, nullable=True)
    department = Column(String, nullable=True)
    current_role = Column(String, nullable=True)
    company = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)

    skills = Column(String, nullable=True)        # comma-separated
    domain = Column(String, nullable=True)
    location = Column(String, nullable=True)

    mentorship_available = Column(Boolean, default=True)

    # One alumni → many interactions
    interactions = relationship("Interaction", back_populates="alumni")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"))
    alumni_id = Column(Integer, ForeignKey("alumni.id"))

    rating = Column(Float, nullable=True)         # 1–5
    comment = Column(String, nullable=True)
    reward = Column(Float, nullable=True)         # for RL later

    # Relationships
    student = relationship("Student", back_populates="interactions")
    alumni = relationship("Alumni", back_populates="interactions")


class ConnectionRequest(Base):
    __tablename__ = "connection_requests"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    alumni_id = Column(Integer, ForeignKey("alumni.id"), nullable=False)

    status = Column(String, default="Pending")  # "Pending", "Accepted", "Rejected"
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships (optional, helpful)
    student = relationship("Student", backref="connection_requests")
    alumni = relationship("Alumni", backref="connection_requests")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, nullable=False)     # can be student or alumni (we'll distinguish later)
    receiver_id = Column(Integer, nullable=False)   # counterpart ID
    sender_type = Column(String, nullable=False)    # "student" or "alumni"
    receiver_type = Column(String, nullable=False)  # "student" or "alumni"

    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # For now, keep it simple (no FK constraints to both tables to avoid complexity)
