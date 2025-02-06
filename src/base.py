from abc import ABC, abstractmethod
import os
import requests
import json
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from google.oauth2 import service_account
from googleapiclient.discovery import build


class base_crawler(ABC):
    def __init__(self):
        # API key từ trang web autocaptcha để giải captcha
        self.api_key_autocaptcha = os.getenv('API_KEY_AUTOCAPTCHA')  # Dùng cho thuedientu, baohiemxahoi
        self.api_key_anticaptcha = os.getenv('API_KEY_ANTICAPTCHA')  # Dùng cho hoadondientu
        # PostgreSQL username
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.webhook_url = os.getenv('WEBHOOK_URL')

    def send_slack_notification(self, message, webhook_url):
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            "text": message  
        }
        try:  
            response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                    print("Thông báo đã được gửi thành công!")
            else:
                    print(f"Lỗi khi gửi thông báo: {response.status_code}, {response.text}")
        except:
            pass

    def initialize_driver(self, work_flow_str=''):
            """Khởi tạo trình duyệt Chrome."""
            self.chrome_options = Options()
            self.chrome_options.add_argument("--headless=new") # for Chrome >= 109
            self.chrome_options.add_argument("--disable-gpu") # Tắt GPU rendering
            self.chrome_options.add_argument("--no-sandbox")  # Bỏ qua chế độ sandbox
            self.chrome_options.add_argument("--disable-dev-shm-usage") 
            self.chrome_options.add_argument("--remote-debugging-port=9222")  
            self.chrome_options.add_argument("--disable-software-rasterizer")  
            self.chrome_options.add_argument("--force-device-scale-factor=1")  
            self.chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
            self.chrome_options.add_argument("--disable-extensions")  
            self.chrome_options.add_argument("--enable-javascript")
            # For HDDT
            self.chrome_options.add_argument("--ignore-certificate-errors")
            
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.maximize_window() 
            time.sleep(5)
            self.send_slack_notification(work_flow_str, self.webhook_url)           

            return self.driver
        
    # Khởi tạo dịch vụ Google Drive
    def initialize_drive_service(self):
        """Khởi tạo dịch vụ Google Drive bằng tài khoản dịch vụ."""
        self.gg_scopes = [os.getenv('SCOPES')]
        self.gg_service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
        
        try:
            if not self.gg_service_account_file or not os.path.exists(self.gg_service_account_file):
                raise FileNotFoundError(f"[ERROR] Service account file not found: {self.gg_service_account_file}")
            
            creds = service_account.Credentials.from_service_account_file(self.gg_service_account_file, scopes=self.gg_scopes)
            service = build('drive', 'v3', credentials=creds)
            print("[SUCCESS] Initialized Google Drive service.")
            return service
        except FileNotFoundError as e:
            print(e)
            return None
        except Exception as e:
            print(f"[ERROR] Failed to initialize Google Drive service: {e}")
            return None
    
    # Hàm tạo và kết nối đến database PostgreSQL
    def create_and_connect_to_database(self):
        """Tạo một database mới nếu chưa tồn tại và kết nối đến nó."""
        # Kết nối đến PostgreSQL
        self.engine = create_engine(f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}', isolation_level='AUTOCOMMIT')

        # Tạo database nếu chưa tồn tại
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_catalog.pg_database WHERE datname = :db_name"), {"db_name": self.db_name})
            exists = result.fetchone()
            if not exists:
                    conn.execute(text(f"CREATE DATABASE {self.db_name}"))
                    print(f"Database '{self.db_name}' đã được tạo.")
            else:
                    print(f"Database '{self.db_name}' đã tồn tại.")

        # Kết nối đến database vừa tạo
        self.engine = create_engine(f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}')
        print(f"Kết nối thành công đến database: {self.db_name}")
        return self.engine 
      
    # Class with abstractmethod of base class must be overrided aka re-implemented by child class
    @abstractmethod
    def parse_arguments(self):
        pass

    @abstractmethod
    def main_logic(self):
        pass