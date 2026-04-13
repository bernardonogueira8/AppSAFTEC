from models.sigaf_contrapartida_model import Sigaf_contrapartidaModel


class SigafContrapartidaController:
    """
    Controller for sigaf_contrapartida page
    """

    def __init__(self, model=None):
        self.model = model or Sigaf_contrapartidaModel

    def get_title(self):
        return "SIGAF: Repasse de Contrapartida"
