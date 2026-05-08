# --- STAGE 1: BASE (Production Dependencies) ---
FROM python:3.12-alpine AS base

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install ONLY production requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- STAGE 2: TESTER (Runs Unit Tests) ---
FROM base AS tester

# Install test-specific requirements
COPY requirements-test.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy all code including tests
COPY . .

# Run tests - the build will stop here if they fail
RUN pytest tests/


# --- STAGE 3: RUNTIME (Production Image) ---
FROM python:3.12-alpine AS runtime

WORKDIR /app

# Runtime libraries for Alpine
RUN apk add --no-cache libpq libffi

# Copy the venv from the BASE stage (does NOT include test tools)
COPY --from=base /opt/venv /opt/venv

# Explicitly copy ONLY application files
COPY main.py .
COPY schemas.py .
#COPY models.py .
COPY auth/ ./auth/
COPY db/ ./db/
COPY router/ ./router/

# Environment setup
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Non-root security
RUN adduser -D dcimuser
USER dcimuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]