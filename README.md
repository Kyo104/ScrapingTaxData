# Crawling Data Project

## Introduction
This project is designed to automate the login process for the websites **hoadondientu**, **thuedientu**, and **baohiemxahoi** to collect data. The repository contains scripts and tools for these tasks, each tailored to a specific website. This documentation consolidates the instructions for all branches into one unified guide.

## Prerequisites
1. **Python Version**: The scripts require Python 3.12.4. Ensure this version is installed on your system.
2. **Library Installation**: Install the required libraries from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
3. **MSYS2 Installation**: For the `hoadondientu` script, download and install MSYS2:
   [Download MSYS2 Installer](https://github.com/msys2/msys2-installer/releases/download/2024-12-08/msys2-x86_64-20241208.exe)

4. **GTK3 Runtime**: Open an MSYS2 shell and run the following commands to install the GTK3 runtime:
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-gtk3
   gcc --version
   ```

## Configuration
Before running the scripts, replace the placeholder values in the code with your actual credentials and API keys.

### API Key
Each script requires an API key from an anti-captcha service:
- For **hoadondientu** and **baohiemxahoi**: Use [anticaptcha.top](https://anticaptcha.top/documentapi).
- For **thuedientu**: Use [autocaptcha.pro](https://autocaptcha.pro/quan-ly.html).

Replace the placeholder in the script with your generated API key:
```python
API_KEY = "#"  # Replace with your actual API key
```

### User Credentials
Update the username and password in the script with your account credentials for the respective website:
```python
username = "#"  # Replace with your username
password = "#"  # Replace with your password
```

## Usage
Follow the steps below to run the data collection scripts for each website:

### Hoadondientu
1. Install the required libraries and configure the API key, username, and password as described above.
2. Run the script for **hoadondientu**:
   ```bash
   python hoadondientu.py
   ```
3. More information in documents (TaiLieuHuongDan)
### Baohiemxahoi
1. Install the required libraries and configure the API key, username, and password as described above.
2. Run the script for **baohiemxahoi**:
   ```bash
   python baohiemxahoi.py
   ```
3. More information in documents (TaiLieuHuongDan)
### Thuedientu
1. Install the required libraries and configure the API key, username, and password as described above.
2. Run the script for **thuedientu**:
   ```bash
   python thuedientu.py
   ```
3. More information in documents (TaiLieuHuongDan)
## Contribution
We welcome contributions to this project. If you would like to contribute, please:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of the changes you’ve made.

## Authors
- **Trần Ngọc Phước**
- **Đỗ Lý Anh Kiệt**
- **Nguyễn Tiến Phúc**
- **Đỗ Hoài Thanh Quyên**

## License
Thank you for your interest and use of our project! 🔥 🔥 🔥

