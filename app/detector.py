import re
from urllib.parse import urlparse
from app.ml_model import predict_phishing


SUSPICIOUS_KEYWORDS = [
    "urgente", "verifica", "bloqueada", "suspendida",
    "cuenta", "contraseña", "seguridad", "confirmar"
]

SUSPICIOUS_TLDS = [".xyz", ".top", ".tk", ".ru", ".cn"]

BRANDS = {
    "paypal": ["paypal.com"],
    "google": ["google.com"],
    "bbva": ["bbva.com"],
    "santander": ["santander.com"]
}


def extract_domains(text: str):
    urls = re.findall(r"https?://[^\s]+", text)
    domains = []
    for url in urls:
        parsed = urlparse(url)
        domains.append(parsed.netloc.lower())
    return domains


def analyze_text(text: str, sender: str = ""):
    score = 0
    reasons = []

    text_lower = text.lower()

    for word in SUSPICIOUS_KEYWORDS:
        if word in text_lower:
            score += 10
            reasons.append(f"Palabra sospechosa: '{word}'")

    domains = extract_domains(text)
    if domains:
        score += 15
        reasons.append("Contiene enlaces")

    for domain in domains:
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                score += 20
                reasons.append(f"Dominio sospechoso: {domain}")

    for brand, legit_domains in BRANDS.items():
        if brand in text_lower:
            for domain in domains:
                if not any(domain.endswith(ld) for ld in legit_domains):
                    score += 25
                    reasons.append(f"Posible suplantación de {brand.capitalize()}")

    if sender:
        sender_lower = sender.lower()
        for brand, legit_domains in BRANDS.items():
            if brand in sender_lower:
                if not any(sender_lower.endswith(ld) for ld in legit_domains):
                    score += 20
                    reasons.append("Remitente sospechoso")

    # 🤖 ML
    ml_probability = predict_phishing(text)
    ml_score = int(ml_probability * 100)

    if ml_score > 70:
        score += 20
        reasons.append(f"ML detecta phishing ({ml_score}%)")

    score = min(score, 100)

    risk_level = (
        "ALTO" if score >= 60 else
        "MEDIO" if score >= 30 else
        "BAJO"
    )

    return {
        "phishing": score >= 60,
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }
