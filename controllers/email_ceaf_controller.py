from core import ft, threading, pd
from models.email_ceaf_model import EmailCeafModel

class EmailCeafController:
    """
    Controller for email_ceaf page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or EmailCeafModel(db_connection) 

    def get_title(self):
            return "Automação: SEI CAJ"
    
    def load_saved_credentials(self, system_name):
        try:
            return self.model.buscar_credenciais(system_name)
        except Exception as e:
            self._show_snack(f"Erro ao buscar: {e}")
            return None

    def save_credentials(self, username, password, system_name):
        if not username or not password:
            self._show_snack("Preencha usuário e senha!")
            return False

        try:
            self.model.salvar_credenciais(username, password, system_name)
            self._show_snack(f"Credenciais do {system_name} salvas!")
            return True
        except Exception as e:
            self._show_snack(f"Erro ao salvar: {e}")
            return False

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.overlay.append(snack)
        self.page.update()
