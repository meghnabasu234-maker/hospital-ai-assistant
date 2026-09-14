# Hospital AI Assistant

An AI-powered hospital management and knowledge assistant built using **FastAPI, PostgreSQL, SQLAlchemy, FAISS, Sentence Transformers, and Groq LLM**.

The system provides secure hospital management APIs along with a RAG-based chatbot that answers hospital-related questions using approved hospital documents.

## Features

### Authentication & Security

* User registration and login
* JWT-based authentication
* Role-based access control
* Supports Admin, Staff, Doctor, and Patient/User roles
* Protected API endpoints

### Hospital Management

* Department CRUD operations
* Doctor CRUD operations
* Patient CRUD operations
* Appointment CRUD operations
* Doctor search and filtering
* Appointment status management
* Appointment scheduling

### Billing

* Appointment bill generation
* Patient payment submission
* Staff/Admin payment confirmation
* Payment status tracking
* Appointment and billing synchronization

### AI & RAG

* Hospital document upload
* Document indexing
* Text chunking
* FAISS vector search
* Sentence Transformers embeddings
* Groq LLM integration
* Retrieval-Augmented Generation (RAG)
* Source references in chatbot responses
* Emergency and safety-aware responses

### Communication

* AI chatbot
* WebSocket-based chat
* Chat history support

### API Documentation & Testing

* Interactive Swagger documentation
* Pytest test suite
* Authentication and protected-route tests

## Technologies Used

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic
* JWT
* FAISS
* Sentence Transformers
* Groq LLM
* Pytest
* Uvicorn

## Project Structure

```text
hospital-ai-assistant/
│
├── .venv/
├── .gitignore
├── requirements.txt
├── README.md
├── tests/
│   └── test_main.py
│
├── documents/
│   └── hospital_info.txt
│
└── app/
    ├── main.py
    ├── database.py
    ├── department.py
    ├── patient.py
    ├── doctor.py
    ├── appointment.py
    ├── chat.py
    ├── rag.py
    │
    ├── models/
    ├── schemas/
    ├── api/
    ├── core/
    └── websocket/
```

## Database

The application uses **PostgreSQL** as the primary database.

Database used by the project:

```text
hospital_db
```

The database stores information related to:

* Users
* Departments
* Doctors
* Patients
* Appointments
* Bills

## Running the Project

### 1. Create and activate the virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start the FastAPI server

```powershell
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

## Swagger Documentation

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to test:

* Authentication
* Departments
* Doctors
* Patients
* Appointments
* Billing
* Document upload
* AI chatbot
* Other protected endpoints

## RAG Workflow

The hospital knowledge assistant follows this workflow:

```text
Hospital Document
       ↓
Document Upload
       ↓
Text Extraction
       ↓
Text Chunking
       ↓
Sentence Transformer Embeddings
       ↓
FAISS Vector Index
       ↓
User Question
       ↓
Relevant Context Retrieval
       ↓
Groq LLM
       ↓
Grounded Answer + Source References
```

The chatbot is designed to answer hospital-related questions using the indexed hospital knowledge base.

## Safety Handling

The chatbot includes an emergency-response mechanism.

For potentially serious emergency questions, the system provides a safety response advising the user to seek immediate medical care instead of relying on the chatbot for emergency treatment.

## Testing

The project includes automated tests using **pytest**.

Run the tests with:

```powershell
pytest -q
```

Example successful result:

```text
3 passed
```

## API Security

Protected endpoints require a valid JWT access token.

Role-based permissions are used to restrict access to different operations.

Examples include:

* Admin/Staff management operations
* Doctor-specific appointment access
* Patient-specific appointment access
* Protected document upload
* Protected billing operations

## Conclusion

The Hospital AI Assistant combines traditional hospital management functionality with an AI-powered knowledge assistant.

The project demonstrates:

* Python programming
* FastAPI REST API development
* PostgreSQL database integration
* SQLAlchemy ORM
* JWT authentication
* Role-based authorization
* CRUD operations
* RAG architecture
* Vector search using FAISS
* LLM integration
* Automated API testing
* WebSocket communication
