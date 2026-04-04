# =====================================
# LatticeReAct Multi-Agent Framework
# =====================================

# Multi-stage build for efficiency
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --fix-missing \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with explicit versions for stability
RUN pip install --user --no-cache-dir --upgrade pip \
    && pip install --user --no-cache-dir \
        python-dotenv \
        langchain \
        langchain-community \
        langchain-ollama \
        requests \
        chromadb \
        ollama \
    && pip install --user --no-cache-dir -r requirements.txt

# =====================================
# Production stage
# =====================================
FROM python:3.9-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --fix-missing \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Create necessary directories and fix permissions
RUN mkdir -p /app/logs /app/cache \
    && chown -R appuser:appuser /app \
    && chown -R appuser:appuser /home/appuser/.local

# Switch to non-root user
USER appuser

# Add local packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "from config import MP_API_KEY; print('Health check passed')" || exit 1

# Expose port for future web interface
EXPOSE 8000

# Default command (show help for now, change to interactive later)
CMD ["python", "-c", "print('LatticeReAct Docker Container Ready!'); import sys; sys.exit(0)"]