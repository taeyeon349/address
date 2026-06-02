import sqlite3
from flask import Flask, render_template, request, jsonify, session, send_from_directory
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'

# 실행중인 파이썬 파일과 같은 위치에 DB 파일이 생성되도록 설정
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT)')
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '1234')")
        except sqlite3.IntegrityError:
            pass
        conn.commit()

# --- [정적 JS 파일 라우팅 처리] ---
# templates 폴더 안의 subfolder(auth, search)에서 .js 파일을 직접 읽어올 수 있게 합니다.
@app.route('/templates/<subfolder>/<filename>.js')
def serve_js(subfolder, filename):
    return send_from_directory(os.path.join(app.template_folder, subfolder), f"{filename}.js", mimetype='application/javascript')

# --- [페이지 렌더링 라우트] ---
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('auth/login.html') # 폴더 구분 반영
    return render_template('search/index.html') # 폴더 구분 반영

# --- [API 라우트: 로그인/로그아웃] ---
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (data.get('username'), data.get('password')))
        user = cursor.fetchone()
    if user:
        session['logged_in'] = True
        session['username'] = data.get('username')
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '로그인 실패'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# --- [API 라우트: 주소록 및 검색] ---
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    if not session.get('logged_in'): return jsonify({'error': '권한없음'}), 403
    search_query = request.args.get('search', '')
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?", (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("SELECT * FROM contacts")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows])

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    if not session.get('logged_in'): return jsonify({'error': '권한없음'}), 403
    data = request.get_json()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (data.get('name'), data.get('phone'), data.get('email')))
        conn.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',port=5000)
