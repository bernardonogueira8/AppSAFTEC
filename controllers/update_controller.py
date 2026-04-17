import httpx
import subprocess
import tempfile
import os
from packaging import version
from version import APP_VERSION
from models.update_model import UpdateModel

GITHUB_VERSION_URL = "https://github.com/bernardonogueira8/AppSAFTEC/releases/latest/download/version.json"

class UpdateController:
    """
    Controller for update page
    """
    def get_remote_version() -> dict | None:
        try:
            r = httpx.get(GITHUB_VERSION_URL, timeout=5)
            return r.json()  
        except Exception:
            return None

    def needs_update(remote: dict) -> bool:
        return version.parse(remote["version"]) > version.parse(APP_VERSION)

    def download_and_install(url: str, on_progress=None):
        with httpx.stream("GET", url, follow_redirects=True) as r:
            total = int(r.headers.get("content-length", 0))
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".exe")
            downloaded = 0
            for chunk in r.iter_bytes(chunk_size=8192):
                tmp.write(chunk)
                downloaded += len(chunk)
                if on_progress and total:
                    on_progress(downloaded / total)
            tmp.close()
            return tmp.name

    def launch_installer_and_exit(exe_path: str):
        subprocess.Popen([exe_path, "/SILENT"])
        os._exit(0)


    def __init__(self, model=None):
        self.model = model or UpdateModel

    def get_title(self):
        return "Atualizar Sistema"
