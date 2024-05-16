# 对同程艺龙 https://www.ly.com/flights的爬取
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random

# 确认你已下载并解压缩的ChromeDriver路径
chrome_driver_path = "../utils/chromedriver-win64/chromedriver.exe"

# 配置Selenium的选项
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features')
options.add_argument('--disable-blink-features=AutomationControlled')

# 设置ChromeDriver服务
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 反检测设置
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

# 定义抓取函数
def scrape_flight_info(url):
    driver.get(url)
    sleep(random.uniform(1, 3))  # 随机等待时间以模拟用户行为
    
    try:
        # 等待页面加载并找到特定元素
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "flight-info-class-name")))

        # 这里是抓取航班信息的代码示例，需要根据实际网页结构调整
        flight_info_elements = driver.find_elements(By.CLASS_NAME, "flight-info-class-name")
        
        for i, element in enumerate(flight_info_elements):
            print(f"航班信息 {i+1}: {element.text}")

    except Exception as e:
        print(f"抓取时出错: {e}")

# 目标URL
target_url = "https://www.ly.com/flights/itinerary/oneway/SHA-PEK?date=2024-05-16&from=%E4%B8%8A%E6%B5%B7&to=%E5%8C%97%E4%BA%AC&fromairport=&toairport=&p=465&childticket=0,0"
scrape_flight_info(target_url)

# 关闭驱动
driver.quit()
