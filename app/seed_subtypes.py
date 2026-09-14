from app.database import SessionLocal
from app.models.department import DepartmentDB
from app.models.department_subtype import DepartmentSubtypeDB


subtypes_data = {
    "Primary Care & General Practice": [
        "General Medicine",
        "Family Medicine",
        "Internal Medicine",
        "Geriatric Medicine",
    ],

    "Medical Specialist": [
        "Cardiology",
        "Neurology",
        "Pediatrics",
        "Dermatology",
        "ENT",
        "Ophthalmology",
        "Gastroenterology",
        "Pulmonology",
        "Nephrology",
        "Urology",
        "Endocrinology",
        "Oncology",
        "Psychiatry",
    ],

    "Acute & Diagnostic Care": [
        "Emergency Medicine",
        "Radiology",
        "Pathology",
    ],

    "Surgical": [
        "General Surgery",
        "Orthopedic Surgery",
        "Neurosurgery",
        "Gynecology & Obstetrics",
        "Dental Surgery",
    ],
}


def seed_subtypes():
    db = SessionLocal()

    try:
        for department_name, subtype_names in subtypes_data.items():

            department = (
                db.query(DepartmentDB)
                .filter(DepartmentDB.name == department_name)
                .first()
            )

            if not department:
                print(f"Department not found: {department_name}")
                continue

            for subtype_name in subtype_names:

                existing = (
                    db.query(DepartmentSubtypeDB)
                    .filter(
                        DepartmentSubtypeDB.department_id == department.id,
                        DepartmentSubtypeDB.name == subtype_name,
                    )
                    .first()
                )

                if not existing:
                    subtype = DepartmentSubtypeDB(
                        department_id=department.id,
                        name=subtype_name,
                    )

                    db.add(subtype)

                    print(
                        f"Added: {department_name} -> {subtype_name}"
                    )

        db.commit()

        print("\nSubtypes added successfully.")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_subtypes()