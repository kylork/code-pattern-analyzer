FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy the code
COPY . .

# Set the entrypoint
ENTRYPOINT ["code-pattern"]

# Default command
CMD ["--help"]