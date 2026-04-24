from core import httpx, subprocess, tempfile, os
from packaging import version
from version import APP_VERSION
from models.update_model import UpdateModel

from core.logger import get_logger
logger = get_logger("App")

GITHUB_VERSION_URL = (
    "https://github.com/bernardonogueira8/AppSAFTEC/releases/latest/download/version.json"
)

class UpdateController:
    """
    Controller for update page
    """

    def __init__(self, model=None):
        self.model = model or UpdateModel

    def get_title(self):
        return "Atualizar Sistema"

    @staticmethod
    def get_remote_version() -> dict | None:
        try:
            r = httpx.get(GITHUB_VERSION_URL, timeout=5, follow_redirects=True)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Erro detalhado: {e}")
            return None

    @staticmethod
    def needs_update(remote: dict) -> bool:
        return version.parse(remote["version"]) > version.parse(APP_VERSION)

    @staticmethod
    def download_and_install(url: str, on_progress=None) -> str:
        tmp_path = ""
        try:
            with httpx.stream("GET", url, follow_redirects=True) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))

                with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
                    tmp_path = tmp.name
                    downloaded = 0
                    for chunk in r.iter_bytes(chunk_size=8192):
                        tmp.write(chunk)
                        downloaded += len(chunk)
                        if on_progress and total:
                            on_progress(downloaded / total)
            return tmp_path
        except Exception as e:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

    @staticmethod
    def launch_installer_and_exit(exe_path: str):   # <-- self removido
        subprocess.Popen([exe_path, "/SILENT"])
        os._exit(0)