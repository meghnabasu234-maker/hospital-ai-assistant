"""initial schema baseline

Revision ID: a4587481e026
Revises:
Create Date: 2026-09-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4587481e026"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the complete hospital AI assistant database schema."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("staff_type", sa.String(), nullable=True),
        sa.Column("patient_type", sa.String(), nullable=True),
        sa.Column("doctor_category", sa.String(), nullable=True),
        sa.Column("doctor_specialization", sa.String(), nullable=True),
    )

    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_unique_constraint(
        "uq_users_username",
        "users",
        ["username"],
    )
    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"],
    )

    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
    )

    op.create_index(
        "ix_departments_id",
        "departments",
        ["id"],
        unique=False,
    )

    op.create_table(
        "department_subtypes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
    )

    op.create_index(
        "ix_department_subtypes_id",
        "department_subtypes",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_department_subtypes_department_id",
        "department_subtypes",
        ["department_id"],
        unique=False,
    )

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(), nullable=False),
        sa.Column("disease", sa.String(), nullable=False),
    )

    op.create_index(
        "ix_patients_id",
        "patients",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_patients_user_id",
        "patients",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("degree", sa.String(), nullable=True),
        sa.Column("specialization", sa.String(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("subtype_id", sa.Integer(), nullable=True),
        sa.Column("appointment_fee", sa.Float(), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
    )

    op.create_index(
        "ix_doctors_id",
        "doctors",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_doctors_user_id",
        "doctors",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(), nullable=True),
        sa.Column("time", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("fee", sa.Float(), nullable=False),
        sa.Column("payment_status", sa.String(), nullable=False),
    )

    op.create_index(
        "ix_appointments_id",
        "appointments",
        ["id"],
        unique=False,
    )

    op.create_table(
        "bills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("appointment_id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("consultation_fee", sa.Float(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=True),
        sa.Column("payment_status", sa.String(), nullable=False),
    )

    op.create_index(
        "ix_bills_id",
        "bills",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_bills_appointment_id",
        "bills",
        ["appointment_id"],
        unique=True,
    )

    op.create_index(
        "ix_bills_patient_id",
        "bills",
        ["patient_id"],
        unique=False,
    )

    op.create_index(
        "ix_bills_doctor_id",
        "bills",
        ["doctor_id"],
        unique=False,
    )

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("file_type", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
    )

    op.create_index(
        "ix_knowledge_documents_id",
        "knowledge_documents",
        ["id"],
        unique=False,
    )

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
    )

    op.create_index(
        "ix_knowledge_chunks_id",
        "knowledge_chunks",
        ["id"],
        unique=False,
    )

    op.create_table(
        "chat_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
    )

    op.create_index(
        "ix_chat_history_id",
        "chat_history",
        ["id"],
        unique=False,
    )

    op.create_table(
        "doctor_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_index(
        "ix_doctor_reviews_id",
        "doctor_reviews",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_doctor_reviews_doctor_id",
        "doctor_reviews",
        ["doctor_id"],
        unique=False,
    )

    op.create_index(
        "ix_doctor_reviews_patient_id",
        "doctor_reviews",
        ["patient_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the complete hospital AI assistant database schema."""

    op.drop_table("doctor_reviews")
    op.drop_table("chat_history")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_documents")
    op.drop_table("bills")
    op.drop_table("appointments")
    op.drop_table("doctors")
    op.drop_table("patients")
    op.drop_table("department_subtypes")
    op.drop_table("departments")
    op.drop_table("users")