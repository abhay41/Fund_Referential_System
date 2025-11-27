# Stage 1: Build Stage (for dependencies and environment setup)
FROM python:3.11-slim as builder

# Install netcat (nc) for the wait-for-neo4j script (required for readiness check)
# FIX: Install netcat-openbsd, which provides the 'nc' command, and clean up apt cache.
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Set environment variables for the builder stage
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Create a non-root user (used to set permissions for the copy)
RUN adduser --disabled-password --gecos '' appuser
WORKDIR ${APP_HOME}

# Copy requirements file and install dependencies
COPY requirements.txt .
# Install dependencies, ensuring the latest pip and wheel are used
RUN pip install --upgrade pip setuptools wheel
# Use the updated requirements.txt with pinned versions
RUN pip install --no-cache-dir -r requirements.txt

# --- FIX 1: EXPLICITLY COPY SCRIPT AND SET PERMISSIONS ---
# This ensures the script is copied successfully and permission is set early.
COPY wait-for-neo4j.sh .
RUN chmod +x wait-for-neo4j.sh

# Copy ALL remaining application code.
COPY . ${APP_HOME}


# Set ownership for the copied files in the builder stage
RUN chown -R appuser:appuser ${APP_HOME}


# Stage 2: Final Production Image
FROM python:3.11-slim

# Install netcat (nc) in the final image too (required for running the script)
# FIX: Install netcat-openbsd, which provides the 'nc' command, and clean up apt cache.
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# FIX: Create the 'appuser' in this stage (required before switching USER)
RUN adduser --disabled-password --gecos '' appuser

# Set environment variables for the runtime stage
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
ENV PORT 8000

# Create application directories (if needed)
RUN mkdir -p ${APP_HOME}/app/database \
    && mkdir -p ${APP_HOME}/app/models \
    && mkdir -p ${APP_HOME}/app/api/routes \
    && mkdir -p ${APP_HOME}/services

# Copy the application code and installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder ${APP_HOME} ${APP_HOME}

# Switch to the non-root user for security
USER appuser

# Set working directory
WORKDIR ${APP_HOME}

EXPOSE 8000

# --- FIX 2: CORRECT CMD SYNTAX FOR SHELL CHAINING ---
# Use /bin/bash -c to correctly execute the sequential flow:
# 1. Wait for Neo4j.
# 2. Run data ingestion.
# 3. Start the Uvicorn API server.
CMD ["/bin/bash", "-c", "/app/wait-for-neo4j.sh neo4j 7687 && python ingest_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
