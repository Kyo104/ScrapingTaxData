from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
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
from sqlalchemy import create_engine
from sqlalchemy.sql import text



print(pd.__version__, np.__version__)
print('hello baohiemxahoi')


# task 1 Đăng nhập vào website https://dichvucong.baohiemxahoi.gov.vn/#/index
def initialize_driver():
      """Khởi tạo trình duyệt Chrome."""
      chrome_options = Options()
      # chrome_options.add_argument("--headless=new") # for Chrome >= 109
      chrome_options.add_argument("--disable-gpu") # Tắt GPU rendering
      chrome_options.add_argument("--no-sandbox")  # Bỏ qua chế độ sandbox
      chrome_options.add_argument("--disable-dev-shm-usage")  # Vô hiệu hóa dev-shm usage
      chrome_options.add_argument("--remote-debugging-port=9222")  # Cấu hình cổng cho DevTools
      chrome_options.add_argument("--disable-software-rasterizer")  # Tắt phần mềm rasterizer (để tránh lỗi bộ nhớ thấp)
      chrome_options.add_argument("--force-device-scale-factor=1")  # Điều chỉnh tỷ lệ hiển thị của thiết bị
      chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Ẩn việc sử dụng WebDriver
      chrome_options.add_argument("--disable-extensions")  # Tắt các tiện ích mở rộng
      chrome_options.add_argument("--enable-javascript")  # Bật JavaScript

      
      
      driver = webdriver.Chrome(options=chrome_options)
      
      driver.maximize_window()  # Mở trình duyệt ở chế độ toàn màn hình
      time.sleep(5)
      return driver
      


# 1.1 Nhập username và password vào trang web 'baohiemxahoi'
def login_to_baohiemxahoi(driver, username, password):
      """Đăng nhập vào trang web 'baohiemxahoi'."""
      url = 'https://dichvucong.baohiemxahoi.gov.vn/#/index'
      driver.get(url)
      print('- Finish initializing a driver')
      time.sleep(5)
      driver.save_screenshot('screenshot1.png')

      # Nhấn nút Đăng nhập
      login_button = driver.find_element(By.XPATH, "//span[contains(text(), ' Đăng nhập ')]")                                   
      login_button.click()
      time.sleep(3)
      print('- Finish Task 1: Login to baohiemxahoi')
      driver.save_screenshot('screenshot2.png')

      
      
      # Nhấn nút Tổ chức
      to_chuc_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Tổ chức')]")
      to_chuc_button.click()
      time.sleep(3)
      print('- Finish Task 1: click to to_chuc')
      driver.save_screenshot('screenshot3.png')


      # Nhập tên đăng nhập
      username_field = driver.find_element(By.XPATH, '//input[@placeholder="Mã số thuế"]')
      username_field.send_keys(username)
      print('- Finish keying in username_field')
      time.sleep(3)
      driver.save_screenshot('screenshot4.png')


      # Nhập mật khẩu
      password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Mật khẩu"]'))
      )
      driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
      driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
      driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", password_field)

      
      # Kiểm tra giá trị sau khi nhập
      entered_password = password_field.get_attribute('value')
      print(f"[DEBUG] Password entered: {entered_password}")
      print('- Finish keying in password_field')
      time.sleep(3)
      driver.save_screenshot('screenshot5.png')
     
      
      

# Tải ảnh CAPTCHA về máy
def save_captcha_image(driver):
      """Tải ảnh CAPTCHA về máy."""
      try:
            # Tìm thẻ <img> có alt="captcha"
            captcha_element = driver.find_element(By.XPATH, '//img[@alt="captcha"]')

            # Lấy giá trị của thuộc tính src chứa ảnh CAPTCHA (dạng base64)
            captcha_src = captcha_element.get_attribute("src")

            # Kiểm tra nếu src chứa dữ liệu base64 (chắc chắn dữ liệu ảnh được mã hóa trong src)
            if captcha_src.startswith("data:image/png;base64,"):
                  # Loại bỏ phần đầu của chuỗi base64 (đến "base64,"), chỉ lấy phần thực tế của dữ liệu ảnh
                  base64_data = captcha_src.split('base64,')[1]

                  # Giải mã base64 để lấy dữ liệu ảnh
                  img_data = base64.b64decode(base64_data)

                  # Tạo ảnh từ dữ liệu byte
                  image = Image.open(BytesIO(img_data))

                  # Lưu ảnh dưới dạng file .png
                  image.save("captcha_image.png")
                  print("[INFO] CAPTCHA đã được lưu tại captcha_image.png")
            else:
                  print("[ERROR] Không tìm thấy dữ liệu base64 trong src của ảnh CAPTCHA.")
      except Exception as e:
            print(f"[ERROR] Lỗi khi lưu ảnh CAPTCHA: {e}")
      
