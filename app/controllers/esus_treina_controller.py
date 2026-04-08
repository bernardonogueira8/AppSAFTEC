from models.esus_treina_model import EsusTreinaModel

class EsusTreinaController:
    """
    Controller for esus_treina page
    """

    def __init__(self, model=None):
        self.model = model or EsusTreinaModel

    def get_title(self):
        return "EsusTreina"
