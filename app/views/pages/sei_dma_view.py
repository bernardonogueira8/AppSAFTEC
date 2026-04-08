import flet as ft
from views.layouts.main_layout import MainLayout
from controllers.sei_dma_controller import SeiDmaController

class Sei_dmaView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = SeiDmaController(page=self.page)

    def render(self):
        credenciais_salvas = self.controller.load_saved_credentials()
        # 2. Verifica se encontrou algo. O fetchone() retorna uma tupla: (username, password)
        # Se for None, deixamos a string vazia ("")
        user_padrao = credenciais_salvas[0] if credenciais_salvas else ""
        pass_padrao = credenciais_salvas[1] if credenciais_salvas else ""

        # 3. Campos de Login já injetando o value
        self.user_input = ft.TextField(
            label="Usuário SEI", 
            value=user_padrao # <-- injeta o dado do banco
        )
        self.pass_input = ft.TextField(
            label="Senha SEI", 
            password=True, 
            can_reveal_password=True, 
            value=pass_padrao # <-- injeta o dado do banco
        )
        
        # Campos da Automação
        self.title_input = ft.TextField(label="Título do Processo")
        self.text_input = ft.TextField(label="Texto do Processo", multiline=True)

        content = ft.Column(
            controls=[
                # Seção de Login
                ft.Text("Credenciais de Acesso", size=20, weight=ft.FontWeight.BOLD),
                self.user_input,
                self.pass_input,
                
                # CORREÇÃO: Utilizando ft.Button e content
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SAVE), 
                            ft.Text("Salvar Credenciais")
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    on_click=lambda e: self.controller.save_credentials(
                        self.user_input.value, 
                        self.pass_input.value
                    )
                ),
                
                ft.Divider(height=30), 
                
                # Seção da Automação
                ft.Text("Dados da Automação", size=20, weight=ft.FontWeight.BOLD),
                self.title_input,
                self.text_input,
                
                # CORREÇÃO: Utilizando ft.Button, content e ft.ButtonStyle para cores
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE), 
                            ft.Text("Iniciar Automação Playwright", color=ft.Colors.WHITE)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700),
                    on_click=lambda e: self.controller.start_automation(
                        self.title_input.value, 
                        self.text_input.value
                    )
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15
        )
        
        return MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )