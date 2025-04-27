import argparse
import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.crawler_baohiemxahoi import crawler_baohiemxahoi
from src.crawler_thuedientu import crawler_thuedientu
from src.crawler_hoadondientu import crawler_hoaddondientu

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Module selection")
    parser.add_argument("--module", default="ALL", required=False, help="Chọn module cần chạy")
    module = parser.parse_args()
    
    if module == "BHXH" or module == "ALL":
        try:
            crawler_bhxh = crawler_baohiemxahoi()
            crawler_bhxh.main_logic()
        except Exception as e:
            print("\n" + "="*50)
            print("[❌] Cảnh báo ở crawler_baohiemxahoi")
            print(f"Chi tiết cảnh báo: {e}")
            print("="*50 + "\n")

    if module == "TDT" or module == "ALL":
        try:
            crawler_tdt = crawler_thuedientu()
            crawler_tdt.main_logic()
        except Exception as e:
            print("\n" + "="*50)
            print("[❌] Cảnh báo ở crawler_thuedientu")
            print(f"Chi tiết cảnh báo: {e}")
            print("="*50 + "\n")
    
    if module == "HDDT" or module == "ALL":
        try:
            crawler_hddt = crawler_hoaddondientu()
            crawler_hddt.main_logic()
        except Exception as e:
            print("\n" + "="*50)
            print("[❌] Cảnh báo ở crawler_hoaddondientu")
            print(f"Chi tiết cảnh báo: {e}")
            print("="*50 + "\n")
