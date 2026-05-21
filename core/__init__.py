import os
import sys

def get_app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_app_dir()

def setup_playwright_env():
    """
    Configura as variáveis de ambiente do Playwright.
    Deve ser chamado ANTES de qualquer import do playwright.
    """
    if not getattr(sys, "frozen", False):
        return  # Em desenvolvimento, deixa o Playwright resolver sozinho

    exe_dir = os.path.dirname(sys.executable)  # AppData\Local\SAFTEC

    # 1. Aponta para os browsers instalados pelo Inno Setup
    browsers_path = os.path.join(exe_dir, "ms-playwright")
    if os.path.exists(browsers_path):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

    # 2. Aponta para o node.exe do driver
    node_path = os.path.join(exe_dir, "playwright_driver", "node.exe")
    if os.path.exists(node_path):
        os.environ["PLAYWRIGHT_NODEJS_PATH"] = node_path

    # 3. DEBUG: loga os caminhos configurados
    from core.logger import get_logger
    log = get_logger("playwright_setup")
    log.info(f"PLAYWRIGHT_BROWSERS_PATH = {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'NÃO DEFINIDO')}")
    log.info(f"PLAYWRIGHT_NODEJS_PATH   = {os.environ.get('PLAYWRIGHT_NODEJS_PATH', 'NÃO DEFINIDO')}")
    log.info(f"browsers_path exists     = {os.path.exists(browsers_path)}")
    log.info(f"node_path exists         = {os.path.exists(node_path)}")

def log_installed_structure():
    """Loga a estrutura de arquivos instalados para diagnóstico."""
    if not getattr(sys, "frozen", False):
        return
    from core.logger import get_logger
    log = get_logger("structure_check")
    exe_dir = os.path.dirname(sys.executable)
    
    for check in ["ms-playwright", "playwright_driver", "site-packages"]:
        path = os.path.join(exe_dir, check)
        exists = os.path.exists(path)
        log.info(f"[CHECK] {path} → {'EXISTS' if exists else 'MISSING'}")
        if exists:
            try:
                items = os.listdir(path)[:5]  # primeiros 5 itens
                log.info(f"        conteúdo: {items}")
            except Exception:
                pass

# ─── Executa ANTES do import do playwright ───────────────
setup_playwright_env()

log_installed_structure()

from playwright.sync_api import sync_playwright

import json
import time
import httpx
import asyncio
import tempfile
import threading
import subprocess
import flet as ft
import pandas as pd
from packaging import version