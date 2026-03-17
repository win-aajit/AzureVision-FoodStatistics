import requests
import torch
import cv2
import numpy as np
from torchvision.transforms import Compose, Resize, ToTensor, Normalize

#Load MiDaS model
model_type = "DPT_Large"  
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.eval()

#Load transforms for the model
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.dpt_transform



endpoint = "https://end-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/429df433-a5d2-4d03-b22e-d9054e79ced5/classify/iterations/MultiIteration1/image"
prediction_key = "key"
image_path = "meal.jpg"

headers = {
    "Prediction-Key": prediction_key,
    "Content-Type": "application/octet-stream"
}

with open(image_path, "rb") as f:
    image_data = f.read()

response = requests.post(endpoint, headers=headers, data=image_data)

#Check results
if response.status_code == 200:
    predictions = response.json()["predictions"]
    #print(predictions)
    i = 0
    foodArr = [None] * len(predictions)
    for pred in predictions:
        foodArr[i] = pred['tagName']
        print(f"{pred['tagName']} : {pred['probability']:.2f}")
        i += 1
else:
    print("Error:", response.status_code, response.text)



API_KEY = "key"
search_query = foodArr[0]

#Search foods
search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}&query={search_query}"
search_resp = requests.get(search_url).json()
foods = search_resp.get("foods", [])

if not foods:
    print("No foods found")
else:
    #Use the first id result
    fdc_id = foods[0]["fdcId"]

    #Get nutrition details
    details_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={API_KEY}"
    details_resp = requests.get(details_url).json()
    print(details_resp)
    #Print nutrient values from dict
    nutrients = details_resp.get("labelNutrients", {})
    for nutrient, info in nutrients.items():
        print(f"{nutrient}: {info['value']}")