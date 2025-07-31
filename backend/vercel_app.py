from app import create_app
from flask import jsonify

app = create_app()

# Vercel使用WSGI处理程序，需要一个名为app的应用实例
# 这个文件作为Vercel的入口点

@app.route('/')
def home():
    return jsonify({'message': 'EasyCook API is running on Vercel'})