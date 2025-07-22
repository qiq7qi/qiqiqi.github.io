import re
import pymysql
import os

DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(DIR, 'all_math_qa_by_section.txt')


def clean_question(question):
    """
    去除题目前缀 "题目X:"、"问："等，只保留纯题干
    """
    # 去掉"题目X："前缀
    question = re.sub(r"^题目\d+\s*[:：]", "", question)
    # 去掉"问："前缀
    question = re.sub(r"^问\s*[:：]", "", question)
    # 再去首尾空格
    return question.strip()


def clean_text(text):
    return re.sub(r'[○●]', '', text).strip()


def extract_company(question):
    """
    从题干末尾（括号）里提取公司名，如 "（腾讯）"，返回“腾讯”。没有则返回空字符串。
    """
    m = re.search(r'（([\u4e00-\u9fa5A-Za-z\d]+)）$', question)
    if m:
        return m.group(1).strip()
    return ""


def main():
    # 1. 连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='tiku',
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # 2. 读取题库文件
    with open(TXT_PATH, encoding='utf-8') as f:
        content = f.read()

    # 3. 按大标题分块
    section_blocks = re.split(r'\n=+ (.+?) =+\n+', content)
    # ['', tag1, block1, tag2, block2, ...]
    all_records = []
    for i in range(1, len(section_blocks), 2):
        tag = section_blocks[i].strip()  # 大标题
        block = section_blocks[i + 1]
        # 每个block内部，按“题目\d+：”分割
        questions = re.split(r'\n题目\d+：', block)
        questions = [q.strip() for q in questions if q.strip()]
        for qblock in questions:
            # 答案：/解析： 分割
            q_match = re.search(r'^(.*?)(答案：|答：)', qblock, re.S)
            a_match = re.search(r'(答案：|答：)\s*(.*?)(解析：|解析|$)', qblock, re.S)
            e_match = re.search(r'(解析：|解析)\s*(.*)', qblock, re.S)

            raw_question = clean_text(q_match.group(1)) if q_match else ''
            answer = clean_text(a_match.group(2)) if a_match else ''
            explanation = clean_text(e_match.group(2)) if e_match else ''

            company_tag = extract_company(raw_question)

            # 去掉末尾括号公司名，再去前缀
            question_no_company = re.sub(r'（[\u4e00-\u9fa5A-Za-z\d]+）$', '', raw_question).strip()
            question_clean = clean_question(question_no_company)

            all_records.append((question_clean, answer, explanation, tag, company_tag))

    print(f"检测到{len(all_records)}道题")

    for idx, (q, a, e, tag, company_tag) in enumerate(all_records, 1):
        print(f'第{idx}题\nQ:{q}\nA:{a}\nE:{e}\nTAG:{tag}\nCOMPANY:{company_tag}\n')
        try:
            sql = "INSERT INTO timu (question, answer, explanation, tag, company_tag) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (q, a, e, tag, company_tag))
        except Exception as ex:
            print(f"第{idx}题插入失败：", ex)

    conn.commit()
    cursor.close()
    conn.close()
    print("所有题目已导入数据库！")


if __name__ == '__main__':
    main()