API_KEY = "Thay API Key Vào đây"  # Thay bằng API Key của bạn từ autocaptcha

# Gửi ảnh lên autocaptcha để giải mã
def solve_captcha(image_base64):
      """Gửi ảnh base64 lên autocaptcha và nhận mã CAPTCHA."""
      url = "https://autocaptcha.pro/api/captcha"
      payload = {
            "apikey": API_KEY,
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
                  return None
      except Exception as e:
            print(f"[ERROR] Lỗi khi gửi yêu cầu giải CAPTCHA: {e}")
            return None
  
# Xử lý ảnh CAPTCHA và giải mã
def solve_captcha_from_file(file_path):
      """Đọc file CAPTCHA và gửi lên AntiCaptcha để giải mã."""
      try:
            # Đọc file captcha
            with open(file_path, 'rb') as file:
                  img = Image.open(file)
                  buffered = BytesIO()
                  img.save(buffered, format="PNG")
                  image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Gửi ảnh base64 lên AntiCaptcha để giải mã
            captcha_text = solve_captcha(image_base64)

            # Chỉ trả về kết quả
            return captcha_text
      except Exception as e:
            print(f"[ERROR] Lỗi khi xử lý ảnh CAPTCHA: {e}")
            return None


# # 1.2 Nhập mã CAPTCHA tự động
# def enter_verification_code(driver, captcha_image_path):
#     """Giải mã CAPTCHA từ file và tự động nhập vào trường xác nhận."""
#     try:
#         # Giải mã CAPTCHA chỉ một lần
#         captcha_code = solve_captcha_from_file(captcha_image_path)
#         if not captcha_code:
#             print("[ERROR] Không thể giải mã CAPTCHA.")
#             return False

#         # Tìm trường nhập CAPTCHA
#         verification_code_field = driver.find_element(By.XPATH, '//input[@placeholder="Nhập mã kiểm tra"]')

#         # Nhập mã CAPTCHA vào trường
#         verification_code_field.clear()
#         verification_code_field.send_keys(captcha_code)
#         time.sleep(2)

#         # Log giá trị sau khi nhập để kiểm tra
#         captcha_value = verification_code_field.get_attribute('value')
#         print(f"[INFO] CAPTCHA đã nhập: {captcha_value}")

#         return True
#     except Exception as e:
#         print(f"[ERROR] Lỗi khi nhập mã CAPTCHA: {e}")
#         return False



# 1.2 Nhập mã captcha thủ công
def enter_verification_code(driver):
      """Nhập mã xác nhận."""
      # Yêu cầu người dùng nhập mã xác nhận
      code = input("Vui lòng nhập mã xác nhận: ")  # Người dùng tự nhập mã xác nhận
      # Tìm và nhập Mã xác nhận
      verification_code_field = driver.find_element(By.XPATH, '//input[@placeholder="Nhập mã kiểm tra"]')
      verification_code_field.clear()
      verification_code_field.send_keys(code)
      print('- Finish keying in verification code')
      time.sleep(2)
      # Log giá trị sau khi nhập
      captcha_value = verification_code_field.get_attribute('value')
      print(f"[DEBUG] Giá trị Mã xác nhận sau khi nhập: {captcha_value}")
      driver.save_screenshot('screenshot6.png')

      
    
    
# Hàm nhập lại các trường thông tin khi mã captcha giải sai
def retry_input(driver, username, password):
    # Nhấn nút Tổ chức
      to_chuc_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Tổ chức')]")
      to_chuc_button.click()
      time.sleep(5)
      print('- Finish Task 2: click to to_chuc')
      driver.save_screenshot('screenshot8.png')
      

      # Nhập tên đăng nhập ma so thue
      username_field = driver.find_element(By.XPATH, '//input[@placeholder="Mã số thuế"]')
      username_field.clear()
      username_field.send_keys(username)
      print('- Finish keying in username_field')
      time.sleep(3)
      driver.save_screenshot('screenshot9.png')
      
      
      
      # # Nhập mật khẩu
      password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Mật khẩu"]'))
      )
      # password_field.send_keys(password)
      driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
      driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
      driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", password_field)
      
      # Kiểm tra giá trị sau khi nhập
      entered_password = password_field.get_attribute('value')
      print(f"[DEBUG] Password entered: {entered_password}")
      print('- Finish keying in password_field')
      time.sleep(3)
      driver.save_screenshot('screenshot10.png')
      
      
      
      
      
      

      
      
      
      
         
