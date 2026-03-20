import socket
import requests
import os
import tempfile
import subprocess

GITHUB_API_URL = "https://api.github.com/repos/hasali2603/KWIEKLLC/releases/latest"

def check_internet(host="8.8.8.8", port=53, timeout=5):
    """Sadece bağlantı durumunu kontrol eder."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

def get_latest_release():
    """GitHub API üzerinden en son sürüm bilgilerini çeker."""
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def download_update_file(url, destination, progress_callback=None):
    """Dosyayı indirir ve callback üzerinden (downloaded, total) bilgisini döner."""
    try:
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        downloaded = 0
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded, total_size)
        return True
    except Exception:
        return False

def prepare_and_run_batch(update_exe_path):
    """Güncelleme dosyasını çalıştıracak ve kendini temizleyecek batch dosyasını hazırlar."""
    temp_dir = tempfile.gettempdir()
    batch_file_path = os.path.join(temp_dir, "run_update.bat")
    with open(batch_file_path, "w") as batch_file:
        batch_file.write(
            f'@echo off\n'
            f'timeout /t 2 > NUL\n'
            f'start "" /b "{update_exe_path}"\n'
            f':wait_loop\n'
            f'tasklist /FI "IMAGENAME eq KWIEKLLC_update.exe" 2>NUL | find /I /N "KWIEKLLC_update.exe">NUL\n'
            f'if "%ERRORLEVEL%"=="0" (\n'
                f'    timeout /t 5 > NUL\n'
                f'    goto wait_loop\n'
            f')\n'
            f'del /f /q "{update_exe_path}"\n'
            f'del /f /q "%~f0" & exit\n'
        )
    subprocess.Popen([batch_file_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)