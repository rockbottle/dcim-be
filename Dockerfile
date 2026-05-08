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


# --- STAGE 2: TESTER (Prepared Environment for Tests) ---
FROM base AS tester

# Install test-specific requirements
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy all code including tests
COPY . .

# NOTE: Removed 'RUN pytest tests/' from here. 
# Unit tests can stay if they don't need a DB, 
# but E2E tests must be triggered by GitHub Actions.

# --- STAGE 3: RUNTIME (Production Image) ---
FROM python:3.12-alpine AS runtime

WORKDIR /app

# Runtime libraries for Alpine (libpq is essential for postgres)
RUN apk add --no-cache libpq libffi

# Copy the venv from the BASE stage
COPY --from=base /opt/venv /opt/venv

# Explicitly copy application files
COPY main.py .
COPY schemas.py .
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