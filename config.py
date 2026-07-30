import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'classroom-attentiveness-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dataset and uploads
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset', 'students')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    
    # Attention Scoring Thresholds & Weights
    EAR_THRESHOLD = 0.21         # Eye Aspect Ratio below this = closed eyes
    EAR_DROWSY_FRAMES = 15       # Frames with closed eyes to count as drowsy
    YAW_THRESHOLD = 25           # Degrees left/right to flag looking away
    PITCH_THRESHOLD = 20         # Degrees up/down to flag looking up/down
    
    # Face Recognition Threshold (Cosine similarity or Euclidean distance)
    RECOGNITION_THRESHOLD = 0.65 # Minimum similarity score for face match
