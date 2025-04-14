# ScrapingTaxData Project

## Introduction
An automated data collection system for Vietnamese tax and invoice services, focusing on streamlined access to hoadondientu and thuedientu websites.

## Features
- Automated login process
- Captcha solving integration
- Data extraction and processing
- Multi-site support (hoadondientu, thuedientu)
- Python-based automation

## Prerequisites
- Python 3.12.4
- Required Python packages (see `requirements.txt`)
- Valid API keys for captcha services
- Access credentials for target systems

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### For Hoadondientu Website
1. Get your API key from [anticaptcha.top](https://anticaptcha.top/documentapi)
2. Configure your credentials in the environment file:
```python
API_KEY = "your_anticaptcha_api_key"
username = "your_username"
password = "your_password"
```

### For Thuedientu Website
1. Get your API key from [autocaptcha.pro](https://autocaptcha.pro/quan-ly.html)
2. Configure your credentials in the environment file:
```python
API_KEY = "your_autocaptcha_api_key"
username = "your_username"
password = "your_password"
```

## Running the Application

### 1. Starting with Docker

1. Ensure Docker and Docker Compose are installed
2. Build and run containers:
```bash
docker-compose up --build -d
```
3. Verify containers are running:
```bash
docker ps
```

### 2. Jenkins Configuration and Execution

1. Access Jenkins through web browser:
   - URL: http://localhost:8080

2. Run crawler through Jenkins:
   - Login to Jenkins
   - Select "crawler" job
   - Click "Build with Parameters"
   - Fill in parameters:
     - **company**: Company name to crawl (e.g., "Company A1")
     - **type**: Data type to crawl ("hoadon" or "thue")
     - **startDate**: Start date (format: DD/MM/YYYY)
     - **endDate**: End date (format: DD/MM/YYYY)
   - Click "Build" to start crawling

### 3. Monitoring

- View crawler logs in Jenkins:
  - Go to "crawler" job
  - Select latest build
  - Click "Console Output"

- View Docker logs:
```bash
docker logs -f scraping-tax-data
```

### 4. System Shutdown

To stop and remove containers:
```bash
docker-compose down
```

## Project Structure
```
ScrapingTaxData/
├── src/                # Source files
├── app/                # Application core
├── init/              # Database initialization
└── requirements.txt   # Project dependencies
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Team and Roles

### Development Team
- **Tran Ngoc Phuoc** 
- **Do Ly Anh Kiet** 

### Database Design Team
- **Nguyen Tien Phuc** 
- **Do Hoai Thanh Quyen** 

## License
This project is proprietary. All rights reserved.

## Security Notes
- Never commit API keys or credentials to version control
- Use environment variables for sensitive data
- Regularly update dependencies for security patches

---
🔥 Thank you for using our project! 🔥
