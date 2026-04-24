import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.plan_ceaf_controller import PlanCeafController


class Plan_ceafView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = PlanCeafController()

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
