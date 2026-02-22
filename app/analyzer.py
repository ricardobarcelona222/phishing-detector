import re
from app.ml.predict import predict_url


# ===============================
# Detectar URLs dentro del texto
# ===============================
def extract_urls(text):
    url_pattern = r"(https?://[^\s]+)"
    return re.findall(url_pattern, text)


# ===============================
# Analizar mensaje completo
# ===============================
def analyze_message(text):

    risk_score = 0
    reasons = []

    text_lower = text.lower()

    # ---------------------------
    # REGLAS BÁSICAS
    # ---------------------------
    suspicious_words = [
        "urgent",
        "verify",
        "password",
        "bank",
        "click",
        "account",
        "suspend",
        "confirm"
    ]

    for word in suspicious_words:
        if word in text_lower:
            risk_score += 1
            reasons.append(f"Palabra sospechosa: {word}")

    # ---------------------------
    # DETECTAR URLS
    # ---------------------------
    urls = extract_urls(text)

    ml_results = []

    for url in urls:

        prediction = predict_url(url)

        ml_results.append({
            "url": url,
            "prediction": prediction
        })

        if prediction == "phishing":
            risk_score += 2
            reasons.append(f"URL phishing detectada: {url}")

    # ---------------------------
    # CLASIFICAR RIESGO
    # ---------------------------
    if risk_score >= 4:
        risk_level = "HIGH"
        phishing = True
    elif risk_score >= 2:
        risk_level = "MEDIUM"
        phishing = True
    else:
        risk_level = "LOW"
        phishing = False

    return {
        "phishing": phishing,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "urls_analyzed": ml_results
    }
