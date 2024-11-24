from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

def get_driver(url):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url) 
    return driver   

driver = get_driver("https://web.whatsapp.com/")
time.sleep(30)
print("done")

for i in range(0,1000):
    elements = driver.find_elements(By.CSS_SELECTOR, ".selectable-text.copyable-text.x15bjb6t.x1n2onr6")
    element = elements[1]
    element.send_keys("فيقي")
    send_buttons = driver.find_elements(by=By.CLASS_NAME,value="x1c4vz4f")
    el = send_buttons[-1]
    el.click()
    time.sleep(0.1)
  


