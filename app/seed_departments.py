from app.database import SessionLocal
from app.models.department import DepartmentDB
from app.models.department_subtype import DepartmentSubtypeDB


departments_data = [
    {
        "name": "Cardiology",
        "description": "Diagnosis and treatment of heart and cardiovascular conditions.",
        "subtypes": [
            "Clinical Cardiology",
            "Interventional Cardiology",
            "Electrophysiology",
        ],
    },
    {
        "name": "Neurology",
        "description": "Diagnosis and treatment of disorders of the brain, nerves and nervous system.",
        "subtypes": [
            "General Neurology",
            "Stroke",
            "Epilepsy",
            "Movement Disorders",
        ],
    },
    {
        "name": "Orthopedics",
        "description": "Treatment of bones, joints, muscles and the musculoskeletal system.",
        "subtypes": [
            "Joint Replacement",
            "Sports Medicine",
            "Spine",
            "Orthopedic Trauma",
        ],
    },
    {
        "name": "Pediatrics",
        "description": "Medical care for infants, children and adolescents.",
        "subtypes": [
            "General Pediatrics",
            "Neonatology",
            "Pediatric Cardiology",
        ],
    },
    {
        "name": "Gynecology & Obstetrics",
        "description": "Women's health, pregnancy and reproductive care.",
        "subtypes": [
            "Obstetrics",
            "Gynecology",
            "High-Risk Pregnancy",
        ],
    },
    {
        "name": "Dermatology",
        "description": "Diagnosis and treatment of skin, hair and nail conditions.",
        "subtypes": [
            "General Dermatology",
            "Cosmetic Dermatology",
            "Pediatric Dermatology",
        ],
    },
    {
        "name": "ENT",
        "description": "Treatment of ear, nose and throat conditions.",
        "subtypes": [
            "Otology",
            "Rhinology",
            "Laryngology",
        ],
    },
    {
        "name": "Ophthalmology",
        "description": "Diagnosis and treatment of eye-related conditions.",
        "subtypes": [
            "Cataract",
            "Retina",
            "Glaucoma",
            "Cornea",
        ],
    },
    {
        "name": "Gastroenterology",
        "description": "Diagnosis and treatment of digestive system disorders.",
        "subtypes": [
            "Gastroenterology",
            "Hepatology",
            "Endoscopy",
        ],
    },
    {
        "name": "Pulmonology",
        "description": "Diagnosis and treatment of respiratory and lung conditions.",
        "subtypes": [
            "Respiratory Medicine",
            "Sleep Medicine",
            "Pulmonary Critical Care",
        ],
    },
    {
        "name": "Nephrology",
        "description": "Diagnosis and treatment of kidney-related diseases.",
        "subtypes": [
            "Kidney Disease",
            "Dialysis",
            "Transplant Nephrology",
        ],
    },
    {
        "name": "Urology",
        "description": "Treatment of urinary tract and male reproductive system conditions.",
        "subtypes": [
            "General Urology",
            "Urologic Oncology",
            "Andrology",
        ],
    },
    {
        "name": "Endocrinology",
        "description": "Diagnosis and treatment of hormonal and metabolic disorders.",
        "subtypes": [
            "Diabetes",
            "Thyroid Disorders",
            "Hormonal Disorders",
        ],
    },
    {
        "name": "Oncology",
        "description": "Diagnosis and treatment of cancer.",
        "subtypes": [
            "Medical Oncology",
            "Surgical Oncology",
            "Radiation Oncology",
        ],
    },
    {
        "name": "Psychiatry",
        "description": "Diagnosis and treatment of mental health and psychiatric conditions.",
        "subtypes": [
            "Adult Psychiatry",
            "Child Psychiatry",
            "Addiction Psychiatry",
        ],
    },
    {
        "name": "General Medicine",
        "description": "Diagnosis and treatment of common and complex adult medical conditions.",
        "subtypes": [
            "Internal Medicine",
            "Infectious Disease",
            "Geriatric Medicine",
        ],
    },
    {
        "name": "General Surgery",
        "description": "Surgical treatment for a wide range of medical conditions.",
        "subtypes": [
            "Laparoscopic Surgery",
            "GI Surgery",
            "Trauma Surgery",
        ],
    },
    {
        "name": "Neurosurgery",
        "description": "Surgical treatment of brain, spine and nervous system conditions.",
        "subtypes": [
            "Brain Surgery",
            "Spine Surgery",
            "Neurotrauma",
        ],
    },
    {
        "name": "Emergency Medicine",
        "description": "Immediate medical care for emergency and critical conditions.",
        "subtypes": [
            "Trauma",
            "Acute Care",
            "Emergency Critical Care",
        ],
    },
    {
        "name": "Radiology",
        "description": "Medical imaging and diagnostic services.",
        "subtypes": [
            "X-Ray",
            "CT Scan",
            "MRI",
            "Ultrasound",
        ],
    },
    {
        "name": "Pathology",
        "description": "Laboratory investigation and diagnosis of diseases.",
        "subtypes": [
            "Clinical Pathology",
            "Histopathology",
            "Cytology",
        ],
    },
    {
        "name": "Physiotherapy",
        "description": "Physical rehabilitation and recovery services.",
        "subtypes": [
            "Orthopedic Rehabilitation",
            "Neurological Rehabilitation",
            "Sports Rehabilitation",
        ],
    },
    {
        "name": "Dentistry",
        "description": "Dental and oral healthcare services.",
        "subtypes": [
            "General Dentistry",
            "Orthodontics",
            "Oral Surgery",
        ],
    },
]


def seed_departments():
    db = SessionLocal()

    try:
        existing_count = db.query(DepartmentDB).count()

        if existing_count > 0:
            print("Departments already exist.")
            return

        for department_data in departments_data:

            department = DepartmentDB(
                name=department_data["name"],
                description=department_data["description"],
            )

            db.add(department)
            db.flush()

            for subtype_name in department_data["subtypes"]:

                subtype = DepartmentSubtypeDB(
                    department_id=department.id,
                    name=subtype_name,
                )

                db.add(subtype)

        db.commit()

        print("Departments and subtypes added successfully.")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_departments()