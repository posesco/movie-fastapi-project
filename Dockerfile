FROM python:3.10-alpine
WORKDIR /src
COPY ./src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src .
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
