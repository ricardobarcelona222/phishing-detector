import os
import joblib

# ======================
# RUTA MODELO
# ======================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "app", "ml", "phishing_model.pkl")

print("Cargando modelo...")

model = joblib.load(MODEL_PATH)

print("Modelo cargado correctamente ✔")


# ======================
# PRUEBAS
# ======================

tests = [
    "https://paypal.com/login",
    "http://secure-paypal-login.verify-account.ru",
    "https://google.com",
    "http://update-bank-account-security-alert.net"
]

for t in tests:
    prediction = model.predict([t])[0]
    print(f"\nURL: {t}")
    print("Resultado:", prediction)
