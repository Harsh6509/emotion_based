FROM python:3.10-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy all files
COPY . .

# Install Python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Render port
ENV PORT=10000
EXPOSE 10000

# Start Flask
CMD ["python", "music.py"]
