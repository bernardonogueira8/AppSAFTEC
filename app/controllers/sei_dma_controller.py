import flet as ft
from models.sei_dma_model import Sei_dmaModel


class SeiDmaController:
    """
    Controller for sei_dma page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        # Injetamos o Model já passando a conexão do banco de dados
        self.model = model or Sei_dmaModel(db_connection)

    def get_title(self):
        return "Automação: SEI DMA"

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
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def start_automation(self, titulo, texto):
        # 1. Recupera as credenciais salvas previamente
        username = self.client_storage.get("sei_user")
        password = self.client_storage.get("sei_pass")

        if not username or not password:
            self._show_snack("Salve as credenciais antes de iniciar!")
            return

        if not titulo or not texto:
            self._show_snack("Preencha o título e o texto!")
            return

        self._show_snack("Iniciando automação Playwright...")

        # 2. Chama a função que conterá seu script do Playwright
        self._run_playwright_script(username, password, titulo, texto)

    def _run_playwright_script(self, username, password, titulo, texto):

        pass

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
