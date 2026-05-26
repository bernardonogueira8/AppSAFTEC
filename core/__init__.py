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

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright