import os
import argparse
from openpyxl import load_workbook

FILE_PATH= 'company_information.xlsx'
HOADON_COMPANY="#"
HOADON_USERNAME="#"
HOADON_PASSWORD="#"


def parse_arguments():
      """Parse command-line arguments."""
      parser = argparse.ArgumentParser(description="Thêm dữ liệu vào file Excel.")
      parser.add_argument('--file-path', default=FILE_PATH, required=False,
                              help="Đường dẫn đến file Excel (mặc định: company_information.xlsx).")
      parser.add_argument('--company', default=HOADON_COMPANY, required=False, help="Tên công ty.")
      parser.add_argument('--hoadon-username',default=HOADON_USERNAME, required=False, help="Username hóa đơn.")
      parser.add_argument('--hoadon-password',default=HOADON_PASSWORD, required=False, help="Password hóa đơn.")
      return parser.parse_args()

def main():
      # Parse các tham số từ dòng lệnh hoặc biến môi trường
      args = parse_arguments()
      # Kiểm tra file tồn tại
      if not os.path.exists(args.file_path):
            print(f"File '{args.file_path}' không tồn tại. Vui lòng kiểm tra lại.")
            exit()
      
      # Mở file Excel
      workbook = load_workbook(args.file_path)
      sheet = workbook.active  # Chọn sheet đầu tiên

      # Thêm dữ liệu mới
      new_data = [args.company, args.hoadon_username, args.hoadon_password]
      sheet.append(new_data)

      # Lưu file
      workbook.save(args.file_path)
      print(f"Thêm dữ liệu thành công vào file '{args.file_path}'!")

if __name__ == "__main__":
      main()


# Truyền dữ liệu vào các cột tương ứng ở file excel [company, hoadon_username, hoadon_password]
# python .\insert_company_info_hoadon.py --company "cong ty mb" --hoadon-username "0123456789" --hoadon-password "AT12346@"