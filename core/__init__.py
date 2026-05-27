import os
import sys
import json
import httpx
import asyncio
import sqlite3
import logging
import tempfile
import importlib
import threading
import subprocess
import flet as ft
import numpy as np
import pandas as pd
from pathlib import Path
from packaging import version
from datetime import datetime
from version import APP_VERSION

APP_NAME = "SAFTEC"

APP_NAME = "SAFTEC"

# Verifica se está rodando via Python (.venv/desenvolvimento) ou via executável compilado
if sys.executable.lower().endswith("python.exe") or sys.executable.lower().endswith("pythonw.exe"):
    # MODO DESENVOLVIMENTO:
    # Como este arquivo é core/__init__.py, a raiz do projeto é a pasta pai da pasta "core"
    install_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
else:
    # MODO PRODUÇÃO:
    # Captura a pasta onde o SAFTEC-app.exe está executando
    install_dir = os.path.dirname(sys.executable)

# Monta o caminho exato para a pasta ms-playwright
playwright_path = os.path.join(install_dir, "ms-playwright")

# Define a variável de ambiente ANTES de importar o Playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = playwright_path

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright