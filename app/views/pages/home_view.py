import flet as ft
from views.layouts.main_layout import MainLayout


class HomeView:
    def __init__(self, page, router):
        self.page = page
        self.router = router

    def render(self):
        content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=24,
            controls=[
                ft.Image(
                    src="icon.png",
                    width=96,
                    height=96,
                    fit="contain",
                ),
                ft.Text(
                    "Automações para SAFTEC",
                    size=36,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Micro Framework MVC for Flet",
                    size=16,
                    color=ft.Colors.GREY_600,
                ),
                ft.Text(
                    "Aplicação desktop desenvolvida com Flet para automações de tarefas.",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    width=420,
                ),
            ],
        )

        # LAYOUT
        return MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )
