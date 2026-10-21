# Library API

A simple REST API that mimics the core operations of a library system. The API allows clients to manage books and library members through HTTP requests.

This project was created to demonstrate the fundamentals of building and interacting with an API.

## Project Purpose

The Library API provides endpoints for:

- Viewing available books
- Adding new books
- Updating book information
- Removing books
- Viewing library members
- Registering new members
- Updating member information
- Removing members

The application uses FastAPI to define the API routes and automatically generates interactive API documentation.

## Technologies

- Python
- FastAPI
- Uvicorn
- Pydantic

## Getting Started

### Prerequisites

Install the following before running the project:

- Python 3.9 or newer
- Git
- pip
- PostreSQL

### Clone the Repository

Clone the repository and switch to the assignment branch:

```bash
git clone https://github.com/jeremy-flanagin/SSD_3310.git
cd SSD_3310
git checkout main
```

### Install Dependencies

Install the required Python packages:
```bash
pip install uv
```

### Create a Virtual Environment

Creating a virtual environment keeps the project's dependencies separate from other Python projects.


```bash
uv venv
```

### Running the API

Before running:
Create the SQL database by running the command, replacing the file link with
your PostgreSQL installation.
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f scripts\setup_database.sql
```

Start the server from the project root:
```bash
uvicorn src.main:api --reload
```
The API should be available at:
```text
http://127.0.0.1:8000
```
The --reload option automatically restarts the server when source files are changed.

### API Documentation

Once the server is running, FastAPI provides two documentation interfaces:
#### Swagger UI: http://127.0.0.1:8000/docs
#### ReDoc: http://127.0.0.1:8000/redoc

Swagger UI allows you to send requests directly from the browser. ReDoc provides a more structured, read-only view of the API schema.
Example Requests

The examples below assume that the API is running at http://127.0.0.1:8000.

#### Books

Get all books
```bash
curl http://127.0.0.1:8000/books
```
Example response:
```json
[
  {
    "id": 1,
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "available": true
  }
]
```
Get one book
```bash
curl http://127.0.0.1:8000/books/1
```
Add a book
```bash

curl -X POST http://127.0.0.1:8000/books \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "available": true
  }'
```
Update a book
```bash

curl -X PUT http://127.0.0.1:8000/books/1 \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "available": false
  }'
```
Delete a book
```bash

curl -X DELETE http://127.0.0.1:8000/books/1
```
#### Members
Get all members
```bash

curl http://127.0.0.1:8000/members
```
Example response:
```json
[
  {
    "id": 1,
    "name": "Alex Smith",
    "email": "alex.smith@example.com"
  }
]
```
Get one member
```bash

curl http://127.0.0.1:8000/members/1
```
Register a member
```bash

curl -X POST http://127.0.0.1:8000/members \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Alex Smith",
    "email": "alex.smith@example.com"
  }'
```
Update a member
```bash

curl -X PUT http://127.0.0.1:8000/members/1 \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Alex Johnson",
    "email": "alex.johnson@example.com"
  }'
```
Delete a member
```bash

curl -X DELETE http://127.0.0.1:8000/members/1
```
#### Request Methods
| Method | Purpose |
|--------|---------|
| GET	   | Retrieve books or members|
| POST   |	Create a new book or member|
| PUT	   |Update an existing book or member|
| DELETE | Remove a book or member|
### Project Structure

The current project structure is:
```text
SSD\_3310/
├── README.md
├── pyproject.toml
├── .env.example
├── uv.lock
└── src/
    ├── __init__.py
    ├── main.py
    ├── exceptions.py
    ├── config.py
    ├── service_accessor.py
    └── database/
        ├── __init__.py
        └── session.py
    └── models/
        ├── __init__.py
        ├── base.py
        ├── book.py
        └── members.py
    └── repositories/
        ├── __init__.py
        ├── book.py
        └── member.py
    └── router/
        ├── __init__.py
        ├── books.py
        ├── http_errors.py
        └── members.py
    └── schema/
        ├── __init__.py
        ├── books.py
        └── members.py
    └── schema/
        └── books/
            ├── __init__.py
            ├── base.py
            ├── database.py
            └── memory.py
        └── members/
            ├── __init__.py
            ├── base.py
            ├── database.py
            └── memory.py
        ├── __init__.py
        ├── in_memory_store.py
```
The main.py file contains the FastAPI application and route definitions.