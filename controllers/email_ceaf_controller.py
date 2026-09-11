from models.email_ceaf_model import EmailCeafModel

class EmailCeafController:
    """
    Controller for email_ceaf page
    """

    def __init__(self, model=None):
        self.model = model or EmailCeafModel

    def get_title(self):
        return "EmailCeaf"
