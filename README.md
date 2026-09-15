# AI-Powered Hospital Knowledge and Appointment Assistant

An AI-powered hospital management and knowledge assistant built using **FastAPI, PostgreSQL, SQLAlchemy, FAISS, Sentence Transformers, and Groq LLM**.

The system provides secure hospital management APIs with JWT authentication, role-based access control, appointment and billing management, document-based RAG, and an AI hospital assistant that provides source-grounded answers from approved hospital knowledge documents.

---

## Features

### Authentication & Security

* User registration and login
* JWT-based authentication
* Role-based access control
* Admin, Staff, Doctor, and Patient/User roles
* Protected API endpoints
* Password reset functionality

### Hospital Management

* Department CRUD operations
* Doctor CRUD operations
* Patient CRUD operations
* Appointment CRUD operations
* Doctor search and filtering
* Appointment scheduling
* Appointment assignment
* Appointment status management

### Billing

* Appointment bill generation
* Patient payment submission
* Staff/Admin payment confirmation
* Payment status tracking
* Appointment and billing synchronization

### AI & RAG

* Hospital knowledge document upload
* Document indexing
* Text extraction
* Text chunking
* Sentence Transformer embeddings
* FAISS vector search
* Groq LLM integration
* Retrieval-Augmented Generation (RAG)
* Source references in chatbot responses
* Emergency and safety-aware responses

### Communication

* AI chatbot
* WebSocket-based chat
* Chat history support

### API Documentation & Testing

* Interactive Swagger/OpenAPI documentation
* Pytest test suite
* Authentication tests
* Protected-route tests
* GitHub Actions CI

---

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
* WebSockets
* Alembic

---

## Project Structure

```text
hospital-ai-assistant/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── department.py
│   ├── patient.py
│   ├── doctor.py
│   ├── appointment.py
│   ├── chat.py
│   ├── rag.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── api/
│   ├── core/
│   └── websocket/
│
├── documents/
│   ├── hospital_info.txt
│   └── test.txt
│
├── frontend/
│
├── migrations/
│   ├── versions/
│   └── env.py
│
├── screenshots/
│   ├── 01_health_endpoint.png
│   ├── 02_login_response.png
│   ├── 03_crud_endpoint.png
│   ├── 04_document_upload.png
│   └── 05_chatbot_sources.png
│
├── tests/
│   └── test_main.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── README.md
└── requirements.txt
```

---

## Prerequisites

Before running the project, install:

* Python 3.11 or compatible Python version
* PostgreSQL
* Git

A **Groq API key** is required for the AI chatbot.

---

## Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hospital_db
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
```

**Never commit `.env` to GitHub.**

Only `.env.example` should be included in the repository.

---

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/meghnabasu234-maker/hospital-ai-assistant.git
cd hospital-ai-assistant
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root and add:

* `DATABASE_URL`
* `SECRET_KEY`
* `GROQ_API_KEY`

Do not upload `.env` to GitHub.

---

## Database Setup

Create a PostgreSQL database named:

```text
hospital_db
```

The application uses PostgreSQL with SQLAlchemy.

The project contains database migration files using **Alembic**.

For a fresh database, apply the migration:

```powershell
alembic upgrade head
```

The current development database has already been stamped with the baseline migration.

---

## Docker Compose Setup

Docker Compose is provided to run the FastAPI application and PostgreSQL database using containers.

### Prerequisites

Install Docker Desktop before running the project with Docker Compose.

### Run with Docker Compose

Create a `.env` file and add:

```env
GROQ_API_KEY=your_groq_api_key


## Start the FastAPI Server

Run:

```powershell
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

---

## Swagger Documentation

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to test:

* Registration and login
* JWT authentication
* Departments
* Doctors
* Patients
* Appointments
* Billing
* Document upload
* RAG indexing
* AI chatbot
* Protected endpoints

---

## API Endpoints

### Authentication

```text
POST /auth/register
POST /auth/login
PUT  /auth/reset-password
```

### Departments

```text
GET    /departments
POST   /departments
GET    /departments/{department_id}
PUT    /departments/{department_id}
DELETE /departments/{department_id}
```

### Doctors

```text
GET    /doctors
POST   /doctors
GET    /doctors/{doctor_id}
PUT    /doctors/{doctor_id}
DELETE /doctors/{doctor_id}
GET    /doctors/search
```

### Patients

```text
GET    /patients
POST   /patients
GET    /patients/{patient_id}
PUT    /patients/{patient_id}
DELETE /patients/{patient_id}
```

### Appointments

```text
GET    /appointments
POST   /appointments
GET    /appointments/{appointment_id}
PUT    /appointments/{appointment_id}
DELETE /appointments/{appointment_id}
PUT    /appointments/{appointment_id}/status
PUT    /appointments/{appointment_id}/assign
POST   /appointments/{appointment_id}/bill
```

### Billing

```text
GET  /bills
GET  /bills/{appointment_id}
POST /bills/{bill_id}/pay
PUT  /bills/{bill_id}/confirm-payment
```

### Documents & RAG

```text
POST /documents/upload
POST /index/{document_id}
POST /chat
GET  /chat-history
```

### Administration

```text
GET    /admin/users/
PUT    /admin/users/{user_id}/role
DELETE /admin/users/{user_id}
```

### Health

```text
GET /health
```

---

## RAG Workflow

The hospital knowledge assistant follows this workflow:

```text
Hospital Knowledge Document
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
     Grounded Answer
          ↓
    Source References
