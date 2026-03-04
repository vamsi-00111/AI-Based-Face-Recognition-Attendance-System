from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import shutil
from face_engine import FaceDetector

load_dotenv()

app = FastAPI()

# Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["attendence_app"]

users = db["users"]
attendance = db["attendence"]

detector = FaceDetector(users)

@app.get("/")
def home():
    return {"message": "API Running"}

@app.post("/register")
async def register(
    student_id: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...)
):
    
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = detector.encoding_face(users, student_id, file_path, name)

    if result is None:
        result = "Student registered successfully"

    return {"status": result}

@app.get("/start")
def start_attendance():
    detector.run(attendance)
    return {"message": "Attendance Started"}

@app.get("/attendance/date/{date}")
def get_attendance_by_date(date: str):
    
    records = list(attendance.find(
        {"date": date},
        {"_id": 0}
    ))

    return {"records": records}

@app.get("/attendance/student/{student_id}")
def total_attendance(student_id: str):

    count = attendance.count_documents({
        "student_id": student_id,
        "status": "Present"
    })

    return {
        "student_id": student_id,
        "total_present": count
    }
