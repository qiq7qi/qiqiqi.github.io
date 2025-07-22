from flask import Flask, render_template
import pymysql

app = Flask(__name__)


def get_all_tiku():
    # 修改为你的MySQL配置
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='tiku',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT question, answer, explanation, tag, company_tag FROM timu ORDER BY id ASC')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # 按tag分组
    from collections import defaultdict
    tag_blocks = defaultdict(list)
    for question, answer, explanation, tag, company_tag in rows:
        tag_blocks[tag].append({
            'question': question,
            'answer': answer,
            'explanation': explanation,
            'company_tag': company_tag
        })
    # 变为 [{'main_title': tag, 'questions': [...]}, ...] 结构，方便模板渲染
    all_blocks = [{'main_title': tag, 'questions': qs} for tag, qs in tag_blocks.items()]
    return all_blocks


@app.route('/')
def index():
    all_blocks = get_all_tiku()
    return render_template('tiku.html', all_blocks=all_blocks)


if __name__ == '__main__':
    app.run(debug=True)
