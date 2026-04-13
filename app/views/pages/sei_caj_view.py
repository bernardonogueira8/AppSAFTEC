import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.sei_caj_controller import SeiCajController


class Sei_cajView:
    def __init__(self, page: ft.Page, router):
        self.page = page
        self.router = router
        self.controller = SeiCajController(page=self.page)
        self.system_name = "SEI"

    async def pick_file_handler(self, e):
        files = await self.file.pick_files(
            allow_multiple=False, allowed_extensions=["xls", "xlsx"]
        )
        if files:
            self.caminho_arquivo_input.value = files[0].path
            self.caminho_arquivo_input.update()

    def render(self):
        # Carregar credenciais
        credenciais_salvas = self.controller.load_saved_credentials(self.system_name)
        user_padrao = credenciais_salvas[0] if credenciais_salvas else ""
        pass_padrao = credenciais_salvas[1] if credenciais_salvas else ""

        # Campos de Login
        self.user_input = ft.TextField(
            label="Usuário SEI",
            value=user_padrao,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=10,
            expand=True,
            filled=True,
        )
        self.pass_input = ft.TextField(
            label="Senha SEI",
            password=True,
            can_reveal_password=True,
            expand=True,
            value=pass_padrao,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=10,
            filled=True,
        )

        # Passo 1: Interface de Login
        self.login_step = ft.Column(
            controls=[
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=70, color=ft.Colors.BLUE_700),
                ft.Text(
                    f"Autenticação {self.system_name}",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Verifique suas credenciais para acessar a automação.",
                    color=ft.Colors.GREY_500,
                ),
                self.user_input,
                self.pass_input,
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "Acessar e Continuar",
                                color=ft.Colors.WHITE,
                                size=16,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_700,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.all(20),
                    ),
                    on_click=self.avancar_passo,
                ),
            ],
            visible=True,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Campos da Automação
        self.numero_sei_input = ft.TextField(
            label="Número SEI",
            border_radius=10,
            filled=True,
            expand=True,
            prefix_icon=ft.Icons.NUMBERS,
        )

        self.file = ft.FilePicker()
        self.page.services.append(self.file)

        self.caminho_arquivo_input = ft.TextField(
            label="Caminho do Arquivo",
            border_radius=10,
            cursor_color=ft.Colors.ORANGE_500,
            expand=True,
        )
        self.button_pick_file = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE,
            icon_color=ft.Colors.ORANGE_500,
            tooltip="Escolher Arquivo",
            on_click=self.pick_file_handler,  # self aqui é a View
        )

        # Passo 2: Interface de Automação
        self.arquivo_input = ft.Row(
            [self.caminho_arquivo_input, self.button_pick_file],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            spacing=10,
        )

        self.automacao_step = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.ROCKET_LAUNCH, size=30, color=ft.Colors.ORANGE_500
                        ),
                        ft.Text(
                            "Dados da Automação", size=26, weight=ft.FontWeight.BOLD
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                self.numero_sei_input,
                self.arquivo_input,
                ft.Row(
                    controls=[
                        ft.Button(
                            content=ft.Text(
                                "Voltar",
                                color=ft.Colors.BLUE_700,
                                weight=ft.FontWeight.BOLD,
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.TRANSPARENT,
                                padding=ft.Padding.all(20),
                            ),
                            expand=True,
                            on_click=self.voltar_passo,
                        ),
                        ft.Button(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE),
                                    ft.Text(
                                        "Iniciar Automação",
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.ORANGE_600,
                                padding=ft.Padding.all(20),
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                            on_click=lambda _: self.controller.start_automation(
                                self.numero_sei_input.value,
                                self.caminho_arquivo_input.value,
                            ),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            visible=False,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        # Estrutura principal
        content = ft.Column(
            controls=[self.login_step, self.automacao_step],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )

        return MainLayout(page=self.page, content=content, router=self.router)

    # --- Navegação ---
    def avancar_passo(self, e):
        sucesso = self.controller.save_credentials(
            self.user_input.value, self.pass_input.value, self.system_name
        )
        if sucesso:
            self.login_step.visible = False
            self.automacao_step.visible = True
            self.page.update()

    def voltar_passo(self, e):
        self.automacao_step.visible = False
        self.login_step.visible = True
        self.page.update()
