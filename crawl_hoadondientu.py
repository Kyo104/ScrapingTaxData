import argparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
import os
import sys
import requests
import base64
from io import BytesIO
import cairosvg
from selenium.webdriver.chrome.service import Service
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from pathlib import Path
from psycopg2 import sql 
import requests
import json

# =================== BIẾN MÔI TRƯỜNG ===================
# Mục thông tin đăng nhập Hóa đơn điện tử
HOADON_USERNAME = "0101652097"  
HOADON_PASSWORD = "At2025@@@"  

# API key cho dịch vụ giải captcha
API_KEY = "#"

# Mục thông tin kết nối database
DB_USER = "postgres" 
DB_PASSWORD = "123456" 
DB_NAME = "data_hoa_don_dien_tu"
DB_HOST = "localhost" 
DB_PORT = "5432" 

# URL Webhook Slack mặc định
WEBHOOK_URL = '#'

print('hello hoadondientu')
# ==============================================================================

def parse_arguments():
    """Parse command line arguments with environment variables as defaults."""
    parser = argparse.ArgumentParser(description='Hóa đơn điện tử Data Crawler')
    
    parser.add_argument('--username', default=HOADON_USERNAME,required=False,
                        help='Tên đăng nhập cho trang web Hóa đơn điện tử')
    parser.add_argument('--password', default=HOADON_PASSWORD, required=False,
                        help='Mật khẩu nhập cho trang web Hóa đơn điện tử')
    parser.add_argument('--api-key', default=API_KEY, required=False,
                        help='API key từ trang web autocaptcha để giải captcha')
    parser.add_argument('--db-user', default=DB_USER, required=False,
                        help='PostgreSQL username')
    parser.add_argument('--db-password', default=DB_PASSWORD, required=False,
                        help='PostgreSQL password')
    parser.add_argument('--db-name', default=DB_NAME, required=False,
                        help='Database name')
    parser.add_argument('--db-host', default=DB_HOST, required=False,
                        help='Database host')
    parser.add_argument('--db-port', default=DB_PORT, required=False,
                        help='Database port')
    parser.add_argument('--webhook-url', default=WEBHOOK_URL, required=False,
                        help='Liên kết webhook từ Slack')  
    
    return parser.parse_args()

args = parse_arguments()
webhook_url = args.webhook_url
print(f"Sử dụng webhook_url: {webhook_url}")

# Đăng nhập vào website https://hoadondientu.gdt.gov.vn/
def initialize_driver():
      """Khởi tạo trình duyệt Chrome."""
      chrome_options = Options()
      chrome_options.add_argument("--ignore-certificate-errors")
      chrome_options.add_argument("--disable-extensions")
      chrome_options.add_argument("--headless=new") # for Chrome >= 109
      chrome_options.add_argument("--disable-gpu") # Tắt GPU rendering
      chrome_options.add_argument("--no-sandbox")  # Bỏ qua chế độ sandbox
      chrome_options.add_argument("--disable-dev-shm-usage") 
      chrome_options.add_argument("--remote-debugging-port=9222")  
      chrome_options.add_argument("--disable-software-rasterizer")  
      chrome_options.add_argument("--force-device-scale-factor=1") 
      chrome_options.add_argument("--disable-blink-features=AutomationControlled")  
      chrome_options.add_argument("--disable-extensions")  
      chrome_options.add_argument("--enable-javascript")  
      driver = webdriver.Chrome(options=chrome_options)
      driver.maximize_window()  # Mở trình duyệt ở chế độ toàn màn hình
      time.sleep(5)
      return driver

# 1.1 Nhập username và password vào trang web 'hoadondientu'
def login_to_thuedientu(driver, username, password):
      
      """Đăng nhập vào trang web 'hoadondientu'."""
      
      url = 'https://hoadondientu.gdt.gov.vn/'
      driver.get(url)
      print('- Finish initializing a driver')
      send_slack_notification('Chương trình đang thực hiện lấy dữ liệu trang hoadondientu', webhook_url)
      time.sleep(3)
      
      try:
            X_button = WebDriverWait(driver, 10).until(
                  EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/button/span'))
            )
            X_button.click()
            print('- Finish: Tắt thông báo')
      except TimeoutException:
            print("X_button không hiển thị hoặc không thể nhấn")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)
      except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

      # Nhấn nút Đăng nhập
      try:
            login_button = WebDriverWait(driver, 10).until(
                  EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'home-header-menu')]//div[contains(@class, 'ant-col home-header-menu-item')]//span[text()='Đăng nhập']"))
            )
            login_button.click()
            print('- Finish: Login to hoadondientu')
      except TimeoutException:
            print("Login button không hiển thị hoặc không thể nhấn")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)
      # Nhập username
      username_field = driver.find_element(By.ID, 'username')
      username_field.send_keys(username)
      print('- Finish keying in username_field')
      time.sleep(3)

      # Nhập password
      password_field = driver.find_element(By.ID, 'password')
      password_field.send_keys(password)
      print('- Finish keying in password_field')
      time.sleep(2)

def send_slack_notification(message, webhook_url):
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "text": message  # Nội dung thông báo
    }
    try:  
      response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
      
      if response.status_code == 200:
            print("Thông báo đã được gửi thành công!")
      else:
            print(f"Lỗi khi gửi thông báo: {response.status_code}, {response.text}")
    except:
          pass

