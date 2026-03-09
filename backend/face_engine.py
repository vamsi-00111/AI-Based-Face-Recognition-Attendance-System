
import face_recognition
import numpy as np
import datetime
import cv2
from logger import logger


class FaceDetector:

    def __init__(self, db_collection):

        self.known_encodings = []
        self.known_names = []
        self.known_ids = []

        self.tolerance = 0.45

        self.load_known_faces(db_collection)

    # ---------------- REGISTER FACE ----------------

    def encoding_face(self, collection, student_id, image_path, name):

        if collection.find_one({"student_id": student_id}):
            return "student already registered"

        logger.info(f"Reading image and encoding for: {name}")

        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            return "no faces found"

        collection.insert_one({
            "student_id": student_id,
            "student_name": name,
            "face_encoding": encodings[0].tolist()
        })

        # reload known faces
        self.load_known_faces(collection)

        return "data entered successfully"

    # ---------------- LOAD KNOWN FACES ----------------

    def load_known_faces(self, collection):

        logger.info("Loading student names and encodings from DB")

        self.known_encodings = []
        self.known_names = []
        self.known_ids = []

        users = list(collection.find(
            {},
            {
                "student_name": 1,
                "face_encoding": 1,
                "student_id": 1,
                "_id": 0
            }
        ))

        for user in users:

            self.known_encodings.append(
                np.array(user["face_encoding"])
            )

            self.known_names.append(
                user["student_name"]
            )

            self.known_ids.append(
                user["student_id"]
            )

        print(f"Loaded {len(self.known_names)} faces from database.")

    # ---------------- DETECT FACES ----------------

    def detect_faces_from_frame(self, frame, attend_db):

        # Convert BGR → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")

        print("Face locations:", face_locations)

        detected_students = []

        if len(face_locations) == 0:
            return detected_students

        try:
            # safer encoding method
            face_encodings = face_recognition.face_encodings(rgb_frame)
        except Exception as e:
            print("Encoding error:", e)
            return detected_students

        print("Encodings:", len(face_encodings))

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

            name = "Unknown"
            s_id = "Unknown"

            if len(self.known_encodings) > 0:

                distances = face_recognition.face_distance(
                    self.known_encodings,
                    face_encoding
                )

                best_match_index = np.argmin(distances)

                if distances[best_match_index] < self.tolerance:

                    name = self.known_names[best_match_index]
                    s_id = self.known_ids[best_match_index]

            # ---------------- MARK ATTENDANCE ----------------

            if name != "Unknown":

                today_date = datetime.datetime.now().strftime("%Y-%m-%d")

                search_query = {
                    "student_id": s_id,
                    "date": today_date
                }

                if not attend_db.find_one(search_query):

                    attendance_data = {
                        "student_id": s_id,
                        "name": name,
                        "date": today_date,
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "status": "Present"
                    }

                    attend_db.insert_one(attendance_data)

                    logger.info(f"Attendance recorded for {name}")

            detected_students.append({
                "student_id": s_id,
                "name": name,
                "top": top,
                "right": right,
                "bottom": bottom,
                "left": left
            })

        return detected_students