from app.database import engine
from sqlalchemy import text

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0"))
    connection.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
    connection.execute(text("UPDATE users SET is_approved = 1"))
    connection.commit()

print("Columnas agregadas correctamente 🚀")
