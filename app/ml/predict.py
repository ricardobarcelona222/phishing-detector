import joblib
import os
import pandas as pd

from app.ml.feature_extractor import extract_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "app", "ml", "model.pkl")

model = joblib.load(MODEL_PATH)

def predict_url(url: str):
    features = extract_features(url)
    df = pd.DataFrame([features])

    prediction = model.predict(df)[0]

    return "phishing" if prediction == 1 else "legitimate"
