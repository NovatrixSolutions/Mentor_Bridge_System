from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import hashlib

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# Fast SHA256 hashing for development
def hash_password(password: str) -> str:
    """Fast SHA256 hash (instant, good for development/testing)"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    """Fast SHA256 verification (1-2ms)"""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest() == hashed

@router.post("/register", response_model=schemas.StudentOut)
def register_student(student_in: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Register new student"""
    existing = db.query(models.Student).filter(models.Student.email == student_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed = hash_password(student_in.password)

    student = models.Student(
        name=student_in.name,
        email=student_in.email,
        password_hash=hashed,
        department=student_in.department,
        year=student_in.year,
        skills=student_in.skills,
        interests=student_in.interests,
        career_goal=student_in.career_goal,
    )

    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.post("/login", response_model=schemas.StudentOut)
def login_student(login_data: schemas.StudentLogin, db: Session = Depends(get_db)):
    """Student login - optimized for speed"""
    student = db.query(models.Student).filter(models.Student.email == login_data.email).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(login_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return student

@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    """Get student profile by ID"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.patch("/{student_id}", response_model=schemas.StudentOut)
def update_student_profile(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update student profile (skills, interests, etc.)"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student

































































# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# import hashlib

# from ..database import get_db
# from .. import models, schemas

# router = APIRouter(
#     prefix="/students",
#     tags=["Students"]
# )


# def hash_password(password: str) -> str:
#     """Simple hash using SHA256 (for demo only)."""
#     return hashlib.sha256(password.encode("utf-8")).hexdigest()


# @router.post("/register", response_model=schemas.StudentOut)
# def register_student(student_in: schemas.StudentCreate, db: Session = Depends(get_db)):
#     # check if email already exists
#     existing = db.query(models.Student).filter(models.Student.email == student_in.email).first()
#     if existing:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered"
#         )

#     hashed = hash_password(student_in.password)

#     student = models.Student(
#         name=student_in.name,
#         email=student_in.email,
#         password_hash=hashed,
#         department=student_in.department,
#         year=student_in.year,
#         skills=student_in.skills,
#         interests=student_in.interests,
#         career_goal=student_in.career_goal,
#     )

#     db.add(student)
#     db.commit()
#     db.refresh(student)

#     return student


# @router.post("/login", response_model=schemas.StudentOut)
# def login_student(login_data: schemas.StudentLogin, db: Session = Depends(get_db)):
#     student = db.query(models.Student).filter(models.Student.email == login_data.email).first()
#     if not student:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     hashed = hash_password(login_data.password)
#     if student.password_hash != hashed:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     return student
