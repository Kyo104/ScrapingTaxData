# Use an official Ubuntu as a parent image
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    openjdk-8-jdk \
    libcairo2 \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the current working directory contents into the container at /app
COPY app /app/app
COPY src /app/src
COPY eSignerJava /app/eSignerJava
COPY requirements.txt /app

# Install Python dependencies
RUN python3.12 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Verify installations
RUN python3.12 --version
RUN java -version

# Set default commands
CMD ["bash"]
