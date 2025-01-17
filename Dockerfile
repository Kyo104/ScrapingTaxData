FROM python:3

# Tạo thư mục ứng dụng
WORKDIR /app

# Cài đặt các công cụ cần thiết và Chrome
RUN apt-get update && apt-get install -y \
      wget \
      unzip \
      chromium \
      chromium-driver && \
      apt-get clean

# Copy file Python và các file cần thiết vào container
COPY crawl_hoadondientu.py /app/crawl_hoadondientu.py

# Cài đặt các gói thư viện từ requirements.txt
# Cài đặt các thư viện Python cần thiết
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt


