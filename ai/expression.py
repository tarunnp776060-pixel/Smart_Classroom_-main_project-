import cv2
import numpy as np

class ExpressionAnalyzer:
    """
    OpenCV Expression & Mouth Openness Analyzer.
    Detects mouth aspect ratio (yawning indicator) in lower face region.
    """
    def analyze_expression_in_chip(self, face_chip_bgr):
        if face_chip_bgr is None or face_chip_bgr.size == 0:
            return {'mouth_ratio': 0.0, 'is_yawning': False, 'expression': 'Neutral'}

        fh, fw, _ = face_chip_bgr.shape
        # Lower third of face contains mouth
        mouth_region = face_chip_bgr[int(fh*0.65):fh, int(fw*0.2):int(fw*0.8)]
        
        if mouth_region.size == 0:
            return {'mouth_ratio': 0.0, 'is_yawning': False, 'expression': 'Neutral'}

        gray_mouth = cv2.cvtColor(mouth_region, cv2.COLOR_BGR2GRAY)
        # Intensity variance ratio
        val = np.std(gray_mouth) / (np.mean(gray_mouth) + 1e-6)

        is_yawning = val > 0.45

        if is_yawning:
            expression = 'Yawning / Drowsy'
        else:
            expression = 'Neutral / Focused'

        return {
            'mouth_ratio': round(float(val), 3),
            'is_yawning': is_yawning,
            'expression': expression
        }
