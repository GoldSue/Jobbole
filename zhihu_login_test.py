import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import requests
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

def generate_track(distance):
    track = []
    current = 0
    while current < distance:
        step = random.randint(2, 5)
        track.append(step)
        current += step
    track += [-2, -1, 1, 1]  # 模拟回弹
    return track

def get_slider_offset_by_edge(bg_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(bg_url, headers=headers)
    img = Image.open(BytesIO(resp.content)).convert("L")
    bg = np.array(img)

    # Sobel 模糊模板进行边缘检测
    sobel = cv2.Sobel(bg, cv2.CV_64F, dx=1, dy=0, ksize=3)
    abs_sobel = np.abs(sobel)
    col_sums = abs_sobel.sum(axis=0)
    offset = int(np.argmax(col_sums))
    return offset - 8  # 按需加上缩量

# 启动 undetected-chromedriver
options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
driver = uc.Chrome(options=options)

try:
    # 打开登录页
    driver.get("https://www.zhihu.com/signin")
    time.sleep(3)

    # 切换到密码登录
    driver.find_element(By.XPATH, "//div[contains(text(),'密码登录')]").click()
    time.sleep(1)

    # 输入账号密码（替换为自己的）
    driver.find_element(By.NAME, "username").send_keys("17752535155")
    driver.find_element(By.NAME, "password").send_keys("Gold7789")

    # 点击登录
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print("✅ 已点击登录，等待验证码加载")
    time.sleep(3)
    for i in range(10):

    # 等待滑块背景图和滑块块体加载
        bg_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.yidun_bg-img"))
        )
        slider_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.yidun_jigsaw"))
        )

        bg_url = bg_img.get_attribute("src")
        slider_url = slider_img.get_attribute("src")
        print(f"✅ 背景图（缺口图）URL: {bg_url}")
        print(f"✅ 滑块小图 URL: {slider_url}")

        # 计算滑动距离
        offset = get_slider_offset_by_edge(bg_url)
        print(f"🎯 计算得到滑动距离: {offset} px")

        # 找滑块按钮
        slider = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "yidun_slider"))
        )
        driver.execute_script("arguments[0].style.border='3px solid red'", slider)
        time.sleep(0.5)

        # 生成拖动轨迹并执行滑动
        track = generate_track(offset)
        action = ActionChains(driver)
        action.click_and_hold(slider).perform()
        for x in track:
            action.move_by_offset(xoffset=x, yoffset=0).perform()
            # time.sleep(random.uniform(0.01, 0.03))
        action.release().perform()
        print("✅ 滑块已拖动")

        # 等待验证结果
        time.sleep(3)
    time.sleep(3)
    try:
        result_tip = driver.find_element(By.CLASS_NAME, "yidun_tips").text
        print(f"🎯 验证提示：{result_tip}")
    except:
        print("ℹ️ 未找到验证提示信息")


    finally:
        driver.quit()
except Exception as e:
    print(f"❌ 发生错误：{e}")


