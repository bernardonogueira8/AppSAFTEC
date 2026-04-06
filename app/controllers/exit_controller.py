from models.exit_model import ExitModel

class ExitController:
    """
    Controller for exit page
    """

    def __init__(self, model=None):
        self.model = model or ExitModel

    def get_title(self):
        return "Exit"
