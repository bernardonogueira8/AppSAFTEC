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
from packaging import version
from playwright.sync_api import sync_playwright


# Configura caminho dos browsers do Playwright para pasta da aplicação (importante para instalações via InnoSetup)
if not os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
    app_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # Se estiver em uma instalação normal, usa a pasta do app
    if not app_dir.endswith('core'):
        app_dir = os.path.dirname(app_dir)
    playwright_path = os.path.join(app_dir, 'ms-playwright')
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_path

APP_NAME = "SAFTEC"