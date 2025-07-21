import pandas as pd
from sqlalchemy import create_engine
import pickle
import json

# 数据库连接
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/movielens?charset=utf8mb4')

# 读取数据
ratings = pd.read_sql('SELECT * FROM ratings', engine)
movies = pd.read_sql('SELECT * FROM movies', engine)

# 1. 评分最高前10（至少50条评分）
highscore = ratings.groupby('movieId').agg(avg_rating=('rating', 'mean'), cnt=('rating', 'count'))
highscore = highscore[highscore['cnt'] > 50]
highscore = highscore.sort_values('avg_rating', ascending=False).head(10)
highscore = highscore.merge(movies[['movieId', 'title']], on='movieId')

# 2. 评分最多前10
most_rated = ratings.groupby('movieId').size().sort_values(ascending=False).head(10).reset_index(name='rating_count')
most_rated = most_rated.merge(movies[['movieId', 'title']], on='movieId')

# 3. 最活跃用户前10
active_users = ratings.groupby('userId').size().sort_values(ascending=False).head(10).reset_index(name='count')

# 4. 观影高峰期（按小时）
ratings['hour'] = pd.to_datetime(ratings['timestamp']).dt.hour
view_peak = ratings.groupby('hour').size().reset_index(name='count')

# ======= 结构化数据，便于前端可视化 =======

result = {
    # 评分最高前10
    "highscore": {
        "titles": highscore['title'].tolist(),
        "avg_ratings": highscore['avg_rating'].round(2).tolist(),
        "counts": highscore['cnt'].tolist(),
    },
    # 评分最多前10
    "mostrated": {
        "titles": most_rated['title'].tolist(),
        "rating_counts": most_rated['rating_count'].tolist(),
    },
    # 最活跃用户前10
    "activeusers": {
        "userIds": active_users['userId'].astype(str).tolist(),
        "counts": active_users['count'].tolist(),
    },
    # 观影高峰期
    "viewpeak": {
        "hours": view_peak['hour'].tolist(),
        "counts": view_peak['count'].tolist(),
    }
}

# 保存为 pickle，供 Flask 后端/接口使用
with open('analysis_results.pkl', 'wb') as f:
    pickle.dump(result, f)

with open('analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("数据分析已完成，结果已保存为 analysis_results.pkl 和 analysis_results.json，可供前端美观可视化使用！")
