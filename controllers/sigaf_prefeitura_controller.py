from models.sigaf_prefeitura_model import Sigaf_prefeituraModel


class SigafPrefeituraController:
    """
    Controller for sigaf_prefeitura page
    """

    def __init__(self, model=None):
        self.model = model or Sigaf_prefeituraModel

    def get_title(self):
        return "SIGAF: Informações do Secretarias de saúde - Em Desenvolvimento"
