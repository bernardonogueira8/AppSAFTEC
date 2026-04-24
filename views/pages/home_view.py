import flet as ft
from version import APP_VERSION
from views.layouts.main_layout import MainLayout


class HomeView:
    def __init__(self, page, router):
        self.page = page
        self.router = router

    def render(self):
        content = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Image(
                        src="waves.png",
                        fit="cover",
                        opacity=0.6,
                    ),
                    width=float("inf"),
                    height=200,
                    border_radius=ft.BorderRadius.only(
                        top_left=40, top_right=40, bottom_left=40, bottom_right=40
                    ),
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Image(src="icon.png", width=50, height=50),
                                ft.Text("Automações da SAFTEC", size=42, weight="bold"),
                                ft.Container(
                                    content=ft.Text(
                                        f"v{APP_VERSION}",
                                        size=24,
                                        weight="bold",
                                        color=ft.Colors.PRIMARY,
                                    ),
                                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                                    padding=ft.Padding.symmetric(
                                        horizontal=12, vertical=4
                                    ),
                                    border_radius=20,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        ft.Text(
                            "Aplicação para automação de tarefas e gestão de dados.",
                            size=18,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.SECONDARY,
                        ),
                        ft.Text(
                            "Micro Framework MVC desenvolvido em Flet, Python e Playwright.",
                            size=14,
                            color=ft.Colors.SECONDARY,
                            italic=True,
                        ),
                        ft.Text(
                            "Desenvolido por Bernardo Nogueira, SAFTEC/DASF",
                            size=16,
                            color=ft.Colors.SECONDARY,
                            italic=True,
                        ),
                    ],
                ),
            ],
        )

        # LAYOUT
        return MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )
