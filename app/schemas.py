from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# --------- Alumni Schemas ---------
class AlumniBase(BaseModel):
    name: str
    email: Optional[str] = None
    graduation_year: Optional[int] = None
    department: Optional[str] = None
    current_role: Optional[str] = None
    company: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    mentorship_available: Optional[bool] = True
    alumni_id: Optional[str] = None


class AlumniCreate(AlumniBase):
    email: str  # Required for register
    graduation_year: int
    department: str


class AlumniOut(AlumniBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    alumni_id: str


# --------- Student Schemas ---------
class StudentCreate(BaseModel):
    name: str
    email: str
    password: str
    department: Optional[str] = None
    year: Optional[int] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    career_goal: Optional[str] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    department: Optional[str] = None
    year: Optional[int] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    career_goal: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    career_goal: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentLogin(BaseModel):
    email: str
    password: str


# --------- Feedback Schemas ---------
class FeedbackCreate(BaseModel):
    student_id: int
    alumni_id: int
    rating: Optional[float] = None
    comment: Optional[str] = None


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    alumni_id: int
    rating: Optional[float] = None
    comment: Optional[str] = None
    reward: Optional[float] = None


# --------- Connection Schemas ---------
class ConnectionRequestCreate(BaseModel):
    student_id: int
    alumni_id: int


class ConnectionRequestUpdateStatus(BaseModel):
    status: str


class ConnectionRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    alumni_id: int
    status: str
    created_at: Optional[datetime] = None


# --------- Chat Schemas ---------
class ChatMessageCreate(BaseModel):
    student_id: int
    alumni_id: int
    message: str


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_id: int
    receiver_id: int
    sender_type: str
    receiver_type: str
    content: str
    created_at: datetime


class ChatReply(BaseModel):
    reply: str


# --------- Email Schema ---------
class EmailToMentor(BaseModel):
    student_id: int
    alumni_id: int
    subject: str
    message: str


# --------- Recommendation Schema (for recommend.py) ---------
class RecommendationOut(AlumniOut):
    match_score: float
    reason: str

    model_config = ConfigDict(from_attributes=True)  # ✅ FIXED: added closing parenthesis














































# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime


# # --------- Alumni Schemas (already there) ---------

# class AlumniBase(BaseModel):
    
#     name: str
#     graduation_year: Optional[int] = None
#     department: Optional[str] = None
#     current_role: Optional[str] = None
#     company: Optional[str] = None
#     experience_years: Optional[int] = None
#     skills: Optional[str] = None
#     domain: Optional[str] = None
#     location: Optional[str] = None
#     mentorship_available: Optional[bool] = True
#     email: Optional[str] = None


# class AlumniOut(AlumniBase):
#     id: int

#     class Config:
#         from_attributes = True


# # --------- Student Schemas ---------

# class StudentCreate(BaseModel):
#     name: str
#     email: str
#     password: str          # we will hash it before saving
#     department: Optional[str] = None
#     year: Optional[int] = None
#     skills: Optional[str] = None        # "Python, SQL, ML"
#     interests: Optional[str] = None
#     career_goal: Optional[str] = None


# class StudentOut(BaseModel):
#     id: int
#     name: str
#     email: str
#     department: Optional[str] = None
#     year: Optional[int] = None
#     skills: Optional[str] = None
#     interests: Optional[str] = None
#     career_goal: Optional[str] = None

#     class Config:
#         from_attributes  = True


# class AlumniCreate(BaseModel):
#     # alumni_id: str
#     name: str
#     email: str
#     graduation_year: int
#     department: str
#     current_role: Optional[str] = None
#     company: Optional[str] = None
#     experience_years: Optional[int] = None
#     skills: Optional[str] = None
#     domain: Optional[str] = None
#     location: Optional[str] = None

#     class Config:
#         from_attributes = True


# class StudentLogin(BaseModel):
#     email: str
#     password: str


# class FeedbackCreate(BaseModel):
#     student_id: int
#     alumni_id: int
#     rating: Optional[float] = None   # 1–5
#     comment: Optional[str] = None


# class FeedbackOut(BaseModel):
#     id: int
#     student_id: int
#     alumni_id: int
#     rating: Optional[float] = None
#     comment: Optional[str] = None
#     reward: Optional[float] = None   # used later for RL

#     class Config:
#         from_attributes = True



# # --------- Connection Request Schemas ---------

# class ConnectionRequestCreate(BaseModel):
#     student_id: int
#     alumni_id: int


# class ConnectionRequestUpdateStatus(BaseModel):
#     status: str  # "Pending", "Accepted", "Rejected"


# class ConnectionRequestOut(BaseModel):
#     id: int
#     student_id: int
#     alumni_id: int
#     status: str

#     class Config:
#         from_attributes = True



# # --------- Chat / Message Schemas ---------



# # --------- Chat / Message Schemas ---------

# class ChatMessageCreate(BaseModel):
#     student_id: int
#     alumni_id: int
#     message: str


# class ChatMessageOut(BaseModel):
#     id: int
#     sender_id: int
#     receiver_id: int
#     sender_type: str
#     receiver_type: str
#     content: str
#     created_at: datetime

#     class Config:
#         from_attributes = True


# class ChatReply(BaseModel):
#     reply: str


# class EmailToMentor(BaseModel):
#     student_id: int
#     alumni_id: int
#     subject: str
#     message: str
