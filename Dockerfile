FROM python:3.12-slim

# Set environment variables for best practices
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY ./src src

# Change ownership to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Run the FastAPI application using the official CLI
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
