from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import random

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/recommend",
    tags=["Recommendations"]
)


def compute_skill_score(student_skills: str, alumni_skills: Optional[str]) -> float:
    """
    Very simple similarity:
    score = common_skills / total_student_skills
    """
    if not student_skills or not alumni_skills:
        return 0.0

    student_list = [s.strip().lower() for s in student_skills.split(",") if s.strip()]
    alumni_list = [s.strip().lower() for s in alumni_skills.split(",") if s.strip()]

    if not student_list:
        return 0.0

    common = set(student_list).intersection(set(alumni_list))
    return len(common) / len(student_list)


class RecommendationOut(schemas.AlumniOut):
    match_score: float
    reason: str


@router.get("/student/{student_id}", response_model=List[RecommendationOut])
def recommend_for_student(student_id: int, db: Session = Depends(get_db), top_k: int = 10):
    """
    Recommend top K alumni for a given student based on skill overlap.
    ✅ Now returns RANDOM recommendations each time!
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    alumni_list = (
        db.query(models.Alumni)
        .filter(models.Alumni.mentorship_available == True)
        .all()
    )

    recommendations: List[RecommendationOut] = []

    for alum in alumni_list:
        score = compute_skill_score(student.skills or "", alum.skills)
        if score == 0:
            reason = "No matching skills"
        else:
            reason = "Common skills: " + ", ".join(
                set(
                    [s.strip() for s in (student.skills or "").split(",")]
                ).intersection(
                    set([s.strip() for s in (alum.skills or "").split(",")])
                )
            )

        rec = RecommendationOut(
            id=alum.id,
            alumni_id=alum.alumni_id,
            name=alum.name,
            graduation_year=alum.graduation_year,
            department=alum.department,
            current_role=alum.current_role,
            company=alum.company,
            experience_years=alum.experience_years,
            skills=alum.skills,
            domain=alum.domain,
            location=alum.location,
            mentorship_available=alum.mentorship_available,
            match_score=round(score, 2),
            reason=reason,
        )
        recommendations.append(rec)

    # ✅ OPTION 1: Sort by score, then SHUFFLE within score groups
    recommendations.sort(key=lambda r: r.match_score, reverse=True)
    
    # Shuffle top matches to add randomness
    if len(recommendations) > top_k:
        # Keep high scorers (>0.5) prioritized but randomized
        high_scores = [r for r in recommendations if r.match_score > 0.3]
        random.shuffle(high_scores)
        return high_scores[:top_k]
    else:
        random.shuffle(recommendations)
        return recommendations


# ✅ OPTION 2: Pure random (uncomment to use)
# @router.get("/student/{student_id}", response_model=List[RecommendationOut])
# def recommend_for_student(student_id: int, db: Session = Depends(get_db), top_k: int = 10):
#     """
#     Recommend K random alumni with at least some skill match.
#     """
#     student = db.query(models.Student).filter(models.Student.id == student_id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")
# 
#     alumni_list = (
#         db.query(models.Alumni)
#         .filter(models.Alumni.mentorship_available == True)
#         .all()
#     )
# 
#     recommendations: List[RecommendationOut] = []
# 
#     for alum in alumni_list:
#         score = compute_skill_score(student.skills or "", alum.skills)
#         if score > 0:  # Only include alumni with some match
#             reason = "Common skills: " + ", ".join(...)
#             rec = RecommendationOut(...)
#             recommendations.append(rec)
# 
#     # ✅ Shuffle and return random top_k
#     random.shuffle(recommendations)
#     return recommendations[:top_k]






































# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from ..database import get_db
# from .. import models, schemas

# router = APIRouter(
#     prefix="/recommend",
#     tags=["Recommendations"]
# )


# def compute_skill_score(student_skills: str, alumni_skills: Optional[str]) -> float:
#     """
#     Very simple similarity:
#     score = common_skills / total_student_skills
#     """
#     if not student_skills or not alumni_skills:
#         return 0.0

#     student_list = [s.strip().lower() for s in student_skills.split(",") if s.strip()]
#     alumni_list = [s.strip().lower() for s in alumni_skills.split(",") if s.strip()]

#     if not student_list:
#         return 0.0

#     common = set(student_list).intersection(set(alumni_list))
#     return len(common) / len(student_list)


# class RecommendationOut(schemas.AlumniOut):
#     match_score: float
#     reason: str


# @router.get("/student/{student_id}", response_model=List[RecommendationOut])
# def recommend_for_student(student_id: int, db: Session = Depends(get_db), top_k: int = 10):
#     """
#     Recommend top K alumni for a given student based on skill overlap.
#     Later we will replace this with embeddings + RL.
#     """
#     student = db.query(models.Student).filter(models.Student.id == student_id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")

#     alumni_list = (
#         db.query(models.Alumni)
#         .filter(models.Alumni.mentorship_available == True)
#         .all()
#     )

#     recommendations: List[RecommendationOut] = []

#     for alum in alumni_list:
#         score = compute_skill_score(student.skills or "", alum.skills)
#         if score == 0:
#             reason = "No matching skills"
#         else:
#             reason = "Common skills: " + ", ".join(
#                 set(
#                     [s.strip() for s in (student.skills or "").split(",")]
#                 ).intersection(
#                     set([s.strip() for s in (alum.skills or "").split(",")])
#                 )
#             )

#         rec = RecommendationOut(
#             id=alum.id,
#             alumni_id=alum.alumni_id,
#             name=alum.name,
#             graduation_year=alum.graduation_year,
#             department=alum.department,
#             current_role=alum.current_role,
#             company=alum.company,
#             experience_years=alum.experience_years,
#             skills=alum.skills,
#             domain=alum.domain,
#             location=alum.location,
#             mentorship_available=alum.mentorship_available,
#             match_score=round(score, 2),
#             reason=reason,
#         )
#         recommendations.append(rec)

#     # sort by score high → low
#     recommendations.sort(key=lambda r: r.match_score, reverse=True)

#     # return top K
#     return recommendations[:top_k]  
