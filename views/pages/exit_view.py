from core import ft
from views.layouts.main_layout import MainLayout
from controllers.exit_controller import ExitController


class ExitView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = ExitController(page)
        
    def render(self):
        self.page.run_task(self.controller.exit_app)