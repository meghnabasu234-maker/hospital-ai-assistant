from urllib import response

from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import os

from app.database import get_db
from app.department import Department
from app.patient import Patient
from app.doctor import Doctor
from app.appointment import Appointment
from app.chat import ChatRequest

from app.models.department import DepartmentDB
from app.models.patient import PatientDB
from app.models.doctor import DoctorDB
from app.models.appointment import AppointmentDB
from app.models.bill import BillDB
from app.models.chat_history import ChatHistoryDB

from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.indexing import router as indexing_router
from app.routes.admin_users import router as admin_users_router
from app.routes.staff import router as staff_router
from app.routes.departments import router as departments_router

from app.core.dependencies import get_current_user, require_role

from app.rag.retriever import retrieve_context
from app.websocket.chat_handler import handle_chat


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in the environment.")

groq_client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI-Powered Hospital Knowledge and Appointment Assistant",
    description=(
        "A secure hospital backend with JWT authentication, "
        "role-based access, appointment management, billing, "
        "document-based RAG, and an AI hospital assistant."
    ),
    version="1.0.0"
)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(indexing_router)
app.include_router(admin_users_router)
app.include_router(staff_router)
app.include_router(departments_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI-Powered Hospital Knowledge and Appointment Assistant is running."
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ============================================================
# BASIC DEPARTMENT CRUD
# ============================================================

@app.post("/departments")
def create_department(
    department: Department,
    db: Session = Depends(get_db)
):
    new_department = DepartmentDB(
        name=department.name,
        description=department.description
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


@app.get("/departments")
def get_departments(
    db: Session = Depends(get_db)
):
    return db.query(DepartmentDB).all()


@app.get("/departments/{department_id}")
def get_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(DepartmentDB).filter(
        DepartmentDB.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


@app.put("/departments/{department_id}")
def update_department(
    department_id: int,
    department: Department,
    db: Session = Depends(get_db)
):
    existing = db.query(DepartmentDB).filter(
        DepartmentDB.id == department_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    existing.name = department.name
    existing.description = department.description

    db.commit()
    db.refresh(existing)

    return existing


@app.delete("/departments/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(DepartmentDB).filter(
        DepartmentDB.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully"
    }


# ============================================================
# PATIENT CRUD
# ============================================================

@app.post("/patients")
def create_patient(
    patient: Patient,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can create patients."
        )

    new_patient = PatientDB(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        disease=patient.disease
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@app.get("/patients")
def get_patients(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    if role in ["admin", "staff", "doctor"]:
        return db.query(PatientDB).all()

    patient = db.query(PatientDB).filter(
        PatientDB.user_id == user_id
    ).first()

    if not patient:
        return []

    return [patient]


@app.get("/patients/{patient_id}")
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if role in ["admin", "staff", "doctor"]:
        return patient

    if patient.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own patient information."
        )

    return patient


@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: int,
    patient: Patient,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    existing = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if role not in ["admin", "staff"]:
        if existing.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own patient information."
            )

    existing.name = patient.name
    existing.age = patient.age
    existing.gender = patient.gender
    existing.disease = patient.disease

    db.commit()
    db.refresh(existing)

    return existing


@app.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can delete patients."
        )

    patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db.delete(patient)
    db.commit()

    return {
        "message": "Patient deleted successfully"
    }


# ============================================================
# DOCTOR CRUD
# ============================================================

@app.post("/doctors")
def create_doctor(
    doctor: Doctor,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can create doctors."
        )

    new_doctor = DoctorDB(
        name=doctor.name,
        degree=doctor.degree,
        specialization=doctor.specialization,
        department_id=doctor.department_id,
        subtype_id=getattr(doctor, "subtype_id", None),
        appointment_fee=getattr(doctor, "appointment_fee", 0.0),
        experience_years=getattr(doctor, "experience_years", 0),
        rating=getattr(doctor, "rating", 0.0)
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


@app.get("/doctors")
def get_doctors(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(DoctorDB).all()


@app.get("/doctors/{doctor_id}")
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    doctor = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    doctor: Doctor,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can update doctors."
        )

    existing = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    existing.name = doctor.name
    existing.degree = doctor.degree
    existing.specialization = doctor.specialization
    existing.department_id = doctor.department_id

    if hasattr(doctor, "subtype_id"):
        existing.subtype_id = doctor.subtype_id

    if hasattr(doctor, "appointment_fee"):
        existing.appointment_fee = doctor.appointment_fee

    if hasattr(doctor, "experience_years"):
        existing.experience_years = doctor.experience_years

    if hasattr(doctor, "rating"):
        existing.rating = doctor.rating

    db.commit()
    db.refresh(existing)

    return existing


@app.delete("/doctors/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can delete doctors."
        )

    doctor = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    db.delete(doctor)
    db.commit()

    return {
        "message": "Doctor deleted successfully"
    }


# ============================================================
# DOCTOR SEARCH / FILTER
# ============================================================

@app.get("/doctors/search")
def search_doctors(
    specialization: str = None,
    name: str = None,
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(DoctorDB)

    if specialization:
        query = query.filter(
            DoctorDB.specialization.ilike(
                f"%{specialization}%"
            )
        )

    if name:
        query = query.filter(
            DoctorDB.name.ilike(
                f"%{name}%"
            )
        )

    if department_id:
        query = query.filter(
            DoctorDB.department_id == department_id
        )

    return query.all()


# ============================================================
# APPOINTMENTS
# ============================================================

@app.post("/appointments")
def create_appointment(
    appointment: Appointment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    patient_id = appointment.patient_id

    if role == "user":
        patient = db.query(PatientDB).filter(
            PatientDB.user_id == user_id
        ).first()

        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient profile not found."
            )

        if patient.id != patient_id:
            raise HTTPException(
                status_code=403,
                detail="You can only create appointments for yourself."
            )

    elif role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to create appointments."
        )

    doctor = db.query(DoctorDB).filter(
        DoctorDB.id == appointment.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found."
        )

    new_appointment = AppointmentDB(
        patient_id=patient_id,
        doctor_id=appointment.doctor_id,
        date=getattr(appointment, "date", None),
        time=getattr(appointment, "time", None),
        reason=appointment.reason,
        status="pending",
        fee=doctor.appointment_fee,
        payment_status="unpaid"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {
        "message": "Appointment created successfully.",
        "appointment_id": new_appointment.id,
        "patient_id": new_appointment.patient_id,
        "doctor_id": new_appointment.doctor_id,
        "date": new_appointment.date,
        "time": new_appointment.time,
        "reason": new_appointment.reason,
        "status": new_appointment.status,
        "fee": new_appointment.fee,
        "payment_status": new_appointment.payment_status
    }


@app.get("/appointments")
def get_appointments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    query = db.query(AppointmentDB)

    if role == "admin" or role == "staff":
        appointments = query.all()

    elif role == "doctor":
        doctor = db.query(DoctorDB).filter(
            DoctorDB.user_id == user_id
        ).first()

        if not doctor:
            return []

        appointments = query.filter(
            AppointmentDB.doctor_id == doctor.id
        ).all()

    else:
        patient = db.query(PatientDB).filter(
            PatientDB.user_id == user_id
        ).first()

        if not patient:
            return []

        appointments = query.filter(
            AppointmentDB.patient_id == patient.id
        ).all()

    result = []

    for appointment in appointments:
        patient = db.query(PatientDB).filter(
            PatientDB.id == appointment.patient_id
        ).first()

        doctor = db.query(DoctorDB).filter(
            DoctorDB.id == appointment.doctor_id
        ).first()

        result.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "patient_name": patient.name if patient else None,
            "doctor_name": doctor.name if doctor else None,
            "date": appointment.date,
            "time": appointment.time,
            "reason": appointment.reason,
            "status": appointment.status,
            "fee": appointment.fee,
            "payment_status": appointment.payment_status
        })

    return result


@app.get("/appointments/{appointment_id}")
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found."
        )

    if role == "user":
        patient = db.query(PatientDB).filter(
            PatientDB.user_id == user_id
        ).first()

        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own appointments."
            )

    elif role == "doctor":
        doctor = db.query(DoctorDB).filter(
            DoctorDB.user_id == user_id
        ).first()

        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own appointments."
            )

    patient = db.query(PatientDB).filter(
        PatientDB.id == appointment.patient_id
    ).first()

    doctor = db.query(DoctorDB).filter(
        DoctorDB.id == appointment.doctor_id
    ).first()

    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "patient_name": patient.name if patient else None,
        "doctor_name": doctor.name if doctor else None,
        "date": appointment.date,
        "time": appointment.time,
        "reason": appointment.reason,
        "status": appointment.status,
        "fee": appointment.fee,
        "payment_status": appointment.payment_status
    }


