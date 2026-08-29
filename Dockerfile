FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV, DICOM, and Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || (COPY backend/requirements.txt ./backend_req.txt && pip install --no-cache-dir -r backend_req.txt)

COPY . .

EXPOSE 8000
EXPOSE 8501

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
