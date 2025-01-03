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
COPY test-captcha-hoadon.py /app/test-captcha-hoadon.py

# Cài đặt các gói thư viện từ requirements.txt
# Cài đặt các thư viện Python cần thiết
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Chạy chương trình khi container khởi động
CMD ["python", "test-captcha-hoadon.py"]
