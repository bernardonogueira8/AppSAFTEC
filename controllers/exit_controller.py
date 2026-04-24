from models.exit_model import ExitModel
from core import subprocess, os

class ExitController:
    """
    Controller for exit page
    """

    def __init__(self, model=None):
        self.model = model or ExitModel()

    def get_title(self):
        return "Sair do Sistema"
    
    def launch_exit(self):
        pass