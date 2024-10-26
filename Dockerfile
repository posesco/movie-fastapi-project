FROM python:3.10-alpine
WORKDIR /app/public
COPY ./src .
COPY .env /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
