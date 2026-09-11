import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.email_ceaf_controller import EmailCeafController

class EmailCeafView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = EmailCeafController(page=self.page)
        self.system_name = "email"
        # Propriedade para armazenar o dicionário lido do JSON
        self.templates = {} 

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
