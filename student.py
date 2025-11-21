from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3

app = FastAPI(title="Student Management API")
# ----------------------------
# Database setup
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

# Create table if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            course TEXT NOT NULL,
            score REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class Student(BaseModel):
    id: int
    name: str
    age: int
    course: str
    score: float = Field(ge=0.0, le=100.0)

class StudentCreate(BaseModel):
    name: str
    age: int
    course: str
    score: float = Field(ge=0.0, le=100.0)

class StudentUpdate(BaseModel):
    name: str
    age: int
    course: str
    score: float = Field(ge=0.0, le=100.0)

# in-memory storage
_students: List[Student] = []
_next_id = 1

def _get_next_id() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid

def _find_index(student_id: int) -> Optional[int]:
    for i, s in enumerate(_students):
        if s.id == student_id:
            return i
    return None

@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate):
    student = Student(id=_get_next_id(), **payload.dict())
    _students.append(student)
    return student

@app.get("/students", response_model=List[Student])
def list_students():
    return _students

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    idx = _find_index(student_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return _students[idx]

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, payload: StudentUpdate):
    idx = _find_index(student_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Student not found")
    updated = Student(id=student_id, **payload.dict())
    _students[idx] = updated
    return updated

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    idx = _find_index(student_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Student not found")
    _students.pop(idx)
    return None

# extra credit: topper
@app.get("/students/topper", response_model=Student)
def get_topper():
    if not _students:
        raise HTTPException(status_code=404, detail="No students")
    topper = max(_students, key=lambda s: s.score)
    return topper
