# 对同程艺龙 https://www.ly.com/flights 的爬取
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

# 设置ChromeDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# 打开目标网页
url = "https://www.ly.com/flights/itinerary/oneway/SHA-PEK?date=2024-05-16&from=%E4%B8%8A%E6%B5%B7&to=%E5%8C%97%E4%BA%A3&fromairport=&toairport=&p=465&childticket=0,0"
driver.get(url)

# 模拟用户行为防止被检测为爬虫
time.sleep(3)

# 等待包含航班信息的容器加载
flights_container = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'flight-lists-container'))
)
flight_items = flights_container.find_elements(By.CLASS_NAME, 'flight-item')

# 创建一个空的DataFrame来存储航班信息
flights_data = []

for i, flight in enumerate(flight_items, start=1):
    try:
        # 航班号
        flight_no = flight.find_element(By.CLASS_NAME, 'flight-item-name').text.strip()
        # 出发时间
        departure_time = flight.find_element(By.CLASS_NAME, 'f-startTime').text.strip()
        # 到达时间
        arrival_time = flight.find_element(By.CLASS_NAME, 'f-endTime').text.strip()
        # 出发机场
        departure_airport = flight.find_element(By.XPATH, './/div[contains(@class, "f-times-con")][1]/em').text.strip()
        # 到达机场
        arrival_airport = flight.find_element(By.XPATH, './/div[contains(@class, "f-times-con")][2]/em').text.strip()
        # 航班价格
        price_text = flight.find_element(By.CLASS_NAME, 'head-prices').text.split('\n')[0]
        price = ''.join(filter(str.isdigit, price_text))

        # 打印航班信息
        print(f"第 {i} 航班:")
        print(f"航班号: {flight_no}")
        print(f"出发时间: {departure_time}")
        print(f"到达时间: {arrival_time}")
        print(f"出发机场: {departure_airport}")
        print(f"到达机场: {arrival_airport}")
        print(f"航班价格: ¥{price} 起")
        print('-' * 40)

        # 将数据添加到列表中
        flights_data.append({
            "航班号": flight_no,
            "出发时间": departure_time,
            "到达时间": arrival_time,
            "出发机场": departure_airport,
            "到达机场": arrival_airport,
            "航班价格": price
        })

    except Exception as e:
        print(f"第 {i} 航班信息抓取失败: {str(e)}")
        continue

driver.quit()

# 获取当前时间，精确到分钟
current_time = datetime.now().strftime("%Y%m%d_%H%M")
# 提取URL中的出发地和日期
route_date = re.search(r"SHA-PEK\?date=(\d{4}-\d{2}-\d{2})", url).group(1)
# 拼接文件名
file_name = f"data/flights_data_{route_date}_{current_time}.csv"

# 将数据保存到CSV文件
df = pd.DataFrame(flights_data)
df.to_csv(file_name, index=False, encoding='utf-8-sig')
print(f"航班信息已保存到 {file_name} 文件中。")

