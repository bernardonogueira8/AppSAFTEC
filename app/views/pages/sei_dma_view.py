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
        # PASSO 1: CONTAINER DE LOGIN (Visível no Início)
        self.login_step = ft.Container(
            content=ft.Column(
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
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),  # Espaçador
                    self.user_input,
                    self.pass_input,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),  # Espaçador
                    # Botão Estilizado
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
                            padding=ft.Padding.all(
                                20
                            ),  # Botão mais "gordinho" e fácil de clicar
                        ),
                        on_click=self.avancar_passo,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centraliza tudo na vertical
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Centraliza tudo na horizontal
            ),
            # Estilo da "Caixa" (Card)
            expand=True,
            visible=True,
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

        self.automacao_step = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.ROCKET_LAUNCH, size=60, color=ft.Colors.ORANGE_500
                    ),
                    ft.Text("Dados da Automação", size=26, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Preencha os dados abaixo para rodar o script no Playwright.",
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.title_input,
                    self.text_input,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    # Botão de Ação Principal
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE),
                                ft.Text(
                                    "Iniciar Robô Playwright",
                                    color=ft.Colors.WHITE,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.ORANGE_600,
                            padding=ft.Padding.all(20),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=lambda e: self.controller.start_automation(
                            self.title_input.value, self.text_input.value
                        ),
                    ),
                    # Botão Secundário para Voltar
                    ft.Button(
                        content=ft.Text(
                            "Voltar para Credenciais", color=ft.Colors.BLUE_700
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.TRANSPARENT,
                            overlay_color=ft.Colors.BLUE_50,
                        ),
                        on_click=self.voltar_passo,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            padding=40,
            border_radius=15,
            bgcolor=ft.Colors.WHITE_10,
            border=ft.border.all(1, ft.Colors.WHITE_24),
            shadow=ft.BoxShadow(
                spread_radius=1, blur_radius=20, color=ft.Colors.BLACK12
            ),
            visible=False,
        )

        # O layout principal que organiza os passos
        content = ft.Column(
            controls=[self.login_step, self.automacao_step],
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
