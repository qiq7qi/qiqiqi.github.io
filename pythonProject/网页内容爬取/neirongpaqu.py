import os
import pickle
import json
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
from bs4 import BeautifulSoup
import re

# ========== 目录路径 =============
ROOT = os.path.dirname(os.path.abspath(__file__))  # 当前py文件目录
DEBUG_DIR = os.path.join(ROOT, "debug")
if not os.path.exists(DEBUG_DIR):
    os.makedirs(DEBUG_DIR)

COOKIE_FILE = os.path.join(ROOT, 'nowcoder_cookies.pkl')
UUID_TITLE_FILE = os.path.join(ROOT, '题库uuid列表.json')
OUTPUT_FILE = os.path.normpath(os.path.join(ROOT, '../MySQL写入/all_math_qa_by_section.txt'))


# ================== Selenium启动与登录 ==================
edge_options = Options()
# edge_options.add_argument('--headless')
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--window-size=1920,1080')
service = Service(executable_path=os.path.join(ROOT, 'msedgedriver.exe'))
driver = webdriver.Edge(service=service, options=edge_options)


def load_cookies(driver, filename, url):
    with open(filename, 'rb') as f:
        cookies = pickle.load(f)
    driver.get(url)
    for cookie in cookies:
        cookie.pop('sameSite', None)
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(2)


# ========== 1. 自动登录 ==========
home_url = "https://www.nowcoder.com"
if not os.path.exists(COOKIE_FILE):
    print("未检测到cookie，请手动登录...")
    driver.get("https://www.nowcoder.com/login")
    input("请手动完成登录后回车（账号/扫码/验证码等）...")
    with open(COOKIE_FILE, 'wb') as f:
        pickle.dump(driver.get_cookies(), f)
    print("已保存cookie，后续将自动登录！")
else:
    print("检测到cookie，自动加载cookie登录...")
    load_cookies(driver, COOKIE_FILE, home_url)

# ========== 2. 读取 uuid+title 列表 ==========
if not os.path.exists(UUID_TITLE_FILE):
    print(f"未找到 {UUID_TITLE_FILE} 文件！请先运行目录采集脚本。")
    driver.quit()
    exit(1)

with open(UUID_TITLE_FILE, 'r', encoding='utf-8') as f:
    uuid_title_list = json.load(f)

print(f"共{len(uuid_title_list)}个题库模块，将自动批量爬取...")


# ========== 3. 工具函数 ==========
def scroll_to_bottom(driver, pause=1.0, max_try=15):
    last_height = driver.execute_script("return document.body.scrollHeight")
    n_try = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        n_try += 1
        if new_height == last_height or n_try >= max_try:
            break
        last_height = new_height


def extract_text_with_img(tag):
    result = ""
    for elem in tag.descendants:
        if getattr(elem, "name", None) == 'img':
            img_src = elem.get('src', '')
            img_alt = elem.get('alt', '')
            if img_alt:
                result += f"[公式:{img_alt}|{img_src}]"
            else:
                result += f"[图片:{img_src}]"
        elif elem.name is None:
            result += str(elem)
        elif elem.name == "br":
            result += "\n"
    return result.strip()


def parse_questions(content_div):
    h2s = content_div.find_all('h2')
    questions = []
    for idx, h2 in enumerate(h2s):
        q_title = extract_text_with_img(h2)
        q_blocks = []
        for sib in h2.next_siblings:
            if getattr(sib, "name", None) == 'h2':
                break
            if getattr(sib, "name", None) or str(sib).strip():
                q_blocks.append(sib)
        block_texts = [extract_text_with_img(b) for b in q_blocks if hasattr(b, 'descendants') or str(b).strip()]
        all_text = "\n".join(block_texts)
        ans_match = re.search(r"(参考答案|答案|Answer)\s*[:：]?\s*([\s\S]*?)(答案解析|解析|$)", all_text)
        exp_match = re.search(r"(答案解析|解析)\s*[:：]?\s*([\s\S]*)", all_text)
        answer = ans_match.group(2).strip() if ans_match else ''
        explanation = exp_match.group(2).strip() if exp_match else ''
        if not answer and block_texts:
            answer = block_texts[0].strip()
        questions.append({
            "question": q_title,
            "answer": answer,
            "explanation": explanation
        })
    return questions


# ========== 4. 主爬取循环 ==========
zhuanlanId = "90YvOm"
base_url = "https://www.nowcoder.com/issue/tutorial?zhuanlanId={}&uuid={}"
all_blocks = []

for idx, item in enumerate(uuid_title_list, 1):
    uuid = item['uuid']
    main_title = item['title']
    url = base_url.format(zhuanlanId, uuid)
    print(f"正在爬取 {idx}/{len(uuid_title_list)} [{main_title}] uuid={uuid}...")
    driver.get(url)
    scroll_to_bottom(driver)
    time.sleep(2)
    html = driver.page_source
    debug_file = os.path.join(DEBUG_DIR, f'debug_{idx}.html')
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(html)
    soup = BeautifulSoup(html, 'lxml')
    content_div = soup.find('div', class_="nc-post-content")
    questions = parse_questions(content_div) if content_div else []
    all_blocks.append({
        "main_title": main_title,
        "questions": questions
    })

driver.quit()

# ========== 5. 写入结果 ==========
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for block in all_blocks:
        f.write(f"\n======= {block['main_title']} =======\n\n")
        for i, item in enumerate(block['questions'], 1):
            f.write(f"题目{i}：{item['question']}\n")
            f.write(f"答案：{item['answer']}\n")
            f.write(f"解析：{item['explanation']}\n\n")
print(f"已按大标题分块保存，共计{len(all_blocks)}个模块。")
