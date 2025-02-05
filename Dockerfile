# Use the official Python image
FROM python:3.12

# Install system dependencies for sound
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libasound2 \
    libasound2-plugins \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (if needed)
EXPOSE 5000

# Run the voice chat server
CMD ["python", "voice_chat.py"]
