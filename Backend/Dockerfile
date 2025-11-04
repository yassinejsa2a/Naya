FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=run.py \
    UPLOAD_FOLDER=/data/uploads

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN mkdir -p "${UPLOAD_FOLDER}"

VOLUME ["/data/uploads"]

EXPOSE 8000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000"]
