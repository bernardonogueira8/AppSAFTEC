import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.exit_controller import ExitController


class ExitView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = ExitController()

    def render(self):
        content = ft.Column(
            controls=[
                ft.Text(self.controller.get_title(), size=24),
            ],
            spacing=16,
        )

        return MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )
