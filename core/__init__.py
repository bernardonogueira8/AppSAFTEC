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

# 1. Captura o caminho do diretório onde o SAFTEC-app.exe está executando
install_dir = os.path.dirname(sys.executable)

# 2. Aponta para a pasta ms-playwright que o Inno Setup colocará na raiz
playwright_path = os.path.join(install_dir, "ms-playwright")

# 3. Define a variável de ambiente ANTES de importar as ferramentas do Playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = playwright_path

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright