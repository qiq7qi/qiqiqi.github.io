import re
import json

with open('all_math_qa_by_section.txt', encoding='utf-8') as f:
    content = f.read()

section_blocks = re.split(r'\n=+ (.+?) =+\n+', content)
all_blocks = []
for i in range(1, len(section_blocks), 2):
    tag = section_blocks[i].strip()
    block = section_blocks[i + 1]
    questions = re.split(r'\n题目\d+：', block)
    questions = [q.strip() for q in questions if q.strip()]
    question_list = []
    for qblock in questions:
        ans_match = re.search(r'(答案：|答：)\s*(.*?)(解析：|解析|$)', qblock, re.S)
        e_match = re.search(r'(解析：|解析)\s*(.*)', qblock, re.S)
        q_match = re.search(r'^(.*?)(答案：|答：)', qblock, re.S)
        question = q_match.group(1).strip() if q_match else ''
        answer = ans_match.group(2).strip() if ans_match else ''
        explanation = e_match.group(2).strip() if e_match else ''
        # 简单公司名抽取
        company_tag = ''
        m = re.search(r'（([\u4e00-\u9fa5A-Za-z\d]+)）$', question)
        if m:
            company_tag = m.group(1)
            question = re.sub(r'（[\u4e00-\u9fa5A-Za-z\d]+）$', '', question).strip()
        question_list.append({
            'question': question,
            'answer': answer,
            'explanation': explanation,
            'company_tag': company_tag
        })
    all_blocks.append({
        'main_title': tag,
        'questions': question_list
    })

with open('all_math_qa_by_section.json', 'w', encoding='utf-8') as f:
    json.dump(all_blocks, f, ensure_ascii=False, indent=2)
