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

        # Criamos um Row para colocar a Sidebar (antiga bottom_bar) e o Content lado a lado
        # O expand=True aqui faz esse Row ocupar todo o resto da tela
        main_content_area = ft.Row(
            controls=[
                self._bottom_bar(), # Agora atua como Sidebar
                ft.VerticalDivider(width=1), # Linha sutil de separação
                ft.Container(
                    content=self.content,
                    expand=True,
                    padding=20, # Um respiro para o conteúdo não colar na borda
                )
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
            if not r.get("show_in_bottom"):
                continue

            items.append(
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(r["icon"]),
                            ft.Text(I18n.t(r["label"]) if "." in r["label"] else r["label"]),
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

    # ---------- BOTTOM BAR (AGORA SIDEBAR) ----------
    def _bottom_bar(self):
        destinations = []

        # Filtramos as rotas que devem aparecer na sidebar
        for r in ROUTES:
            if not r.get("show_in_top"): # Mantendo a flag original para não quebrar sua config
                continue
            
            destinations.append(
                ft.NavigationRailDestination(
                    icon=r["icon"],
                    label=I18n.t(r["label"]) if "." in r["label"] else r["label"],
                )
            )

        # Retornamos o NavigationRail (Sidebar)
        return ft.NavigationRail(
            selected_index=None, # Você pode lógica para setar o índice baseado na rota atual
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            extended=True, # Mostra os nomes ao lado dos ícones
            destinations=destinations,
            on_change=lambda e: self._handle_sidebar_change(e, destinations),
        )

    def _handle_sidebar_change(self, e, destinations):
        # Lógica para navegar baseada no clique da sidebar
        # Como o NavigationRail usa índice, precisamos mapear de volta para a rota
        target_routes = [r for r in ROUTES if r.get("show_in_bottom")]
        selected_route = target_routes[e.control.selected_index]
        self.router.navigate(selected_route["path"])