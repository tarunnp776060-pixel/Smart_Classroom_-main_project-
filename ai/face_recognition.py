import cv2
import numpy as np

class FaceRecognizerEngine:
    def __init__(self, threshold=0.65):
        self.threshold = threshold

    def extract_face_embedding(self, face_chip_bgr):
        """
        Extracts a normalized 128-dimensional spatial feature embedding vector from face crop.
        Uses normalized multi-scale spatial histogram and intensity distribution.
        """
        if face_chip_bgr is None or face_chip_bgr.size == 0:
            return None

        # Resize to standard 64x64 resolution
        resized = cv2.resize(face_chip_bgr, (64, 64))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # 1. Spatial cell intensity histogram (64 dims)
        cells = []
        for row in range(4):
            for col in range(4):
                cell = gray[row*16:(row+1)*16, col*16:(col+1)*16]
                hist = cv2.calcHist([cell], [0], None, [4], [0, 256]).flatten()
                cells.extend(hist)

        # 2. Sobel edge gradient spatial distribution (64 dims)
        sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(sobelx, sobely)
        mag_resized = cv2.resize(magnitude, (8, 8)).flatten()

        vec = np.concatenate([cells, mag_resized]).astype(np.float32)
        vec_norm = np.linalg.norm(vec) + 1e-6
        vec = vec / vec_norm

        # Ensure exactly 128 dimensions
        if len(vec) > 128:
            vec = vec[:128]
        elif len(vec) < 128:
            vec = np.pad(vec, (0, 128 - len(vec)))

        return vec.tolist()

    def compare_embeddings(self, embedding1, embedding2):
        """
        Computes Cosine Similarity between two 128-d feature embeddings.
        Returns similarity score (0.0 to 1.0) and boolean match flag.
        """
        if embedding1 is None or embedding2 is None:
            return 0.0, False

        v1 = np.array(embedding1, dtype=np.float32)
        v2 = np.array(embedding2, dtype=np.float32)

        min_dim = min(len(v1), len(v2))
        v1 = v1[:min_dim]
        v2 = v2[:min_dim]

        v1 = v1 / (np.linalg.norm(v1) + 1e-6)
        v2 = v2 / (np.linalg.norm(v2) + 1e-6)

        cosine_sim = float(np.dot(v1, v2))
        similarity = float((cosine_sim + 1.0) / 2.0)
        
        is_match = similarity >= self.threshold
        return similarity, is_match

    def identify_face(self, query_embedding, registered_students_encodings):
        """
        Match query embedding against registered database encodings.
        """
        if not query_embedding or not registered_students_encodings:
            return None

        best_match = None
        highest_similarity = 0.0

        for item in registered_students_encodings:
            stored_enc = item.get('encoding')
            similarity, is_match = self.compare_embeddings(query_embedding, stored_enc)
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                if similarity >= self.threshold:
                    best_match = {
                        'student_db_id': item.get('student_db_id'),
                        'student_id': item.get('student_id'),
                        'name': item.get('name'),
                        'roll_number': item.get('roll_number'),
                        'similarity': similarity
                    }

        return best_match
