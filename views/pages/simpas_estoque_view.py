import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.simpas_estoque_controller import SimpasEstoqueController


class Simpas_estoqueView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = SimpasEstoqueController()

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
