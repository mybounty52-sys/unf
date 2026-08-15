import os
import sys
import subprocess
import urllib.request
import zipfile
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser

# ============ НАСТРОЙКИ ============
# ЗДЕСЬ ВАШ URL ОТ RAILWAY (ПОТОМ ЗАМЕНИТЕ)
API_URL = "https://ваш-проект.railway.app"  # <-- ИЗМЕНИТЕ ПОСЛЕ ДЕПЛОЯ!

# Путь к игре (игрок может изменить)
GAME_PATH = "C:/Program Files (x86)/Rockstar Games/GTA San Andreas"
# ===================================

class GTALauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 GTA San Andreas Launcher")
        self.root.geometry("750x550")
        self.root.configure(bg='#1a1a2e')
        
        # Заголовок
        title = tk.Label(root, text="🚗 GTA San Andreas Launcher", 
                        font=("Arial", 24, "bold"), bg='#1a1a2e', fg='#e94560')
        title.pack(pady=15)
        
        # Статус
        self.status_label = tk.Label(root, text="🔄 Проверка обновлений...", 
                                     font=("Arial", 11), bg='#1a1a2e', fg='#eeeeee')
        self.status_label.pack(pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(root, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        self.play_btn = tk.Button(btn_frame, text="🎮 ИГРАТЬ", command=self.play_game,
                                 bg='#e94560', fg='white', font=("Arial", 14, "bold"),
                                 width=12, height=2, relief='flat')
        self.play_btn.pack(side=tk.LEFT, padx=8)
        
        self.update_btn = tk.Button(btn_frame, text="📥 ОБНОВИТЬ", command=self.check_updates,
                                   bg='#0f3460', fg='white', font=("Arial", 12),
                                   width=12, height=2, relief='flat')
        self.update_btn.pack(side=tk.LEFT, padx=8)
        
        self.settings_btn = tk.Button(btn_frame, text="⚙️ НАСТРОЙКИ", command=self.open_settings,
                                     bg='#16213e', fg='white', font=("Arial", 12),
                                     width=12, height=2, relief='flat')
        self.settings_btn.pack(side=tk.LEFT, padx=8)
        
        # Новости
        news_frame = tk.LabelFrame(root, text="📰 Новости", bg='#1a1a2e', fg='#eeeeee',
                                  font=("Arial", 11, "bold"))
        news_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.news_text = tk.Text(news_frame, height=4, bg='#16213e', fg='#eeeeee',
                                 font=("Arial", 9), wrap=tk.WORD, relief='flat')
        self.news_text.pack(fill=tk.BOTH, padx=5, pady=5)
        self.news_text.insert(tk.END, "Загрузка новостей...")
        self.news_text.config(state=tk.DISABLED)
        
        # Лог
        log_frame = tk.LabelFrame(root, text="📋 Лог", bg='#1a1a2e', fg='#eeeeee')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, bg='#16213e',
                                                  fg='#00ff88', font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Загружаем данные
        self.log("🚀 Лаунчер запущен")
        self.load_server_data()
    
    def log(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def load_server_data(self):
        """Загружает данные с сервера"""
        try:
            self.log("📡 Подключение к серверу...")
            
            # Проверяем, жив ли сервер
            with urllib.request.urlopen(f"{API_URL}/", timeout=5) as response:
                data = json.loads(response.read().decode())
                self.log(f"✅ Сервер онлайн: {data.get('status', 'unknown')}")
            
            # Получаем версии
            versions_url = f"{API_URL}/api/versions"
            with urllib.request.urlopen(versions_url, timeout=5) as response:
                self.versions = json.loads(response.read().decode())
                self.log(f"📦 Версия модов: {self.versions.get('mods_version', 'unknown')}")
                
                if self.versions.get('update_required', False):
                    self.log("⚠️ Доступно обновление!")
                    self.status_label.config(text="⚠️ Есть обновление! Нажмите 'ОБНОВИТЬ'")
                else:
                    self.log("✅ Моды актуальны")
                    self.status_label.config(text="✅ Моды актуальны! Можно играть")
            
            # Получаем новости
            news_url = f"{API_URL}/api/news"
            with urllib.request.urlopen(news_url, timeout=5) as response:
                news_data = json.loads(response.read().decode())
                self.news_text.config(state=tk.NORMAL)
                self.news_text.delete(1.0, tk.END)
                for news in news_data.get('news', []):
                    self.news_text.insert(tk.END, f"🔹 {news['title']} ({news['date']})\n")
                    self.news_text.insert(tk.END, f"   {news['text']}\n\n")
                self.news_text.config(state=tk.DISABLED)
                
        except Exception as e:
            self.log(f"❌ Ошибка: {str(e)}")
            self.log("💡 Проверьте интернет или URL сервера")
            self.status_label.config(text="⚠️ Офлайн-режим")
    
    def check_updates(self):
        """Обновляет моды"""
        self.log("🔄 Начинаю обновление...")
        self.update_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.DISABLED)
        
        try:
            # Проверяем путь
            if not os.path.exists(GAME_PATH):
                self.log("⚠️ Путь к игре не найден!")
                messagebox.showerror("Ошибка", "Укажите путь к GTA San Andreas в настройках!")
                return
            
            # Скачиваем
            mods_url = f"{API_URL}/api/download/mods"
            mods_path = os.path.join(os.getcwd(), "mods_temp.zip")
            
            self.log(f"📥 Скачивание модов...")
            urllib.request.urlretrieve(mods_url, mods_path)
            
            # Распаковываем
            mods_folder = os.path.join(GAME_PATH, "modloader", "MyMissions")
            os.makedirs(mods_folder, exist_ok=True)
            
            self.log(f"📦 Распаковка в {mods_folder}")
            with zipfile.ZipFile(mods_path, 'r') as zip_ref:
                zip_ref.extractall(mods_folder)
            
            os.remove(mods_path)
            self.log("✅ Моды обновлены!")
            self.status_label.config(text="✅ Моды обновлены! Играйте!")
            messagebox.showinfo("Успех", "Моды успешно обновлены!")
            
        except Exception as e:
            self.log(f"❌ Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось обновить:\n{str(e)}")
        
        self.update_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
    
    def play_game(self):
        """Запускает игру"""
        exe_path = os.path.join(GAME_PATH, "gta_sa.exe")
        if not os.path.exists(exe_path):
            messagebox.showerror("Ошибка", f"Не найден gta_sa.exe в:\n{GAME_PATH}")
            return
        
        self.log("🎮 Запуск игры...")
        try:
            subprocess.Popen([exe_path], cwd=GAME_PATH)
            self.log("✅ Игра запущена!")
        except Exception as e:
            self.log(f"❌ Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    def open_settings(self):
        """Настройки"""
        win = tk.Toplevel(self.root)
        win.title("Настройки")
        win.geometry("450x200")
        win.configure(bg='#1a1a2e')
        
        tk.Label(win, text="Путь к папке с GTA San Andreas:", 
                font=("Arial", 11), bg='#1a1a2e', fg='#eeeeee').pack(pady=10)
        
        path_var = tk.StringVar(value=GAME_PATH)
        entry = tk.Entry(win, textvariable=path_var, width=50)
        entry.pack(pady=5)
        
        def save():
            global GAME_PATH
            GAME_PATH = path_var.get()
            self.log(f"📂 Путь сохранён: {GAME_PATH}")
            win.destroy()
        
        tk.Button(win, text="💾 Сохранить", command=save,
                 bg='#e94560', fg='white', font=("Arial", 12), width=12).pack(pady=15)

# ============ ЗАПУСК ============
if __name__ == "__main__":
    root = tk.Tk()
    app = GTALauncher(root)
    root.mainloop()
