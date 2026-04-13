import flet as ft
import json
import os
import threading
from core.logger import get_logger
from playwright.sync_api import sync_playwright
from models.sei_caj_model import Sei_cajModel

logger = get_logger("App")


class SeiCajController:
    """
    Controller for sei_caj page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or Sei_cajModel(db_connection)

    def get_title(self):
        return "Automação: SEI CAJ"

    def load_saved_credentials(self, system_name):
        try:
            return self.model.buscar_credenciais(system_name)
        except Exception as e:
            print(f"Erro ao buscar: {e}")
            return None

    def save_credentials(self, username, password, system_name):
        if not username or not password:
            self._show_snack("Preencha usuário e senha!")
            return False  # Retorna Falso, não avança a tela

        try:
            self.model.salvar_credenciais(username, password, system_name)
            self._show_snack(f"Credenciais do {system_name} prontas!")
            return True  # Retorna Verdadeiro, permite avançar
        except Exception as e:
            self._show_snack(f"Erro ao salvar: {e}")
            return False

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.overlay.append(snack)
        self.page.update()

    def start_automation(self, numero_sei_input, caminho_arquivo_input):  
        # 1. Recupera as credenciais salvas previamente
        credentials = self.load_saved_credentials("SEI")

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if bool(numero_sei_input) == bool(caminho_arquivo_input):
            self._show_snack("Preencha o número SEI ou selecione o arquivo!")
            return

        self._show_snack("Iniciando automação Playwright...")

        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(credentials[0], credentials[1], numero_sei_input, caminho_arquivo_input),
        )
        automacao_thread.start()

    def _run_playwright_script(self, username, password, numero_sei, caminho_arquivo):
        """
        Executa a rotina de automação no sistema SEI.
        """
        self._show_snack(f"Iniciando automação no SEI para o usuário: {username}")
        try:
            # Inicializa o Playwright de forma síncrona
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=False, slow_mo=500)
                page = browser.new_page()
                logger.info("Navegador aberto. Acessando a página de login...")

                self.open_browser(page, username, password)
                browser.close()

        except Exception as e:
            logger.error(f"Erro: {e}")
            raise e

    def open_browser(self, page, username, password):
        page.goto("https://seibahia.ba.gov.br")
        page.get_by_role("textbox", name="Usuário").fill(username)
        page.get_by_role("textbox", name="Senha").fill(password)
        page.locator("#selOrgao").select_option("23")
        page.get_by_role("button", name="ACESSAR").click()
