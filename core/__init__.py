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

# 1. Captura o caminho absoluto do diretório onde o SAFTEC-app.exe está instalado
install_dir = os.path.dirname(sys.executable)

# 2. Monta o caminho exato para a pasta ms-playwright que veio no Inno Setup
playwright_path = os.path.join(install_dir, "ms-playwright")

# 3. Força o Playwright a usar essa pasta em vez do cache padrão do Windows
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = playwright_path

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright