# Use an official Ubuntu as a parent image
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/app/venv/bin:$PATH"

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

# Install Chrome & ChromeDriver
RUN apt-get update && apt-get install -y wget curl unzip && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver compatible with Chrome 133
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.53/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Set the working directory
WORKDIR /app

# Copy the current working directory contents into the container at /app
COPY app /app/app
COPY src /app/src
COPY eSignerJava /app/eSignerJava
COPY requirements.txt /app
COPY api-google.json /app/

# Install Python dependencies inside venv
RUN python3.12 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

# Verify installations
RUN python3.12 --version
RUN java -version
RUN google-chrome --version
RUN chromedriver --version

# Set default command
CMD ["bash"]
