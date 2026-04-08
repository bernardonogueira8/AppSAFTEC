from models.sei_caj_model import Sei_cajModel

class SeiCajController:
    """
    Controller for sei_caj page
    """

    def __init__(self, model=None):
        self.model = model or Sei_cajModel

    def get_title(self):
        return "Automação: SEI CAJ"
