import flet as ft
from version import APP_VERSION
from views.layouts.main_layout import MainLayout


class HomeView:
    def __init__(self, page, router):
        self.page = page
        self.router = router

    def render(self):
        # Banner estilo Hero - Ocupando mais espaço e sem bordas restritivas
        banner = ft.Container(
            content=ft.Image(
                src="waves.png",
                fit="cover",
                opacity=0.6,
            ),
            width=float("inf"), 
            height=200,        
            border_radius=ft.border_radius.only(top_left=40, top_right=40,bottom_left=40, bottom_right=40),
        )

        # Conteúdo Centralizado
        info_section = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                # Linha do Título com Ícone
                ft.Row(
                    controls=[
                        ft.Image(src="icon.png", width=50, height=50),
                        ft.Text("Automações da SAFTEC", size=42, weight="bold"),
                        ft.Container(
                            content=ft.Text(f"v{APP_VERSION}", size=24, weight="bold"),
                            bgcolor=ft.Colors.BLUE_GREY_800,
                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                            border_radius=20,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Text(
                        "Aplicação para automação de tarefas e gestão de dados.",
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_400,
                    ),
                    width=450,
                ),
                ft.Text(
                    "Micro Framework MVC desenvolvido em Flet, Python e Playwright.",
                    size=14,
                    color=ft.Colors.GREY_500,
                    italic=True
                ),
                ft.Text(
                    "Desenvolido por Bernardo Nogueira, SAFTEC/DASF",
                    size=16,
                    color=ft.Colors.GREY_400,
                    italic=True
                ),
            ]
        )

        # Layout Principal usando Column para empilhar Banner + Info
        content = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                banner,
                ft.Container(content=info_section, padding=ft.padding.only(top=20))
            ]
        )

        return MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )