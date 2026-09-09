# Hospital AI Assistant

A hospital management and AI assistant API built using FastAPI, PostgreSQL, RAG, FAISS, Sentence Transformers, and Groq LLM.

## Features

- Hospital department management
- Patient management
- Doctor management
- Appointment management
- Complete CRUD operations
- PostgreSQL database integration
- RAG-based hospital information retrieval
- AI-powered chat assistant
- Swagger API documentation

## Technologies Used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- FAISS
- Sentence Transformers
- Groq LLM
- Pydantic

## Project Structure

```text
hospital-ai-assistant/
│
├── .venv/
├── .gitignore
├── requirements.txt
├── README.md
│
├── documents/
│   └── hospital_info.txt
│
└── app/
    ├── main.py
    ├── department.py
    ├── patient.py
    ├── doctor.py
    ├── appointment.py
    ├── chat.py
    ├── rag.py
    ├── database.py
    └── models.py