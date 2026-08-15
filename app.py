from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
import json
import hashlib
import datetime

app = Flask(__name__)
CORS(app)

# Папка для хранения файлов
STORAGE_FOLDER = "storage"
MODS_FILE = os.path.join(STORAGE_FOLDER, "mods.zip")
VERSIONS_FILE = "versions.json"

# Проверяем и создаём папку (если её нет)
if not os.path.exists(STORAGE_FOLDER):
    os.makedirs(STORAGE_FOLDER)
    
# ============ ОСНОВНЫЕ ЭНДПОИНТЫ ============

@app.route('/')
def index():
    """Проверка, что сервер работает"""
    return jsonify({
        "status": "online",
        "service": "GTA SA Launcher API",
        "version": "1.0.0",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/versions')
def get_versions():
    """Возвращает версии модов"""
    try:
        with open(VERSIONS_FILE, 'r') as f:
            versions = json.load(f)
        return jsonify(versions)
    except FileNotFoundError:
        default = {
            "mods_version": "1.0.0",
            "launcher_version": "1.0.0",
            "update_required": False,
            "message": "Добро пожаловать! Все моды установлены."
        }
        with open(VERSIONS_FILE, 'w') as f:
            json.dump(default, f, indent=2)
        return jsonify(default)

@app.route('/api/news')
def get_news():
    """Новости для лаунчера"""
    return jsonify({
        "news": [
            {
                "title": "🎉 Первый релиз!",
                "date": "2026-08-15",
                "text": "Лаунчер запущен! Скачивайте новые миссии."
            },
            {
                "title": "🚗 Новые миссии готовятся",
                "date": "2026-08-16",
                "text": "Скоро добавятся 5 новых миссий с ограблениями."
            }
        ]
    })

@app.route('/api/download/mods')
def download_mods():
    """Скачивание архива с модами"""
    if os.path.exists(MODS_FILE):
        return send_file(
            MODS_FILE, 
            as_attachment=True, 
            download_name="mods.zip"
        )
    else:
        return jsonify({"error": "Файл с модами не найден"}), 404

@app.route('/api/mods/info')
def mods_info():
    """Информация о модах"""
    if os.path.exists(MODS_FILE):
        file_size = os.path.getsize(MODS_FILE)
        with open(MODS_FILE, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return jsonify({
            "exists": True,
            "size": file_size,
            "hash": file_hash,
            "url": "/api/download/mods"
        })
    else:
        return jsonify({"exists": False})

# ============ АДМИНКА ДЛЯ ЗАГРУЗКИ МОДОВ ============

@app.route('/admin/upload', methods=['POST'])
def upload_mods():
    """Загрузка нового архива с модами (для вас)"""
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Имя файла пустое"}), 400
    
    file.save(MODS_FILE)
    
    # Обновляем версию
    try:
        with open(VERSIONS_FILE, 'r') as f:
            versions = json.load(f)
    except:
        versions = {}
    
    old_version = versions.get("mods_version", "1.0.0")
    major, minor, patch = old_version.split('.')
    patch = str(int(patch) + 1)
    new_version = f"{major}.{minor}.{patch}"
    versions["mods_version"] = new_version
    versions["update_required"] = True
    versions["message"] = f"Новая версия {new_version} готова к установке!"
    
    with open(VERSIONS_FILE, 'w') as f:
        json.dump(versions, f, indent=2)
    
    return jsonify({
        "status": "success",
        "new_version": new_version,
        "message": "Моды успешно загружены!"
    })

# ============ ЗАПУСК ============

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
