import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "phishing_urls.csv")

print("Cargando dataset desde:", DATA_PATH)

df = pd.read_csv(DATA_PATH)

# Convertir status a número
df["status"] = df["status"].map({"legitimate": 0, "phishing": 1})

# Seleccionar features que SÍ tenemos en extractor
FEATURES = [
    "length_url",
    "length_hostname",
    "nb_dots",
    "nb_hyphens",
    "nb_at",
    "nb_slash",
    "nb_qm",
    "nb_and",
    "nb_subdomains",
    "https_token",
    "ratio_digits_url"
]

X = df[FEATURES]
y = df["status"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

MODEL_PATH = os.path.join(BASE_DIR, "app", "ml", "model.pkl")
joblib.dump(model, MODEL_PATH)

print("Modelo guardado en:", MODEL_PATH)


from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_path = "./phishing_model"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

def predict_phishing(text):

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)

    phishing_prob = probs[0][1].item()

    return phishing_prob

