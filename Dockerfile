FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose port (Render/HuggingFace default routing)
EXPOSE 8501

# Run the startup script
CMD ["./start.sh"]
