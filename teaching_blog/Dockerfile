FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    langchain>=0.3.0 \
    langchain-core>=0.3.0 \
    pypdf>=4.0.0 \
    python-docx>=1.1.0 \
    flask>=3.0.0 \
    werkzeug>=3.0.0 \
    requests>=2.31.0 \
    python-multipart>=0.0.6 \
    pydantic>=2.0.0 \
    gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:create_app()"]