from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import pickle
import re
from bs4 import BeautifulSoup
import json

# ========== 公共弹窗关闭函数 ==========
def close_dialogs(driver):
    # 多次尝试，兼容多种弹窗
    for _ in range(5):
        dialogs = driver.find_elements(By.CSS_SELECTOR, "div.el-dialog__wrapper, div.login-dialog")
        for dialog in dialogs:
            try:
                close_btns = dialog.find_elements(By.CSS_SELECTOR, "button.el-dialog__headerbtn, .el-dialog__close")
                if close_btns:
                    for btn in close_btns:
                        try:
                            btn.click()
                            print("自动关闭弹窗。")
                            time.sleep(0.3)
                        except Exception:
                            pass
            except Exception:
                pass
        time.sleep(0.3)

# ========== 启动浏览器 ==========
edge_options = Options()
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--window-size=1920,1080')
service = Service(executable_path='msedgedriver.exe')
driver = webdriver.Edge(service=service, options=edge_options)

# ========== 1. 自动加载cookie登录 ==========
def load_cookies(driver, cookie_file):
    driver.get('https://www.nowcoder.com')
    with open(cookie_file, 'rb') as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        # selenium 4.x不支持'sameSite'
        if 'sameSite' in cookie:
            del cookie['sameSite']
        if 'expiry' in cookie and isinstance(cookie['expiry'], float):
            cookie['expiry'] = int(cookie['expiry'])
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass
    driver.refresh()
    time.sleep(2)

load_cookies(driver, "nowcoder_cookies.pkl")

# ========== 2. 打开专栏主页 ==========
main_url = "https://www.nowcoder.com/issue/tutorial?zhuanlanId=90YvOm"
driver.get(main_url)
time.sleep(2)

# ========== 3. 解析目录（title列表） ==========
soup = BeautifulSoup(driver.page_source, "lxml")

sidebar_div = None
for div in soup.find_all('div', class_=re.compile(r'tw-mb-3')):
    if "数理基础" in div.get_text():
        sidebar_div = div
        break

title_list = []
if sidebar_div:
    for item in sidebar_div.find_all('span', recursive=True):
        title = item.get_text(strip=True)
        if title:
            title_list.append(title)
else:
    print("未找到左侧目录div！")

print("目录题库：", title_list)

# ========== 4. 遍历点击目录，提取uuid ==========
all_uuid_titles = []
for idx, title in enumerate(title_list):
    print(f"\n点击第{idx+1}项: {title}")
    # 每次操作前先关闭弹窗
    close_dialogs(driver)
    # 重新查找所有span（避免DOM刷新失效）
    spans = driver.find_elements(By.XPATH, '//div[contains(@class,"tw-overflow-hidden")]/span')
    # 保证下标不越界
    if idx >= len(spans):
        print("目录下标超出span数量！")
        continue
    try:
        spans[idx].click()
        time.sleep(2)  # 等待页面跳转
        cur_url = driver.current_url
        m = re.search(r"uuid=([\w\d]+)", cur_url)
        uuid = m.group(1) if m else ""
        print(f"uuid: {uuid}")
        all_uuid_titles.append({"uuid": uuid, "title": title})
    except Exception as e:
        print(f"点击第{idx+1}项失败: {e}")
        continue

print("所有 uuid+title：", all_uuid_titles)

# ========== 5. 保存为JSON ==========
with open('题库uuid列表.json', 'w', encoding='utf-8') as f:
    json.dump(all_uuid_titles, f, ensure_ascii=False, indent=2)

driver.quit()
print("全部目录/uuid已提取完毕！")
