from flask import Flask, request, redirect, url_for, session, send_from_directory
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = 'rocket_secret_key'
DB_NAME = 'database.db'

# --- НАСТРОЙКИ СЕКРЕТНОСТИ ---
SECRET_URL = 'api/v1/status' # Секретный URL (будет выглядеть как системная страница)
PASSWORD = 'superpassword123' # Твой пароль

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dox 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  key_name TEXT UNIQUE, 
                  info TEXT)''')
    conn.commit()
    conn.close()

# --- СТИЛИ ---
STYLE = """
<style>
    body { font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 40px; }
    input, button, textarea { padding: 10px; margin: 5px 0; border-radius: 5px; border: 1px solid #333; background: #222; color: #fff; }
    button { background: #007bff; cursor: pointer; border: none; font-weight: bold; }
    button:hover { background: #0056b3; }
    .card { background: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #007bff; }
    a { color: #00d4ff; text-decoration: none; }
    .cat-container { text-align: center; margin-top: 50px; }
    .cat-img { max-width: 400px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
</style>
"""

# --- ОБЫЧНЫЙ САЙТ (ЗАГЛУШКА) ---
FAKE_HTML = STYLE + """
<div class="cat-container">
    <h1>Мой личный сайт</h1>
    <p>Сайт находится в разработке. Скоро здесь будет много интересного!</p>
    <!-- Ссылка на картинку кота -->
    <img src="https://cataas.com/cat?width=400" class="cat-img" alt="Милый котик">
    <p><small>© 2026</small></p>
</div>
"""

# --- ФОРМА ВХОДА ---
LOGIN_HTML = STYLE + """
<h1>Вход в систему</h1>
<form method="POST">
    <input type="password" name="password" placeholder="Введите пароль" required>
    <button type="submit">Войти</button>
</form>
"""

# --- БАЗА ДАННЫХ (ИНТЕРФЕЙС) ---
INDEX_HTML = STYLE + """
<h1>База данных</h1>
<form method="GET" action="/{secret_url}">
    <input type="text" name="q" placeholder="Поиск по ключу..." value="{query}">
    <button type="submit">Искать</button>
    <a href="/{secret_url}/add"><button type="button" style="background: #28a745;">Добавить запись</button></a>
</form>
<hr>
<div>{results}</div>
"""

ADD_HTML = STYLE + """
<h1>Новая запись</h1>
<form method="POST" action="/{secret_url}/add">
    <label>Ключ (Никнейм, ФИО, Телефон):</label><br>
    <input type="text" name="key_name" required style="width: 100%;"><br>
    <label>Данные (Информация):</label><br>
    <textarea name="info" rows="5" required style="width: 100%;"></textarea><br>
    <button type="submit" style="background: #28a745;">Сохранить</button>
</form>
<br>
<a href="/{secret_url}">Назад</a>
"""

# --- МАРШРУТЫ ---
# Обычная страница (Кот)
@app.route('/')
def home():
    return FAKE_HTML

# Секретная страница с базой
@app.route(f'/{SECRET_URL}', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        if request.method == 'POST':
            if request.form['password'] == PASSWORD:
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                return LOGIN_HTML + "<p style='color:red;'>Неверный пароль</p>"
        return LOGIN_HTML

    query = request.args.get('q', '')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if query:
        c.execute("SELECT key_name, info FROM dox WHERE key_name LIKE ?", ('%' + query + '%',))
    else:
        c.execute("SELECT key_name, info FROM dox")
    rows = c.fetchall()
    conn.close()
    
    if rows:
        results = "".join([f'<div class="card"><h3>Ключ: {r[0]}</h3><p><strong>Данные:</strong> {r[1]}</p></div>' for r in rows])
    else:
        results = "<p>Ничего не найдено.</p>"
        
    return INDEX_HTML.format(query=query, results=results, secret_url=SECRET_URL)

# Секретная страница добавления
@app.route(f'/{SECRET_URL}/add', methods=['GET', 'POST'])
def add():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        key_name = request.form['key_name']
        info = request.form['info']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO dox (key_name, info) VALUES (?, ?)", (key_name, info))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return ADD_HTML.format(secret_url=SECRET_URL)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)