# ============================================================
# UPDATE APPOINTMENT STATUS
# ============================================================

class AppointmentStatusUpdate(BaseModel):
    status: str


@app.put("/appointments/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    request: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found."
        )

    new_status = request.status.lower()
    current_status = appointment.status.lower()

    allowed_statuses = [
        "pending",
        "accepted",
        "rejected",
        "scheduled",
        "completed",
        "cancelled"
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid appointment status."
        )

    if current_status in ["rejected", "completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Appointment is already {current_status} and cannot be changed."
        )

    if role == "doctor":
        doctor = db.query(DoctorDB).filter(
            DoctorDB.user_id == int(current_user["sub"])
        ).first()

        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own appointments."
            )

        if current_status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Doctor can only accept or reject pending appointments."
            )

        if new_status not in ["accepted", "rejected"]:
            raise HTTPException(
                status_code=400,
                detail="Doctor can only accept or reject appointments."
            )

    elif role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update appointment status."
        )

    appointment.status = new_status

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment status updated successfully.",
        "appointment_id": appointment.id,
        "status": appointment.status
    }


# ============================================================
# ASSIGN / SCHEDULE APPOINTMENT
# ============================================================

class AppointmentAssignRequest(BaseModel):
    date: str
    time: str


@app.put("/appointments/{appointment_id}/assign")
def assign_appointment(
    appointment_id: int,
    request: AppointmentAssignRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can schedule appointments."
        )

    appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found."
        )

    if appointment.status.lower() != "accepted":
        raise HTTPException(
            status_code=400,
            detail="Only accepted appointments can be scheduled."
        )

    appointment.date = request.date
    appointment.time = request.time
    appointment.status = "scheduled"

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment scheduled successfully.",
        "appointment_id": appointment.id,
        "date": appointment.date,
        "time": appointment.time,
        "status": appointment.status
    }


