import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np

class PetFeatureExtractor:
    def __init__(self, model_name='resnet50'):
        # Load pre-trained model
        if model_name == 'resnet50':
            self.model = models.resnet50(pretrained=True)
            # Remove the classification layer
            self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def extract_features(self, img_path):
        """Extract feature vector from image."""
        # Load and transform image
        print(img_path)
        img = Image.open(img_path).convert('RGB')
        img_tensor = self.transform(img)
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
        
        # Extract features
        with torch.no_grad():
            features = self.model(img_tensor)
        
        # Flatten and convert to numpy array
        features = features.squeeze().numpy()
        
        # Normalize feature vector
        normalized_features = features / np.linalg.norm(features)
        return normalized_features
    
    def compare_images(self, img_path1, img_path2, threshold=0.75):
        """Compare two images and return similarity score."""
        # Extract features
        features1 = self.extract_features(img_path1)
        features2 = self.extract_features(img_path2)
        
        # Calculate cosine similarity
        similarity = np.dot(features1, features2)
        
        # Check if similarity is above threshold
        is_match = similarity > threshold
        
        return {
            'similarity': float(similarity),
            'is_match': bool(is_match)
        }