from models.test_model import TestModel

class TestController:
    """
    Controller for test page
    """

    def __init__(self, model=None):
        self.model = model or TestModel

    def get_title(self):
        return "Test"
