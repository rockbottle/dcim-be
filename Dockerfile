# --- STAGE 1: BUILDER ---
FROM python:3.12-alpine AS builder

# Install build dependencies for C-based Python packages (e.g., psycopg2, SQLAlchemy)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

WORKDIR /app

# Create a virtual environment to keep dependencies isolated and easy to copy
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: RUNTIME ---
FROM python:3.12-alpine

WORKDIR /app

# Install runtime libraries only (no compilers needed here)
RUN apk add --no-cache libpq libffi

# Copy ONLY the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy your application code
COPY . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run the FastAPI application
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]