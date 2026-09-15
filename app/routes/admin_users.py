from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserDB
from app.models.patient import PatientDB
from app.models.appointment import AppointmentDB
from app.models.bill import BillDB
from app.core.dependencies import require_role


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin User Management"]
)


# =========================================================
# GET ALL USERS
# =========================================================

@router.get("/")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    users = db.query(UserDB).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,

            # Staff information
            "staff_type": user.staff_type,

            # Patient information
            "patient_type": user.patient_type,

            # Doctor information
            "doctor_category": user.doctor_category,
            "doctor_specialization": user.doctor_specialization
        }
        for user in users
    ]


# =========================================================
# CHANGE USER ROLE
# =========================================================

@router.put("/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    # Allowed main account roles
    allowed_roles = [
        "user",
        "staff",
        "doctor",
        "admin"
    ]

    if role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Choose user, staff, doctor, or admin."
        )

    user = db.query(UserDB).filter(
        UserDB.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent admin from changing their own role
    if int(current_user["sub"]) == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own admin role."
        )

    # Change main role
    user.role = role

    # Clear subtype information first.
    # This prevents old role information from remaining
    # after changing the account's role.

    user.staff_type = None
    user.patient_type = None
    user.doctor_category = None
    user.doctor_specialization = None

    db.commit()
    db.refresh(user)

    return {
        "message": "User role updated successfully",
        "username": user.username,
        "role": user.role,
        "staff_type": user.staff_type,
        "patient_type": user.patient_type,
        "doctor_category": user.doctor_category,
        "doctor_specialization": user.doctor_specialization
    }


# =========================================================
# DELETE USER
# =========================================================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    user = db.query(UserDB).filter(
        UserDB.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if int(current_user["sub"]) == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own admin account"
        )

    # Find linked patient
    patient = db.query(PatientDB).filter(
        PatientDB.user_id == user_id
    ).first()

    if patient:
        # Find all appointments of this patient
        appointments = db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient.id
        ).all()

        # Delete bills first, then appointments
        for appointment in appointments:
            bills = db.query(BillDB).filter(
                BillDB.appointment_id == appointment.id
            ).all()

            for bill in bills:
                db.delete(bill)

            db.delete(appointment)

        # Delete patient
        db.delete(patient)

    # Delete user
    db.delete(user)

    db.commit()

    return {
        "message": "User, linked patient, appointments and bills deleted successfully"
    }