FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . .

# Esponi la porta
EXPOSE 8000

# Usa shell form per espandere le variabili d'ambiente
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}