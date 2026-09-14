from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserDB
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/staff",
    tags=["Staff"]
)


@router.get("/")
def get_all_staff(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    # Admin, Staff and Doctor
    # can view staff information.
    if role not in ["admin", "staff", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Staff records are not available for this account."
        )

    staff_members = db.query(UserDB).filter(
        UserDB.role == "staff"
    ).all()

    return [
        {
            "id": staff.id,
            "username": staff.username,
            "email": staff.email,
            "staff_type": staff.staff_type
        }
        for staff in staff_members
    ]