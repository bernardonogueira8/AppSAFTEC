import flet as ft
from core.state import AppState
from core.i18n import I18n
from configs.routes import ROUTES


class MainLayout(ft.Column):
    def __init__(self, page, content, router):
        super().__init__(expand=True)
        self._page = page
        self.router = router
        self.content = content

        self._build()

    def _build(self):
        self.controls.clear()

        # TOP BAR continua no topo (dentro da Column principal)
        self.controls.append(self._top_bar())

        # Criamos um Row para colocar a Sidebar e o Content lado a lado
        # O expand=True aqui faz esse Row ocupar todo o resto da tela
        main_content_area = ft.Row(
            controls=[
                self._sidebar(),  # Chamada renomeada para _sidebar()
                ft.VerticalDivider(width=1),  # Linha sutil de separação
                ft.Container(
                    content=self.content,
                    expand=True,
                    padding=20,  # Um respiro para o conteúdo não colar na borda
                ),
            ],
            expand=True,
            spacing=0,
        )

        self.controls.append(main_content_area)

    # ---------- TOP BAR ----------
    def _top_bar(self):
        # Mantida a lógica original de AppBar
        items = []
        for r in ROUTES:
            if not r.get("show_in_top"):
                continue

            items.append(
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(r["icon"]),
                            ft.Text(
                                I18n.t(r["label"]) if "." in r["label"] else r["label"]
                            ),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda e, p=r["path"]: self.router.navigate(p),
                )
            )

        return ft.AppBar(
            title=ft.Text(I18n.t("app.name")),
            actions=[
                ft.PopupMenuButton(
                    icon=ft.Icons.MENU,
                    items=items,
                )
            ],
        )

    # ---------- SIDEBAR ----------
    def _sidebar(self):
        nav_routes = [r for r in ROUTES if r.get("show_in_slidebar")]
        sidebar_items = []
        for r in nav_routes:
            # Verifica se esta é a rota ativa
            is_selected = r["path"] == self.router.current_route
            label_text = I18n.t(r["label"]) if "." in r["label"] else r["label"]
            # Cada item é um Container para podermos estilizar o fundo/clique
            sidebar_items.append(
                ft.Container(
                    content=ft.Text(
                        label_text,
                        size=14,
                        weight=(
                            ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                        ),
                        color=ft.Colors.WHITE if is_selected else ft.Colors.WHITE70,
                    ),
                    padding=ft.Padding.symmetric(vertical=12, horizontal=15),
                    border_radius=8,
                    # Cor de destaque se estiver selecionado
                    bgcolor=ft.Colors.WHITE10 if is_selected else None,
                    ink=True,
                    on_click=lambda e, path=r["path"]: self._handle_sidebar_change(
                        path
                    ),
                )
            )

        # Retornamos o ListView com os itens
        return ft.Container(
            content=ft.ListView(
                controls=sidebar_items,
                spacing=5,
                expand=True,
            ),
            padding=ft.Padding.all(10),
            width=250,
        )

    def _handle_sidebar_change(self, route_path):
        self.router.navigate(route_path)
        self.page.update()
