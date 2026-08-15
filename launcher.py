import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# ============ НАСТРОЙКИ ============
# ПУТЬ К ВАШЕЙ GTA SAN ANDREAS (ИЗМЕНИТЕ ПОД СЕБЯ!)
GAME_PATH = "C:/Program Files (x86)/Rockstar Games/GTA San Andreas"
# ===================================

class GTALauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 GTA San Andreas Launcher")
        self.root.geometry("400x250")
        self.root.configure(bg='#1a1a2e')
        
        # Заголовок
        title = tk.Label(root, text="🚗 GTA San Andreas", 
                        font=("Arial", 24, "bold"), bg='#1a1a2e', fg='#e94560')
        title.pack(pady=20)
        
        # Кнопка игры
        self.play_btn = tk.Button(root, text="🎮 ИГРАТЬ", command=self.play_game,
                                 bg='#e94560', fg='white', font=("Arial", 16, "bold"),
                                 width=15, height=2, relief='flat')
        self.play_btn.pack(pady=15)
        
        # Кнопка настроек
        self.settings_btn = tk.Button(root, text="⚙️ НАСТРОЙКИ", command=self.open_settings,
                                     bg='#0f3460', fg='white', font=("Arial", 12),
                                     width=15, height=1, relief='flat')
        self.settings_btn.pack(pady=5)
        
        # Статус
        self.status_label = tk.Label(root, text="✅ Готов к запуску!", 
                                     font=("Arial", 10), bg='#1a1a2e', fg='#00ff88')
        self.status_label.pack(pady=10)
    
    def play_game(self):
        """Запускает игру"""
        exe_path = os.path.join(GAME_PATH, "gta_sa.exe")
        if not os.path.exists(exe_path):
            messagebox.showerror("Ошибка", f"Не найден gta_sa.exe в:\n{GAME_PATH}")
            return
        
        self.status_label.config(text="🎮 Игра запускается...")
        try:
            subprocess.Popen([exe_path], cwd=GAME_PATH)
            self.status_label.config(text="✅ Игра запущена! Приятной игры!")
        except Exception as e:
            self.status_label.config(text="❌ Ошибка запуска")
            messagebox.showerror("Ошибка", str(e))
    
    def open_settings(self):
        """Настройки"""
        win = tk.Toplevel(self.root)
        win.title("Настройки")
        win.geometry("450x150")
        win.configure(bg='#1a1a2e')
        
        tk.Label(win, text="Путь к папке с GTA San Andreas:", 
                font=("Arial", 11), bg='#1a1a2e', fg='#eeeeee').pack(pady=10)
        
        path_var = tk.StringVar(value=GAME_PATH)
        entry = tk.Entry(win, textvariable=path_var, width=50)
        entry.pack(pady=5)
        
        def save():
            global GAME_PATH
            GAME_PATH = path_var.get()
            self.status_label.config(text="✅ Путь сохранён!")
            win.destroy()
        
        tk.Button(win, text="💾 Сохранить", command=save,
                 bg='#e94560', fg='white', font=("Arial", 12), width=12).pack(pady=15)

# ============ ЗАПУСК ============
if __name__ == "__main__":
    root = tk.Tk()
    app = GTALauncher(root)
    root.mainloop()