# ============================================================
# BILLING
# ============================================================

@app.post("/appointments/{appointment_id}/bill")
def generate_bill(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can generate bills."
        )

    appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found."
        )

    if appointment.status.lower() not in ["accepted", "scheduled"]:
        raise HTTPException(
            status_code=400,
            detail="Bill can only be generated for accepted or scheduled appointments."
        )

    existing_bill = db.query(BillDB).filter(
        BillDB.appointment_id == appointment_id
    ).first()

    if existing_bill:
        raise HTTPException(
            status_code=400,
            detail="Bill already exists for this appointment."
        )

    bill = BillDB(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        consultation_fee=appointment.fee,
        total_amount=appointment.fee,
        payment_status="unpaid"
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)

    return {
        "message": "Bill generated successfully.",
        "bill_id": bill.id,
        "appointment_id": bill.appointment_id,
        "patient_id": bill.patient_id,
        "doctor_id": bill.doctor_id,
        "consultation_fee": bill.consultation_fee,
        "total_amount": bill.total_amount,
        "payment_status": bill.payment_status
    }


@app.get("/bills")
def get_all_bills(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or staff can view all bills."
        )

    return db.query(BillDB).all()


@app.get("/bills/{appointment_id}")
def get_bill(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    bill = db.query(BillDB).filter(
        BillDB.appointment_id == appointment_id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    if role == "user":
        patient = db.query(PatientDB).filter(
            PatientDB.user_id == user_id
        ).first()

        if not patient or bill.patient_id != patient.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own bill."
            )

    elif role == "doctor":
        doctor = db.query(DoctorDB).filter(
            DoctorDB.user_id == user_id
        ).first()

        if not doctor or bill.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access bills for your appointments."
            )

    return bill


# ============================================================
# OFFLINE PAYMENT SUBMISSION
# ============================================================

class PaymentRequest(BaseModel):
    payment_method: str


