import os
import sys
import json
import time
import httpx
import asyncio
import tempfile
import threading
import subprocess
import flet as ft
import pandas as pd
from pathlib import Path
from packaging import version

APP_NAME = "SAFTEC"

# ─── Resolve o diretório base corretamente ────────────────────────────────────
def _get_base_dir() -> Path:
    """
    Em produção (build Flet), o .exe está em {app}\ e os recursos também.
    Em desenvolvimento, usa o pai do pai deste arquivo.
    """
    if getattr(sys, "frozen", False):
        # Executável empacotado: usa o diretório do .exe
        return Path(sys.executable).parent
    else:
        # Desenvolvimento local
        return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()

# ─── Aponta o Playwright para os browsers empacotados ─────────────────────────
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(BASE_DIR / "ms-playwright")

# ─── Só importa depois de setar o env ─────────────────────────────────────────
from playwright.sync_api import sync_playwright

# Debug — remova após confirmar
_pw_path = BASE_DIR / "ms-playwright"
print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] Playwright browsers path: {_pw_path}")
print(f"[DEBUG] Path exists: {_pw_path.exists()}")
print(f"[DEBUG] frozen: {getattr(sys, 'frozen', False)}")