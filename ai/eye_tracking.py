import cv2
import numpy as np

class EyeTracker:
    def __init__(self, ear_threshold=0.21):
        self.ear_threshold = ear_threshold
        cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        self.eye_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze_eyes_in_face(self, face_chip_bgr):
        """
        Analyze eyes in face crop.
        Returns left_ear, right_ear, avg_ear, eye_status, is_closed.
        """
        if face_chip_bgr is None or face_chip_bgr.size == 0:
            return {'avg_ear': 0.0, 'eye_status': 'Not Detected', 'is_closed': False}

        fh, fw, _ = face_chip_bgr.shape
        # Top half of face contains eyes
        top_half = face_chip_bgr[0:int(fh*0.6), :]
        gray_top = cv2.cvtColor(top_half, cv2.COLOR_BGR2GRAY)
        gray_top = cv2.equalizeHist(gray_top)

        eyes = self.eye_cascade.detectMultiScale(
            gray_top,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(int(fw*0.15), int(fh*0.12))
        )

        num_eyes = len(eyes)

        if num_eyes >= 2:
            # Measure aspect ratios of detected eye regions
            ears = []
            for (ex, ey, ew, eh) in eyes[:2]:
                ear = float(eh / (ew + 1e-6))
                ears.append(ear)
            avg_ear = float(np.mean(ears))
            status = 'Eyes Open'
            is_closed = False
        elif num_eyes == 1:
            ex, ey, ew, eh = eyes[0]
            avg_ear = float(eh / (ew + 1e-6))
            if avg_ear >= 0.18:
                status = 'Eyes Open'
                is_closed = False
            else:
                status = 'Partial / Blinking'
                is_closed = False
        else:
            # No eye cascade detection usually means eyes are closed or turned away
            avg_ear = 0.12
            status = 'Eyes Closed / Drowsy'
            is_closed = True

        return {
            'left_ear': round(avg_ear, 3),
            'right_ear': round(avg_ear, 3),
            'avg_ear': round(avg_ear, 3),
            'eye_status': status,
            'is_closed': is_closed
        }
