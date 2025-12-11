from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


def compute_reward_from_rating(rating: float | None) -> float | None:
    """
    Simple reward function for now:
    - If rating is None -> reward = None
    - Else reward = rating / 5  (so range 0.0–1.0)
    """
    if rating is None:
        return None
    return round(float(rating) / 5.0, 3)


@router.post("/", response_model=schemas.FeedbackOut)
def submit_feedback(
    fb: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    # check student and alumni exist
    student = db.query(models.Student).filter(models.Student.id == fb.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    alumni = db.query(models.Alumni).filter(models.Alumni.id == fb.alumni_id).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")

    reward = compute_reward_from_rating(fb.rating)

    interaction = models.Interaction(
        student_id=fb.student_id,
        alumni_id=fb.alumni_id,
        rating=fb.rating,
        comment=fb.comment,
        reward=reward,
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return interaction


@router.get("/", response_model=List[schemas.FeedbackOut])
def list_feedback(db: Session = Depends(get_db)):
    return db.query(models.Interaction).all()
