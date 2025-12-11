from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/connect",
    tags=["Connections"]
)

def auto_accept_old_requests(requests, db: Session):
    """
    Auto-accept pending requests that are older than 30 seconds.
    """
    changed = False
    now = datetime.utcnow()
    for req in requests:
        if req.status == "Pending" and req.created_at and (now - req.created_at) >= timedelta(minutes=1):
            req.status = "Accepted"
            changed = True

    if changed:
        db.commit()
        # Refresh objects after commit so latest values are returned
        for req in requests:
            db.refresh(req)


@router.post("/request", response_model=schemas.ConnectionRequestOut)
def send_connection_request(
    req: schemas.ConnectionRequestCreate,
    db: Session = Depends(get_db)
):
    """Student sends a connection request to an alumni."""

    # Check student exists
    student = db.query(models.Student).filter(models.Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check alumni exists
    alumni = db.query(models.Alumni).filter(models.Alumni.id == req.alumni_id).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")

    # Check if a pending request already exists
    existing = (
        db.query(models.ConnectionRequest)
        .filter(
            models.ConnectionRequest.student_id == req.student_id,
            models.ConnectionRequest.alumni_id == req.alumni_id,
            models.ConnectionRequest.status == "Pending"
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request already exists for this student and alumni.",
        )

    new_req = models.ConnectionRequest(
        student_id=req.student_id,
        alumni_id=req.alumni_id,
        status="Pending"
    )

    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return new_req


@router.get("/student/{student_id}", response_model=List[schemas.ConnectionRequestOut])
def get_student_requests(student_id: int, db: Session = Depends(get_db)):
    """List all connection requests for a given student."""
    requests = (
        db.query(models.ConnectionRequest)
        .filter(models.ConnectionRequest.student_id == student_id)
        .all()
    )

    # Auto-accept old pending ones
    auto_accept_old_requests(requests, db)

    return requests


@router.get("/alumni/{alumni_id}", response_model=List[schemas.ConnectionRequestOut])
def get_alumni_requests(alumni_id: int, db: Session = Depends(get_db)):
    """List all connection requests for a given alumni."""
    requests = (
        db.query(models.ConnectionRequest)
        .filter(models.ConnectionRequest.alumni_id == alumni_id)
        .all()
    )

    auto_accept_old_requests(requests, db)

    return requests



@router.post("/{request_id}/status", response_model=schemas.ConnectionRequestOut)
def update_request_status(
    request_id: int,
    body: schemas.ConnectionRequestUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Update status of a connection request.
    Normally alumni would call this through their UI.
    """

    req = db.query(models.ConnectionRequest).filter(models.ConnectionRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Connection request not found")

    new_status = body.status.capitalize()
    if new_status not in ["Pending", "Accepted", "Rejected"]:
        raise HTTPException(status_code=400, detail="Status must be Pending, Accepted, or Rejected")

    req.status = new_status
    db.commit()
    db.refresh(req)

    return req
