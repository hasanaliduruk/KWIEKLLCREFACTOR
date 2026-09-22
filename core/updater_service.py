import requests
import os
import tempfile
import subprocess

GITHUB_API_URL = "https://api.github.com/repos/hasanaliduruk/KWIEKLLCREFACTOR/releases/latest"
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "OperationsToolkit-Updater",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_latest_release_details(timeout=(5, 15)):
    """Return release JSON and a user-facing error without an unreliable DNS probe."""
    try:
        response = requests.get(GITHUB_API_URL, headers=GITHUB_HEADERS, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not data.get("tag_name"):
            return None, {
                "state": "invalid-response",
                "message": "Güncelleme sunucusundan geçersiz bir yanıt alındı.",
            }
        return data, None
    except requests.exceptions.ProxyError:
        return None, {
            "state": "proxy-error",
            "message": "Proxy bağlantısı GitHub erişimini engelledi.",
        }
    except requests.exceptions.SSLError:
        return None, {
            "state": "tls-error",
            "message": "Güvenli bağlantı kurulamadı. Sertifika/TLS ayarlarını kontrol edin.",
        }
    except requests.exceptions.Timeout:
        return None, {
            "state": "timeout",
            "message": "Güncelleme sunucusu zamanında yanıt vermedi.",
        }
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status == 403:
            message = "GitHub güncelleme kontrolünü geçici olarak sınırlandırdı. Birkaç dakika sonra tekrar deneyin."
        else:
            message = f"Güncelleme sunucusu HTTP {status or 'hatası'} döndürdü."
        return None, {"state": "http-error", "message": message}
    except requests.exceptions.ConnectionError:
        return None, {
            "state": "connection-failed",
            "message": "GitHub'a ulaşılamadı. DNS, güvenlik duvarı veya internet bağlantısını kontrol edin.",
        }
    except (requests.exceptions.RequestException, ValueError):
        return None, {
            "state": "check-failed",
            "message": "Güncelleme kontrolü tamamlanamadı.",
        }


def check_internet(timeout=5):
    """Check the service actually needed by the updater over HTTPS."""
    _, error = get_latest_release_details(timeout=(timeout, timeout))
    return error is None


def get_latest_release():
    """GitHub API üzerinden en son sürüm bilgilerini çeker."""
    data, _ = get_latest_release_details()
    return data


def download_update_file(url, destination, progress_callback=None):
    """Dosyayı indirir ve callback üzerinden (downloaded, total) bilgisini döner."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": GITHUB_HEADERS["User-Agent"]},
            stream=True,
            timeout=(10, 60),
        )
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        downloaded = 0
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
        return True
    except Exception:
        return False


def prepare_and_run_batch(update_exe_path):
    """İndirilen kurulum dosyasını (OperationsToolkit_Setup.exe) sessizce
    çalıştıracak ve kendini temizleyecek batch dosyasını hazırlar.

    Inno Setup kurulumu aynı AppId ile mevcut kurulumun üzerine yazar
    (yükseltme). Uygulama kapanınca batch kurulumu başlatır.
    """
    temp_dir = tempfile.gettempdir()
    batch_file_path = os.path.join(temp_dir, "run_update.bat")
    with open(batch_file_path, "w") as batch_file:
        batch_file.write(
            f"@echo off\n"
            f"timeout /t 2 > NUL\n"
            f'start "" /wait "{update_exe_path}" /SILENT /SUPPRESSMSGBOXES /NORESTART\n'
            f'del /f /q "{update_exe_path}"\n'
            f'del /f /q "%~f0" & exit\n'
        )
    subprocess.Popen(
        [batch_file_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