@app.post("/bills/{bill_id}/pay")
def pay_bill(
    bill_id: int,
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    if role != "user":
        raise HTTPException(
            status_code=403,
            detail="Only patients can submit payment."
        )

    if request.payment_method.lower() != "offline":
        raise HTTPException(
            status_code=400,
            detail="Only offline payment is currently supported."
        )

    bill = db.query(BillDB).filter(
        BillDB.id == bill_id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    patient = db.query(PatientDB).filter(
        PatientDB.user_id == user_id
    ).first()

    if not patient or bill.patient_id != patient.id:
        raise HTTPException(
            status_code=403,
            detail="You can only pay your own bill."
        )

    if bill.payment_status != "unpaid":
        raise HTTPException(
            status_code=400,
            detail=f"Bill payment status is already {bill.payment_status}."
        )

    bill.payment_method = "offline"
    bill.payment_status = "payment_submitted"

    db.commit()
    db.refresh(bill)

    return {
        "message": "Offline payment submitted successfully. Awaiting staff confirmation.",
        "bill_id": bill.id,
        "payment_method": bill.payment_method,
        "payment_status": bill.payment_status
    }


# ============================================================
# STAFF / ADMIN PAYMENT CONFIRMATION
# ============================================================

@app.put("/bills/{bill_id}/confirm-payment")
def confirm_payment(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Only staff or admin can confirm payments."
        )

    bill = db.query(BillDB).filter(
        BillDB.id == bill_id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    if bill.payment_status != "payment_submitted":
        raise HTTPException(
            status_code=400,
            detail="Only submitted payments can be confirmed."
        )

    bill.payment_status = "paid"

    appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == bill.appointment_id
    ).first()

    if appointment:
        appointment.payment_status = "paid"

    db.commit()
    db.refresh(bill)

    return {
        "message": "Payment confirmed successfully.",
        "bill_id": bill.id,
        "payment_status": bill.payment_status,
        "appointment_payment_status": (
            appointment.payment_status
            if appointment
            else None
        )
    }


# ============================================================
# EMERGENCY / MEDICAL SAFETY
# ============================================================

def is_emergency_question(question: str) -> bool:
    emergency_keywords = [
        "heart attack",
        "chest pain",
        "difficulty breathing",
        "can't breathe",
        "cannot breathe",
        "severe bleeding",
        "unconscious",
        "stroke",
        "seizure",
        "suicide",
        "self harm",
        "poisoning",
        "overdose"
    ]

    question_lower = question.lower()

    return any(
        keyword in question_lower
        for keyword in emergency_keywords
    )


def is_medical_advice_question(question: str) -> bool:
    medical_keywords = [
        "diagnose me",
        "what medicine should i take",
        "which medicine should i take",
        "prescribe",
        "dosage",
        "dose should i take",
        "should i stop my medicine",
        "what medication should i take"
    ]

    question_lower = question.lower()

    return any(
        keyword in question_lower
        for keyword in medical_keywords
    )


# ============================================================
# AI CHAT
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_id = int(current_user["sub"])

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    # ========================================================
    # MEDICAL SAFETY
    # ========================================================

    if is_emergency_question(question):
        return {
            "response": (
                "This may be a medical emergency. Please seek immediate "
                "emergency medical care or contact your local emergency "
                "services. Do not rely on this chatbot for emergency treatment."
            ),
            "sources": []
        }

    if is_medical_advice_question(question):
        return {
            "response": (
                "I can provide general health information, but I cannot "
                "diagnose medical conditions or prescribe medicines. "
                "Please consult a qualified healthcare professional for "
                "personalized medical advice."
            ),
            "sources": []
        }

    # ========================================================
    # RAG RETRIEVAL
    # ========================================================

    try:
        context = retrieve_context(question, db)

        print("\n================ RAG CONTEXT ================")
        print(context)
        print("==============================================\n")

    except Exception as e:
        print("\n================ RAG ERROR ==================")
        print(e)
        print("==============================================\n")

        context = []

    # ========================================================
    # CONVERT RAG RESULTS INTO TEXT
    # ========================================================

    rag_text = ""

    if isinstance(context, list):

        rag_parts = []

        for item in context:

            if isinstance(item, dict):

                text = item.get("text", "")

                if text:
                    rag_parts.append(text)

        rag_text = "\n\n".join(rag_parts)

    elif isinstance(context, str):

        rag_text = context

    # ========================================================
    # HOSPITAL DATABASE DATA
    # ========================================================

    departments = db.query(DepartmentDB).all()
    doctors = db.query(DoctorDB).all()
    patients = db.query(PatientDB).all()
    appointments = db.query(AppointmentDB).all()

    # ========================================================
    # DEPARTMENT DATA
    # ========================================================

    department_data = [
        {
            "id": department.id,
            "name": department.name,
            "description": department.description
        }
        for department in departments
    ]

    # ========================================================
    # DOCTOR DATA
    # ========================================================

    doctor_data = [
        {
            "id": doctor.id,
            "user_id": doctor.user_id,
            "name": doctor.name,
            "degree": doctor.degree,
            "specialization": doctor.specialization,
            "department_id": doctor.department_id,
            "experience_years": doctor.experience_years,
            "rating": doctor.rating
        }
        for doctor in doctors
    ]

    # ========================================================
    # PATIENT DATA
    # ========================================================

    if role in ["admin", "staff", "doctor"]:

        patient_data = [
            {
                "id": patient.id,
                "user_id": patient.user_id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "disease": patient.disease
            }
            for patient in patients
        ]

    else:

        patient = db.query(PatientDB).filter(
            PatientDB.user_id == user_id
        ).first()

        if patient:

            patient_data = [
                {
                    "id": patient.id,
                    "user_id": patient.user_id,
                    "name": patient.name,
                    "age": patient.age,
                    "gender": patient.gender,
                    "disease": patient.disease
                }
            ]

        else:
            patient_data = []

    # ========================================================
    # APPOINTMENT DATA
    # ========================================================

    if role in ["admin", "staff"]:

        appointment_data = [
            {
                "id": appointment.id,
                "patient_id": appointment.patient_id,
                "doctor_id": appointment.doctor_id,
                "date": appointment.date,
                "time": appointment.time,
                "reason": appointment.reason,
                "status": appointment.status
            }
            for appointment in appointments
        ]

    elif role == "doctor":

        doctor = db.query(DoctorDB).filter(
            DoctorDB.user_id == user_id
        ).first()

        if doctor:

            appointment_data = [
                {
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "doctor_id": appointment.doctor_id,
                    "date": appointment.date,
                    "time": appointment.time,
                    "reason": appointment.reason,
                    "status": appointment.status
                }
                for appointment in appointments
                if appointment.doctor_id == doctor.id
            ]

        else:
            appointment_data = []

    else:

        patient = db.query(PatientDB).filter(
            PatientDB.user_id == user_id
        ).first()

        if patient:

            appointment_data = [
                {
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "doctor_id": appointment.doctor_id,
                    "date": appointment.date,
                    "time": appointment.time,
                    "reason": appointment.reason,
                    "status": appointment.status
                }
                for appointment in appointments
                if appointment.patient_id == patient.id
            ]

        else:
            appointment_data = []

    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = f"""
You are the AI Hospital Assistant for City Care Hospital.

User role: {role}

IMPORTANT INSTRUCTION:

The RAG CONTEXT below comes from the hospital's approved knowledge base.

If the user's question can be answered using the RAG CONTEXT,
you MUST use that information.

Never say that information is unavailable when it is clearly present
in the RAG CONTEXT.

Never tell the user to visit another website or use another application
when the answer is available in the RAG CONTEXT.

Do not invent hospital information.

If the RAG CONTEXT does not contain the answer, you may use the
structured hospital database information provided below.

If neither source contains the answer, clearly say that the information
is not available in the current hospital knowledge base.

========================================================
RAG CONTEXT
========================================================

{rag_text}

========================================================
HOSPITAL DEPARTMENTS
========================================================

{department_data}

========================================================
HOSPITAL DOCTORS
========================================================

{doctor_data}

========================================================
PATIENT INFORMATION AVAILABLE TO THIS USER
========================================================

{patient_data}

========================================================
APPOINTMENTS AVAILABLE TO THIS USER
========================================================

{appointment_data}

========================================================
SECURITY RULES
========================================================

1. Do not reveal another patient's private information.
2. Admin and staff can access hospital-wide operational information.
3. Doctors can access information relevant to their patients and appointments.
4. Patients can access only their own information.
5. Do not expose private patient information to normal users.
6. Do not diagnose serious medical conditions.
7. Do not prescribe medicines.
8. For emergencies, advise the user to seek immediate emergency medical care.
9. Be professional and concise.
"""

    # ========================================================
    # GROQ AI
    # ========================================================

    try:

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.2
        )

        response = completion.choices[0].message.content

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )

    # ========================================================
    # SOURCE REFERENCES
    # ========================================================

    sources = []

    if isinstance(context, list):

        sources = list({
            item.get("filename")
            for item in context
            if isinstance(item, dict)
            and item.get("filename")
        })

    elif isinstance(context, str) and context.strip():

        sources = [
            "City Care Hospital Knowledge Base"
        ]

    # ========================================================
    # SAVE CHAT HISTORY
    # ========================================================

    user_id = int(current_user["sub"])

    chat_history = ChatHistoryDB(
    user_id=user_id,
    question=question,
    answer=response
)

    db.add(chat_history)
    db.commit()

# ========================================================
# FINAL RESPONSE
# ========================================================

    return {
    "response": response,
    "sources": sources
}


# ============================================================
# PROTECTED TEST ROUTE
# ============================================================

@app.get("/protected")
def protected_route(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "You have access to this protected route.",
        "user": current_user
    }


# ============================================================
# ADMIN ONLY TEST ROUTE
# ============================================================

@app.get("/admin-only")
def admin_only_route(
    current_user: dict = Depends(require_role("admin"))
):
    return {
        "message": "Welcome Admin.",
        "user": current_user
    }


# ============================================================
# WEBSOCKET CHAT
# ============================================================

@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket
):
    await handle_chat(websocket)

@app.get("/chat-history")
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    history = (
        db.query(ChatHistoryDB)
        .filter(ChatHistoryDB.user_id == user_id)
        .order_by(ChatHistoryDB.id.desc())
        .all()
    )

    return history