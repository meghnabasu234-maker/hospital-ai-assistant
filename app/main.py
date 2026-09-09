from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import os
from groq import Groq

from app.department import Department
from app.patient import Patient
from app.doctor import Doctor
from app.appointment import Appointment
from app.chat import ChatRequest
from app.rag import retrieve_context

from app.database import get_db
from app.models import DepartmentDB, PatientDB, DoctorDB, AppointmentDB

app = FastAPI(
    title="Hospital AI Assistant",
    version="1.0.0"
)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)




@app.get("/")
def home():
    return {
        "message": "Welcome to Hospital AI Assistant"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/departments")
def create_department(
    department: Department,
    db: Session = Depends(get_db)
):
    new_department = DepartmentDB(
        id=department.id,
        name=department.name,
        description=department.description
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department

@app.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    return db.query(DepartmentDB).all()

@app.put("/departments/{department_id}")
def update_department(
    department_id: int,
    department: Department,
    db: Session = Depends(get_db)
):
    existing_department = db.query(DepartmentDB).filter(
        DepartmentDB.id == department_id
    ).first()

    if not existing_department:
        return {"message": "Department not found"}

    existing_department.name = department.name
    existing_department.description = department.description

    db.commit()
    db.refresh(existing_department)

    return existing_department

@app.delete("/departments/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    existing_department = db.query(DepartmentDB).filter(
        DepartmentDB.id == department_id
    ).first()

    if not existing_department:
        return {"message": "Department not found"}

    db.delete(existing_department)
    db.commit()

    return {"message": "Department deleted successfully"}


@app.post("/patients")
def create_patient(
    patient: Patient,
    db: Session = Depends(get_db)
):
    new_patient = PatientDB(
        id=patient.id,
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
def get_patients(db: Session = Depends(get_db)):
    return db.query(PatientDB).all()

@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: int,
    patient: Patient,
    db: Session = Depends(get_db)
):
    existing_patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if not existing_patient:
        return {"message": "Patient not found"}

    existing_patient.name = patient.name
    existing_patient.age = patient.age
    existing_patient.gender = patient.gender
    existing_patient.disease = patient.disease

    db.commit()
    db.refresh(existing_patient)

    return existing_patient

@app.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    existing_patient = db.query(PatientDB).filter(
        PatientDB.id == patient_id
    ).first()

    if not existing_patient:
        return {"message": "Patient not found"}

    db.delete(existing_patient)
    db.commit()

    return {"message": "Patient deleted successfully"}

@app.post("/doctors")
def create_doctor(
    doctor: Doctor,
    db: Session = Depends(get_db)
):
    new_doctor = DoctorDB(
        id=doctor.id,
        name=doctor.name,
        specialization=doctor.specialization,
        department_id=doctor.department_id
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor



@app.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    return db.query(DoctorDB).all()


@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    doctor: Doctor,
    db: Session = Depends(get_db)
):
    existing_doctor = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if not existing_doctor:
        return {"message": "Doctor not found"}

    existing_doctor.name = doctor.name
    existing_doctor.specialization = doctor.specialization
    existing_doctor.department_id = doctor.department_id

    db.commit()
    db.refresh(existing_doctor)

    return existing_doctor



@app.delete("/doctors/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    existing_doctor = db.query(DoctorDB).filter(
        DoctorDB.id == doctor_id
    ).first()

    if not existing_doctor:
        return {"message": "Doctor not found"}

    db.delete(existing_doctor)
    db.commit()

    return {"message": "Doctor deleted successfully"}


@app.post("/appointments")
def create_appointment(
    appointment: Appointment,
    db: Session = Depends(get_db)
):
    new_appointment = AppointmentDB(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        time=appointment.time,
        reason=appointment.reason,
        status=appointment.status
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment



@app.get("/appointments")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(AppointmentDB).all()


@app.put("/appointments/{appointment_id}")
def update_appointment(
    appointment_id: int,
    appointment: Appointment,
    db: Session = Depends(get_db)
):
    existing_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if not existing_appointment:
        return {"message": "Appointment not found"}

    existing_appointment.patient_id = appointment.patient_id
    existing_appointment.doctor_id = appointment.doctor_id
    existing_appointment.date = appointment.date
    existing_appointment.time = appointment.time
    existing_appointment.reason = appointment.reason
    existing_appointment.status = appointment.status

    db.commit()
    db.refresh(existing_appointment)

    return existing_appointment



@app.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    existing_appointment = db.query(AppointmentDB).filter(
        AppointmentDB.id == appointment_id
    ).first()

    if not existing_appointment:
        return {"message": "Appointment not found"}

    db.delete(existing_appointment)
    db.commit()

    return {"message": "Appointment deleted successfully"}


@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # Get relevant information from hospital document
    retrieved_chunks = retrieve_context(request.question)
    if retrieved_chunks:
        document_context = "\n\n".join(retrieved_chunks)
    else:
        document_context = "No relevant information was found in the hospital documents."

    # Get current structured hospital data
    hospital_data = {
    "departments": [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description
        }
        for d in db.query(DepartmentDB).all()
    ],

    "doctors": [
        {
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "department_id": d.department_id
        }
        for d in db.query(DoctorDB).all()
    ],

    "patients": [
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "disease": p.disease
        }
        for p in db.query(PatientDB).all()
    ],

    "appointments": [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.date,
            "time": a.time,
            "reason": a.reason,
            "status": a.status
        }
        for a in db.query(AppointmentDB).all()
    ]
}

    prompt = f"""
You are a helpful Hospital AI Assistant.

Use the hospital documents and hospital application data below
to answer the user's question.

Hospital documents:
{document_context}

Hospital application data:
{hospital_data}

User question:
{request.question}

Rules:
- Use the provided hospital documents and application data.
- Do not invent information.
- If the information is not available, clearly say that it is not available.
- Give a concise and helpful answer.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful hospital AI assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "question": request.question,
        "answer": response.choices[0].message.content
    }