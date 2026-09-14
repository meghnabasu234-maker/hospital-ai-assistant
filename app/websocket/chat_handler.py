from fastapi import WebSocket

from app.websocket.manager import ConnectionManager

from app.rag.retriever import retrieve_context

from app.rag.safety import (
    is_emergency_question,
    is_medical_advice_question
)

from app.database import SessionLocal

from app.models import (
    DepartmentDB,
    DoctorDB,
    PatientDB,
    AppointmentDB,
    ChatHistoryDB
)

from app.core.security import verify_token

from groq import Groq

import os


manager = ConnectionManager()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


async def handle_chat(websocket: WebSocket):

    # -------------------------------------------------
    # GET JWT TOKEN
    # -------------------------------------------------

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    # -------------------------------------------------
    # VERIFY JWT TOKEN
    # -------------------------------------------------

    current_user = verify_token(token)

    if current_user is None:
        await websocket.close(code=1008)
        return

    # -------------------------------------------------
    # GET USER INFORMATION FROM JWT
    # -------------------------------------------------

    user_id = current_user.get("sub")
    role = current_user.get("role", "user")

    staff_type = current_user.get("staff_type")
    patient_type = current_user.get("patient_type")
    doctor_category = current_user.get("doctor_category")
    doctor_specialization = current_user.get(
        "doctor_specialization"
    )

    if not user_id:
        await websocket.close(code=1008)
        return

    # -------------------------------------------------
    # CONNECT WEBSOCKET
    # -------------------------------------------------

    await manager.connect(websocket)

    db = SessionLocal()

    try:

        while True:

            # -------------------------------------------------
            # RECEIVE MESSAGE
            # -------------------------------------------------

            message = await websocket.receive_text()

            question = message.strip()

            if not question:

                await websocket.send_text(
                    "Please enter a question."
                )

                continue

            # -------------------------------------------------
            # EMERGENCY CHECK
            # -------------------------------------------------

            if is_emergency_question(question):

                answer = (
                    "This may be a medical emergency. "
                    "Please seek immediate emergency medical care "
                    "or contact your local emergency services. "
                    "Do not rely on this chatbot for emergency treatment."
                )

                await websocket.send_text(answer)

                continue

            # -------------------------------------------------
            # MEDICAL ADVICE CHECK
            # -------------------------------------------------

            if is_medical_advice_question(question):

                answer = (
                    "I can provide general health information, "
                    "but I cannot diagnose medical conditions or "
                    "prescribe medicines. Please consult a qualified "
                    "healthcare professional for personalized medical advice."
                )

                await websocket.send_text(answer)

                continue

            # -------------------------------------------------
            # STAFF APPOINTMENT QUESTIONS
            # -------------------------------------------------

            if role == "staff":

                appointment_keywords = [
                    "take an appointment",
                    "take appointment",
                    "book an appointment",
                    "book appointment",
                    "booking an appointment",
                    "booking appointment",
                    "how to book appointment",
                    "how to take appointment",
                    "schedule an appointment",
                    "schedule appointment",
                    "manage appointment",
                    "manage appointments",
                    "appointment process"
                ]

                question_lower = question.lower()

                if any(
                    keyword in question_lower
                    for keyword in appointment_keywords
                ):

                    answer = (
                        "As hospital staff, you do not book a "
                        "personal appointment. Your responsibility "
                        "is to manage appointment requests made by "
                        "patients.\n\n"

                        "Staff appointment workflow:\n\n"

                        "1. Open the Appointments section.\n"
                        "2. Find pending appointment requests.\n"
                        "3. Check the patient name, selected doctor "
                        "and reason for the appointment.\n"
                        "4. Check the selected doctor's availability.\n"
                        "5. Assign an available date and time.\n"
                        "6. Click Confirm Appointment if the slot "
                        "is available.\n"
                        "7. If the request cannot be scheduled, "
                        "reject the appointment.\n\n"

                        "Patients initially create appointment "
                        "requests without a date and time. "
                        "Staff assigns the date and time after "
                        "checking the doctor's availability."
                    )

                    await websocket.send_text(answer)

                    # Save private chat history
                    chat_record = ChatHistoryDB(
                        user_id=int(user_id),
                        question=question,
                        answer=answer
                    )

                    db.add(chat_record)
                    db.commit()

                    continue

            # -------------------------------------------------
            # RAG DOCUMENT RETRIEVAL
            # -------------------------------------------------

            retrieved_chunks = retrieve_context(
                question,
                db
            )

            if retrieved_chunks:

                document_context = "\n\n".join(
                    chunk["text"]
                    for chunk in retrieved_chunks
                )

            else:

                document_context = (
                    "No relevant information was found "
                    "in the hospital documents."
                )

            # -------------------------------------------------
            # COMMON HOSPITAL DATA
            # -------------------------------------------------

            departments = [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description
                }
                for d in db.query(DepartmentDB).all()
            ]

            doctors = [
                {
                    "id": d.id,
                    "name": d.name,
                    "specialization": d.specialization,
                    "department_id": d.department_id
                }
                for d in db.query(DoctorDB).all()
            ]

            # -------------------------------------------------
            # ROLE-SPECIFIC DATA
            # -------------------------------------------------

            role_specific_data = {}

            # =================================================
            # PATIENT / USER
            # =================================================

            if role == "user":

                role_specific_data = {

                    "account_type": "Patient/User",

                    "patient_type": patient_type,

                    "instructions": [
                        "The logged-in user is a patient.",
                        "The patient can request an appointment.",
                        "The patient can choose a doctor.",
                        "The patient provides the reason for the appointment.",
                        "The patient does not assign the appointment date or time.",
                        "Staff checks doctor availability.",
                        "Staff assigns the date and time.",
                        "Staff confirms or rejects the appointment."
                    ],

                    "departments": departments,

                    "doctors": doctors
                }

            # =================================================
            # STAFF
            # =================================================

            elif role == "staff":

                patients = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "age": p.age,
                        "gender": p.gender,
                        "disease": p.disease
                    }
                    for p in db.query(PatientDB).all()
                ]

                appointments = [
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

                role_specific_data = {

                    "account_type": "Hospital Staff",

                    "staff_type": staff_type,

                    "instructions": [
                        "The logged-in user is hospital staff.",
                        "Staff does NOT book personal patient appointments.",
                        "Staff manages appointment requests made by patients.",
                        "Staff checks doctor availability.",
                        "Staff assigns appointment date and time.",
                        "Staff confirms or rejects pending appointments.",
                        "Never assume an appointment belongs to the staff user.",
                        "An appointment belongs to the patient identified by patient_id."
                    ],

                    "departments": departments,

                    "doctors": doctors,

                    "patients": patients,

                    "appointments": appointments
                }

            # =================================================
            # DOCTOR
            # =================================================

            elif role == "doctor":

                patients = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "age": p.age,
                        "gender": p.gender,
                        "disease": p.disease
                    }
                    for p in db.query(PatientDB).all()
                ]

                appointments = [
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

                role_specific_data = {

                    "account_type": "Doctor",

                    "doctor_category": doctor_category,

                    "doctor_specialization": doctor_specialization,

                    "instructions": [
                        "The logged-in user is a doctor.",
                        "The doctor is not a patient.",
                        "Patients request appointments.",
                        "Staff manages appointment scheduling.",
                        "Staff assigns date and time.",
                        "Do not tell the doctor to book an appointment as a patient.",
                        "Do not claim an appointment belongs to the doctor personally."
                    ],

                    "departments": departments,

                    "doctors": doctors,

                    "patients": patients,

                    "appointments": appointments
                }

            # =================================================
            # ADMIN
            # =================================================

            elif role == "admin":

                patients = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "age": p.age,
                        "gender": p.gender,
                        "disease": p.disease
                    }
                    for p in db.query(PatientDB).all()
                ]

                appointments = [
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

                role_specific_data = {

                    "account_type": "Hospital Administrator",

                    "instructions": [
                        "The logged-in user is an administrator.",
                        "The administrator manages hospital operations.",
                        "The administrator is not a patient.",
                        "Patients request appointments.",
                        "Staff manages appointment scheduling.",
                        "Staff assigns appointment date and time.",
                        "Do not tell the administrator to book a personal appointment.",
                        "Do not claim an appointment belongs to the administrator."
                    ],

                    "departments": departments,

                    "doctors": doctors,

                    "patients": patients,

                    "appointments": appointments
                }

            # =================================================
            # UNKNOWN ROLE
            # =================================================

            else:

                role_specific_data = {

                    "account_type": "Unknown",

                    "instructions": [
                        "The user's role is unknown.",
                        "Do not assume the user is a patient.",
                        "Do not claim the user has an appointment.",
                        "Only provide general hospital information."
                    ],

                    "departments": departments,

                    "doctors": doctors
                }

            # -------------------------------------------------
            # ROLE-AWARE GROQ PROMPT
            # -------------------------------------------------

            prompt = f"""
You are the Hospital AI Assistant.

The logged-in user's role is:

{role}

USER INFORMATION:

{role_specific_data}

HOSPITAL DOCUMENTS:

{document_context}

IMPORTANT ROLE RULES:

- Always answer according to the logged-in user's role.
- Never assume every user is a patient.
- Never say that the logged-in user has an appointment
  simply because appointments exist in the database.
- An appointment's patient_id identifies the patient.
- patient_id does NOT mean the current logged-in user.

PATIENT / USER:
- Can request an appointment.
- Can choose a doctor.
- Provides the reason.
- Does not assign date or time.
- Staff assigns date and time.

STAFF:
- Manages patient appointment requests.
- Checks doctor availability.
- Assigns date and time.
- Confirms or rejects appointments.
- Does not book personal appointments.

DOCTOR:
- Is a medical professional, not a patient.
- Can ask about doctor-related hospital information.
- Patients request appointments.
- Staff manages scheduling.

ADMIN:
- Manages and monitors hospital operations.
- Can ask about hospital appointments, doctors, patients
  and departments.
- Does not book personal appointments.

GENERAL RULES:
- Do not invent information.
- Use the supplied hospital data.
- Use hospital documents when appropriate.
- If information is unavailable, say so.
- Do not diagnose medical conditions.
- Do not prescribe medicines.
- Keep answers clear and concise.

USER QUESTION:

{question}
"""

            # -------------------------------------------------
            # CALL GROQ
            # -------------------------------------------------

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a role-aware Hospital AI Assistant. "
                            "Always respect the logged-in user's role. "
                            "Never assume the user is a patient."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response.choices[0].message.content

            # -------------------------------------------------
            # SEND ANSWER
            # -------------------------------------------------

            await websocket.send_text(answer)

            # -------------------------------------------------
            # SAVE PRIVATE CHAT HISTORY
            # -------------------------------------------------

            chat_record = ChatHistoryDB(
                user_id=int(user_id),
                question=question,
                answer=answer
            )

            db.add(chat_record)
            db.commit()

    except Exception as e:

        print("WebSocket error:", e)

        try:
            await websocket.send_text(
                "Sorry, something went wrong while processing your message."
            )
        except Exception:
            pass

    finally:

        manager.disconnect(websocket)

        db.close()