from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.department import DepartmentDB
from app.models.department_subtype import DepartmentSubtypeDB


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.get("")
def get_departments(db: Session = Depends(get_db)):

    departments = db.query(DepartmentDB).all()

    result = []

    for department in departments:

        subtypes = (
            db.query(DepartmentSubtypeDB)
            .filter(
                DepartmentSubtypeDB.department_id == department.id
            )
            .all()
        )

        result.append({
            "id": department.id,
            "name": department.name,
            "description": department.description,
            "subtypes": [
                {
                    "id": subtype.id,
                    "name": subtype.name
                }
                for subtype in subtypes
            ]
        })

    return result