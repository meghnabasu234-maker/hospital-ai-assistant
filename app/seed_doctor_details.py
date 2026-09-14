from app.database import SessionLocal
from app.models.doctor import DoctorDB


doctor_data = {
    "Dr. Arjun Roy": {
        "department_id": 2,
        "subtype_id": 5,
        "fee": 800,
    },
    "Dr. Priya Sen": {
        "department_id": 2,
        "subtype_id": 6,
        "fee": 800,
    },
    "Dr. Arindam Sen": {
        "department_id": 1,
        "subtype_id": 3,
        "fee": 500,
    },
    "Dr. Riya Mukherjee": {
        "department_id": 2,
        "subtype_id": 7,
        "fee": 600,
    },
    "Dr. Soumitra Ghosh": {
        "department_id": 1,
        "subtype_id": 3,
        "fee": 500,
    },
    "Dr. Ananya Roy": {
        "department_id": 2,
        "subtype_id": 7,
        "fee": 600,
    },
    "Dr. Sayan Roy": {
        "department_id": 2,
        "subtype_id": 16,
        "fee": 900,
    },
    "Dr. Ishita Das": {
        "department_id": 2,
        "subtype_id": 17,
        "fee": 700,
    },
    "Dr. Nandini Ghosh": {
        "department_id": 2,
        "subtype_id": 17,
        "fee": 600,
    },
    "Dr. Ritwick Sen": {
        "department_id": 2,
        "subtype_id": 16,
        "fee": 850,
    },
    "Dr. Moumita Dey": {
        "department_id": 2,
        "subtype_id": 17,
        "fee": 650,
    },
    "Dr. Priyanka Bose": {
        "department_id": 2,
        "subtype_id": 17,
        "fee": 600,
    },
    "Dr. Abhishek Dutta": {
        "department_id": 3,
        "subtype_id": 18,
        "fee": 700,
    },
    "Dr. Soumya Bhattacharya": {
        "department_id": 3,
        "subtype_id": 19,
        "fee": 600,
    },
    "Dr. Kunal Basu": {
        "department_id": 3,
        "subtype_id": 20,
        "fee": 600,
    },
    "Dr. Aritra Paul": {
        "department_id": 3,
        "subtype_id": 18,
        "fee": 650,
    },
    "Dr. Tanmoy Chakraborty": {
        "department_id": 3,
        "subtype_id": 19,
        "fee": 600,
    },
    "Dr. Rakesh Saha": {
        "department_id": 3,
        "subtype_id": 20,
        "fee": 550,
    },
    "Dr. Rahul Mitra": {
        "department_id": 4,
        "subtype_id": 21,
        "fee": 800,
    },
    "Dr. Debanjan Bose": {
        "department_id": 4,
        "subtype_id": 22,
        "fee": 900,
    },
    "Dr. Arjun Mukherjee": {
        "department_id": 4,
        "subtype_id": 21,
        "fee": 750,
    },
    "Dr. Kaushik Das": {
        "department_id": 4,
        "subtype_id": 22,
        "fee": 850,
    },
}


def seed_doctor_details():
    db = SessionLocal()

    try:
        for doctor_name, details in doctor_data.items():

            doctor = (
                db.query(DoctorDB)
                .filter(DoctorDB.name == doctor_name)
                .first()
            )

            if not doctor:
                print(f"Doctor not found: {doctor_name}")
                continue

            doctor.department_id = details["department_id"]
            doctor.subtype_id = details["subtype_id"]
            doctor.appointment_fee = details["fee"]

            print(
                f"Updated: {doctor_name} | "
                f"Department ID: {details['department_id']} | "
                f"Subtype ID: {details['subtype_id']} | "
                f"Fee: ₹{details['fee']}"
            )

        db.commit()
        print("\nAll doctor details updated successfully.")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_doctor_details()