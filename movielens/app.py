from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


@app.route('/data')
def data():
    with open('analysis_results.json', 'r', encoding='utf-8') as f:
        result = json.load(f)
    return jsonify(result)


@app.route('/')
def index():
    return render_template('dashboard.html')  # 只负责前端模板
