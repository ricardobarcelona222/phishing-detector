from app.detector import analyze_text

def analyze_message(message: str):
    # reutilizamos tu detector actual
    result = analyze_text(message, sender="")

    return {
        "phishing": result["phishing"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "reasons": result["reasons"]
    }
