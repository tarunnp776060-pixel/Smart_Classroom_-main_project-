import cv2
import numpy as np

class FaceDetector:
    def __init__(self, min_neighbors=5):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.min_neighbors = min_neighbors

    def detect_faces(self, frame_bgr):
        """
        Detect faces in a BGR frame using OpenCV Haar Cascade.
        Returns list of dicts: [{ 'bbox': (x, y, w, h), 'confidence': float }]
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return []

        h, w, _ = frame_bgr.shape
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=self.min_neighbors,
            minSize=(40, 40)
        )

        detected_faces = []
        for (x, y, bw, bh) in faces:
            detected_faces.append({
                'bbox': (int(x), int(y), int(bw), int(bh)),
                'confidence': 0.88,
                'relative_bbox': (x/w, y/h, bw/w, bh/h)
            })

        return detected_faces