# lưu ảnh captcha về máy dưới dạng svg (tải ảnh về chuẩn rồi)
def crawl_img(driver):
      try:
            # Tìm phần tử img chứa ảnh captcha
            img = driver.find_element(By.CLASS_NAME, 'Captcha__Image-sc-1up1k1e-1.kwfLHT')

            # Lấy giá trị của thuộc tính 'src' của thẻ img
            img_src = img.get_attribute('src')

            # Kiểm tra nếu src bắt đầu bằng 'data:image/svg+xml;base64,' (đặc trưng của ảnh base64)
            if img_src.startswith('data:image/svg+xml;base64,'):
                  # Loại bỏ phần 'data:image/svg+xml;base64,' từ chuỗi base64
                  base64_data = img_src.split('data:image/svg+xml;base64,')[1]

                  # Giải mã base64 thành dữ liệu nhị phân
                  img_data = base64.b64decode(base64_data)

                  # Tạo tên file cho ảnh (có thể thay đổi theo nhu cầu)
                  file_name = 'captcha_image.svg'

                  # Lưu ảnh dưới dạng file SVG
                  with open(file_name, 'wb') as f:
                        f.write(img_data)
                  
                  print(f"Ảnh đã được tải về và lưu thành công với tên: {file_name}")

            else:
                  print("Không tìm thấy ảnh SVG base64 trong src của thẻ img.")
      
      except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

