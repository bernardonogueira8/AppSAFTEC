from core import os, ft, threading, sync_playwright
from models.esus_treina_model import Esus_treinaModel

from core.logger import get_logger
logger = get_logger("App")


class EsusTreinaController:
    """
    Controller for esus_treina page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or Esus_treinaModel(db_connection)

    def get_title(self):
        return "E-SUS Treinamento - Em Desenvolvimento"

    def load_saved_credentials(self, system_name):
        try:
            return self.model.buscar_credenciais(system_name)
        except Exception as e:
            logger.error(f"Erro ao buscar: {e}")
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

    def start_automation(self, titulo, texto):
        # 1. Recupera as credenciais salvas previamente
        credentials = self.load_saved_credentials("ESUS_TREINA")

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if not titulo or not texto:
            self._show_snack("Preencha o título e o texto!")
            return

        self._show_snack("Iniciando automação Playwright...")

        # 2. Chama a função que conterá seu script do Playwright
        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(credentials[0], credentials[1], titulo, texto),
        )
        automacao_thread.start()  # Inicia a thread para não travar a UI

    def _run_playwright_script(self, username, password, titulo, texto):
        """
        Executa a rotina de automação no sistema SEI.

        Esta função recebe apenas dados puros (strings, dicionários, etc.)
        e não tem NENHUMA dependência da interface gráfica (Tkinter).
        """
        # Configurações de URL
        BASE_URL = "https://treinamento.esus.saude.ba.gov.br/"
        try:
            # Inicializa o Playwright de forma síncrona
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=False, slow_mo=500)
                page = browser.new_page()  # [1]
                logger.info("Navegador aberto. Acessando a página de login...")

                # Acessa a página de login
                page.goto(BASE_URL)

        except Exception as e:
            logger.error(f"Erro: {e}")
            raise e
