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


APP_NAME = "SAFTEC"