# Hàm gửi ảnh đến AntiCaptcha
def solve_captcha(image_base64):
    url = "https://anticaptcha.top/api/captcha"
    payload = {
        "apikey": API_KEY,
        "img": image_base64,
        "type": 28  # Loại captcha, có thể cần thay đổi nếu không đúng
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        # Gửi POST request
        response = requests.post(url, json=payload, headers=headers)

        # Kiểm tra nếu có lỗi trong phản hồi HTTP
        if response.status_code != 200:
            print(f"Error with request: {response.status_code}")
            print(f"Response Text: {response.text}")
            return None
        
        # Phân tích phản hồi JSON
        response_data = response.json()
        
        # Kiểm tra xem API trả về thành công
        if response_data.get("success") and "captcha" in response_data:
            print(f"Mã captcha đã giải: {response_data['captcha']}")
            return response_data["captcha"]
        else:
            print(f"API response indicates failure: {response_data}")
            return None
    except Exception as e:
        print(f"Error with request: {str(e)}")
        send_slack_notification('Chương trình chạy thất bại', webhook_url)
        return None

# Hàm xử lý ảnh captcha và gửi lên AntiCaptcha
def solve_captcha_from_file(file_path):
    try:
        # Đọc file captcha
        with open(file_path, 'rb') as file:
            # Kiểm tra nếu file là SVG
            if file_path.endswith(".svg"):
                # Đọc nội dung của file SVG
                svg_content = file.read()

                # Chuyển đổi file SVG thành PNG
                png_bytes = cairosvg.svg2png(bytestring=svg_content)

                # Mã hóa ảnh PNG thành base64
                image_base64 = base64.b64encode(png_bytes).decode("utf-8")
            else:
                # Nếu là ảnh raster (PNG, JPEG), chuyển sang PNG và mã hóa base64
                img = Image.open(file)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        captcha_text = solve_captcha(image_base64)

        # Trả về mã captcha đã giải, không in ra nhiều lần
        return captcha_text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        send_slack_notification('Chương trình chạy thất bại', webhook_url)
        return None

# 1.2 Nhập mã Captcha (tự động)
def enter_verification_code(driver, captcha_image_path):
      try:
            # Giải mã captcha bằng hàm solve_captcha_from_file
            captcha_code = solve_captcha_from_file(captcha_image_path)
            if not captcha_code:
                  print("[ERROR] Không thể giải mã captcha.")
                  sys.exit(1)  # Thoát chương trình
                  return False

            # Tìm tất cả phần tử có id 'cvalue'
            elements = driver.find_elements(By.ID, 'cvalue')
            print(f"[DEBUG] Số phần tử với id='cvalue': {len(elements)}")

            # Nếu có nhiều hơn một phần tử, chọn phần tử cụ thể 
            if len(elements) > 1:
                  captcha_field = elements[1]  
            else:
                  captcha_field = elements[0]

            # Nhập CAPTCHA
            captcha_field.clear()
            captcha_field.send_keys(captcha_code)
            time.sleep(2)

            # Log giá trị sau khi nhập
            captcha_value = captcha_field.get_attribute('value')
            print(f"[DEBUG] Giá trị CAPTCHA sau khi nhập: {captcha_value}")

            return True
      except Exception as e:
            print(f"[ERROR] Lỗi khi nhập mã CAPTCHA: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)
            return False

# 1.3 Nhấn nút đăng nhập sau cùng hoàn tất việc login vào trang web
def submit_form(driver, captcha_image_path):
      """Nhấn nút để hoàn tất đăng nhập."""
      login_attempt = 0  # Biến đếm số lần đăng nhập

      try:
            while True:
                  # Nhấn nút để gửi biểu mẫu
                  submit_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div[2]/form/div/div[6]/button')
                  submit_button.click()
                  print(f'- Finish submitting the form (Lần {login_attempt + 1})')
                  send_slack_notification(f'Chương trình đang thực hiên login lần {login_attempt + 1}', webhook_url)
                  # Kiểm tra nếu có thông báo lỗi CAPTCHA
                  try:
                        # Chờ thông báo lỗi CAPTCHA
                        error_message = WebDriverWait(driver, 2).until(
                              EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Mã captcha không đúng.")]'))
                        )
                        if error_message:
                              print("[ERROR] Mã xác nhận nhập sai. Đang thử lại...")
                              send_slack_notification('Login thất bại, đang thử lại', webhook_url)
                              # Lưu và giải mã CAPTCHA mới
                              crawl_img(driver)
                              # enter_verification_code(driver, captcha_image_path) # Tự động
                              enter_verification_code(driver, captcha_image_path)
                              login_attempt += 1  # Tăng số lần thử đăng nhập
                              continue  # Thử lại
                  except TimeoutException:
                        print("[DEBUG] Mã xác nhận được xác thực thành công")

                        # Kiểm tra nếu đăng nhập thành công
                  try:
                        # Chờ thẻ div có id "ddtabs1" xuất hiện
                        WebDriverWait(driver, 5).until(
                              EC.presence_of_element_located((By.CLASS_NAME, "ant-row-flex.flex-space"))
                        )
                        # Tìm trong ul có id "tabmenu" và kiểm tra thẻ span với text "Tra cứu"
                        tra_cuu_element = driver.find_element(
                              By.XPATH, '//*[@id="__next"]/section/section/div/div/div/div/div[8]/div/span'
                        )
                        if tra_cuu_element:
                              print("[INFO] Đăng nhập thành công! Đã vào trang chính.")
                              send_slack_notification('Chương trình đã login thành công vào trang hoadondientu', webhook_url)
                              if login_attempt == 0:
                                    crawl(driver)  # Lần đầu tiên, gọi hàm crawl
                              else:
                                    crawls(driver)  # Các lần tiếp theo, gọi hàm crawls
                              return  # Thoát khỏi hàm khi thành công
                  except TimeoutException:
                        print("[DEBUG] Không tìm thấy dấu hiệu đăng nhập thành công. Thử lại...")
                        send_slack_notification('Chương trình chạy thất bại', webhook_url)
                        login_attempt += 1  # Tăng số lần thử đăng nhập
                        continue  # Thử lại nếu không tìm thấy dấu hiệu thành công

                  # Nếu không vào được vòng lặp, thoát ra
                  break
      except Exception as e:
            print(f"Đã xảy ra lỗi khi nhấn nút submit: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

# 2.1 chọn vào mục ( Tra cứu hóa đơn ) khi giải captcha lần đầu thành công
def crawl(driver):
      # Nhấn nút tra cứu 
      tra_cuu_button = driver.find_element(By.XPATH, '//*[@id="__next"]/section/section/div/div/div/div/div[8]/div/span')
      tra_cuu_button.click()                          
      print('- Finish click tra cứu')
      time.sleep(3)
      
      # Chọn vào mục ( Tra cứu hóa đơn )
      tra_cuu_hd_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/ul/li[1]/a')  
      tra_cuu_hd_button.click()                             
      print('- Finish click tra cứu hóa đơn')
      time.sleep(3)
      
# 2.2 chọn vào mục ( Tra cứu hóa đơn ) khi giải captcha các lần sau thành công
def crawls(driver):
      # Nhấn nút tra cứu 
      tra_cuu_button = driver.find_element(By.XPATH, '//*[@id="__next"]/section/section/div/div/div/div/div[8]/div/span')
      tra_cuu_button.click()              
      print('- Finish click tra cứu')
      time.sleep(3)
      
      # Chọn vào mục ( Tra cứu hóa đơn )
      tra_cuu_hd_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/ul/li[1]/a')  
      tra_cuu_hd_button.click()                             
      print('- Finish click tra cứu hóa đơn')
      time.sleep(3)

# 3. chọn vào tab ( - Tra cứu hóa đơn điện tử mua vào - ) để crawl dữ liệu
def crawl_hoa_don_mua_vao(driver):
      # Chọn Tra cứu hóa đơn điện tử mua vào
      mua_vao_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[1]/div/div/div/div/div[1]/div[2]/span'))
      )
      mua_vao_button.click()
      print('- Finish click tab tra cứu hóa đơn mua vào')
      time.sleep(3)
      
      # Chọn ngày (Từ ngày -> Đến ngày)
      try:
      # Chờ cho các thẻ input xuất hiện
            inputs = WebDriverWait(driver, 10).until(
                  EC.presence_of_all_elements_located((By.XPATH, '//*[@id="tngay"]/div/input'))
            )
           
            # Chọn thẻ input ở vị trí thứ 3 (index bắt đầu từ 0 trong Python)
            target_input_to = inputs[1]  # Lấy thẻ input thứ 3
            
            target_input_to.click()
            print("- click thành công vào input")
            
            # user có thể tự chọn tháng muốn crawl dữ liệu (chọn tháng thủ công trong 6s)     
           
            time.sleep(15)
            print("- Bạn đã chọn thời gian tìm kiếm.")

      except Exception as e:
            print(f"[ERROR] Gặp lỗi khi thao tác với thẻ input: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)
      
      # Chọn nút Tìm kiếm 
      tim_kiem = driver.find_element(By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[3]/div[2]/div[3]/div[1]/div/div/form/div[3]/div[1]/button')        
      tim_kiem.click()                 
      print('- Finish click tìm kiếm hóa đơn mua vào')
      time.sleep(2)
      
# ( Hàm Thêm stt sau mỗi file trùng tên )
def get_unique_filename(base_filename):
      if not os.path.exists(base_filename):
            return base_filename

      base, ext = os.path.splitext(base_filename)
      counter = 1
      new_filename = f"{base} ({counter}){ext}"

      while os.path.exists(new_filename):
            counter += 1
            new_filename = f"{base} ({counter}){ext}"

      return new_filename
        
# Task 4 xuất các hàng dữ liệu ở trang ( - Tra cứu hóa đơn điện tử mua vào - ) ra file csv     
def extract_table_mua_vao_to_csv(driver, output_file):
      """Lấy dữ liệu từ bảng ngang có thanh cuộn và lưu vào file CSV."""
      try:
            
            # Tạo tên file duy nhất nếu cần
            unique_output_file = get_unique_filename(output_file)
            # Chờ bảng hiển thị
            table1 = WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[3]/div[2]/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div/div/div/div/div[1]/table'))
            )                                                
            # Tìm thanh cuộn ngang
            scrollable_div = driver.find_element(By.XPATH, '/html/body/div/section/section/main/div/div/div/div/div[3]/div[2]/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div/div/div/div/div[2]')

            # Lấy chiều rộng cuộn tối đa
            max_scroll_width = driver.execute_script("return arguments[0].scrollWidth;", scrollable_div)
            current_scroll_position = 0
            scroll_step = 500  # Số pixel cuộn ngang mỗi lần

            # Khởi tạo lưu trữ dữ liệu
            all_headers = []
            all_rows = []

            while current_scroll_position < max_scroll_width:
                  # Lấy HTML hiện tại của bảng có thead class 'ant-table-thead'
                  table_html = table1.get_attribute('outerHTML')
                  soup = BeautifulSoup(table_html, 'html.parser')

                  # Lấy tiêu đề nếu tồn tại
                  header_row = soup.find('thead')
                  if header_row:
                        header_columns = header_row.find_all('th')
                        headers = [header.text.strip() for header in header_columns]
                        # Chỉ thêm các tiêu đề mới
                        if not all_headers:
                              all_headers = headers
                        elif len(headers) > len(all_headers):
                              all_headers += headers[len(all_headers):]  # Thêm cột mới vào cuối
                  else:
                        print("[WARNING] Không tìm thấy tiêu đề bảng.")
            
                  # Lấy dữ liệu từ tbody
                  # Tìm tất cả phần tử có class 'ant-table-tbody'
                  elements2 = driver.find_elements(By.CLASS_NAME, 'ant-table-tbody')
                  # print(f"[DEBUG] Số phần tử với class='ant-table-body': {len(elements2)}")

                  # Chọn phần tử thứ hai (index 1)
                  if len(elements2) > 1:
                        tbody = elements2[1]
                  else:
                        raise Exception("Không tìm thấy phần tử ant-table-body thứ hai.")

                  # Lấy tất cả các hàng hiện tại
                  rowsbody = tbody.find_elements(By.XPATH, ".//tr")
                  # Duyệt qua các hàng
                  for row in rowsbody:
                        cols = row.find_elements(By.XPATH, "./td")
                        row_data = [col.text.strip() for col in cols]
                        # Đảm bảo chiều dài hàng phù hợp với số cột
                        while len(row_data) < len(all_headers):
                              row_data.append("")  # Thêm ô trống
                        all_rows.append(row_data)

                  # Cuộn thanh cuộn ngang
                  current_scroll_position += scroll_step
                  driver.execute_script(f"arguments[0].scrollLeft = {current_scroll_position};", scrollable_div)
                  time.sleep(1)

                  # Kiểm tra cuộn xong chưa
                  new_scroll_position = driver.execute_script("return arguments[0].scrollLeft;", scrollable_div)
                  if new_scroll_position == current_scroll_position:
                        break

            # Lưu vào DataFrame
            if not all_headers:
                  print("[ERROR] Không tìm thấy tiêu đề để tạo DataFrame.")
                  return

            df = pd.DataFrame(all_rows, columns=all_headers)
            df.to_csv(unique_output_file, index=False, encoding="utf-8-sig")
            print(f"- Dữ liệu đã được lưu vào file: {unique_output_file}")
            send_slack_notification(f'Chương trình đã lưu thành công file {unique_output_file}', webhook_url)

      except Exception as e:
            print(f"[ERROR] Không thể lấy dữ liệu từ bảng: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

# Chụp màn hình hóa đơn chi tiết
def capture_full_page(driver, save_path):
      try:
            WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.CLASS_NAME, "ant-modal-body"))
            )
            print("[DEBUG] Đã tìm thấy .ant-modal-body.")

            element_height = driver.execute_script("""
                  var element = document.querySelector('.ant-modal-body');
                  return element ? element.scrollHeight : 0;
            """)
            viewport_height = driver.execute_script("""
                  var element = document.querySelector('.ant-modal-body');
                  return element ? element.clientHeight : 0;
            """)
            print(f"[DEBUG] Chiều cao tổng: {element_height}, Chiều cao viewport: {viewport_height}")

            current_scroll = 0
            screenshots = []

            while current_scroll < element_height:
                  # Cuộn xuống
                  driver.execute_script(f"""
                  var element = document.querySelector('.ant-modal-body');
                  element.scrollTop = {current_scroll};
                  """)
                  time.sleep(1.5)  # Chờ nội dung được render

                  # Chụp màn hình
                  screenshot_path = f"temp_{current_scroll}.png"
                  driver.save_screenshot(screenshot_path)
                  screenshots.append(screenshot_path)
                  print(f"[DEBUG] Đã chụp tại: {current_scroll}")
                  

                  # Cập nhật vị trí cuộn
                  current_scroll += viewport_height

            # Ghép ảnh
            print("[DEBUG] Đang ghép ảnh.")
            images = [Image.open(img) for img in screenshots]
            total_width, _ = images[0].size
            total_height = len(images) * viewport_height
            combined_image = Image.new("RGB", (total_width, total_height))

            y_offset = 0
            for img in images:
                  combined_image.paste(img, (0, y_offset))
                  y_offset += img.size[1]
                  img.close()

            combined_image.save(save_path)
            print(f"[SUCCESS] Ảnh đã lưu tại: {save_path}")
            send_slack_notification(f'Chương trình đã lưu thành công file {save_path}', webhook_url)

            # Xóa ảnh tạm
            for img in screenshots:
                  os.remove(img)

      except Exception as e:
            print(f"[ERROR] Lỗi khi chụp màn hình: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)
        
# 4.1 xuất từng ảnh ( hóa đơn mua vào chi tiết ) của từng hàng dữ liệu bảng
def extract_img_hoa_don_mua_vao(driver):
      try:
            # Tìm tất cả phần tử với class 'ant-table-tbody'
            elements2 = driver.find_elements(By.CLASS_NAME, 'ant-table-tbody')
            print(f"[DEBUG] Số phần tử với class='ant-table-tbody': {len(elements2)}")

            # Chọn phần tử thứ hai (index 1)
            if len(elements2) > 1:
                  tbody = elements2[1]
            else:
                  raise Exception("Không tìm thấy phần tử ant-table-tbody thứ hai.")

            # Lấy tất cả các hàng hiện tại
            rowsbody = tbody.find_elements(By.XPATH, ".//tr")
            print(f"[DEBUG] Số hàng dữ liệu trong tbody: {len(rowsbody)}")

            # Lặp qua từng hàng và click
            for index, row in enumerate(rowsbody):
                  try:
                        # Đưa con trỏ tới hàng để chắc chắn có thể click
                        ActionChains(driver).move_to_element(row).perform()
                        print(f"[DEBUG] Click vào hàng thứ {index + 1}")
                        
                        # Click vào hàng
                        row.click()

                        # Có thể thêm logic chờ đợi hoặc xử lý sau khi click
                        time.sleep(2)  # Tạm dừng để quan sát trong 2s
                        
                        # =========================
                        # click vào nút " Xem hóa đơn"  chi tiết 
                        img_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[3]/div[2]/div[3]/div[2]/div[1]/div[2]/div/div[5]/button')                         
                        img_btn.click()
                        print(f"- Finish click btn xem hóa đơn chi tiết ở hàng thứ {index + 1}")
                        time.sleep(3)
                        
                        # Chụp màn hình toàn bộ hóa đơn
                        base_file_name = f"hoadon_muavao_chitiet_stt_{index + 1}.png"
                        unique_file_name = get_unique_filename(base_file_name)
                        capture_full_page(driver, unique_file_name)

                        # Đóng modal
                        close_btn = driver.find_element(By.CLASS_NAME, 'ant-modal-close')
                        close_btn.click()
                        time.sleep(1)
                        
                  except ElementNotInteractableException as e:
                        print(f"[ERROR] Không thể click vào hàng thứ {index + 1}: {e}")
                  except Exception as e:
                        print(f"[ERROR] Lỗi khác xảy ra với hàng thứ {index + 1}: {e}")

      except Exception as e:
            print(f"[ERROR] Lỗi chung: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

# 5. chọn vào tab ( - Tra cứu hóa đơn điện tử bán ra - ) để crawl dữ liệu    
def crawl_hoa_don_ban_ra(driver):
      # Chọn Tra cứu hóa đơn điện tử bán ra (đảm bảo đã click vào tab này trước)
      mua_vao_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[1]/div/div/div/div/div[1]/div[1]/span'))
      )                                               
      mua_vao_button.click()
      print('- Finish click tab tra cứu hóa đơn bán ra')
      time.sleep(3)
      try:
      # Chờ cho các thẻ input xuất hiện
            inputs = WebDriverWait(driver, 10).until(
                  EC.presence_of_all_elements_located((By.XPATH, '//*[@id="tngay"]/div/input'))
            )
           
            # Chọn thẻ input ở vị trí thứ 1 (index bắt đầu từ 0 trong Python)
            target_input_to = inputs[0]  # Lấy thẻ input thứ 1
            
            target_input_to.click()
            print("- click thành công vào input")
            
            # users có thể tự chọn tháng muốn crawl dữ liệu về (chọn tháng thủ công trong 6s)     
           
            time.sleep(6)
            print("- Bạn đã chọn thời gian tìm kiếm.")

      except Exception as e:
            print(f"[ERROR] Gặp lỗi khi thao tác với thẻ input: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)
      # Chọn nút Tìm kiếm 
      tim_kiem = driver.find_element(By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[3]/div[1]/div[3]/div[1]/div/div/form/div[3]/div[1]/button')        
      tim_kiem.click()                          
                                                
      print('- Finish click tìm kiếm hóa bán ra')
      time.sleep(2)
      
# 6. xuất dữ liệu ở trang ( - Tra cứu hóa đơn điện tử bán ra - ) ra file csv
def extract_table_ban_ra_to_csv(driver, output_file_ra):
      """Lấy dữ liệu từ bảng ngang có thanh cuộn và lưu vào file CSV."""
      
      try:
            # Tạo tên file duy nhất nếu cần
            unique_output_file = get_unique_filename(output_file_ra)
            # Chờ bảng hiển thị
            table2 = WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[3]/div[1]/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div/div/div/div/div[1]/table'))
            )                                                
            # Tìm thanh cuộn ngang
            scrollable_div = driver.find_element(By.XPATH, '/html/body/div/section/section/main/div/div/div/div/div[3]/div[1]/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div/div/div/div/div[2]')
                                                            
            # Lấy chiều rộng cuộn tối đa                    
            max_scroll_width = driver.execute_script("return arguments[0].scrollWidth;", scrollable_div)
            current_scroll_position = 0
            scroll_step = 500  # Số pixel cuộn ngang mỗi lần

            # Khởi tạo lưu trữ dữ liệu
            all_headers = []
            all_rows = []

            while current_scroll_position < max_scroll_width:
                  # Lấy HTML hiện tại của bảng có thead class 'ant-table-thead'
                  table_html = table2.get_attribute('outerHTML')
                  soup = BeautifulSoup(table_html, 'html.parser')

                  # Lấy tiêu đề nếu tồn tại
                  header_row = soup.find('thead')
                  if header_row:
                        header_columns = header_row.find_all('th')
                        headers = [header.text.strip() for header in header_columns]
                        # Chỉ thêm các tiêu đề mới
                        if not all_headers:
                              all_headers = headers
                        elif len(headers) > len(all_headers):
                              all_headers += headers[len(all_headers):]  # Thêm cột mới vào cuối
                  else:
                        print("[WARNING] Không tìm thấy tiêu đề bảng.")
                
                  # Lấy dữ liệu từ tbody
                  # Tìm tất cả phần tử có class 'ant-table-tbody'
                  elements2 = driver.find_elements(By.CLASS_NAME, 'ant-table-tbody')
                  # print(f"[DEBUG] Số phần tử với class='ant-table-body': {len(elements2)}")

                  # Chọn phần tử thứ hai (index 1)
                  if len(elements2) > 1:
                        tbody = elements2[0]
                  else:
                        raise Exception("Không tìm thấy phần tử ant-table-body thứ hai.")

                  # Lấy tất cả các hàng hiện tại
                  rowsbody = tbody.find_elements(By.XPATH, ".//tr")
                  # Duyệt qua các hàng
                  for row in rowsbody:
                        cols = row.find_elements(By.XPATH, "./td")
                        row_data = [col.text.strip() for col in cols]
                        # Đảm bảo chiều dài hàng phù hợp với số cột
                        while len(row_data) < len(all_headers):
                              row_data.append("")  # Thêm ô trống
                        all_rows.append(row_data)

                  # Cuộn thanh cuộn ngang
                  current_scroll_position += scroll_step
                  driver.execute_script(f"arguments[0].scrollLeft = {current_scroll_position};", scrollable_div)
                  time.sleep(1)

                  # Kiểm tra cuộn xong chưa
                  new_scroll_position = driver.execute_script("return arguments[0].scrollLeft;", scrollable_div)
                  if new_scroll_position == current_scroll_position:
                        break

            # Lưu vào DataFrame
            if not all_headers:
                  print("[ERROR] Không tìm thấy tiêu đề để tạo DataFrame.")
                  return

            df = pd.DataFrame(all_rows, columns=all_headers)
            df.to_csv(unique_output_file, index=False, encoding="utf-8-sig")
            print(f"- Dữ liệu đã được lưu vào file: {unique_output_file}")
            send_slack_notification(f'Chương trình đã lưu thành công file {unique_output_file}', webhook_url)
      except Exception as e:
            print(f"[ERROR] Không thể lấy dữ liệu từ bảng: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

# 6.1 xuất từng ảnh ( hóa đơn bán ra chi tiết ) của từng hàng dữ liệu trong bảng
def extract_img_hoa_don_ban_ra(driver):
      try:
            # Tìm tất cả phần tử với class 'ant-table-tbody'
            elements2 = driver.find_elements(By.CLASS_NAME, 'ant-table-tbody')
            print(f"[DEBUG] Số phần tử với class='ant-table-tbody': {len(elements2)}")

            # Chọn phần tử thứ nhất (index 0)
            if len(elements2) > 1:
                  tbody = elements2[0]
            else:
                  raise Exception("Không tìm thấy phần tử ant-table-tbody thứ hai.")

            # Lấy tất cả các hàng hiện tại
            rowsbody = tbody.find_elements(By.XPATH, ".//tr")
            print(f"[DEBUG] Số hàng dữ liệu trong tbody: {len(rowsbody)}")

            # Lặp qua từng hàng và click
            for index, row in enumerate(rowsbody):
                  try:
                        # Đưa con trỏ tới hàng để chắc chắn có thể click
                        ActionChains(driver).move_to_element(row).perform()
                        print(f"[DEBUG] Click vào hàng thứ {index + 1}")
                        
                        # Click vào hàng
                        row.click()

                        # Có thể thêm logic chờ đợi hoặc xử lý sau khi click
                        time.sleep(2)  # Tạm dừng để quan sát 
                        
                        # =========================
                        # click vào nút " Xem hóa đơn"  chi tiết 
                        img_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/section/section/main/div/div/div/div/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[5]/button')                         
                        img_btn.click()                           
                        print(f"- Finish click btn xem hóa đơn chi tiết ở hàng thứ {index + 1}")
                        time.sleep(3)
                        
                        # Chụp màn hình toàn bộ hóa đơn
                        base_file_name = f"hoadon_banra_chitiet_stt_{index + 1}.png"
                        unique_file_name = get_unique_filename(base_file_name)
                        capture_full_page(driver, unique_file_name)

                        # Đóng modal
                        close_btn = driver.find_element(By.CLASS_NAME, 'ant-modal-close')
                        close_btn.click()
                        time.sleep(1)
                        
                  except ElementNotInteractableException as e:
                        print(f"[ERROR] Không thể click vào hàng thứ {index + 1}: {e}")
                  except Exception as e:
                        print(f"[ERROR] Lỗi khác xảy ra với hàng thứ {index + 1}: {e}")

      except Exception as e:
            print(f"[ERROR] Lỗi chung: {e}")
            send_slack_notification('Chương trình chạy thất bại', webhook_url)

def get_db_config(args):
    return {
        'dbname': args.db_name,
        'user': args.db_user,
        'password': args.db_password,
        'host': args.db_host,
        'port': args.db_port
    }

# Tạo bảng nếu chưa tồn tại
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS invoices (
      id SERIAL PRIMARY KEY,
      mau_so VARCHAR(255),
      ky_hieu VARCHAR(255),
      so_hoa_don VARCHAR(255) UNIQUE,
      ngay_lap DATE,
      tong_tien NUMERIC,
      trang_thai VARCHAR(255),
      image_path VARCHAR(255),
      image_data BYTEA,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mua_vao (
      id INT PRIMARY KEY REFERENCES invoices(id) ON DELETE CASCADE,
      ky_hieu VARCHAR(255),
      so_hoa_don VARCHAR(255),
      tong_tien NUMERIC,
      image_path VARCHAR(255),
      image_data BYTEA,
      thong_tin_nguoi_ban TEXT
);

CREATE TABLE IF NOT EXISTS ban_ra (
      id INT PRIMARY KEY REFERENCES invoices(id) ON DELETE CASCADE,
      ky_hieu VARCHAR(255),
      so_hoa_don VARCHAR(255),
      tong_tien NUMERIC,
      image_path VARCHAR(255),
      image_data BYTEA,
      thong_tin_nguoi_mua TEXT
);
"""

# Hàm kết nối PostgreSQL
def get_connection():
      return psycopg2.connect(**DB_CONFIG)

def convert_date(date_str):
      """Chuyển định dạng ngày từ 'DD/MM/YYYY' sang 'YYYY-MM-DD'."""
      return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')

# Hàm lưu dữ liệu vào PostgreSQL
def get_latest_files_by_timestamp(csv_pattern, img_pattern):
    """
    Get the latest CSV and corresponding images based on creation timestamp
    Returns tuple of (csv_file, list_of_images)
    """
    try:
        # Get all matching files with their timestamps
        csv_files = list(Path('.').glob(csv_pattern))
        img_files = list(Path('.').glob(img_pattern))
        
        if not csv_files:
            print(f"No CSV files found matching pattern: {csv_pattern}")
            return None, []
            
        # Get the latest CSV file
        latest_csv = max(csv_files, key=os.path.getctime)
        csv_timestamp = os.path.getctime(latest_csv)
        
        # Filter images created after the CSV file
        relevant_images = [
            img for img in img_files 
            if os.path.getctime(img) >= csv_timestamp
        ]
        
        # Sort images by creation time
        relevant_images.sort(key=os.path.getctime)
        
        return str(latest_csv), [str(img) for img in relevant_images]
        
    except Exception as e:
        print(f"Error getting latest files: {e}")
        send_slack_notification('Chương trình chạy thất bại', webhook_url)
        return None, []

def save_to_database(data, image_paths, loai_hoa_don):
    """
    Modified save_to_database function to handle multiple images per CSV
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for idx, (_, row) in enumerate(data.iterrows()):
                    # Get corresponding image path for this row
                    image_path = image_paths[idx] if idx < len(image_paths) else None
                    
                    invoice_query = """
                    INSERT INTO invoices (mau_so, ky_hieu, so_hoa_don, ngay_lap, tong_tien, trang_thai, image_path, image_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (so_hoa_don) DO UPDATE
                    SET mau_so = EXCLUDED.mau_so,
                        ngay_lap = EXCLUDED.ngay_lap,
                        tong_tien = EXCLUDED.tong_tien,
                        trang_thai = EXCLUDED.trang_thai,
                        image_path = EXCLUDED.image_path,
                        image_data = EXCLUDED.image_data
                    RETURNING id;
                    """
                    
                    image_data = None
                    if image_path and os.path.exists(image_path):
                        with open(image_path, 'rb') as img_file:
                            image_data = img_file.read()
                            
                    invoice_values = (
                        row.get('mau_so'),
                        row.get('ky_hieu'),
                        row.get('so_hoa_don'),
                        convert_date(row.get('ngay_lap')),
                        row.get('tong_tien').replace('.', '') if row.get('tong_tien') else None,
                        row.get('trang_thai'),
                        image_path,
                        image_data
                    )

                    cur.execute(invoice_query, invoice_values)
                    invoice_id = cur.fetchone()[0]

                    # Handle specific invoice type tables
                    if loai_hoa_don == "mua_vao":
                        specific_query = """
                        INSERT INTO mua_vao (id, ky_hieu, so_hoa_don, tong_tien, image_path, image_data, thong_tin_nguoi_ban)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET ky_hieu = EXCLUDED.ky_hieu,
                            so_hoa_don = EXCLUDED.so_hoa_don,
                            tong_tien = EXCLUDED.tong_tien,
                            image_path = EXCLUDED.image_path,
                            image_data = EXCLUDED.image_data,
                            thong_tin_nguoi_ban = EXCLUDED.thong_tin_nguoi_ban;
                        """
                        specific_values = (
                            invoice_id,
                            row.get('ky_hieu'),
                            row.get('so_hoa_don'),
                            row.get('tong_tien').replace('.', '') if row.get('tong_tien') else None,
                            image_path,
                            image_data,
                            row.get('thong_tin_nguoi_ban')
                        )
                    else:  # ban_ra
                        specific_query = """
                        INSERT INTO ban_ra (id, ky_hieu, so_hoa_don, tong_tien, image_path, image_data, thong_tin_nguoi_mua)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET ky_hieu = EXCLUDED.ky_hieu,
                            so_hoa_don = EXCLUDED.so_hoa_don,
                            tong_tien = EXCLUDED.tong_tien,
                            image_path = EXCLUDED.image_path,
                            image_data = EXCLUDED.image_data,
                            thong_tin_nguoi_mua = EXCLUDED.thong_tin_nguoi_mua;
                        """
                        specific_values = (
                            invoice_id,
                            row.get('ky_hieu'),
                            row.get('so_hoa_don'),
                            row.get('tong_tien').replace('.', '') if row.get('tong_tien') else None,
                            image_path,
                            image_data,
                            row.get('thong_tin_nguoi_mua')
                        )
                    
                    cur.execute(specific_query, specific_values)
                    
        print(f"Dữ liệu hóa đơn {loai_hoa_don} đã được lưu thành công.")
        send_slack_notification(f'Chương trình đã đưa dữ liệu {loai_hoa_don} lên database', webhook_url)
    except Exception as e:
        print(f"Lỗi xảy ra khi lưu dữ liệu vào database: {e}")

def get_latest_file(pattern):
    files = list(Path('.').glob(pattern))
    if not files:
      print(f"No files found matching pattern: {pattern}")
      return None
    latest_file = max(files, key=os.path.getmtime)
    return str(latest_file)

latest_mua_vao_csv = get_latest_file("hoa_don_mua_vao*.csv")
latest_ban_ra_csv = get_latest_file("hoa_don_ban_ra*.csv")
latest_png_mua = get_latest_file("hoadon_muavao_chitiet_stt_*.png")
latest_png_ban = get_latest_file("hoadon_banra_chitiet_stt_*.png")

if latest_mua_vao_csv:
    print(f"Using latest mua vao file: {latest_mua_vao_csv}")
if latest_ban_ra_csv:
    print(f"Using latest ban ra file: {latest_ban_ra_csv}")
if latest_png_mua:
    print(f"Using latest PNG_mua file: {latest_png_mua}")
if latest_png_ban:
    print(f"Using latest PNG_ban file: {latest_png_ban}")

# Quy trình database chính
def main_db_workflow():
    # Tạo bảng nếu chưa tồn tại
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_QUERY)

    # Get latest files for both types
    mua_vao_csv, mua_vao_images = get_latest_files_by_timestamp(
        "hoa_don_mua_vao*.csv", 
        "hoadon_muavao_chitiet_stt_*.png"
    )
    ban_ra_csv, ban_ra_images = get_latest_files_by_timestamp(
        "hoa_don_ban_ra*.csv", 
        "hoadon_banra_chitiet_stt_*.png"
    )

    # Process mua vao
    if mua_vao_csv:
        data = pd.read_csv(mua_vao_csv)
        data.rename(columns={
            'Ký hiệumẫu số': 'mau_so',
            'Ký hiệuhóa đơn': 'ky_hieu',
            'Số hóa đơn': 'so_hoa_don',
            'Ngày lập': 'ngay_lap',
            'Thông tin người bán': 'thong_tin_nguoi_ban',
            'Tổng tiềnthanh toán': 'tong_tien',
            'Trạng tháihóa đơn': 'trang_thai'
        }, inplace=True)
        
        if 'thong_tin_nguoi_ban' not in data.columns:
            data['thong_tin_nguoi_ban'] = None
            
        save_to_database(data, mua_vao_images, "mua_vao")
        print(f"Processed mua vao data from {mua_vao_csv}")

    # Process ban ra
    if ban_ra_csv:
        data = pd.read_csv(ban_ra_csv)
        data.rename(columns={
            'Ký hiệumẫu số': 'mau_so',
            'Ký hiệuhóa đơn': 'ky_hieu',
            'Số hóa đơn': 'so_hoa_don',
            'Ngày lập': 'ngay_lap',
            'Thông tin hóa đơn': 'thong_tin_nguoi_mua',
            'Tổng tiềnthanh toán': 'tong_tien',
            'Trạng tháihóa đơn': 'trang_thai'
        }, inplace=True)
        
        if 'thong_tin_nguoi_mua' not in data.columns:
            data['thong_tin_nguoi_mua'] = None
            
        save_to_database(data, ban_ra_images, "ban_ra")
        print(f"Processed ban ra data from {ban_ra_csv}")

    # Fetch and verify saved images
    fetch_image_data('mua_vao')
    fetch_image_data('ban_ra')

def fetch_image_data(table_name):
    query = f"SELECT id, image_path, image_data FROM {table_name};"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                for row in rows:
                    record_id, image_path, image_data = row
                    print(f"ID: {record_id}, Path: {image_path}")
                    if image_data:
                        # Quyết định đuôi file hình ảnh là .png
                        file_extension = image_path.split('.')[-1] if image_path else 'png'
                        save_path = f"{table_name}_retrieved_{record_id}.{file_extension}"
                        
                        # Lưu hình ảnh
                        with open(save_path, 'wb') as f:
                            f.write(image_data)
                        print(f"Dữ liệu hình ảnh từ database được lưu thành: {save_path}")
    except Exception as e:
        print(f"Lỗi chuyển đổi hình ảnh từ bảng {table_name}: {e}")

def ensure_database_exists(args): #Cái này Phúc mới thêm
    try:
        # Kết nối đến database tên "postgres" mặc định để kiểm tra kết nối
        connection = psycopg2.connect(
            dbname="postgres",
            user=args.db_user,
            password=args.db_password,
            host=args.db_host,
            port=args.db_port
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            # Kiểm tra nếu database tồn tại
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (args.db_name,)
            )
            exists = cursor.fetchone()
            if not exists:
                # Tạo mới database
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(args.db_name)
                ))
                print(f"Database '{args.db_name}' created successfully.")
            else:
                print(f"Database '{args.db_name}' already exists.")
    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        raise
    finally:
        if connection:
            connection.close()

def main():
    
    """Chạy tất cả các Function trong quy trình crawl data hoadondientu"""
    
    args = parse_arguments()
    ensure_database_exists(args)
    
    # Update DB_CONFIG with parsed arguments
    global DB_CONFIG
    DB_CONFIG = get_db_config(args)
    
    driver = initialize_driver()
    
    output_file = "hoa_don_mua_vao.csv"
    output_file_ra = "hoa_don_ban_ra.csv"
    captcha_image_path = "captcha_image.svg"
    
    try:
        login_to_thuedientu(driver, args.username, args.password)
        crawl_img(driver) 
        enter_verification_code(driver, captcha_image_path)
        submit_form(driver, captcha_image_path)
        crawl_hoa_don_mua_vao(driver)
        extract_table_mua_vao_to_csv(driver, output_file)
        extract_img_hoa_don_mua_vao(driver)
        crawl_hoa_don_ban_ra(driver)
        extract_table_ban_ra_to_csv(driver, output_file_ra)
        extract_img_hoa_don_ban_ra(driver)
        main_db_workflow() 
    except Exception as e:
        print(f"An error occurred: {e}")
        send_slack_notification("Chương trình chạy thất bại", webhook_url)

if __name__ == '__main__':
    main()
