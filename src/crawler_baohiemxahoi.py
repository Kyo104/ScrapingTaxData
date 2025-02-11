from .base import base_crawler
import datetime
import glob
import psycopg2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.chrome.options import Options
from openpyxl import load_workbook
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import os
import requests
from PIL import Image
from io import BytesIO
import base64
import pdfplumber
from sqlalchemy import DateTime, ForeignKey, MetaData, String, create_engine, Column, Table, Integer, inspect, Boolean
from sqlalchemy.sql import text
import argparse
import requests
import json
from datetime import datetime


class crawler_baohiemxahoi(base_crawler):
    def __init__(self):
        # Use init from base class
        super().__init__()

    # Overrides base class method
    def parse_arguments(self):
        current_date = datetime.now()

        self.parser = argparse.ArgumentParser(description="BHXH Data Crawler")
        
        self.parser.add_argument("--month", default=str(current_date.month), required=False, help="Tháng cần crawl (1-12)")
        self.parser.add_argument("--year", type=str, required=False, default=str(current_date.year), help="Năm cần tra cứu (1990-hiện tại)")
        self.parser.add_argument(
            "--months-ago",
            type=int,
            default=0,
            required=False,
            help="Số tháng cần quay lại từ tháng hiện tại. "
            "0: Tháng hiện tại, "
            "1: Lùi về 1 tháng",
        )

        self.parser.add_argument(
            "--crawl-months",
            type=int,
            default=1,
            required=False,
            help="Số lượng tháng muốn crawl. Mặc định: 1 tháng",
        )
        return self.parser.parse_args()

    # Đăng nhập vào website https://dichvucong.baohiemxahoi.gov.vn/#/index
    # 1. Nhập username và password vào trang web 'baohiemxahoi'
    def login_to_baohiemxahoi(self, username, password, company):
        """Đăng nhập vào trang web 'baohiemxahoi'."""
        url = "https://dichvucong.baohiemxahoi.gov.vn/#/index"
        self.driver.get(url)
        time.sleep(5)

        # Kiểm tra và nhấn nút Thoát trong dropdown menu tài khoản, nếu có
        try:
            # Tìm nút dropdown menu tài khoản
            account_menu_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='accountMenuBtn']"))
            )
            actions = ActionChains(self.driver)
            actions.move_to_element(account_menu_button).perform()
            time.sleep(2)  # Đợi dropdown menu xuất hiện

            # Tìm và nhấn nút Thoát trong menu dropdown
            logout_button = self.driver.find_element(By.XPATH,"//*[@id='header']/div[1]/div/div/div[2]/div/div/div[2]/div/button")
            logout_button.click()
            print("- Finish: Nhấn nút Thoát thành công.")
        except (TimeoutException, NoSuchElementException):
            print("[WARNING] Không tìm thấy nút Thoát hoặc menu tài khoản không khả dụng, bỏ qua...")

        # Nhấn nút Đăng nhập
        try:
            print(f"- Đang đăng nhập cho công ty: {company}")
            self.send_slack_notification(f"[INFO] Chương trình đang login vào công ty: {company}",self.webhook_url_bhxh)
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), ' Đăng nhập ')]"))
            )
            login_button.click()
            print("- Finish: Đăng nhập vào trang bhxh.")
            time.sleep(3)
        except TimeoutException:
            print("[ERROR] Nút Đăng nhập không hiển thị hoặc không thể nhấn.")

        # Nhấn nút Tổ chức
        to_chuc_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Tổ chức')]")
        to_chuc_button.click()
        time.sleep(3)
        print("- Finish click to to_chuc")

        # Nhập tên đăng nhập
        username_field = self.driver.find_element(By.XPATH, '//input[@placeholder="Mã số thuế"]')
        username_field.send_keys(username)
        print("- Finish keying in username_field")
        time.sleep(3)

        # Nhập mật khẩu
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Mật khẩu"]'))
        )
        self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",password_field)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",password_field)

        # Kiểm tra giá trị sau khi nhập
        entered_password = password_field.get_attribute("value")
        print(f"[DEBUG] Password entered: {entered_password}")
        print("- Finish keying in password_field")
        time.sleep(3)

    # 1.1 Tải ảnh CAPTCHA về máy
    def save_captcha_image(self, driver):
        """Tải ảnh CAPTCHA về máy."""
        try:
            captcha_element = driver.find_element(By.XPATH, '//img[@alt="captcha"]')

            # Lấy giá trị của thuộc tính src chứa ảnh CAPTCHA (dạng base64)
            captcha_src = captcha_element.get_attribute("src")

            # Kiểm tra nếu src chứa dữ liệu base64 (chắc chắn dữ liệu ảnh được mã hóa trong src)
            if captcha_src.startswith("data:image/png;base64,"):
                # Loại bỏ phần đầu của chuỗi base64 (đến "base64,"), chỉ lấy phần thực tế của dữ liệu ảnh
                base64_data = captcha_src.split("base64,")[1]

                # Giải mã base64 để lấy dữ liệu ảnh
                img_data = base64.b64decode(base64_data)

                # Tạo ảnh từ dữ liệu byte
                image = Image.open(BytesIO(img_data))

                # Đường dẫn file để lưu ảnh
                file_path = "captcha_image.png"

                # Lưu ảnh dưới dạng file .png
                image.save(file_path)
                print("[INFO] CAPTCHA đã được lưu tại captcha_image.png")
            else:
                print("[ERROR] Không tìm thấy dữ liệu base64 trong src của ảnh CAPTCHA.")
                self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed",self.webhook_url_bhxh)
        except Exception as e:
            print(f"[ERROR] Lỗi khi lưu ảnh CAPTCHA: {e}")
            self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed", self.webhook_url_bhxh)

    # 1.2 Gửi ảnh lên autocaptcha để giải mã
    def solve_captcha(self, image_base64):
        """Gửi ảnh base64 lên autocaptcha và nhận mã CAPTCHA."""
        url = "https://autocaptcha.pro/api/captcha"
        payload = {
            "apikey": self.api_key_autocaptcha,
            "img": image_base64,
            "type": 14  # Loại captcha, có thể cần thay đổi nếu không đúng
        }
        headers = {"Content-Type": "application/json"}

        try:
            # Gửi POST request
            response = requests.post(url, json=payload, headers=headers)

            # Kiểm tra nếu có lỗi trong phản hồi HTTP
            if response.status_code != 200:
                print(f"[ERROR] Error with request: {response.status_code}")
                print(f"[DEBUG] Response Text: {response.text}")
                return None

            # Phân tích phản hồi JSON
            response_data = response.json()

            # Kiểm tra xem API trả về thành công
            if response_data.get("success") and "captcha" in response_data:
                print(f"Mã captcha đã giải: {response_data['captcha']}")
                return response_data["captcha"]
            else:
                print(f"[ERROR] API response indicates failure: {response_data}")
                self.send_slack_notification(f"[ERROR] Workflow crawling data baohiemxahoi failed {response_data}",self.webhook_url_bhxh)
                return None
        except Exception as e:
            print(f"[ERROR] Lỗi khi gửi yêu cầu giải CAPTCHA: {e}")
            self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed", self.webhook_url_bhxh)
            return None

    # Xử lý ảnh CAPTCHA và giải mã
    def solve_captcha_from_file(self, file_path):
        """Đọc file CAPTCHA và gửi lên AntiCaptcha để giải mã."""
        try:
            # Đọc file captcha
            with open(file_path, "rb") as file:
                img = Image.open(file)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Gửi ảnh base64 lên AntiCaptcha để giải mã
            captcha_text = self.solve_captcha(image_base64)

            # Chỉ trả về kết quả
            return captcha_text
        except Exception as e:
            print(f"[ERROR] Lỗi khi xử lý ảnh CAPTCHA: {e}")
            self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed", self.webhook_url_bhxh)
            return None

    # 1.3 Nhập mã CAPTCHA tự động
    def enter_verification_code(self, driver, captcha_image_path):
        """Giải mã CAPTCHA từ file và tự động nhập vào trường xác nhận."""
        try:
            # Giải mã CAPTCHA chỉ một lần
            captcha_code = self.solve_captcha_from_file(captcha_image_path)
            if not captcha_code:
                print("[ERROR] Không thể giải mã CAPTCHA.")
                return False

            # Tìm trường nhập CAPTCHA
            verification_code_field = driver.find_element(By.XPATH, '//input[@placeholder="Nhập mã kiểm tra"]')

            # Nhập mã CAPTCHA vào trường
            verification_code_field.clear()
            verification_code_field.send_keys(captcha_code)
            time.sleep(2)

            # Log giá trị sau khi nhập để kiểm tra
            captcha_value = verification_code_field.get_attribute("value")
            print(f"[INFO] CAPTCHA đã nhập: {captcha_value}")

            return True
        except Exception as e:
            print(f"[ERROR] Lỗi khi nhập mã CAPTCHA: {e}")
            return False

    # Nhập lại các trường thông tin khi mã captcha giải sai
    def retry_input(self, username, password):
        # Nhấn nút Tổ chức
        to_chuc_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Tổ chức')]")
        to_chuc_button.click()
        time.sleep(5)
        print("- Finish Task 2: click to to_chuc")

        # Nhập tên đăng nhập ma so thue
        username_field = self.driver.find_element(By.XPATH, '//input[@placeholder="Mã số thuế"]')
        username_field.clear()
        username_field.send_keys(username)
        print("- Finish keying in username_field")
        time.sleep(3)

        # Nhập mật khẩu
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Mật khẩu"]'))
        )
        # password_field.send_keys(password)
        self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",password_field)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",password_field)

        # Kiểm tra giá trị sau khi nhập
        entered_password = password_field.get_attribute("value")
        print(f"[DEBUG] Password entered: {entered_password}")
        print("- Finish keying in password_field")
        time.sleep(3)

    # 1.4 Nhấn nút đăng nhập sau cùng hoàn tất việc login vào trang web nếu login failed thì login lại
    def submit_form(self, driver, username, password, captcha_image_path):
        """Nhấn nút để hoàn tất đăng nhập và kiểm tra kết quả đăng nhập."""
        try:
            attempt = 0  # Biến theo dõi số lần thử đăng nhập
            # Sử dụng vòng lặp để thử lại nếu đăng nhập thất bại
            while True:
                attempt += 1  # Tăng số lần thử đăng nhập

                # Xây dựng XPath cho nút đăng nhập tùy thuộc vào số lần thử
                submit_button_xpath = f'//*[@id="mat-dialog-{attempt - 1}"]/app-dialog-login/form/div/div[2]/button[2]/span'

                try:
                    submit_button = driver.find_element(By.XPATH, submit_button_xpath)
                    submit_button.click()
                    print(f"- Finish submitting the form (attempt {attempt})")
                    self.send_slack_notification(f"[INFO] Chương trình đang thực hiên login lần {attempt}",self.webhook_url_bhxh)
                except NoSuchElementException:
                    print(f"[ERROR] Không tìm thấy nút đăng nhập cho attempt {attempt}. Đang thử lại...")
                    self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed",self.webhook_url_bhxh)
                    # Kiểm tra nếu đăng nhập thành công (dựa trên sự xuất hiện của thẻ span với class idAccount)
                try:
                    # Kiểm tra sự xuất hiện của thẻ span có class 'idAccount'
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "idAccount"))
                    )
                    print("[INFO] Đăng nhập thành công!")
                    self.send_slack_notification("[SUCCESS] Chương trình đã login thành công vào trang BHXH",self.webhook_url_bhxh)
                    break  # Đăng nhập thành công, thoát khỏi vòng lặp
                except TimeoutException:
                    print(f"[DEBUG] Không thấy thẻ idAccount ở attempt {attempt}. Đang thử lại...")

                    # Đăng nhập không thành công, nhập lại thông tin
                    print("[ERROR] Đăng nhập thất bại. Đang thử lại...")
                    self.send_slack_notification(f"[ERROR] Login thất bại, thực hiện retry lần {attempt}",self.webhook_url_bhxh)
                    # Nhập lại các trường thông tin
                    self.retry_input(username, password)

                    # Lưu và giải mã CAPTCHA mới
                    self.save_captcha_image(driver)
                    
                    self.enter_verification_code(driver, captcha_image_path)  # Nhập mã CAPTCHA tự động
        except Exception as e:
            print(f"Đã xảy ra lỗi khi nhấn nút submit: {e}")
            self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed", self.webhook_url_bhxh)

    def get_unique_filename(self, base_filename):
        """
        Tạo tên file duy nhất nếu file đã tồn tại, bằng cách thêm số thứ tự theo định dạng (1), (2),...
        """
        if not os.path.exists(base_filename):
            return base_filename

        base, ext = os.path.splitext(base_filename)
        counter = 1
        new_filename = f"{base} ({counter}){ext}"

        while os.path.exists(new_filename):
            counter += 1
            new_filename = f"{base} ({counter}){ext}"

        return new_filename

    def download_blob_pdf(self, driver, save_path):
        try:
            print("[INFO] Đang trích xuất nội dung từ blob URL qua JavaScript...")
            pdf_data = driver.execute_script("""
                    const blobUrl = arguments[0];
                    return new Promise((resolve, reject) => {
                    fetch(blobUrl)
                        .then(response => response.blob())
                        .then(blob => {
                                const reader = new FileReader();
                                reader.onloadend = () => resolve(reader.result.split(",")[1]);
                                reader.onerror = reject;
                                reader.readAsDataURL(blob);
                        })
                        .catch(reject);
                    });
            """,driver.current_url)

            # Tạo tên file duy nhất và lưu file
            unique_save_path = self.get_unique_filename(save_path)
            with open(unique_save_path, "wb") as pdf_file:
                pdf_file.write(base64.b64decode(pdf_data))
            print(f"[INFO] Tệp PDF đã được lưu tại: {unique_save_path}")
            return unique_save_path  # Trả về đường dẫn file PDF duy nhất
        except Exception as e:
            print(f"[ERROR] Lỗi khi tải file từ blob URL: {e}")
            self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed", self.webhook_url_bhxh)
            return None

    def download_tab_data(self,  save_path):
        """
        Lấy dữ liệu từ tab mới, kiểm tra và tải file PDF nếu URL là blob.
        """
        try:
            # Lấy danh sách các tab hiện tại
            current_tabs = self.driver.window_handles

            # Chuyển sang tab mới nhất
            self.driver.switch_to.window(current_tabs[-1])
            print("[INFO] Đã chuyển sang tab mới.")

            # Lấy URL của tab mới
            current_url = self.driver.current_url
            print(f"[INFO] URL tab mới: {current_url}")

            # Kiểm tra nếu URL là blob và tải file PDF
            if current_url.startswith("blob:"):
                print("[INFO] Đang xử lý file từ blob URL...")
                # Truyền `driver` thay vì `current_url`
                return self.download_blob_pdf(self.driver, save_path)
            else:
                print("[INFO] URL không phải blob, kiểm tra lại cấu trúc hoặc xử lý thêm.")
                return None
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy dữ liệu từ tab mới: {e}")
            self.send_slack_notification("[ERROR] Workflow crawling data baohiemxahoi failed", self.webhook_url_bhxh)
            return None

    def find_months(self, month):
        try:
            # Chuyển đổi tháng sang số nguyên và validate
            thang = int(month)
            if not 1 <= thang <= 12:
                raise ValueError(f"Tháng không hợp lệ: {thang}. Vui lòng chọn từ 1-12")

            # Xác định ID tương ứng với tháng
            thang_id = f"mat-option-{thang - 1}"

            # Nhấn vào phần tử tương ứng
            du_lieu_button = self.driver.find_element(By.ID, thang_id)
            du_lieu_button.click()
            print(f"- Finish click vào tháng {thang}")
            time.sleep(3)
        except ValueError as e:
            print(f"Lỗi: {e}")
            raise
        except Exception as e:
            print(f"Không thể click vào tháng {thang}. Lỗi: {e}")
            raise

    def find_year(self, year):
        try:
            # Lấy năm hiện tại thời gian thực
            current_year = datetime.now().year

            # Chuyển đổi năm sang số nguyên và validate
            nam = int(year)
            if not 1990 <= nam <= current_year:
                raise ValueError(f"Năm không hợp lệ: {nam}. Vui lòng chọn từ 1990-{current_year}")

            # Tìm phần tử input nhập năm bằng thuộc tính formcontrolname="year"
            nam_input = self.driver.find_element(By.CSS_SELECTOR,"input[formcontrolname='year'][matinput][type='number']")

            # Xóa nội dung cũ và nhập năm mới
            nam_input.clear()
            nam_input.send_keys(str(nam))

            print(f"- Finish nhập năm {nam}")
            time.sleep(3)
        except ValueError as e:
            print(f"Lỗi: {e}")
            raise
        except Exception as e:
            print(f"Không thể nhập năm {year}. Lỗi: {e}")
            raise

    # Hàm trích xuất dữ liệu và xuất ra CSV:
    def extract_specific_rows(self, pdf_path, output_csv_path, company, month, year):
        # Các tiêu đề cần tìm trong PDF
        target_keywords = [
            "Kỳ trước mang sang",
            "Phát sinh trong kỳ",
            "Số tiền đã nộp trong kỳ",
            "Phân bổ tiền đóng",
            "Chuyển kỳ sau"
        ]

        # Lưu dữ liệu sau khi trích xuất
        extracted_data = {key: None for key in target_keywords}

        # Mở file PDF
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()  # Trích xuất bảng từ trang
                if table:
                    for row in table:
                        # Duyệt qua từng tiêu đề để tìm hàng khớp
                        for keyword in target_keywords:
                            if keyword in row:
                                # Lấy giá trị cột cuối cùng (CỘNG)
                                extracted_data[keyword] = row[-1]

        # Đảm bảo tên file CSV là duy nhất
        output_csv_path = f"{company}_{month}_{year}_data_bhxh.csv"  # Đường dẫn lưu file CSV mặc định
        unique_csv_path = self.get_unique_filename(output_csv_path)

        # Tạo DataFrame và lưu ra file CSV
        df = pd.DataFrame([extracted_data])
        df.to_csv(unique_csv_path, index=False, encoding="utf-8-sig")
        print(f"[INFO] Dữ liệu đã được lưu tại: {unique_csv_path}")

    # 2. Chọn vào mục Tra cứu Hồ sơ >> Tra cứu C12 >> Tra cứu để crawl data về
    def crawl(self, company, month, year):
        try:
            # Nhấn nút tra cứu Hồ sơ
            tra_cuu_button = self.driver.find_element(By.XPATH, '//*[@id="content"]/div[1]/div/div/div[2]/div[1]/ul/li[4]/a')
            tra_cuu_button.click()
            print("- Finish click Tra cứu Hồ sơ")
            time.sleep(3)

            # Nhấn nút Tra cứu C12
            tra_cuu_c12_button = self.driver.find_element(By.XPATH,"/html/body/app-root/app-portal/div/app-siderbar/div/div/ul/li[9]/a/span/span",)
            tra_cuu_c12_button.click()
            print("- Finish click Tra cứu C12")
            time.sleep(3)

            # Nhấn vào nút sổ các tháng cần tra cứu
            du_lieu_button = self.driver.find_element(By.CLASS_NAME, "mat-select-arrow-wrapper")
            du_lieu_button.click()
            print("- Finish click các tháng cần tra cứu")
            time.sleep(3)

            # Gọi đến hàm find_months với tháng từ argument
            self.find_months(month)
            self.find_year(year)

            # Nhấn vào nút Tra cứu
            du_lieu_button = self.driver.find_element(By.CLASS_NAME, "mat-raised-button")
            du_lieu_button.click()
            print("- Finish click nút Tra cứu")
            time.sleep(10)

            # Gọi đến hàm lưu dữ liệu về máy
            save_path = "BangDuLieuTheoThang.pdf"
            unique_pdf_path = self.download_tab_data(save_path)
            if unique_pdf_path:
                output_csv_path = f"{company}_{month}_{year}_data_bhxh.csv"
                self.extract_specific_rows(unique_pdf_path, output_csv_path, company, month, year)
            else:
                print(f"[WARNING] Không tìm thấy dữ liệu cho tháng {month}. Bỏ qua tháng này.")

        except Exception as e:
            print(f"[ERROR] Lỗi khi crawl dữ liệu tháng {month}: {e}")

    # Tạo bảng data_bhxh

    def create_data_bhxh_table(self, engine):
        metadata = MetaData()

        data_bhxh = Table("data_bhxh", metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("Kỳ trước mang sang", String),
            Column("Phát sinh trong kỳ", String),
            Column("Số tiền đã nộp trong kỳ", String),
            Column("Phân bổ tiền đóng", String),
            Column("Chuyển kỳ sau", String),
            Column("month", String),
            Column("year", String),
            Column("created_at", DateTime),
            Column("company", String(255)),
        )
        metadata.create_all(engine)  # Tạo bảng nếu chưa tồn tại
        print("[INFO] Bảng 'data_bhxh' đã được tạo.")

    # Thêm khóa ngoại cho cột 'company' trong bảng
    def add_foreign_key(self, engine):
        """Thêm khóa ngoại cho cột 'company' trong bảng 'data_bhxh' nếu chưa tồn tại."""
        with engine.begin() as connection:
            try:
                # Kiểm tra xem khóa ngoại đã tồn tại hay chưa
                result = connection.execute(text("""
                    SELECT 1 
                    FROM information_schema.table_constraints 
                    WHERE constraint_name = 'fk_company' 
                    AND table_name = 'data_bhxh';
                """))
                exists = result.fetchone()

                if not exists:
                    # Nếu khóa ngoại chưa tồn tại, thêm vào
                    connection.execute(text("""
                        ALTER TABLE data_bhxh
                        ADD CONSTRAINT fk_company
                        FOREIGN KEY (company) REFERENCES company_information (company);
                    """))
                    print("[INFO] Khóa ngoại đã được thêm thành công.")
                else:
                    print("[INFO] Khóa ngoại 'fk_company' đã tồn tại, bỏ qua.")

            except Exception as e:
                print(f"[WARNING] Không thể thêm khóa ngoại: {e}")

    # Lưu dữ liệu từ file CSV vào database

    def load_csv_to_database(self, engine, company, month, year):
        try:
            # Tạo tên file theo định dạng: {tên công ty}_data_bhxh*.csv
            file_pattern = f"{company}_{month}_{year}_data_bhxh*.csv"
            list_of_files = glob.glob(file_pattern)

            if not list_of_files:
                print(f"[WARNING] Không tìm thấy file CSV nào cho công ty {company}, tháng {month}.")
                return False

            # Lấy file CSV mới nhất
            latest_csv_file = max(list_of_files, key=os.path.getctime)
            df = pd.read_csv(latest_csv_file, encoding="utf-8-sig")
            df = df.fillna("")  # Điền giá trị rỗng nếu có NaN
            if df.empty:
                print(f"[WARNING] File CSV không có dữ liệu. Bỏ qua tháng {month}.")
                return False

            # Kiểm tra sự tồn tại của bảng
            if not inspect(engine).has_table("data_bhxh"):
                print("[ERROR] Bảng 'data_bhxh' không tồn tại trong database.")
                return False

            connection = engine.connect()
            current_time = datetime.now()

            # Bắt đầu transaction
            with connection.begin():
                # Xóa tất cả các bản ghi cũ trùng lặp trong bảng (cùng company, month, year)
                connection.execute(text("""
                    DELETE FROM data_bhxh
                    WHERE company = :company AND month = :month AND year = :year;
                """), {"company": company, "month": month, "year": year})

                # Thêm dữ liệu mới vào bảng và đặt is_latest = True cho tất cả
                df["company"] = company
                df["month"] = month
                df["year"] = year
                df["created_at"] = current_time
                df.to_sql("data_bhxh", engine, if_exists="append", index=False)

            print(f"[INFO] Dữ liệu đã được cập nhật cho công ty {company}, tháng {month}, năm {year}.")
            return True

        except Exception as e:
            print(f"[ERROR] Lỗi khi lưu dữ liệu vào database: {e}")
            return False

    # Hàm lấy dữ liệu từ bảng company_information

    def fetch_company_information(self, engine):
        query = text("SELECT company, bhxh_username, bhxh_password FROM company_information;")
        try:
            with engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()

                # Lọc các công ty không có bhxh_username hoặc bhxh_password
                filtered_rows = [
                    {"company": row[0], "bhxh_username": row[1], "bhxh_password": row[2]}
                    for row in rows
                    if row[1] and row[2]
                ]

                return filtered_rows
        except Exception as e:
            print(f"Error fetching data from 'company_information': {e}")
            return []

    def clean_data(self, directory_path=".", file_extensions=(".csv", ".pdf")):
        """
        Xóa tất cả các file dữ liệu trong thư mục được chỉ định có phần mở rộng cụ thể.

        Args:
            directory_path (str): Đường dẫn đến thư mục chứa file dữ liệu. Mặc định là thư mục hiện tại.
            file_extensions (tuple): Các phần mở rộng của file cần xóa. Mặc định là ('.csv', '.pdf').

        Returns:
            None
        """
        try:
            files_removed = 0
            for file_name in os.listdir(directory_path):
                if file_name.endswith(file_extensions):
                    file_path = os.path.join(directory_path, file_name)
                    os.remove(file_path)
                    files_removed += 1
                    print(f"[INFO] Đã xóa file: {file_path}")

            if files_removed == 0:
                print(f"[INFO] Không có file nào với đuôi {file_extensions} trong thư mục '{directory_path}' để xóa.")
            else:
                print(f"[INFO] Tổng số file đã xóa: {files_removed}")

        except Exception as e:
            print(f"[ERROR] Lỗi khi xóa dữ liệu: {e}")

    

    def main_logic(self):
        print('=============')
        args = self.parse_arguments()
        captcha_image_path = "captcha_image.png"

        # Khởi tạo trình duyệt
        self.driver = self.initialize_driver()
        self.send_slack_notification("======== Workflow BaoHiemXaHoi ==========", self.webhook_url_bhxh)
        engine = self.create_and_connect_to_database()

        # Lấy danh sách công ty từ database
        companies = self.fetch_company_information(engine)
        if not companies:
            print("Không có công ty nào để xử lý. Kết thúc chương trình.")
            self.driver.quit()
            return

        total_companies = len(companies)
        print(f"Tổng số công ty cần xử lý: {total_companies}")

        overall_success = 0
        overall_failure = 0
        company_results = {}

        for idx, company_data in enumerate(companies, start=1):
            company, username, password = (
                company_data["company"],
                company_data["bhxh_username"],
                company_data["bhxh_password"],
            )

            

            max_month = int(args.month)
            months_to_run = list(range(1, max_month + 1))

            print(f"\nĐang xử lý công ty thứ {idx}/{total_companies}: {company}")
            print(f"Tổng Số tháng cần chạy: {len(months_to_run)}")
            print(f"Danh sách các tháng cần chạy: {months_to_run}")
            self.send_slack_notification(f"Danh sách các tháng cần chạy: {months_to_run}", self.webhook_url_bhxh)

            company_success = 0
            company_failure = 0

            try:
                # Đăng nhập vào hệ thống
                self.login_to_baohiemxahoi(username, password, company)
                self.save_captcha_image(self.driver)
                self.enter_verification_code(self.driver, captcha_image_path)
                self.submit_form(self.driver, username, password, captcha_image_path)

                for month in months_to_run:
                    print(f"\nĐang xử lý tháng {month} cho công ty {company}")
                    try:
                        # Mở tab mới trước khi xử lý
                        self.driver.execute_script("window.open('https://dichvucong.baohiemxahoi.gov.vn/#/index', '_blank');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])

                        # Gọi hàm crawl
                        self.crawl(company, str(month), args.year)

                        # Lưu dữ liệu vào database
                        self.create_data_bhxh_table(engine)
                        self.add_foreign_key(engine)
                        if self.load_csv_to_database(engine, company, str(month), args.year):
                            print(f"[INFO] Tháng {month} của công ty {company} lưu thành công.")
                            company_success += 1
                        else:
                            print(f"[WARNING] Tháng {month} của công ty {company} không có dữ liệu.")
                            company_failure += 1

                        # Sau khi xử lý xong, đóng tất cả tab cũ, chỉ giữ lại tab hiện tại
                        current_tab = self.driver.current_window_handle
                        for handle in self.driver.window_handles:
                            if handle != current_tab:
                                self.driver.switch_to.window(handle)
                                self.driver.close()
                        self.driver.switch_to.window(current_tab)

                    except Exception as e:
                        print(f"[ERROR] Lỗi khi xử lý tháng {month} cho công ty {company}: {e}")
                        company_failure += 1

            except Exception as e:
                print(f"[ERROR] Lỗi khi xử lý công ty {company}: {e}")
                company_failure += len(months_to_run)

            finally:
                company_results[company] = {
                    "success": company_success,
                    "failure": company_failure,
                }
                overall_success += company_success
                overall_failure += company_failure

        self.clean_data(directory_path=".", file_extensions=(".csv", ".pdf"))

        # Báo cáo tổng kết
        print("\n=========== Báo cáo tổng kết ===========")
        self.send_slack_notification("=========== Báo cáo tổng kết ===========", self.webhook_url_bhxh)
        print(f"Tổng số công ty có trong database: {total_companies}")
        self.send_slack_notification(f"[INFO] Tổng số công ty có trong database: {total_companies}",self.webhook_url_bhxh)
        print(f"Tổng số công ty chạy thành công: {sum(1 for r in company_results.values() if r['success'] > 0)}")
        self.send_slack_notification(f"[SUCCESS] Tổng số công ty chạy thành công: {sum(1 for r in company_results.values() if r['success'] > 0)}",self.webhook_url_bhxh)
        
        print(f"Tổng số công ty chạy thất bại: {sum(1 for r in company_results.values() if r['success'] == 0)}")
        self.send_slack_notification(f"[FAILED] Tổng số công ty chạy thất bại: {sum(1 for r in company_results.values() if r['success'] == 0)}",self.webhook_url_bhxh)
        for company, results in company_results.items():
            print(f"Công ty {company}: Thành công {results['success']} tháng, Thất bại {results['failure']} tháng")
            self.send_slack_notification(f"[INFO] Công ty {company}: Lấy dữ liệu Thành công {results['success']} tháng, Thất bại {results['failure']} tháng",self.webhook_url_bhxh)

        self.driver.quit()
