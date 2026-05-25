from models.exit_model import ExitModel
from core import ft

class ExitController:
    """
    Controller for exit page
    """
    
    def __init__(self, page, model=None):
        self.model = model or ExitModel()
        self.page = page
        
    async def exit_app(self):
        await self.page.window.destroy()

        