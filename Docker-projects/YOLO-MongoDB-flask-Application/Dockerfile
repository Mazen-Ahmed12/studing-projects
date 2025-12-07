FROM python:3.12-slim-bookworm AS builder

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2: Final runtime (super tiny)
FROM python:3.12-slim-bookworm

# Only OpenCV system deps (not the full libgl1-mesa-glx bloat)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy your code
COPY app.py .
COPY detection.py .
COPY templates ./templates


EXPOSE 5000
CMD ["python", "app.py", "--host=0.0.0.0"]