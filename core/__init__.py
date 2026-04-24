import os
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


BASE_DIR = os.getcwd()
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(BASE_DIR, "ms-playwright")
