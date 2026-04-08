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
            prefix_icon=ft.Icons.PERSON_OUTLINE, # Ícone dentro do campo
            border_radius=10,
            filled=True
        )
        self.pass_input = ft.TextField(
            label="Senha SEI", 
            password=True, 
            can_reveal_password=True, 
            value=pass_padrao,
            prefix_icon=ft.Icons.LOCK_OUTLINE, # Ícone dentro do campo
            border_radius=10,
            filled=True,
        )
        # PASSO 1: CONTAINER DE LOGIN (Visível no Início)
        self.login_step = ft.Column(
            controls=[
                ft.Text(f"Login para {self.system_name}", size=20, weight=ft.FontWeight.BOLD),
                self.user_input,
                self.pass_input,
                ft.Button(
                    content=ft.Row(
                        controls=[ft.Icon(ft.Icons.ARROW_FORWARD), ft.Text("Salvar e Próximo")],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    on_click=self.avancar_passo
                )
            ],
            visible=True 
        )

        # PASSO 2: CONTAINER DE AUTOMAÇÃO (Oculto no Início)
        # Campos da Automação
        self.title_input = ft.TextField(label="Título do Processo")
        self.text_input = ft.TextField(label="Texto do Processo", multiline=True)

        self.automacao_step = ft.Column(
            controls=[
                ft.Text("Dados da Automação", size=20, weight=ft.FontWeight.BOLD),
                self.title_input,
                self.text_input,
                ft.Button(
                    content=ft.Row(
                        controls=[ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE), ft.Text("Iniciar Automação", color=ft.Colors.WHITE)],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700),
                    on_click=lambda e: self.controller.start_automation(self.title_input.value, self.text_input.value)
                ),
                # Um botão amigável caso o usuário queira voltar para trocar a senha
                ft.Button(
                    content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK), ft.Text("Voltar para Credenciais")], alignment=ft.MainAxisAlignment.CENTER),
                    on_click=self.voltar_passo
                )
            ],
            visible=False # <- Inicia escondido
        )

        # O layout principal que organiza os passos
        content = ft.Column(
            controls=[self.login_step, self.automacao_step],
            scroll=ft.ScrollMode.AUTO,
            spacing=20
        )


        return MainLayout(page=self.page, content=content, router=self.router)

    # --- Funções de navegação entre as etapas ---
    def avancar_passo(self, e):
        # Envia os dados para o Controller salvar
        sucesso = self.controller.save_credentials(self.user_input.value, self.pass_input.value, self.system_name)
        
        if sucesso:
            # Se a gravação deu certo (retornou True), nós escondemos o Login e mostramos a Automação
            self.login_step.visible = False
            self.automacao_step.visible = True
            self.page.update() # Atualiza a tela instantaneamente

    def voltar_passo(self, e):
        # Esconde a Automação e mostra o Login de novo
        self.automacao_step.visible = False
        self.login_step.visible = True
   