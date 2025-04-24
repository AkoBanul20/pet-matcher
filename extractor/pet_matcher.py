import numpy as np
from . pet_extractor import PetFeatureExtractor

class PetMatcher:
    def __init__(self):
        self.feature_extractor = PetFeatureExtractor()

    def compare_pet_images(self, lost_pet_image_path, reported_image_path, threshold=0.65):
        """
        Direct comparison between a lost pet image and a reported sighting image.
        Returns similarity score and boolean indicating if it's a match.
        """
        # Extract features from both images
        lost_pet_features = self.feature_extractor.extract_features(lost_pet_image_path)
        reported_features = self.feature_extractor.extract_features(reported_image_path)
        
        # Calculate similarity (cosine similarity)
        similarity = np.dot(lost_pet_features, reported_features)
        
        # Determine if it's a match based on threshold
        is_match = similarity > threshold
        
        return {
            'similarity_score': float(similarity),
            'is_match': bool(is_match),
            'confidence': self._calculate_confidence(similarity)
        }
    
    def _calculate_confidence(self, similarity):
        """Convert similarity score to a confidence percentage."""
        # Map similarity range (typically 0.5-1.0) to percentage (0-100%)
        # Adjust these boundaries based on your testing
        if similarity < 0.5:
            return 0
        elif similarity > 0.95:
            return 100
        else:
            # Linear mapping from 0.5-0.95 to 0-100%
            return int(((similarity - 0.5) / 0.45) * 100)
    