from flask import Flask, render_template
from markupsafe import Markup
import json
import re
import os

app = Flask(__name__)

# ─────────────────────────────────────────────
# 工具：把题干/答案/解析里的图片占位符转换为 <img>
# ─────────────────────────────────────────────
IMG_PAT = re.compile(
    r'\['                       # 开头 [
    r'(?:公式|图片)'             # 公式:  或  图片:
    r'[^|\]]*'                  # 可能带说明文字，非竖线/右括号
    r'\|'                       # |
    r'(https?://[^\]]+?)'       # 1⃣ URL
    r']'                        # ]
)

def convert_media(text: str) -> Markup:
    """把自定义图片占位符替换为 <img> 标签"""
    def _img(m):
        url = m.group(1)
        # 直接返回 img，不带任何额外文字
        return f'<img src="{url}" alt="图片" class="img-fluid my-2" ' \
               f'style="max-width:100%;">'
    html = IMG_PAT.sub(_img, text)
    # \n → <br>，并允许 HTML
    html = html.replace('\n', '<br>')
    return Markup(html)

# ─────────────────────────────────────────────
# 读取 JSON
# ─────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__),
                         'all_math_qa_by_section.json')
with open(DATA_PATH, encoding='utf-8') as f:
    QA_DATA = json.load(f)

@app.route('/')
def index():
    return render_template('tiku.html',
                           blocks=QA_DATA,
                           media=convert_media)

if __name__ == '__main__':
    # debug=True 方便热重载；生产环境请去掉
    app.run(host='0.0.0.0', port=5000, debug=True)
