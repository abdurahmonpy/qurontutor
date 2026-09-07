"""
One-click Runner for Quran Recitation Checker Ecosystem
Starts Django REST Backend, FastAPI ASR Microservice, and optionally Telegram Bot.
"""
import sys
import os
import subprocess
import time
import signal

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable

    print("=" * 65)
    print(" 📖  Qur'on Tilovat Tekshiruvchi (Telegram Bot + Web App)")
    print("=" * 65)

    processes = []

    try:
        # 1. Start FastAPI ASR Service on Port 8001
        print("\n[1/2] FastAPI ASR & Tajvid mikroservisi ishga tushirilmoqda (Port 8001)...")
        asr_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "asr_service.main:app", "--host", "127.0.0.1", "--port", "8001"],
            cwd=root_dir
        )
        processes.append(('FastAPI ASR', asr_proc))
        time.sleep(1.5)

        # 2. Start Django REST Backend & WebApp on Port 8000
        print("\n[2/2] Django REST Backend va WebApp ishga tushirilmoqda (Port 8000)...")
        django_proc = subprocess.Popen(
            [python_exe, "backend/manage.py", "runserver", "0.0.0.0:8000"],
            cwd=root_dir
        )
        processes.append(('Django Backend', django_proc))
        time.sleep(1.5)

        print("\n" + "=" * 65)
        print(" 🎉 Barcha xizmatlar muvaffaqiyatli ishga tushdi!")
        print(" 🌐 Telegram Mini App (Brauzerda): http://localhost:8000/")
        print(" 🔌 Django REST API:              http://localhost:8000/api/")
        print(" 🎙️ FastAPI ASR & Tajvid Service: http://127.0.0.1:8001/docs")
        print("=" * 65)
        print("\nTo'xtatish uchun Ctrl + C tugmalarini bosing.\n")

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nXizmatlar to'xtatilmoqda...")
        for name, proc in processes:
            print(f"To'xtatilmoqda: {name} (PID: {proc.pid})")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("Barcha jarayonlar to'xtatildi.")

if __name__ == '__main__':
    main()
