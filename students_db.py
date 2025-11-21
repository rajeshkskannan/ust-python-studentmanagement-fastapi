from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3

app = FastAPI(title="Student Management API")
# ----------------------------
# Database setup
# ----------------------------
DB_PATH = "students.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

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

def row_to_student(row: sqlite3.Row) -> Student:
    return Student(
        id=row["id"],
        name=row["name"],
        age=row["age"],
        course=row["course"],
        score=row["score"],
    )

@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (name, age, course, score) VALUES (?, ?, ?, ?)",
            (payload.name, payload.age, payload.course, payload.score),
        )
        conn.commit()
        student_id = cur.lastrowid
        row = cur.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.close()
        return row_to_student(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students", response_model=List[Student])
def list_students():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute("SELECT * FROM students").fetchall()
        conn.close()
        return [row_to_student(r) for r in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.close()
        if row is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return row_to_student(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, payload: StudentUpdate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET name = ?, age = ?, course = ?, score = ? WHERE id = ?",
            (payload.name, payload.age, payload.course, payload.score, student_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Student not found")
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.close()
        return row_to_student(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Student not found")
        conn.close()
        return None
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

# extra credit: topper
@app.get("/students/topper", response_model=Student)
def get_topper():
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM students ORDER BY score DESC LIMIT 1").fetchone()
        conn.close()
        if row is None:
            raise HTTPException(status_code=404, detail="No students")
        return row_to_student(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
