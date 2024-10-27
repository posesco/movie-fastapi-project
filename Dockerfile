FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./src src
CMD ["fastapi", "run", "src/main.py"]
