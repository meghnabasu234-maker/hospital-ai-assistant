from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import UserDB
from app.models.patient import PatientDB
from app.models.doctor import DoctorDB

from app.schemas.auth import UserRegister, UserLogin, PasswordReset, Token

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # CHECK USERNAME
    # -------------------------------------------------

    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # -------------------------------------------------
    # CHECK EMAIL
    # -------------------------------------------------

    existing_email = db.query(UserDB).filter(
        UserDB.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # -------------------------------------------------
    # VALID ROLES
    # -------------------------------------------------

    if user.role not in ["user", "staff", "doctor", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Choose user, staff, doctor, or admin."
        )

    # -------------------------------------------------
    # STAFF TYPES
    # -------------------------------------------------

    allowed_staff_types = [
        "Nursing Staff",
        "Floor / Operations Staff",
        "Patient & Family Support Staff",
        "Staff Well-being Staff",
        "Hospital Administration Staff"
    ]

    # -------------------------------------------------
    # PATIENT TYPES
    # -------------------------------------------------

    allowed_patient_types = [
        "New Patient",
        "Existing Patient",
        "Emergency Patient"
    ]

    # -------------------------------------------------
    # DOCTOR TYPES
    # -------------------------------------------------

    doctor_types = {
        "Primary Care & General Practice": [
            "General Practitioner",
            "Pediatrician"
        ],

        "Medical Specialist": [
            "Cardiologist",
            "Neurologist",
            "Oncologist",
            "Psychiatrist",
            "Psychologist"
        ],

        "Acute & Diagnostic Care": [
            "Emergency Medicine Physician",
            "Radiologist",
            "Pathologist"
        ],

        "Surgical": [
            "Surgeon"
        ]
    }

    # -------------------------------------------------
    # ADMIN VALIDATION
    # -------------------------------------------------

    if user.role == "admin":

        if (
            user.staff_type is not None
            or user.patient_type is not None
            or user.doctor_category is not None
            or user.doctor_specialization is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Admin accounts cannot have a subtype."
            )

    # -------------------------------------------------
    # STAFF VALIDATION
    # -------------------------------------------------

    elif user.role == "staff":

        if user.staff_type not in allowed_staff_types:
            raise HTTPException(
                status_code=400,
                detail="Please select a valid Staff Type."
            )

        if (
            user.patient_type is not None
            or user.doctor_category is not None
            or user.doctor_specialization is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Staff accounts cannot have Patient or Doctor details."
            )

    # -------------------------------------------------
    # DOCTOR VALIDATION
    # -------------------------------------------------

    elif user.role == "doctor":

        if user.doctor_category not in doctor_types:
            raise HTTPException(
                status_code=400,
                detail="Please select a valid Doctor Category."
            )

        allowed_specializations = doctor_types[
            user.doctor_category
        ]

        if user.doctor_specialization not in allowed_specializations:
            raise HTTPException(
                status_code=400,
                detail="Please select a valid Doctor Specialization."
            )

        if (
            user.staff_type is not None
            or user.patient_type is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Doctor accounts cannot have Staff or Patient subtypes."
            )

    # -------------------------------------------------
    # PATIENT VALIDATION
    # -------------------------------------------------

    elif user.role == "user":

        if user.patient_type not in allowed_patient_types:
            raise HTTPException(
                status_code=400,
                detail="Please select a valid Patient Type."
            )

        if (
            user.staff_type is not None
            or user.doctor_category is not None
            or user.doctor_specialization is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Patient accounts cannot have Staff or Doctor details."
            )

    # -------------------------------------------------
    # CREATE USER
    # -------------------------------------------------

    new_user = UserDB(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        staff_type=user.staff_type,
        patient_type=user.patient_type,
        doctor_category=user.doctor_category,
        doctor_specialization=user.doctor_specialization
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # -------------------------------------------------
    # CREATE PATIENT RECORD
    # -------------------------------------------------

    if user.role == "user":

        new_patient = PatientDB(
            user_id=new_user.id,
            name=user.username,
            age=user.age if user.age is not None else 0,
            gender=user.gender if user.gender else "Not specified",
            disease=user.disease if user.disease else "Not specified"

        )

        db.add(new_patient)

    # -------------------------------------------------
    # CREATE DOCTOR RECORD
    # -------------------------------------------------

    elif user.role == "doctor":

        new_doctor = DoctorDB(
            user_id=new_user.id,
            name=user.username,
            specialization=user.doctor_specialization,
            department_id=0
        )

        db.add(new_doctor)

    db.commit()

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "staff_type": new_user.staff_type,
        "patient_type": new_user.patient_type,
        "doctor_category": new_user.doctor_category,
        "doctor_specialization": new_user.doctor_specialization
    }


# =====================================================
# LOGIN
# =====================================================

@router.post("/login", response_model=Token)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(existing_user.id),
            "role": existing_user.role,
            "staff_type": existing_user.staff_type,
            "patient_type": existing_user.patient_type,
            "doctor_category": existing_user.doctor_category,
            "doctor_specialization": existing_user.doctor_specialization
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =====================================================
# RESET PASSWORD
# =====================================================

@router.put("/reset-password")
def reset_password(
    user: PasswordReset,
    db: Session = Depends(get_db)
):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_user.password_hash = hash_password(
        user.new_password
    )

    db.commit()

    return {
        "message": "Password reset successfully"
    }