```

---

## What is RAG?

**RAG stands for Retrieval-Augmented Generation.**

RAG combines document retrieval with a language model.

Instead of asking the language model to answer only from its general knowledge, the system first retrieves relevant information from approved hospital knowledge documents. The retrieved information is then provided to the language model to generate a grounded answer.

In this project, RAG helps the chatbot answer hospital-specific questions using indexed hospital documents.

---

## What is Chunking?

**Chunking** means dividing a large document into smaller pieces called chunks.

Large documents can be difficult to search efficiently as one complete block. By splitting the document into smaller sections, the system can retrieve only the information relevant to the user's question.

```text
Large Hospital Document
          ↓
       Chunk 1
       Chunk 2
       Chunk 3
       Chunk 4
```

The relevant chunks are retrieved during vector search.

---

## What is an Embedding?

An **embedding** is a numerical representation of text.

The Sentence Transformer model converts each text chunk into a vector of numbers that represents its meaning.

```text
"Hospital opening hours"
          ↓
 Sentence Transformer
          ↓
    Numerical Vector
```

Texts with similar meanings produce vectors that are close to each other in vector space.

---

## What is Vector Search?

**Vector search** finds text that is semantically similar to a user's question.

FAISS is used as the vector search engine in this project.

```text
User Question
      ↓
Question Embedding
      ↓
  FAISS Search
      ↓
Relevant Document Chunks
```

This allows the chatbot to retrieve relevant hospital information even when the user's wording differs from the wording in the document.

---

## Why is JWT Used?

**JWT (JSON Web Token)** is used to securely authenticate users.

After successful login, the server generates a JWT access token. The client sends this token when accessing protected endpoints.

JWT helps the project by:

* Providing stateless authentication
* Protecting API endpoints
* Identifying the logged-in user
* Supporting role-based authorization
* Providing different permissions for different user roles

---

## Why is FastAPI Used?

**FastAPI** is used to build the backend REST API.

FastAPI is suitable for this project because it provides:

* High performance
* Easy API route creation
* Automatic Swagger/OpenAPI documentation
* Request validation using Pydantic
* Dependency injection
* Authentication support
* Easy database and AI integration
* Asynchronous programming support
* WebSocket support

---

## API Security

Protected endpoints require a valid JWT access token.

Role-based permissions restrict different operations.

Examples include:

* Admin-only user management
* Staff/Admin document upload
* Protected appointment operations
* Doctor-specific operations
* Protected billing operations
* Protected chatbot access

---

## Emergency & Safety Handling

The chatbot includes an emergency-response mechanism.

For potentially serious emergency questions, the system provides a safety response advising the user to seek immediate medical care instead of relying on the chatbot for emergency treatment.

Example:

```text
User:
I am having severe chest pain and difficulty breathing.

System:
This may be a medical emergency. Please seek immediate
medical care or contact your local emergency services.
Do not rely on this chatbot for emergency treatment.
```

---

## Sample Knowledge Documents

The `documents/` directory contains sample hospital knowledge documents used for testing the RAG system.

The documents can contain information such as:

* Hospital timings
* Emergency services
* Hospital departments
* Available services
* General hospital information

---

## Testing

The project includes automated tests using **pytest**.

Run:

```powershell
pytest -q
```

Current test result:

```text
3 passed
```

The tests verify important workflows including:

* API availability
* User registration and login
* JWT-protected endpoints

The project also includes GitHub Actions for automated testing.

---

## Database Migrations

The project uses **Alembic** for database schema migration management.

Migration files are stored in:

```text
migrations/
```

To view migration history:

```powershell
alembic history
```

To check the current database migration:

```powershell
alembic current
```

For a fresh database:

```powershell
alembic upgrade head
```

This allows database schema changes to be managed through version-controlled migration files.

---

## Screenshots / Demo Evidence

The `screenshots/` directory contains evidence of the working application.

The submission screenshots include:

1. **Swagger Health Endpoint**

   * `/health`
   * Successful response

2. **Login Response**

   * `/auth/login`
   * Successful JWT access token response

3. **CRUD Endpoint**

   * Successful hospital management API operation

4. **Document Upload and Indexing**

   * `/documents/upload`
   * RAG document processing

5. **Chatbot Answer with Sources**

   * `/chat`
   * Hospital-specific answer
   * Source filename shown in the response

---

## GitHub Actions

The project includes a GitHub Actions workflow for automated testing.

The workflow runs the project's test suite to help verify that changes do not break important application functionality.

---

## Project Objective

The objective of this project is to combine traditional hospital management functionality with an AI-powered hospital knowledge assistant.

The system demonstrates:

* Python programming
* FastAPI REST API development
* PostgreSQL database integration
* SQLAlchemy ORM
* JWT authentication
* Role-based authorization
* CRUD operations
* Document processing
* Text chunking
* Embeddings
* FAISS vector search
* RAG architecture
* LLM integration
* Source-grounded chatbot responses
* Emergency safety handling
* WebSocket communication
* Automated testing
* GitHub Actions CI
* Database migrations

---

## Conclusion

The **AI-Powered Hospital Knowledge and Appointment Assistant** provides a secure backend for hospital management together with an AI-powered knowledge assistant.

The combination of FastAPI, PostgreSQL, JWT authentication, FAISS, Sentence Transformers, and Groq LLM demonstrates how traditional backend systems can be integrated with modern AI and RAG technologies.

The project also demonstrates secure API development, database management, role-based access control, document retrieval, source-grounded AI responses, automated testing, and database migration management.
