from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "Ricardo787848/phishing-detector-transformer"

device = torch.device("cpu")  # Render no usa GPU

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

model.to(device)
model.eval()
print("MODELO CARGADO DESDE HUGGINGFACE")


def predict_phishing(text: str):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)

    phishing_prob = probs[0][1].item()

    return phishing_prob
