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

### Clone the Repository

Clone the repository and switch to the assignment branch:

```bash
git clone https://github.com/jeremy-flanagin/SSD_3310.git
cd SSD_3310
git checkout main
```
### Create a Virtual Environment

Creating a virtual environment keeps the project's dependencies separate from other Python projects.


macOS and Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
### Install Dependencies

Install the required Python packages:
```bash
pip install fastapi uvicorn
```
If the project includes a dependency file, install from it instead:
```bash
pip install -r requirements.txt
```
### Running the API

Start the development server from the project root:
```bash
uvicorn main:app --reload
```
The API should be available at:
```text
http://127.0.0.1:8000
```
The --reload option automatically restarts the server when source files are changed.

If the application's FastAPI instance is located in a different module, update the command accordingly. For example:
```bash
uvicorn app.main:app --reload
```
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
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py
    ├── models.py
    └── routes/
        ├── __init__.py
        ├── books.py
        └── members.py
```
The main.py file contains the FastAPI application and route definitions. The requirements.txt file contains the Python dependencies needed to run the API.

