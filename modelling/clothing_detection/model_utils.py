from transformers import CLIPProcessor, CLIPModel
from torchvision import models, transforms
from PIL import Image
import torch

# ============================
# CLIP Model (Open AI) - Базовая версия
# ============================
clip_base_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_base_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def classify_image_clip_base(image_path):
    image = Image.open(image_path)
    inputs = clip_base_processor(text=['Is clothes', 'Is not clothes'], images=image, return_tensors="pt", padding=True)
    outputs = clip_base_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    return probs[0][0].item()  # Вероятность наличия одежды

# ============================
# CLIP Model (Open AI) - Большая версия
# ============================
clip_large_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
clip_large_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

def classify_image_clip_large(image_path):
    image = Image.open(image_path)
    inputs = clip_large_processor(text=['Is clothes', 'Is not clothes'], images=image, return_tensors="pt", padding=True)
    outputs = clip_large_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    return probs[0][0].item()  # Вероятность наличия одежды

# # ============================
# # ResNet50 Model - Pretrained on ImageNet
# # ============================
# resnet_model = models.resnet50(pretrained=True)
# resnet_model.eval()

# # Преобразование для входных изображений для моделей на базе ImageNet
# imagenet_transform = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
# ])

# def classify_image_resnet(image_path):
#     image = Image.open(image_path)
#     image = imagenet_transform(image).unsqueeze(0)
    
#     with torch.no_grad():
#         outputs = resnet_model(image)
#         probs = torch.nn.functional.softmax(outputs, dim=1)
#         return probs[0][0].item()  # Вероятность наличия одежды (условно)

# # ============================
# # EfficientNet-B0 Model - Pretrained on ImageNet
# # ============================
# efficientnet_model = models.efficientnet_b0(pretrained=True)
# efficientnet_model.eval()

# def classify_image_efficientnet(image_path):
#     image = Image.open(image_path)
#     image = imagenet_transform(image).unsqueeze(0)
    
#     with torch.no_grad():
#         outputs = efficientnet_model(image)
#         probs = torch.nn.functional.softmax(outputs, dim=1)
#         return probs[0][0].item()  # Вероятность наличия одежды (условно)

# # ============================
# # Vision Transformer (ViT) - Pretrained on ImageNet
# # ============================
# vit_base_model = CLIPModel.from_pretrained("google/vit-base-patch16-224")
# vit_base_processor = CLIPProcessor.from_pretrained("google/vit-base-patch16-224")

# def classify_image_vit(image_path):
#     image = Image.open(image_path)
#     inputs = vit_base_processor(images=image, return_tensors="pt")
#     outputs = vit_base_model(**inputs)
#     logits_per_image = outputs.logits_per_image
#     probs = logits_per_image.softmax(dim=1)
#     return probs[0][0].item()  # Вероятность наличия одежды

# # ============================
# # Vision Transformer (ViT) - Pretrained on ImageNet
# # ============================
# vit_huge_model = CLIPModel.from_pretrained("google/vit-huge-patch14-224")
# vit_huge_processor = CLIPProcessor.from_pretrained("google/vit-huge-patch14-224")

# def classify_image_vit(image_path):
#     image = Image.open(image_path)
#     inputs = vit_huge_processor(images=image, return_tensors="pt")
#     outputs = vit_huge_model(**inputs)
#     logits_per_image = outputs.logits_per_image
#     probs = logits_per_image.softmax(dim=1)
#     return probs[0][0].item()  # Вероятность наличия одежды

