import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "models/phishing_model.joblib"

# ⚙️ Entrenar modelo (solo si no existe)
def train_model():
    texts = [
        "urgent verify your account",
        "your account has been suspended",
        "confirm your password now",
        "hello how are you",
        "meeting tomorrow at 10",
        "invoice attached"
    ]

    labels = [1, 1, 1, 0, 0, 0]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression()
    model.fit(X, labels)

    joblib.dump((vectorizer, model), MODEL_PATH)

    return vectorizer, model


# 🧠 Cargar modelo
if os.path.exists(MODEL_PATH):
    vectorizer, model = joblib.load(MODEL_PATH)
else:
    vectorizer, model = train_model()


# 🔮 Predicción
def predict_phishing(text: str) -> float:
    X = vectorizer.transform([text])
    prob = model.predict_proba(X)[0][1]
    return prob
