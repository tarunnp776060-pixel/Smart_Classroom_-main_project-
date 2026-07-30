import cv2
import numpy as np

class HeadPoseEstimator:
    def __init__(self, yaw_threshold=22, pitch_threshold=18):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        
        # 3D Canonical facial model points
        self.model_points_3d = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye center
            (225.0, 170.0, -135.0),      # Right eye center
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)

        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def estimate_pose_from_chip(self, face_chip_bgr, full_w, full_h, bbox):
        """
        Estimate Pitch, Yaw, Roll Euler angles in degrees using OpenCV solvePnP.
        """
        if face_chip_bgr is None or face_chip_bgr.size == 0:
            return {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0, 'status': 'Unknown', 'facing_camera': False}

        bx, by, bw, bh = bbox
        
        # Approximate 2D image landmark coordinates relative to face box
        nose_x = bx + bw * 0.5
        nose_y = by + bh * 0.55
        chin_x = bx + bw * 0.5
        chin_y = by + bh * 0.95
        l_eye_x = bx + bw * 0.3
        l_eye_y = by + bh * 0.35
        r_eye_x = bx + bw * 0.7
        r_eye_y = by + bh * 0.35
        l_mouth_x = bx + bw * 0.35
        l_mouth_y = by + bh * 0.75
        r_mouth_x = bx + bw * 0.65
        r_mouth_y = by + bh * 0.75

        # Detect actual eye centers if available in face crop
        gray_crop = cv2.cvtColor(face_chip_bgr[0:int(bh*0.6), :], cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=4)
        if len(eyes) >= 2:
            eyes_sorted = sorted(eyes, key=lambda e: e[0]) # Sort by X coordinate
            l_eye_x = bx + eyes_sorted[0][0] + eyes_sorted[0][2]/2.0
            l_eye_y = by + eyes_sorted[0][1] + eyes_sorted[0][3]/2.0
            r_eye_x = bx + eyes_sorted[1][0] + eyes_sorted[1][2]/2.0
            r_eye_y = by + eyes_sorted[1][1] + eyes_sorted[1][3]/2.0

        image_points_2d = np.array([
            [nose_x, nose_y],
            [chin_x, chin_y],
            [l_eye_x, l_eye_y],
            [r_eye_x, r_eye_y],
            [l_mouth_x, l_mouth_y],
            [r_mouth_x, r_mouth_y]
        ], dtype=np.float64)

        focal_length = full_w
        center = (full_w / 2.0, full_h / 2.0)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1))

        success, rvec, tvec = cv2.solvePnP(
            self.model_points_3d,
            image_points_2d,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0, 'status': 'Facing Forward', 'facing_camera': True}

        rmat, _ = cv2.Rodrigues(rvec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        pitch = float(angles[0])
        yaw = float(angles[1])
        roll = float(angles[2])

        # Classification
        orientations = []
        if abs(yaw) > self.yaw_threshold:
            orientations.append('Looking Right' if yaw > 0 else 'Looking Left')
        if abs(pitch) > self.pitch_threshold:
            orientations.append('Looking Down' if pitch > 0 else 'Looking Up')

        if not orientations:
            status = 'Facing Forward'
            facing_camera = True
        else:
            status = ' & '.join(orientations)
            facing_camera = False

        return {
            'pitch': pitch,
            'yaw': yaw,
            'roll': roll,
            'status': status,
            'facing_camera': facing_camera
        }
