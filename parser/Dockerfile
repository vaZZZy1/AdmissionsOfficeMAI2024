# Dockerfile для parser
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ../requirements.txt
RUN pip install -r ../requirements.txt

COPY . .

CMD ["python", "parser/main.py"]
