import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.sei_dma_controller import SeiDmaController


class Sei_dmaView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = SeiDmaController(page=self.page)
        self.system_name = "SEI"

    def render(self):
        credenciais_salvas = self.controller.load_saved_credentials(self.system_name)
        user_padrao = credenciais_salvas[0] if credenciais_salvas else ""
        pass_padrao = credenciais_salvas[1] if credenciais_salvas else ""

        self.user_input = ft.TextField(
            label=f"Usuário {self.system_name}",
            value=user_padrao,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=10,
            expand=True,
            filled=True,
        )
        self.pass_input = ft.TextField(
            label=f"Senha {self.system_name}",
            password=True,
            can_reveal_password=True,
            expand=True,
            value=pass_padrao,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=10,
            filled=True,
        )
        # PASSO 1: CONTAINER DE LOGIN (Visível no Início)
        self.login_step = ft.Column(
            controls=[
                # Ícone de Avatar no topo do Card
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

        # PASSO 2: CONTAINER DE AUTOMAÇÃO (Oculto no Início)
        # Campos da Automação
        self.title_input = ft.TextField(
            label="Título do Processo",
            border_radius=10,
            filled=True,
            prefix_icon=ft.Icons.TITLE,
            expand=True,
        )
        self.text_input = ft.TextField(
            label="Texto do Processo",
            multiline=True,
            border_radius=10,
            filled=True,
            prefix_icon=ft.Icons.DESCRIPTION,
            min_lines=3,
            expand=True,
        )
        self.btn_copy_sei = ft.ElevatedButton(  # Usei ElevatedButton por padrão, mas pode manter seu style
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CONTENT_COPY, color=ft.Colors.WHITE),
                    ft.Text(
                        "Copiar número do SEI",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                padding=ft.Padding.all(20),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.controller.copy_from_sei,
            expand=False,
            disabled=True,  # <--- Começa desabilitado
        )

        self.text_caminho = ft.Text(
            "Caminho do arquivo: ",
            color=ft.Colors.GREY_600,
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
                self.title_input,
                self.text_input,  # Este campo gigante dominará o centro
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
                            on_click=lambda e: self.controller.start_automation(
                                self.title_input.value, self.text_input.value
                            ),
                            expand=True,  # Faz o botão esticar horizontalmente
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(
                    height=30, thickness=1, color=ft.Colors.GREY_300
                ),  # Separador visual
                ft.Row(
                    controls=[
                        self.text_caminho,
                        self.btn_copy_sei,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=20,
                ),
            ],
            visible=False,
            expand=False,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        # O layout principal que organiza os passos
        content = ft.Column(
            controls=[
                self.login_step,
                self.automacao_step,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )

        return MainLayout(page=self.page, content=content, router=self.router)

    # --- Funções de navegação entre as etapas ---
    def avancar_passo(self, e):
        # Envia os dados para o Controller salvar
        sucesso = self.controller.save_credentials(
            self.user_input.value, self.pass_input.value, self.system_name
        )

        if sucesso:
            # Se a gravação deu certo (retornou True), nós escondemos o Login e mostramos a Automação
            self.login_step.visible = False
            self.automacao_step.visible = True
            self.page.update()  # Atualiza a tela instantaneamente

    def voltar_passo(self, e):
        # Esconde a Automação e mostra o Login de novo
        self.automacao_step.visible = False
        self.login_step.visible = True
