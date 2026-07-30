import numpy as np

class AttentionScorer:
    """
    Explainable Attention Scoring Engine.
    Computes a 0 to 100 attention index based on Eye Aspect Ratio,
    Head Pose orientation (Yaw, Pitch), and Expression.
    """
    def __init__(self, ear_weight=35.0, head_weight=45.0, temporal_decay=0.85):
        self.ear_weight = ear_weight
        self.head_weight = head_weight
        self.temporal_decay = temporal_decay
        # Student history buffer for temporal smoothing: { student_id: float_score }
        self.student_history = {}

    def calculate_attention(self, eye_data, head_data, expression_data, student_id=None):
        """
        Calculates explainable score (0-100) and category classification.
        """
        base_score = 100.0
        penalties = {}

        # 1. Eye Closure Penalty (Max 35 points penalty)
        avg_ear = eye_data.get('avg_ear', 0.3)
        if avg_ear >= 0.22:
            p_eye = 0.0
        elif avg_ear >= 0.16:
            p_eye = 12.0
        else: # Closed / Drowsy
            p_eye = 35.0
        penalties['eye_penalty'] = round(p_eye, 1)

        # 2. Yaw Penalty (Looking Left/Right) (Max 35 points penalty)
        abs_yaw = abs(head_data.get('yaw', 0.0))
        if abs_yaw <= 15.0:
            p_yaw = 0.0
        else:
            p_yaw = min(35.0, (abs_yaw - 15.0) * 1.6)
        penalties['yaw_penalty'] = round(p_yaw, 1)

        # 3. Pitch Penalty (Looking Up/Down) (Max 20 points penalty)
        abs_pitch = abs(head_data.get('pitch', 0.0))
        if abs_pitch <= 15.0:
            p_pitch = 0.0
        else:
            p_pitch = min(20.0, (abs_pitch - 15.0) * 1.4)
        penalties['pitch_penalty'] = round(p_pitch, 1)

        # 4. Yawning Penalty (Max 15 points penalty)
        if expression_data.get('is_yawning', False):
            p_yawn = 15.0
        else:
            p_yawn = 0.0
        penalties['yawn_penalty'] = round(p_yawn, 1)

        # Raw Score calculation
        raw_score = base_score - p_eye - p_yaw - p_pitch - p_yawn
        raw_score = max(0.0, min(100.0, raw_score))

        # Temporal Smoothing if student_id is provided
        if student_id:
            prev_score = self.student_history.get(student_id, raw_score)
            smooth_score = (self.temporal_decay * prev_score) + ((1.0 - self.temporal_decay) * raw_score)
            self.student_history[student_id] = smooth_score
            final_score = float(smooth_score)
        else:
            final_score = float(raw_score)

        # Categorization
        if final_score >= 80.0:
            category = 'Attentive'
            badge_color = 'success' # Green
        elif final_score >= 50.0:
            category = 'Partially Attentive'
            badge_color = 'warning' # Yellow/Orange
        else:
            category = 'Inattentive'
            badge_color = 'danger' # Red

        return {
            'score': round(final_score, 1),
            'category': category,
            'badge_color': badge_color,
            'penalties': penalties,
            'details': {
                'eye_status': eye_data.get('eye_status', 'Unknown'),
                'head_pose_status': head_data.get('status', 'Unknown'),
                'expression': expression_data.get('expression', 'Neutral')
            }
        }
