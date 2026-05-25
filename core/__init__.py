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

APP_NAME = "SAFTEC"

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(BASE_DIR, "ms-playwright")

from playwright.sync_api import sync_playwright