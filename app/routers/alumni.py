from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
import pandas as pd
import time
import random
from ..database import get_db

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/alumni",
    tags=["Alumni"]
)


# ---------------------------------------------------------
# 1) Get all alumni
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.AlumniOut])
def get_all_alumni(db: Session = Depends(get_db)):
    """Return all alumni from the database."""
    return db.query(models.Alumni).all()


# ---------------------------------------------------------
# 2) One-time CSV import (existing code, kept same)
# ---------------------------------------------------------
@router.post("/import_csv")
def import_alumni_from_csv(db: Session = Depends(get_db)):
    """
    One-time endpoint to import alumni from alumni_dataset.csv into the DB.
    If data already exists, it just returns the count.
    """

    existing_count = db.query(models.Alumni).count()
    if existing_count > 0:
        return {
            "status": "already_imported",
            "rows_in_db": existing_count
        }

    # CSV path: backend/alumni_dataset.csv
    csv_path = Path(__file__).resolve().parents[2] / "alumni_dataset.csv"

    if not csv_path.exists():
        return {"status": "error", "detail": f"CSV file not found at {csv_path}"}

    df = pd.read_csv(csv_path)

    # Columns expected:
    # ID, Name, Grad Year, Dept, Current Role, Company,
    # Exp (yrs), Skills, Domain, Location, Mentor Available
    for _, row in df.iterrows():
        mentor_available_str = str(row["Mentor Available"]).strip().lower()
        mentor_available = mentor_available_str == "yes"

        alumni = models.Alumni(
            alumni_id=str(row["ID"]),
            name=row["Name"],
            # if your model has email and CSV doesn’t, keep it None
            email=None,
            graduation_year=int(row["Grad Year"]),
            department=row["Dept"],
            current_role=row["Current Role"],
            company=row["Company"],
            experience_years=int(row["Exp (yrs)"]),
            skills=row["Skills"],
            domain=row["Domain"],
            location=row["Location"],
            mentorship_available=mentor_available,
        )

        db.add(alumni)

    db.commit()
    inserted_count = db.query(models.Alumni).count()

    return {
        "status": "imported",
        "rows_inserted": inserted_count
    }


# ---------------------------------------------------------
# 3) Alumni self-registration from frontend
# ---------------------------------------------------------
@router.post(
    "/register",
    response_model=schemas.AlumniOut,
    status_code=status.HTTP_201_CREATED
)
def register_alumni(payload: schemas.AlumniCreate, db: Session = Depends(get_db)):
    """
    Register a new alumni from the frontend form.
    Uses email to avoid duplicates and generates a unique alumni_id.
    """

    # Optional: avoid duplicate alumni by email
    if payload.email:
        existing = (
            db.query(models.Alumni)
            .filter(models.Alumni.email == payload.email)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An alumni with this email already exists."
            )

    # Generate a unique alumni_id if your DB column is NOT NULL
    unique_suffix = f"{int(time.time())}{random.randint(100, 999)}"
    generated_alumni_id = f"ALU{unique_suffix}"

    # Experience can be null from frontend → store 0
    exp_years = payload.experience_years if payload.experience_years is not None else 0

    alumni = models.Alumni(
        alumni_id=generated_alumni_id,
        name=payload.name,
        email=payload.email,
        graduation_year=payload.graduation_year,
        department=payload.department,
        current_role=payload.current_role,
        company=payload.company,
        experience_years=exp_years,
        skills=payload.skills,
        domain=payload.domain,
        location=payload.location,
        # default: they are willing to mentor
        mentorship_available=True,
    )

    db.add(alumni)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # This will show the REAL DB error in Swagger instead of a blank 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB error while saving alumni: {e}"
        )

    db.refresh(alumni)
    return alumni







