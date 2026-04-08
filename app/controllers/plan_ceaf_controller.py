from models.plan_ceaf_model import Plan_ceafModel

class PlanCeafController:
    """
    Controller for plan_ceaf page
    """

    def __init__(self, model=None):
        self.model = model or Plan_ceafModel

    def get_title(self):
        return "Planilhas de Avaliação CEAF"
