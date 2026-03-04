from logger import logger
import face_recognition
import cv2
import numpy as np
import datetime


class FaceDetector:
    def __init__(self, db_collection):
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        self.load_known_faces(db_collection)
        
        self.frame_rescale = 0.25  
        self.scale_inv = int(1 / self.frame_rescale)
        self.tolerance = 0.5  
        
        self.face_locations = []
        self.face_names = []
        self.process_current_frame = True
        
    def encoding_face(self, collection, student_id, image_path, name):
        '''Used for registering and encoding new faces into MongoDB'''
        if collection.find_one({"student_id": student_id}):
            return "student already registered"
        
        logger.info(f"Reading image and encoding for: {name}")
        load_image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(load_image)
        
        if len(encodings) == 0:
            return "no faces found"
            
        logger.info("entering data into mongodb")
        collection.insert_one({
            "student_id": student_id,
            "student_name": name,
            "face_encoding": encodings[0].tolist()
        })
        
        # Refresh local lists after new registration
        self.load_known_faces(collection)
        logger.info("data entered and local memory updated")
        return "data entered successfully"

    def load_known_faces(self, collection):
        """Pre-loads faces into memory for fast matching"""
        logger.info("loading student names and face encodings from DB")
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        
        users = list(collection.find({}, {"student_name": 1, "face_encoding": 1, "student_id": 1, "_id": 0}))
        for user in users:
            self.known_encodings.append(np.array(user["face_encoding"]))
            self.known_names.append(user["student_name"])
            self.known_ids.append(user["student_id"])
        print(f"Loaded {len(self.known_names)} faces from database.")

    def run(self, attend_db):
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        try:
            while True:
                ret, frame = video_capture.read()
                if not ret: break

                if self.process_current_frame:
                    # 1. Resize and Convert
                    small_frame = cv2.resize(frame, (0, 0), fx=self.frame_rescale, fy=self.frame_rescale)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                    # 2. Find and Encode faces
                    self.face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                    self.face_names = []
                    for face_encoding in face_encodings:
                        name = "Unknown"
                        s_id = "Unknown"
                        
                        # Check matches
                        if self.known_encodings:
                            distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                            best_match_index = np.argmin(distances)
                            
                            if distances[best_match_index] < self.tolerance:
                                name = self.known_names[best_match_index]
                                s_id = self.known_ids[best_match_index]
                        
                        # CRITICAL: Always append so the count matches face_locations
                        self.face_names.append(name)

                        # 3. Attendance Logic (Only for recognized students)
                        if name != "Unknown":
                            today_date = datetime.datetime.now().strftime("%d:%m:%Y")
                            search_criteria = {"student_id": s_id, "date": today_date}
                            
                            if not attend_db.find_one(search_criteria, {"_id": 1}):
                                attendance_data = {
                                    "student_id": s_id,
                                    "name": name,
                                    "date": today_date,
                                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                                    "status": "Present"
                                }
                                attend_db.insert_one(attendance_data)
                                logger.info(f"Attendance recorded for {name}")

                self.process_current_frame = not self.process_current_frame

                # 4. Drawing Logic
                for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                    # Scale back up
                    top *= self.scale_inv
                    right *= self.scale_inv
                    bottom *= self.scale_inv
                    left *= self.scale_inv

                    # Red for Unknown, Green for Known
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

                cv2.imshow('Attendance System', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
            
    def check_attendence_for_one_student(self,db,student_id):
        '''this function checks how many days a student present '''
        
        student_id = student_id
        present_count = db.count_documents({
        "student_id": student_id, 
        "status": "Present"
                        })
        print(f"Student {student_id} was present for {present_count} days.")
        
        
        

        

