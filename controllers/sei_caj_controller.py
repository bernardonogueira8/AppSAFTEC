from core import ft, threading, pd, sync_playwright, os, sys, json
from models.sei_caj_model import Sei_cajModel


class SeiCajController:
    """
    Controller for sei_caj page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or Sei_cajModel(db_connection)

    # --- NOVO MÉTODO: Carrega os templates do arquivo JSON ---
    def load_templates_from_json(self):
        try:
            # Detecta o caminho correto se está em desenvolvimento ou compilado
            if sys.executable.lower().endswith(("python.exe", "pythonw.exe")):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            else:
                base_dir = os.path.dirname(sys.executable)

            json_path = os.path.join(base_dir, "assets", "templates.json")

            if not os.path.exists(json_path):
                self._show_snack("Arquivo templates.json não encontrado em assets!")
                return {}

            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._show_snack(f"Erro ao carregar os templates: {e}")
            return {}

    def get_title(self):
        return "Automação: SEI CAJ"

    def load_saved_credentials(self, system_name):
        try:
            return self.model.buscar_credenciais(system_name)
        except Exception as e:
            self._show_snack(f"Erro ao buscar: {e}")
            return None

    def save_credentials(self, username, password, system_name):
        if not username or not password:
            self._show_snack("Preencha usuário e senha!")
            return False

        try:
            self.model.salvar_credenciais(username, password, system_name)
            self._show_snack(f"Credenciais do {system_name} salvas!")
            return True
        except Exception as e:
            self._show_snack(f"Erro ao salvar: {e}")
            return False

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.overlay.append(snack)
        self.page.update()

    # --- MODIFICADO: Agora recebe o parâmetro 'template_content' ---
    def start_automation(self, numero_sei_input, caminho_arquivo_input, template_content):
        credentials = self.load_saved_credentials("SEI")

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if bool(numero_sei_input) == bool(caminho_arquivo_input):
            self._show_snack("Preencha o número SEI ou selecione o arquivo!")
            return

        if not template_content:
            self._show_snack("Selecione um modelo de documento válido!")
            return

        self._show_snack("Iniciando automação Playwright...")

        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(
                credentials[0],
                credentials[1],
                numero_sei_input,
                caminho_arquivo_input,
                template_content, # <--- Passando o HTML dinâmico para a thread
            ),
        )
        automacao_thread.start()

    # --- MODIFICADO: Adicionado 'template_content' nos argumentos ---
    def _run_playwright_script(self, username, password, numero_sei, caminho_arquivo, template_content):
        """
        Executa a rotina de automação no sistema SEI.
        """
        self._show_snack(f"Iniciando automação no SEI para o usuário: {username}")
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=False, slow_mo=500)
                page = browser.new_page()
                self._show_snack("Navegador aberto. Acessando a página de login...")

                # Encaminha o conteúdo dinâmico para a função de navegação do browser
                self.open_browser(page, username, password, numero_sei, caminho_arquivo, template_content)
                browser.close()

        except Exception as e:
            self._show_snack(f"Erro: {e}")
            raise e

    # --- MODIFICADO: Adicionado 'template_content' e removido a string estática ---
    def open_browser(self, page, username, password, numero_sei, caminho_arquivo, template_content):
        df = (
            pd.read_excel(caminho_arquivo)
            if caminho_arquivo
            else pd.DataFrame({"SEI": [numero_sei]})
        )
        self._show_snack("Acessando o SEI...")
        page.goto("https://seibahia.ba.gov.br")
        page.get_by_role("textbox", name="Usuário").fill(username)
        page.get_by_role("textbox", name="Senha").fill(password)
        page.locator("#selOrgao").select_option("23")
        page.get_by_role("button", name="ACESSAR").click()

        for df, row in df.iterrows():
            sei = row["SEI"]
            self._show_snack(f"Pesquisando o processo SEI: {sei}...")
            page.wait_for_timeout(2000)
            page.get_by_role("textbox", name="Pesquisar...").click()
            page.get_by_role("textbox", name="Pesquisar...").fill(sei)
            page.get_by_role("img", name="Pesquisa Rápida").click()
            
            modal_frame = page.frame_locator('iframe[name="modal-frame"]')
            senha_input = modal_frame.get_by_role("textbox", name="Senha:")

            if senha_input.is_visible(timeout=2000):
                senha_input.fill(password)
                modal_frame.get_by_role("button", name="Acessar").click()

            try:
                page.frame_locator('iframe[name="ifrVisualizacao"]').get_by_role(
                    "link", name="Reabrir Processo"
                ).click(timeout=1500)
            except:
                pass

            page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
                "link", name="Incluir Documento"
            ).click()
            page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
                "link", name="Informação para Processo"
            ).click()
            page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_text(
                "Público"
            ).click()
            with page.expect_popup() as page1_info:
                page.locator('iframe[name="ifrVisualizacao"]').content_frame.locator(
                    "#divInfraBarraComandosSuperior"
                ).get_by_role("button", name="Salvar").click()
            page1 = page1_info.value
            
            # --- AGORA DINÂMICO: Recebe o conteúdo que veio da View ---
            content = template_content

            page1.locator('iframe[title="Corpo do Texto"]').content_frame.get_by_text(
                "[Insira aqui o conteúdo do"
            ).click()
            page1.get_by_role("button", name="Código-Fonte").click()
            campo = page1.get_by_role("textbox", name="Corpo do Texto")
            valor_atual = campo.input_value()
            parte_remover = '<p class="Texto_Justificado_Arial_12_Espaçamento_Simples">[Insira aqui&nbsp;o conte&uacute;do do documento]</p>'
            valor_limpo = valor_atual.replace(parte_remover, "")
            parte_remover = "\n\n<p>&nbsp;</p>"
            valor_limpo = valor_limpo.replace(parte_remover, "")
            parte_remover = '<p style="font-size:12pt;">&nbsp;</p>'
            valor_limpo = valor_limpo.replace(parte_remover, "")
            valor_final = valor_limpo + content
            campo.evaluate(
                "(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }",
                valor_final,
            )
            page1.get_by_role("button", name="Salvar").click()
            page1.get_by_role("button", name="Código-Fonte").click()
            page1.get_by_role("button", name="Salvar").click()
            page1.close()

            page.locator('iframe[name="ifrVisualizacao"]').content_frame.get_by_role(
                "link", name="Assinar Documento"
            ).click()
            page.locator('iframe[name="modal-frame"]').content_frame.get_by_role(
                "textbox", name="Senha"
            ).click()
            page.locator('iframe[name="modal-frame"]').content_frame.get_by_role(
                "textbox", name="Senha"
            ).fill(password)
            page.locator('iframe[name="modal-frame"]').content_frame.get_by_role(
                "button", name="Assinar"
            ).click()

            page.wait_for_timeout(2000)
            frame = page.frame_locator('iframe[name="ifrVisualizacao"]')
            frame.get_by_role("link", name="Enviar Processo").click()
            unidade_input = frame.locator("#txtUnidade")
            unidade_input.wait_for(state="visible", timeout=5000)
            unidade_input.press_sequentially("SESAB/GAB/NAJS", delay=100)
            page.wait_for_timeout(2000)
            opcao_link = frame.get_by_role("link", name="SESAB/GAB/NAJS - Núcleo de")
            opcao_link.wait_for(state="visible", timeout=5000)
            opcao_link.click()
            page.wait_for_timeout(2000)
            page.locator("iframe[name=\"ifrVisualizacao\"]").content_frame.get_by_role("button", name="Enviar").click()
            page.wait_for_timeout(15000)