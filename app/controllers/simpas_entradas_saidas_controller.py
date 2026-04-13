from models.simpas_entradas_saidas_model import Simpas_entradas_saidasModel


class SimpasEntradasSaidasController:
    """
    Controller for simpas_entradas_saidas page
    """

    def __init__(self, model=None):
        self.model = model or Simpas_entradas_saidasModel

    def get_title(self):
        return "SIMPAS: Entradas e Saídas"
