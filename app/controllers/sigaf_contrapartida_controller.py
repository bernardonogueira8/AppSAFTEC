import flet as ft
import json
import os
import threading
from core.logger import get_logger
from playwright.sync_api import sync_playwright
from models.sigaf_contrapartida_model import Sigaf_contrapartidaModel

logger = get_logger("App")

class SigafContrapartidaController:
    """
    Controller for sigaf_contrapartida page
    """

    def __init__(self, page,db_connection=None, model=None):
        self.model = model or Sigaf_contrapartidaModel(db_connection)

    def get_title(self):
        return "SIGAF: Repasse de Contrapartida"
    
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

    def start_automation(self,number_cib_input, caminho_arquivo_input, system_name):  
        credentials = self.load_saved_credentials(system_name)

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if not number_cib_input or not caminho_arquivo_input:
            self._show_snack("Preencha o número da CIB e selecione o arquivo!")
            return

        self._show_snack("Iniciando automação Playwright...")

        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(credentials[0], credentials[1], number_cib_input, caminho_arquivo_input),
        )
        automacao_thread.start()

    def _run_playwright_script(self, username, password, number_cib, caminho_arquivo):
        """
        Executa a rotina de automação no sistema SEI.
        """
        logger.info(
            f"Iniciando automação no SIGAF para o usuário: {username} | Número da CIB: {number_cib}"
        )
        try:
            df = pd.read_excel(caminho_arquivo).copy()
            # Verificação básica de colunas
            colunas_necessarias = ["DATA", "MUNICIPIO", "COMPETENCIA", "Nº NOB", "VALOR"]
            if not all(col in df.columns for col in colunas_necessarias):
                raise ValueError("A planilha não possui as colunas necessárias.")
            # Forma mais segura de criar colunas:
            df.loc[:, "DESCRIÇÃO"] = "REPASSE FINANCEIRO AO FUNDO MUNICIPAL DE SAÚDE CONFORME RES CIB/BA Nº " + valor_cib + " COMPETÊNCIA " + df["COMPETENCIA"].astype(str) + " -  NOB  " + df["Nº NOB"].astype(str)
            df.loc[:, "VALOR_STR"] = df["VALOR"].apply(lambda x: "{:.2f}".format(x).replace(".", ","))
            df.loc[:, "MUNICIPIO_BUSCA"] = "PREFEITURA MUNICIPAL DE " + df["MUNICIPIO"].str.upper()
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