# 1.3 Nhấn nút đăng nhập sau cùng hoàn tất việc login vào trang web nếu login failed thì login lại
def submit_form(driver, username, password, captcha_image_path):
      """Nhấn nút để hoàn tất đăng nhập và kiểm tra kết quả đăng nhập."""
      try:
            attempt = 0  # Biến theo dõi số lần thử đăng nhập
            # Sử dụng vòng lặp để thử lại nếu đăng nhập thất bại
            while True:
                  attempt += 1  # Tăng số lần thử đăng nhập

                  # Xây dựng XPath cho nút đăng nhập tùy thuộc vào số lần thử
                  submit_button_xpath = f'//*[@id="mat-dialog-{attempt-1}"]/app-dialog-login/form/div/div[2]/button[2]/span'
                  driver.save_screenshot('screenshot7.png')

                  
                  
                  try:
                        submit_button = driver.find_element(By.XPATH, submit_button_xpath)
                        submit_button.click()
                        print(f'- Finish submitting the form (attempt {attempt})')
                  except NoSuchElementException:
                        print(f"[ERROR] Không tìm thấy nút đăng nhập cho attempt {attempt}. Đang thử lại...")

                        # Kiểm tra nếu đăng nhập thành công (dựa trên sự xuất hiện của thẻ span với class idAccount)
                  try:
                        # Kiểm tra sự xuất hiện của thẻ span có class 'idAccount'
                        WebDriverWait(driver, 10).until(
                              EC.presence_of_element_located((By.CLASS_NAME, "idAccount")) 
                        )
                        print("[INFO] Đăng nhập thành công!")
                        break  # Đăng nhập thành công, thoát khỏi vòng lặp
                  except TimeoutException:
                        print(f"[DEBUG] Không thấy thẻ idAccount ở attempt {attempt}. Đang thử lại...")

                        # Đăng nhập không thành công, nhập lại thông tin
                        print("[ERROR] Đăng nhập thất bại. Đang thử lại...")

                        # Nhập lại các trường thông tin
                        retry_input(driver, username, password)

                        # Lưu và giải mã CAPTCHA mới
                        save_captcha_image(driver)
                        enter_verification_code(driver)  # Nhập mã CAPTCHA thủ công
                        # enter_verification_code(driver, captcha_image_path)  # Nhập mã CAPTCHA tự động
      except Exception as e:
            print(f"Đã xảy ra lỗi khi nhấn nút submit: {e}")



def get_unique_filename(base_filename):
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

            
            
