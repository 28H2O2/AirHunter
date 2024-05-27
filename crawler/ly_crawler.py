from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
from datetime import datetime

# ChromeDriver路径
chrome_driver_path = "../utils/chromedriver-win64/chromedriver.exe"

def setup_driver(chrome_driver_path):
    """
    设置和初始化ChromeDriver。
    """
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    return driver

def fetch_flight_data(driver, url):
    """
    从指定URL获取航班信息。
    """
    driver.get(url)
    time.sleep(3)  # 模拟用户行为防止被检测为爬虫
    flights_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'flight-lists-container'))
    )
    return flights_container.find_elements(By.CLASS_NAME, 'flight-item')

def extract_flight_info(flight):
    """
    从单个航班元素中提取航班信息。
    """
    # 航班号及其拆分
    flight_no = flight.find_element(By.CLASS_NAME, 'flight-item-name').text.strip()
    airline = re.search(r'([\u4e00-\u9fa5]+)', flight_no).group(0)  # 提取中文部分
    flight_code = re.search(r'([A-Z]{2}\d+)', flight_no).group(0)  # 提取二字代码和数字
    
    # 时间处理，去除机场名
    departure_time = flight.find_element(By.CLASS_NAME, 'f-startTime').text.split('\n')[0].strip()
    arrival_time = flight.find_element(By.CLASS_NAME, 'f-endTime').text.split('\n')[0].strip()

    # 机场
    departure_airport = flight.find_element(By.XPATH, './/div[contains(@class, "f-times-con")][1]/em').text.strip()
    arrival_airport = flight.find_element(By.XPATH, './/div[contains(@class, "f-times-con")][2]/em').text.strip()

    # 价格处理
    price_text = flight.find_element(By.CLASS_NAME, 'head-prices').text.split('\n')[0]
    price = ''.join(filter(str.isdigit, price_text))

    # 机型
    flight_type = flight.find_element(By.CLASS_NAME, 'flight-item-type').text.strip()

    # 餐食
    try:
        meal_info = flight.find_element(By.CLASS_NAME, 'red-labels').text.strip()
    except:
        meal_info = '无餐食信息'

    return {
        "航空公司": airline,
        "航班号": flight_code,
        "出发时间": departure_time,
        "到达时间": arrival_time,
        "出发机场": departure_airport,
        "到达机场": arrival_airport,
        "航班价格": price,
        "机型": flight_type,
        "餐食": meal_info
    }

def save_to_csv(data, url, path='data/ly_flights'):
    """
    将采集到的数据保存为CSV文件，并按出发时间排序。
    """
    df = pd.DataFrame(data)
    df['出发时间'] = pd.to_datetime(df['出发时间'], format='%H:%M')
    df.sort_values('出发时间', inplace=True)  # 按出发时间排序
    df['出发时间'] = df['出发时间'].dt.strftime('%H:%M')  # 转换回时间格式字符串

    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    route_date = re.search(r"SHA-PEK\?date=(\d{4}-\d{2}-\d{2})", url).group(1)
    file_name = f"{path}/flights_data_{route_date}_{current_time}.csv"
    
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"航班信息已保存到 {file_name} 文件中。")

# 主执行函数
def main():
    url = "https://www.ly.com/flights/itinerary/oneway/SHA-PEK?date=2024-05-30&from=%E4%B8%8A%E6%B5%B7&to=%E5%8C%97%E4%BA%AC&fromairport=&toairport=&p=465&childticket=0,0"
    driver = setup_driver(chrome_driver_path)
    try:
        flight_items = fetch_flight_data(driver, url)
        flights_data = [extract_flight_info(flight) for flight in flight_items]
        save_to_csv(flights_data, url)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
