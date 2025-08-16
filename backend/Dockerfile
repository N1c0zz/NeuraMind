FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e installa requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice
COPY . .

# Esponi la porta
EXPOSE 8000

# Comando di avvio
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]