def download_blob_pdf(driver, save_path):
      """
      Tải file PDF từ blob URL thông qua JavaScript và lưu vào đường dẫn chỉ định.
      """
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
            """, driver.current_url)

            # Tạo tên file duy nhất và lưu file
            unique_save_path = get_unique_filename(save_path)
            with open(unique_save_path, "wb") as pdf_file:
                  pdf_file.write(base64.b64decode(pdf_data))
            print(f"[INFO] Tệp PDF đã được lưu tại: {save_path}")
            return unique_save_path # Trả về đường dẫn file PDF duy nhất
      except Exception as e:
            print(f"[ERROR] Lỗi khi tải file từ blob URL: {e}")
            return None
            
            

def download_tab_data(driver, save_path):
      """
      Lấy dữ liệu từ tab mới, kiểm tra và tải file PDF nếu URL là blob.
      """
      try:
            # Lấy danh sách các tab hiện tại
            current_tabs = driver.window_handles

            # Chuyển sang tab mới nhất
            driver.switch_to.window(current_tabs[-1])
            print("[INFO] Đã chuyển sang tab mới.")

            # Lấy URL của tab mới
            current_url = driver.current_url
            print(f"[INFO] URL tab mới: {current_url}")

            # Kiểm tra nếu URL là blob và tải file PDF
            if current_url.startswith("blob:"):
                  print("[INFO] Đang xử lý file từ blob URL...")
                  return download_blob_pdf(driver, save_path)  # Truyền `driver` thay vì `current_url`
            else:
                  print("[INFO] URL không phải blob, kiểm tra lại cấu trúc hoặc xử lý thêm.")
                  return None
      except Exception as e:
            print(f"[ERROR] Lỗi khi lấy dữ liệu từ tab mới: {e}")
            return None




def chon_thang(driver):
    while True:
        try:
            # Nhập số từ 1 đến 12
            thang = int(input("Nhập số tương ứng với tháng (1 đến 12): "))
            if 1 <= thang <= 12:
                break
            else:
                print("Vui lòng nhập số từ 1 đến 12.")
        except ValueError:
            print("Vui lòng nhập một số hợp lệ.")

    # Xác định ID tương ứng với tháng
    thang_id = f"mat-option-{thang - 1}"  # ID bắt đầu từ 'mat-option-0' cho tháng 1

    try:
        # Nhấn vào phần tử tương ứng
        du_lieu_button = driver.find_element(By.ID, thang_id)
        du_lieu_button.click()
        print(f"- Finish click vào tháng {thang}")
        time.sleep(3)
    except Exception as e:
        print(f"Không thể click vào tháng {thang}. Lỗi: {e}")


# Hàm trích xuất dữ liệu và xuất ra CSV:
def extract_specific_rows(pdf_path, output_csv_path):
      """
      Trích xuất các cột cuối cùng từ các hàng chứa các tiêu đề cụ thể
      và lưu thông tin ra file CSV.
      
      Args:
            pdf_path (str): Đường dẫn đến file PDF.
            output_csv_path (str): Đường dẫn lưu file CSV.
      """
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
      unique_csv_path = get_unique_filename(output_csv_path) 
                      
      # Tạo DataFrame và lưu ra file CSV
      df = pd.DataFrame([extracted_data])
      df.to_csv(unique_csv_path, index=False, encoding="utf-8-sig")
      print(f"[INFO] Dữ liệu đã được lưu tại: {unique_csv_path}")
        
                   
      
# Task 2 Chọn vào mục Tra cứu Hồ sơ >> Tra cứu C12 >> Tra cứu để crawl data về máy
def crawl(driver):
      # Nhấn nút tra cứu Hồ sơ
      tra_cuu_button = driver.find_element(By.XPATH, '//*[@id="content"]/div[1]/div/div/div[2]/div[1]/ul/li[4]/a')
      tra_cuu_button.click()
      print('- Finish click Tra cuu Hồ sơ')
      time.sleep(3)
      
      # Nhấn nút Tra cứu C12
      tra_cuu_c12_button = driver.find_element(By.XPATH, '/html/body/app-root/app-portal/div/app-siderbar/div/div/ul/li[9]/a/span/span')
      tra_cuu_c12_button.click()
      print('- Finish click Tra cuu C12')
      time.sleep(3)
      
      # nhấn vào nút sổ các tháng cần tra cứu
      du_lieu_button = driver.find_element(By.CLASS_NAME, 'mat-select-arrow-wrapper')
      du_lieu_button.click()
      print('- Finish click các tháng cần tra cứu')
      time.sleep(3)
      
      # # nhấn vào tháng 4 để tra cứu
      # du_lieu_button = driver.find_element(By.ID, 'mat-option-6') 
      # du_lieu_button.click()
      # print('- Finish click các tháng Bảy')
      # time.sleep(3)
      
      # Gọi đến hàm chon_thang cần crawl data về 
      chon_thang(driver) # Nhập tháng cần lấy data

      # nhấn vào nút Tra cứu 
      du_lieu_button = driver.find_element(By.CLASS_NAME, 'mat-raised-button')
      du_lieu_button.click()
      print('- Finish click nút Tra cứu')
      time.sleep(10)
      
      
      # gọi đến hàm lưu dữ liệu về máy
      save_path = "Mau_C12_TS.pdf"  # Đường dẫn lưu file
      
      
      unique_pdf_path = download_tab_data(driver, save_path)
      if unique_pdf_path:
            # Gọi hàm để trích xuất dữ liệu ra file CSV
            output_csv_path = "extracted_data.csv"  # Đường dẫn lưu file CSV mặc định
            extract_specific_rows(unique_pdf_path, output_csv_path)
      else:
            print("[ERROR] Không tải được file PDF, không thể trích xuất dữ liệu.")
      
      

 # Hàm tạo và kết nối đến database PostgreSQL
def create_and_connect_to_database(db_name, user, password, host='localhost', port='5432'):
    """Tạo một database mới nếu chưa tồn tại và kết nối đến nó."""
    # Kết nối đến PostgreSQL
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}', isolation_level='AUTOCOMMIT')

    # Tạo database nếu chưa tồn tại
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM pg_catalog.pg_database WHERE datname = :db_name"), {"db_name": db_name})
        exists = result.fetchone()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' đã được tạo.")
        else:
            print(f"Database '{db_name}' đã tồn tại.")

    # Kết nối đến database vừa tạo
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')
    print(f"Kết nối thành công đến database: {db_name}")
    return engine     
    
def load_csv_to_database(csv_file_path, engine):
    try:
        # Đọc file CSV vào DataFrame
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')  # Sử dụng encoding phù hợp
        
        # Lưu DataFrame vào bảng trong database
        df.to_sql('extracted_data', engine, if_exists='append', index=False)  # Thay thế bảng nếu đã tồn tại
        print(f"[INFO] Dữ liệu đã được lưu vào bảng 'extracted_data' trong database.")
    except Exception as e:
        print(f"[ERROR] Lỗi khi lưu dữ liệu vào database: {e}")

    
      
def main():
      """Chạy tất cả các bước trong quy trình đăng nhập."""
      driver = initialize_driver()
      
      # Thay thế username, password vào
      # username = input("Nhập tên đăng nhập (username): ")                      #  0101850613
      # password = input("Nhập mật khẩu (password): ")                          #  @ATDT2024
      
      username = "0101850613"                      
      password =  "@ATDT2024"                                                                                                 
      
      captcha_image_path = "captcha_image.png"

      # Thông tin PostgreSQL
      pg_user = "postgres"  # Tên người dùng PostgreSQL
      pg_password = "123456"  # Mật khẩu PostgreSQL
      db_name = 'data_bao_hiem_xa_hoi'  # Tên database

      save_path = "Mau_C12_TS.pdf"
      
      try:
            login_to_baohiemxahoi(driver, username, password)
            
            save_captcha_image(driver)
            
            enter_verification_code(driver) #thủ công
            # enter_verification_code(driver, captcha_image_path) # tự động
            
            submit_form(driver, username, password, captcha_image_path)
            
            crawl(driver)

            # Kết nối tới database PostgreSQL
            print("[INFO] Đang kết nối tới database PostgreSQL...")
            engine = create_and_connect_to_database(db_name, pg_user, pg_password)

            # Đường dẫn tới file CSV
            output_csv_path = "extracted_data.csv"  # Đường dẫn lưu file CSV
            extract_specific_rows(save_path, output_csv_path)

            # Gọi hàm để lưu dữ liệu từ CSV vào database
            load_csv_to_database(output_csv_path, engine)
            
      except Exception as e:
            print(f"An error occurred: {e}")
      #     finally:
      #         driver.quit()  # Đóng trình duyệt sau khi hoàn thành

if __name__ == '__main__':
      main()
      