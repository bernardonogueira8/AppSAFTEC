from models.simpas_estoque_model import Simpas_estoqueModel


class SimpasEstoqueController:
    """
    Controller for simpas_estoque page
    """

    def __init__(self, model=None):
        self.model = model or Simpas_estoqueModel

    def get_title(self):
        return "SIMPAS: Cruzamento de Estoque - Em Desenvolvimento"
