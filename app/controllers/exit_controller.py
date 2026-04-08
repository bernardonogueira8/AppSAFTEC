from models.exit_model import ExitModel


class ExitController:
    """
    Controller for exit page
    """

    # O ideal é injetar a 'page' na inicialização do controller
    def __init__(self, model=None):
        self.model = model or ExitModel()  # Recomendado instanciar o modelo ()

    def get_title(self):
        return "Sair do Sistema"
