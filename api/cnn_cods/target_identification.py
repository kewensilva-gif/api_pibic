import torch
from torchvision import transforms
from PIL import Image
import torch.nn.functional as F
from cnn_cods.cnn import CNN
import os
num_classes = 5
device = 'cuda' if torch.cuda.is_available() else 'cpu'

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.8128030896186829, 0.5365262627601624, 0.5638176798820496], std=[0.1239788755774498, 0.2561289966106415, 0.2529338300228119])
])

model = CNN(num_classes).to(device)
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "modelo.pth")
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

class_names = ["lampada", "colcheias", "floco", "helice", "tv"]

def transform_image(image):
    global device
    image = Image.open(image).convert("RGB")
    return transform(image).unsqueeze(0).to(device)

def prediction(image):
    with torch.no_grad():
        output = model(image)
        probabilities = F.softmax(output, dim=1)  # Converte logits em probabilidades
        confidence, predicted = torch.max(probabilities, 1)  # Pega a maior probabilidade

    return predicted, confidence.item()

def test_images_from_coordenadas(coordenadas):
    for coordenada in coordenadas:
        coordenada["predicted"] = test_image(coordenada['recorte'])

def test_image(recorte):
    image = transform_image(recorte)
    predicted, confidence = prediction(image)
    predicted_class = class_names[predicted.item()] if predicted.item() < len(class_names) else str(predicted.item())
    print(f"Predição: {predicted_class} ({(confidence*100):.2f}% de confiança)")
    if(confidence > 0.85):
        return predicted_class
    else:
        return None
            