import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.crawler_baohiemxahoi import crawler_baohiemxahoi

if __name__ == '__main__':
    crawler = crawler_baohiemxahoi()
    crawler.main_logic()
