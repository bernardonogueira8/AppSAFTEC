import os
import flet as ft
import json
import threading
import pandas as pd
from playwright.sync_api import sync_playwright
import httpx
import subprocess
import tempfile


BASE_DIR = os.getcwd()
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(BASE_DIR, "ms-playwright")
