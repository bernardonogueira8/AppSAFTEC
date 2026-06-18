from core import ft, threading, sync_playwright
from models.sei_dma_model import Sei_dmaModel
from core.logger import get_logger
logger = get_logger("App")

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
            logger.error(f"Erro ao buscar: {e}")
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
            logger.error(f"Erro ao salvar: {e}")
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

                self.login_sei(page, username, password)
                self.create_process(page, titulo, texto)

                browser.close()


        except Exception as e:
            self._show_snack(f"Erro: {e}")
            raise e

    def formatar_para_sei(self, content):
        if not content:
            return ""
        
        # Tratamos os recuos de 4 espaços primeiro
        content = content.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        linhas = content.split("\n")
        
        content_html = ""
        for linha in linhas:
            texto_linha = linha if linha.strip() else "<br/>"
            content_html += (
                f'<p class="Texto_Justificado_Recuo_Primeira_Linha">{texto_linha}</p>'
            )
        
        # Faltava o return no seu snippet
        return content_html
    
    def inserir_conteudo_ck5(self, page1, content_html):
        page1.wait_for_selector('[role="textbox"][aria-label="Corpo do Texto"]', timeout=10000)
        
        # Aguarda o editor CK5 terminar de inicializar completamente
        page1.wait_for_function("""
            () => {
                const el = document.querySelector('[role="textbox"][aria-label="Corpo do Texto"]');
                if (!el) return false;
                // Editor pronto quando o placeholder desaparece ou tem conteúdo real
                const texto = el.innerText.trim();
                return texto.length > 0;
            }
        """, timeout=10000)

        # Clica para focar
        page1.locator('[role="textbox"][aria-label="Corpo do Texto"]').click()
        page1.wait_for_timeout(800)

        # Seleciona tudo com Ctrl+A e deleta
        page1.locator('[role="textbox"][aria-label="Corpo do Texto"]').press("Control+a")
        page1.wait_for_timeout(300)
        page1.locator('[role="textbox"][aria-label="Corpo do Texto"]').press("Delete")
        page1.wait_for_timeout(300)

        # Injeta o HTML via clipboard (mais confiável que execCommand)
        resultado = page1.evaluate("""
            async (html) => {
                const el = document.querySelector('[role="textbox"][aria-label="Corpo do Texto"]');
                el.focus();
                
                // Cria um elemento temporário para parsear o HTML
                const temp = document.createElement('div');
                temp.innerHTML = html;
                
                // Usa ClipboardItem para colar como HTML
                try {
                    const blob = new Blob([html], { type: 'text/html' });
                    const item = new ClipboardItem({ 'text/html': blob });
                    await navigator.clipboard.write([item]);
                    document.execCommand('paste');
                    return 'OK: clipboard paste';
                } catch(e) {
                    // Fallback: seta direto e força eventos do CK5
                    el.innerHTML = html;
                    ['input', 'keyup', 'change'].forEach(ev => 
                        el.dispatchEvent(new Event(ev, { bubbles: true }))
                    );
                    return 'OK: fallback eventos - ' + e.message;
                }
            }
        """, content_html)

        print(f"CK5 resultado: {resultado}")
        page1.wait_for_timeout(1000)

        conteudo_atual = page1.evaluate("""
            () => document.querySelector('[role="textbox"][aria-label="Corpo do Texto"]').innerHTML
        """)
        print(f"Conteúdo atual: {conteudo_atual[:300]}")
    
    def login_sei(self, page, username, password):
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
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.get_by_role("link", name="Gerenciar Marcador").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.locator("a").nth(1).click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.locator("a").filter(has_text="TI/DMA").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("button", name="Salvar").click()

        # 3. Criando o Despacho
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.get_by_role("link", name="Incluir Documento").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("link", name="Despacho").click()

        with page.expect_popup() as page1_info:
            page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.locator("#divInfraBarraComandosSuperior").get_by_role("button", name="Salvar").click()

        page1 = page1_info.value

        # Captura logs do browser para debug
        page1.on("console", lambda msg: print(f"[BROWSER] {msg.type}: {msg.text}"))

        # Preenche interessado
        page1.get_by_text("[Insira aqui o interessado]").click()
        page1.get_by_role("cell", name="[Insira aqui o interessado]").fill("CGTICS")

        # Insere conteúdo no editor
        content_html = self.formatar_para_sei(content)
        self.inserir_conteudo_ck5(page1, content_html)

        page1.wait_for_timeout(2000)
        page1.get_by_role("button", name="Salvar").click()
        page1.close()
    
        # 5. Incluir em Bloco de Assinatura
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.locator("html").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.get_by_role("link", name="Incluir em Bloco de Assinatura").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("button", name="Novo Bloco").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("textbox", name="Descrição:").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("textbox", name="Descrição:").fill(title)
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("button", name="Salvar").click()
        page.locator("iframe[name=\"ifrConteudoVisualizacao\"]").content_frame.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("button", name="Incluir", exact=True).click()
