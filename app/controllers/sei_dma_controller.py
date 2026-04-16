import flet as ft
import json
import os
import threading
from playwright.sync_api import sync_playwright
from models.sei_dma_model import Sei_dmaModel

class SeiDmaController:
    """
    Controller for sei_dma page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        # Injetamos o Model já passando a conexão do banco de dados
        self.model = model or Sei_dmaModel(db_connection)

    def get_title(self):
        return "Automação: SEI DMA"

    def load_saved_credentials(self, system_name):
        try:
            return self.model.buscar_credenciais(system_name)
        except Exception as e:
            print(f"Erro ao buscar: {e}")
            return None

    def save_credentials(self, username, password, system_name):
        if not username or not password:
            self._show_snack("Preencha usuário e senha!")
            return False  # Retorna Falso, não avança a tela

        try:
            self.model.salvar_credenciais(username, password, system_name)
            self._show_snack(f"Credenciais do {system_name} salvas!")
            return True  # Retorna Verdadeiro, permite avançar
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.overlay.append(snack)
        self.page.update()

    def start_automation(self, titulo, texto):
        # 1. Recupera as credenciais salvas previamente
        credentials = self.load_saved_credentials("SEI")

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if not titulo or not texto:
            self._show_snack("Preencha o título e o texto!")
            return

        self._show_snack("Iniciando automação Playwright...")

        # 2. Chama a função que conterá seu script do Playwright
        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(credentials[0], credentials[1], titulo, texto),
        )
        automacao_thread.start()  # Inicia a thread para não travar a UI

    def copy_from_sei(self, e):
        # O número SEI foi guardado no 'data' do componente lá no passo anterior
        numero = self.view.btn_copy_sei.data
        
        if numero:
            # Comando oficial do Flet para copiar
            self.view.page.set_clipboard(numero)
            self._show_snack(f"Número {numero} copiado para a área de transferência!")
        else:
            self._show_snack("Nenhum número encontrado para copiar.")
    
    
    
    def _run_playwright_script(self, username, password, titulo, texto):
        """
        Executa a rotina de automação no sistema SEI.

        Esta função recebe apenas dados puros (strings, dicionários, etc.)
        e não tem NENHUMA dependência da interface gráfica (Tkinter).
        """
        self._show_snack(f"Iniciando automação...")
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=False, slow_mo=500)
                page = browser.new_page()
                
                self.open_browser(page, username, password)
                numero_sei = self.create_process(page, titulo, texto)
                
                # Captura o caminho do arquivo retornado pelo download
                caminho_pdf = self.download_file(page)
                
                browser.close()

                # --- ATUALIZAÇÃO DA UI ---
                # 1. Habilita o botão de copiar
                self.view.btn_copy_sei.disabled = False
                
                # 2. Armazena o número SEI no botão ou no controller para uso posterior
                self.view.btn_copy_sei.data = numero_sei 
                
                # 3. Atualiza o texto do caminho
                if caminho_pdf:
                    self.view.text_caminho.value = f"Caminho do arquivo: {caminho_pdf}"
                
                # 4. Dá o refresh na tela
                self.view.update() 
                
                return numero_sei

        except Exception as e:
            self._show_snack(f"Erro: {e}")
            # Caso dê erro, é bom garantir que o botão continue desabilitado
            self.view.btn_copy_sei.disabled = True
            self.view.update()
            raise e

    def formatar_para_sei(self, content):
        if not content:
            return ""
        # 1. Tratamos os recuos de 4 espaços primeiro
        content = content.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")

        # 2. Dividimos o texto por linhas e limpamos espaços vazios no fim de cada uma
        linhas = content.split("\n")
        # 3. Envolvemos cada linha em um <p> com a classe que o SEI usa
        # Se a linha estiver vazia, colocamos um <br/> dentro do <p> para manter o espaço
        content = ""
        for linha in linhas:
            texto_linha = linha if linha.strip() else "<br/>"
            content += (
                f'<p class="Texto_Justificado_Recuo_Primeira_Linha">{texto_linha}</p>'
            )

        # Retornamos o HTML puro (o json.dumps deve ser usado no momento da injeção no SEI_DMA.py)
        return content

    def open_browser(self, page, username, password):
        # 1. Login
        page.goto("https://seibahia.ba.gov.br")
        page.get_by_role("textbox", name="Usuário").fill(username)
        page.get_by_role("textbox", name="Senha").fill(password)
        page.locator("#selOrgao").select_option("23")
        page.get_by_role("button", name="ACESSAR").click()

    def create_process(self, page, title, content):
        # 2. Criar Processo
        page.get_by_role("link", name="Iniciar Processo").click()
        # Ajuste o nome do tipo de processo conforme sua necessidade real
        page.get_by_role(
            "link", name="Documento tramitável: Comunicação Interna"
        ).click()
        page.get_by_role("textbox", name="Especificação:").click()
        page.get_by_role("textbox", name="Especificação:").fill(title)
        page.locator("#divInfraBarraComandosSuperior").get_by_role(
            "button", name="Salvar"
        ).click()
        # 2. Incluir em Tag
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "link", name="Gerenciar Marcador"
        ).click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.locator("a").nth(
            1
        ).click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.locator(
            "a"
        ).filter(has_text="TI/DMA").click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "button", name="Salvar"
        ).click()

        # Capturar o número do SEI
        tree_frame = page.frame_locator("#ifrArvore")
        span_processo = tree_frame.locator(".infraArvoreNoSelecionado")
        numero_sei = span_processo.inner_text()

        self._show_snack(f"Processo/Documento identificado: {numero_sei}")
        # Clicar no link (<a>) que contém esse número
        tree_frame.locator("a:has(.infraArvoreNoSelecionado)").click()

        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "link", name="Incluir Documento"
        ).click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "link", name="Despacho"
        ).click()
        with page.expect_popup() as page1_info:
            page.locator('iframe[name="ifrVisualizacao"]').content_frame.locator(
                "#divInfraBarraComandosSuperior"
            ).get_by_role("button", name="Salvar").click()

        # 3. Editando o Despacho
        page1 = page1_info.value
        page1.locator(
            'iframe[title="Processo e Interessado"]'
        ).content_frame.get_by_text("Insira aqui o órgão").click()
        page1.locator(
            'iframe[title="Processo e Interessado"]'
        ).content_frame.get_by_role("cell", name="[Insira aqui o órgão").fill("CGTICS")
        page1.locator('iframe[title="Corpo do Texto"]').content_frame.get_by_text(
            "[Insira aqui o conteúdo do"
        ).click()
        content = self.formatar_para_sei(content)
        content = json.dumps(content)
        page1.locator('iframe[title="Corpo do Texto"]').content_frame.get_by_text(
            "[Insira aqui o conteúdo do"
        ).evaluate(f"(el) => el.innerHTML = {content}")
        page1.get_by_role("button", name="Salvar").click()
        page1.close()
        # Clicar no link (<a>) que contém esse número
        tree_frame.locator("a:has(.infraArvoreNoSelecionado)").click()

        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "link", name="Incluir em Bloco de Assinatura"
        ).click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "button", name="Novo Bloco"
        ).click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "textbox", name="Descrição:"
        ).fill(title)
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "button", name="Salvar"
        ).click()
        page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
            "button", name="Incluir", exact=True
        ).click()
        # Clicar no link (<a>) que contém esse número
        tree_frame.locator("a:has(.infraArvoreNoSelecionado)").click()

        return numero_sei

    def download_file(self, page, save_path="downloads/"):
        # Garante que a pasta de destino existe (bom para o seu projeto de TI)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 1. Localiza a árvore e garante que o documento certo está clicado
        tree_frame = page.frame_locator("#ifrArvore")
        tree_frame.locator("a:has(.infraArvoreNoSelecionado)").click()

        # 2. Acessa o frame de visualização
        visualizacao_frame = page.locator(
            'iframe[name="ifrVisualizacao"]'
        ).content_frame

        # 3. Clica para abrir a tela de geração de PDF
        visualizacao_frame.get_by_role(
            "link", name="Gerar Arquivo PDF do Documento"
        ).click()

        # 4. processar o PDF
        try:
            with page.expect_download(timeout=60000) as download_info:
                visualizacao_frame.get_by_role(
                    "button", name="Gerar"
                ).click()  # Corrigido: adicionado ()

            download = download_info.value

            # Salva o arquivo
            final_path = os.path.join(save_path, download.suggested_filename)
            download.save_as(final_path)

            self._show_snack(f"PDF salvo com sucesso em: {final_path}")
            return final_path

        except Exception as e:
            self._show_snack(f"Erro ao baixar o PDF: {e}")
            return None
