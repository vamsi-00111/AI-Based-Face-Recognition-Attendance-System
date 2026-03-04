from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import shutil
import numpy as np
import cv2
from face_engine import FaceDetector


# ---------------- LOAD ENV ----------------

load_dotenv()

# ---------------- FASTAPI APP ----------------

app = FastAPI(title="Face Recognition Attendance API")


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- MONGODB ----------------

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)

db = client["attendence_app"]

users = db["users"]
attendance = db["attendence"]

print("Connected to MongoDB")
print("Collections:", db.list_collection_names())


# ---------------- FACE DETECTOR ----------------

detector = FaceDetector(users)


# ---------------- HOME ----------------

@app.get("/")
def home():
    return {"message": "Face Recognition Attendance API Running"}


# ---------------- REGISTER STUDENT ----------------

@app.post("/register")
async def register_student(
    student_id: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...)
):

    try:

        file_path = f"temp_{student_id}.jpg"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = detector.encoding_face(users, student_id, file_path, name)

        os.remove(file_path)

        return {
            "status": "success",
            "message": result
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ---------------- FACE DETECTION ----------------

@app.post("/detect")
async def detect_face(file: UploadFile = File(...)):

    try:

        contents = await file.read()

        np_img = np.frombuffer(contents, np.uint8)

        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if frame is None:
            return {"detected_faces": []}

        detected_faces = detector.detect_faces_from_frame(frame, attendance)

        return {"detected_faces": detected_faces}

    except Exception as e:

        return {
            "detected_faces": [],
            "error": str(e)
        }


# ---------------- ATTENDANCE BY DATE ----------------

@app.get("/attendance/date/{date}")
def get_attendance_by_date(date: str):

    try:

        records = list(
            attendance.find(
                {"date": date},
                {"_id": 0}
            )
        )

        return {
            "date": date,
            "records": records
        }

    except Exception as e:

        return {"error": str(e)}


# ---------------- TOTAL ATTENDANCE ----------------

@app.get("/attendance/student/{student_id}")
def total_attendance(student_id: str):

    try:

        count = attendance.count_documents({
            "student_id": student_id,
            "status": "Present"
        })

        return {
            "student_id": student_id,
            "total_present": count
        }

    except Exception as e:

        return {"error": str(e)}