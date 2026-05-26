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
import pandas as pd
from pathlib import Path
from packaging import version
from version import APP_VERSION

APP_NAME = "SAFTEC"

from playwright.async_api import async_playwright