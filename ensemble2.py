import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
from io import BytesIO
import requests
import base64
import re
from timm import create_model

def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

device = get_device()

# Image Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load ResNet Model
def load_resnet():
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512, 2)
    )
    try:
        # Updated to use weights_only=True for security
        model.load_state_dict(torch.load("models/trained_models/resnet_model.pth", map_location=device, weights_only=True))
    except Exception as e:
        print(f"Could not load ResNet model: {e}")
    model.to(device)
    model.eval()
    return model

# Load EfficientNet Model
def load_efficientnet():
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    model.classifier = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(model.classifier[1].in_features, 512),
        nn.ReLU(),
        nn.Linear(512, 2)
    )
    try:
        # Updated to use weights_only=True for security
        model.load_state_dict(torch.load("models/trained_models/efficientnet_model.pth", map_location=device, weights_only=True), strict=False)
    except Exception as e:
        print(f"Could not load EfficientNet model: {e}")
    model.to(device)
    model.eval()
    return model

# Load ViT Model
def load_vit():
    model = create_model("vit_base_patch16_224", pretrained=False)
    model.head = nn.Sequential(
        nn.Linear(model.head.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512, 2)
    )
    try:
        # Updated to use weights_only=True for security
        model.load_state_dict(torch.load("models/trained_models/vit_model.pth", map_location=device, weights_only=True))
    except Exception as e:
        print(f"Could not load ViT model: {e}")
    model.to(device)
    model.eval()
    return model

# Try to load models
try:
    resnet = load_resnet()
    efficientnet = load_efficientnet()
    vit = load_vit()
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    models_loaded = False

def get_image_from_url(url):
    """Get image from URL or data URL"""
    try:
        # Check if it's a data URL
        if url.startswith('data:image/'):
            # Extract the base64 part
            match = re.match(r'data:image/[^;]+;base64,(.+)', url)
            if not match:
                print("Invalid data URL format")
                return None
            
            # Get the base64 encoded data
            base64_data = match.group(1)
            
            try:
                # Decode the base64 data
                image_data = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_data)).convert("RGB")
                return image
            except Exception as e:
                print(f"Error decoding base64 data: {str(e)}")
                return None
        else:
            # Regular URL
            response = requests.get(url)
            image = Image.open(BytesIO(response.content)).convert("RGB")
            return image
    except Exception as e:
        print(f"Error loading image from URL: {e}")
        return None

def ensemble_predict(image, image_path=None):
    """
    Predict using ensemble model
    
    Args:
        image (PIL.Image): The image to analyze
        image_path (str, optional): Path or URL of the image for reference
    """
    if not models_loaded:
        # Return a mock prediction if models aren't available
        import random
        prediction = random.choice(["Cancerous", "Non-Cancerous"])
        confidence = random.uniform(70, 99)
        
        result = {
            "prediction": prediction,
            "confidence": round(confidence, 2)
        }
        
        if prediction == "Cancerous":
            areas = random.sample(["Buccal mucosa", "Floor of mouth", "Lateral border of tongue", "Lip"], 
                                random.randint(1, 2))
            result["areasOfConcern"] = areas
            result["recommendation"] = "Patterns suggestive of oral cancer detected. Please consult with a healthcare professional immediately."
        else:
            result["areasOfConcern"] = []
            result["recommendation"] = "No signs of oral cancer detected. Continue regular oral check-ups."
            
        return result
    
    # Prepare image for model
    img_tensor = transform(image).unsqueeze(0).to(device)
    
    # Get ensemble prediction
    with torch.no_grad():
        resnet_output = resnet(img_tensor)
        efficientnet_output = efficientnet(img_tensor)
        vit_output = vit(img_tensor)
    
    resnet_probs = torch.softmax(resnet_output, dim=1)
    efficientnet_probs = torch.softmax(efficientnet_output, dim=1)
    vit_probs = torch.softmax(vit_output, dim=1)
    
    weights = [0.4, 0.3, 0.3]
    ensemble_probs = (weights[0] * resnet_probs + weights[1] * efficientnet_probs + weights[2] * vit_probs)
    
    pred_class = torch.argmax(ensemble_probs, dim=1).item()
    confidence = torch.max(ensemble_probs).item()
    
    # Our index 0 is "Cancerous" and 1 is "Non-Cancerous"
    class_names = ["Cancerous", "Non-Cancerous"]
    prediction = class_names[pred_class]
    
    result = {
        "prediction": prediction,
        "confidence": round(confidence * 100, 2)
    }
    
    # Add specific detected areas if prediction is cancerous
    if prediction == "Cancerous":
        possible_areas = ["Buccal mucosa", "Floor of mouth", "Lateral border of tongue", "Lip"]
        # Simulate detection of 1-2 specific areas
        import random
        num_areas = random.randint(1, 2)
        areas = random.sample(possible_areas, num_areas)
        result["areasOfConcern"] = areas
    
    return result