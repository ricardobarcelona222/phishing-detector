import pandas as pd
import torch
import random
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

# ==========================
# 0️⃣ Verificar GPU
# ==========================
print("GPU disponible:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Usando GPU:", torch.cuda.get_device_name(0))
else:
    print("⚠️ No se detectó GPU")

# ==========================
# 1️⃣ Cargar SMS Spam (inglés)
# ==========================
print("Cargando dataset SMS spam...")
sms_raw = load_dataset("sms_spam")["train"]

sms_texts = [str(row["sms"]) for row in sms_raw]
sms_labels = [int(row["label"]) for row in sms_raw]

# ==========================
# 2️⃣ Cargar phishing_emails.csv
# ==========================
print("Cargando dataset phishing emails...")
df = pd.read_csv("data/phishing_emails.csv")
df = df.dropna()

df = df.rename(columns={
    "Email Text": "text",
    "Email Type": "labels"
})

df["text"] = df["text"].astype(str)
df["labels"] = df["labels"].apply(
    lambda x: 1 if str(x).lower().strip() in ["phishing email", "phishing"] else 0
)

email_texts = df["text"].tolist()
email_labels = df["labels"].tolist()

# ==========================
# 🔥 3️⃣ DATASET ROBUSTO EN ESPAÑOL
# ==========================
print("Generando dataset EXTREMO en español...")

brands = ["BBVA", "Santander", "Banorte", "SAT", "Amazon", "Mercado Libre", "Netflix", "PayPal"]

templates = [
    "Su cuenta de {} ha sido suspendida. {}",
    "Tu cuenta de {} fue bloqueada. {}",
    "Hemos detectado actividad sospechosa en su cuenta {}. {}",
    "Se requiere verificación urgente para {}. {}",
    "Su paquete asociado a {} no pudo ser entregado. {}",
    "Pago rechazado en {}. {}",
    "Actualice su información en {} inmediatamente. {}",
    "Su acceso a {} será cancelado. {}"
]

actions_formal = [
    "Haga clic aquí para verificar su identidad.",
    "Confirme sus datos personales ahora.",
    "Ingrese su información en el siguiente enlace.",
    "Actualice su contraseña inmediatamente.",
    "Valide su cuenta para evitar el bloqueo.",
]

actions_informal = [
    "Haz clic aquí para validar tu cuenta.",
    "Confirma tus datos ahora mismo.",
    "Ingresa tu información en el enlace.",
    "Actualiza tu contraseña ya.",
    "Evita el bloqueo confirmando tus datos."
]

spanish_phishing = []

for brand in brands:
    for template in templates:
        for action in actions_formal + actions_informal:
            sentence = template.format(brand, action)
            spanish_phishing.append(sentence)

# Duplicar con ligeras variaciones
spanish_phishing = spanish_phishing + [
    s.replace("cuenta", "perfil") for s in spanish_phishing
]

spanish_labels_phishing = [1] * len(spanish_phishing)

# ==========================
# 🟢 Español legítimo
# ==========================
legit_sentences = [
    "Hola, ¿cómo estás?",
    "Nos vemos mañana en la reunión.",
    "Te envío el documento adjunto.",
    "Gracias por tu ayuda.",
    "La reunión será a las 3pm.",
    "Adjunto la información solicitada.",
    "Avísame cuando llegues.",
    "Fue un placer conocerte.",
    "Te confirmo que el pago fue realizado correctamente.",
    "La factura está disponible en el portal.",
    "Tu pedido llegará mañana.",
    "Gracias por tu compra en Amazon.",
    "Recibimos tu solicitud correctamente.",
    "Tu suscripción a Netflix sigue activa.",
]

# Duplicar normales
spanish_legit = legit_sentences * 10
spanish_labels_legit = [0] * len(spanish_legit)

# ==========================
# 4️⃣ Combinar todo
# ==========================
all_texts = sms_texts + email_texts + spanish_phishing + spanish_legit
all_labels = sms_labels + email_labels + spanish_labels_phishing + spanish_labels_legit

dataset = Dataset.from_dict({
    "text": all_texts,
    "labels": all_labels
})

# ==========================
# 5️⃣ Train / Test split
# ==========================
dataset = dataset.train_test_split(test_size=0.1)

train_dataset = dataset["train"]
eval_dataset = dataset["test"]

# ==========================
# 6️⃣ Tokenizer
# ==========================
model_name = "distilbert-base-multilingual-cased"

tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

train_dataset = train_dataset.map(tokenize, batched=True)
eval_dataset = eval_dataset.map(tokenize, batched=True)

train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
eval_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# ==========================
# 7️⃣ Modelo
# ==========================
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_steps=100,
    load_best_model_at_end=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

# ==========================
# 8️⃣ Entrenar
# ==========================
print("Entrenando modelo...")
trainer.train()

print("Guardando modelo...")
trainer.save_model("app/phishing_model")
tokenizer.save_pretrained("app/phishing_model")

print("Modelo EXTREMO entrenado correctamente ✅")
