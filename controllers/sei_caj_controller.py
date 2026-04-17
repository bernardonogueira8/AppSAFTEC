from core import ft, threading, pd, sync_playwright
from models.sei_caj_model import Sei_cajModel


class SeiCajController:
    """
    Controller for sei_caj page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or Sei_cajModel(db_connection)

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
            return False  # Retorna Falso, não avança a tela

        try:
            self.model.salvar_credenciais(username, password, system_name)
            self._show_snack(f"Credenciais do {system_name} salvas!")
            return True  # Retorna Verdadeiro, permite avançar
        except Exception as e:
            self._show_snack(f"Erro ao salvar: {e}")
            return False

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.overlay.append(snack)
        self.page.update()

    def start_automation(self, numero_sei_input, caminho_arquivo_input):
        # 1. Recupera as credenciais salvas previamente
        credentials = self.load_saved_credentials("SEI")

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if bool(numero_sei_input) == bool(caminho_arquivo_input):
            self._show_snack("Preencha o número SEI ou selecione o arquivo!")
            return

        self._show_snack("Iniciando automação Playwright...")

        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(
                credentials[0],
                credentials[1],
                numero_sei_input,
                caminho_arquivo_input,
            ),
        )
        automacao_thread.start()

    def _run_playwright_script(self, username, password, numero_sei, caminho_arquivo):
        """
        Executa a rotina de automação no sistema SEI.
        """
        self._show_snack(f"Iniciando automação no SEI para o usuário: {username}")
        try:
            # Inicializa o Playwright de forma síncrona
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=False, slow_mo=500)
                page = browser.new_page()
                self._show_snack("Navegador aberto. Acessando a página de login...")

                self.open_browser(page, username, password, numero_sei, caminho_arquivo)
                browser.close()

        except Exception as e:
            self._show_snack(f"Erro: {e}")
            raise e

    def open_browser(self, page, username, password, numero_sei, caminho_arquivo):
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

        # 2. Acessar SEI
        for df, row in df.iterrows():
            sei = row["SEI"]
            self._show_snack(f"Pesquisando o processo SEI: {sei}...")
            page.get_by_role("textbox", name="Pesquisar...").click()
            page.get_by_role("textbox", name="Pesquisar...").fill(sei)
            page.get_by_role("img", name="Pesquisa Rápida").click()
            # Caso precise Reabrir o processo, clicar no link "Reabrir Processo"
            modal_frame = page.frame_locator('iframe[name="modal-frame"]')
            senha_input = modal_frame.get_by_role("textbox", name="Senha:")

            # Verifica se o campo de senha aparece em até 2 segundos
            if senha_input.is_visible(timeout=2000):
                senha_input.fill(password)
                modal_frame.get_by_role("button", name="Acessar").click()

            try:
                page.frame_locator('iframe[name="ifrVisualizacao"]').get_by_role(
                    "link", name="Reabrir Processo"
                ).click(timeout=1500)
            except:
                pass

            # Incluido documento, informação para processo, marcar como sigiloso e selecionar hipótese legal
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
            content = """
            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><b>AO NAJS</b></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Para conhecimento e, se necess&aacute;rio, atualiza&ccedil;&atilde;o da CI Inaugural (<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei146466273" style="text-indent:0;">00135702387</a></span>).</span></span></span></span></span></span></span></span></span></span></span><br />
            &nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Conforme delibera&ccedil;&atilde;o SAFTEC, contida em processo de n&deg; <span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei4287480" style="text-indent:0;">019.8699.2019.0003499-27</a></span> (<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei142178159" style="text-indent:0;">00131714112</a></span>), especificamente, quanto &agrave; ado&ccedil;&atilde;o da seguinte provid&ecirc;ncia:</span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:200px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><em><strong>Ademais, cumpre destacar que, nos casos de processos de aquisi&ccedil;&atilde;o por meio de Saque de Registro de Pre&ccedil;os, <u>dever&aacute; a Coordena&ccedil;&atilde;o de A&ccedil;&atilde;o Judicial da Assist&ecirc;ncia Farmac&ecirc;utica &ndash; CAJ/DASF/SAFTEC registrar, de forma expressa, a impossibilidade de aquisi&ccedil;&atilde;o pelo pre&ccedil;o registrado, bem como dar ci&ecirc;ncia do respectivo cen&aacute;rio nos processos judiciais correlatos, de modo a viabilizar a ado&ccedil;&atilde;o das medidas cab&iacute;veis pelo ju&iacute;zo competente</u>, assegurando-se, simultaneamente, a legalidade da atua&ccedil;&atilde;o administrativa, a economicidade da despesa p&uacute;blica e a efetividade da ordem judicial.</strong></em></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Trata-se de processo referente &agrave; aquisi&ccedil;&atilde;o do item <strong>&quot;</strong></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span><strong>M</strong></span></span></span></span></span></span></span></span></span></span></span><strong>ICOFENOLATO MOFETILA 500 MG COMPRIMIDO</strong><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><strong>&quot;</strong>, destinado ao atendimento de demandas judiciais/administrativas, por meio de Registro de Pre&ccedil;os, Preg&atilde;o Eletr&ocirc;nico n&ordm; </span></span></span></span></span></span></span></span></span></span></span>044/2025<span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">, adjudicado &agrave; empresa </span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span><strong data-end="516" data-start="487">MEDISIL MEDICAMENTOS LTDA,</strong><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"> tendo como <strong>fabricante n&atilde;o exclusivo</strong> a </span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span><strong data-end="717" data-start="710">EMS</strong><strong data-end="516" data-start="509">/SA</strong><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><strong>.</strong><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><strong>, </strong>evento SEI n&ordm; <span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei146804818" style="text-indent:0;">00136018331</a></span><strong>.</strong></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Conforme orienta&ccedil;&otilde;es constantes no processo SEI n&ordm; <span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei114794542" style="text-indent:0;">019.8719.2025.0006359-55</a></span>, especialmente no despacho do evento SEI n&ordm; <span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137807519" style="text-indent:0;">00127620222</a></span>, que estabelece:</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Citacao" style="text-align:justify; margin-top:5px; margin-right:0; margin-bottom:5px; margin-left:160px"><span style="font-size:10pt"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:10pt"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:10pt"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:10pt"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">&quot;<strong data-end="1487" data-start="1417">b) Quanto aos medicamentos </strong><strong data-end="684" data-start="631">do Grupo A e de oncologia </strong><strong data-end="1487" data-start="1417"><span style="background-color:#f1c40f">com fornecedores diversos</span> (n&atilde;o exclusivos)</strong>, mant&eacute;m-se o entendimento de que o <strong data-end="1553" data-start="1523">pre&ccedil;o unit&aacute;rio referencial</strong> deve observar os valores previamente negociados e acordados pelo Minist&eacute;rio da Sa&uacute;de, consoante estabelece a referida S&uacute;mula Vinculante n&ordm; 60. <u>Contudo, <strong data-end="1757" data-start="1711"><span style="background-color:#f1c40f">havendo negativa do fornecedor em negociar</span></strong><span style="background-color:#f1c40f">, dever&aacute; a DA/SAFTEC proceder conforme entendimento da PGE exposto nos opinativos mencionados, adotando-se o pre&ccedil;o referencial com observ&acirc;ncia do limite estabelecido pelo </span><strong data-end="1936" data-start="1928"><span style="background-color:#f1c40f">PMVG</span></strong><span style="background-color:#f1c40f">, de modo a assegurar a continuidade do processo de aquisi&ccedil;&atilde;o e o regular cumprimento das demandas judiciais.&quot;</span></u></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Citacao" style="text-align:justify; margin-top:5px; margin-right:0; margin-bottom:5px; margin-left:160px">&nbsp;</p>

            <p class="Citacao" style="text-align:justify; margin-top:5px; margin-right:0; margin-bottom:5px; margin-left:160px"><span style="font-size:10pt"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Para mais, encaminha-se, em anexo, a planilha de refer&ecirc;ncia (evento SEI n&ordm; <span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137826499" style="text-indent:0;">00127637914</a></span>), contendo a rela&ccedil;&atilde;o dos medicamentos classificados como exclusivos, conforme informa&ccedil;&otilde;es prestadas pela Diretoria de Assist&ecirc;ncia Farmac&ecirc;utica &ndash; DASF/SAFTEC, pela Diretoria Administrativa &ndash; DA/SAFTEC e por esta Superintend&ecirc;ncia.</span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Citacao" style="text-align:justify; margin-top:5px; margin-right:0; margin-bottom:5px; margin-left:160px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">E, conforme novas delibera&ccedil;&otilde;es SAFTEC, contidas <span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">em processo de n&deg; 019.5022.2025.0174083-22, para prosseguimento de aquisi&ccedil;&otilde;es de medicamentos afetados pelo Tema 1234/STF.</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Portando, considerando que: a) o item n&atilde;o possui fabrica&ccedil;&atilde;o exclusiva; b) n&atilde;o logrou-se &ecirc;xito na negocia&ccedil;&atilde;o junto ao fornecedor do MS; c) o medicamento n&atilde;o consta no rol dos medicamentos elencados na supracitada planilha de refer&ecirc;ncia, elaborada pela SAFTEC.</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial">Encaminhamos os autos para:</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><strong data-end="1952" data-start="1942">Ao NRP</strong>: proceder com a libera&ccedil;&atilde;o<b> </b><strong data-end="2006" data-start="1965">da Ata de Registro de Pre&ccedil;os</strong>, viabilizando o saque do item;</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px">&nbsp;</p>

            <p class="Tabela_Texto_Justificado" style="text-align:justify; margin-top:0; margin-right:4px; margin-bottom:0; margin-left:4px"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><span style="font-size:medium"><span style="font-family:Arial"><span style="overflow-wrap:normal"><span style="color:#000000"><span style="font-style:normal"><span style="font-variant-ligatures:normal"><span style="font-weight:400"><span style="white-space:normal"><span style="text-decoration-thickness:initial"><span style="text-decoration-style:initial"><span style="text-decoration-color:initial"><strong data-end="2049" data-start="2040">&Agrave; CCO</strong>: dar seguimento &agrave; aquisi&ccedil;&atilde;o conforme previsto, observando a formaliza&ccedil;&atilde;o dos instrumentos aquisitivos e financeiros.</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></p>

            <p data-end="754" data-start="285">Em atendimento ao&nbsp;<strong data-end="330" data-start="303">Despacho n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei146709896" style="text-indent:0;">00135930086</a></span></strong>, informo que o item&nbsp;<strong data-end="398" data-start="351">MICOFENOLATO DE MOFETILA 500 MG, COMPRIMIDO</strong>, destinado ao atendimento da&nbsp;<strong data-end="460" data-start="428">A&ccedil;&atilde;o Judicial n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei136580545" style="text-indent:0;">00126472923</a></span></strong>, foi adjudicado &agrave; empresa&nbsp;<strong data-end="516" data-start="487">MEDISIL MEDICAMENTOS LTDA</strong>, no &acirc;mbito do&nbsp;<strong data-end="563" data-start="531">Preg&atilde;o Eletr&ocirc;nico n&ordm; 44/2025</strong>, atrav&eacute;s do&nbsp;<strong data-end="620" data-start="576">processo SEI n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei109370413" style="text-indent:0;">019.8712.2024.0185167-94</a></span></strong>, e se encontra&nbsp;<strong data-end="684" data-start="636">pausado para atendimento de demanda judicial</strong>, com vig&ecirc;ncia at&eacute;&nbsp;<strong data-end="717" data-start="703">16/06/2026</strong>, ao valor unit&aacute;rio de&nbsp;<strong data-end="751" data-start="740">R$ 1,04</strong>.</p>

            <p data-end="1145" data-start="756">Considerando que o referido item &eacute; atualmente distribu&iacute;do pelo&nbsp;<strong data-end="842" data-start="819">Minist&eacute;rio da Sa&uacute;de</strong>&nbsp;ao valor de&nbsp;<strong data-end="878" data-start="855">R$ 0,69 por unidade</strong>&nbsp;(<strong data-end="910" data-start="880">Nota Fiscal n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137436164" style="text-indent:0;">00127271715</a></span></strong>), este&nbsp;<strong data-end="950" data-start="918">N&uacute;cleo de Registro de Pre&ccedil;os</strong>&nbsp;solicitou &agrave; empresa&nbsp;<strong data-end="982" data-start="971">EMS S/A</strong>, fabricante respons&aacute;vel, a&nbsp;<strong data-end="1043" data-start="1010">adequa&ccedil;&atilde;o do valor registrado</strong>&nbsp;ao pre&ccedil;o praticado pelo Minist&eacute;rio da Sa&uacute;de, conforme registrado no&nbsp;<strong data-end="1142" data-start="1112">Instrumento n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137470564" style="text-indent:0;">00127303970</a></span></strong>.</p>

            <p data-end="1778" data-start="1147">Em resposta (<strong data-end="1185" data-start="1160">evento n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137548572" style="text-indent:0;">00127376982</a></span></strong>), a empresa&nbsp;<strong data-end="1252" data-start="1198">manifestou impossibilidade de atender &agrave; negocia&ccedil;&atilde;o</strong>, sob a justificativa de que os valores praticados pelo Minist&eacute;rio da Sa&uacute;de decorrem de&nbsp;<strong data-end="1376" data-start="1340">condi&ccedil;&otilde;es comerciais espec&iacute;ficas</strong>, tais como volume de compra, log&iacute;stica centralizada, regularidade dos pedidos e demais particularidades inerentes ao &oacute;rg&atilde;o federal. Argumentou, ainda, que tais circunst&acirc;ncias&nbsp;<strong data-end="1641" data-start="1552">inviabilizam a pr&aacute;tica de pre&ccedil;os equivalentes aos pactuados com o Minist&eacute;rio da Sa&uacute;de</strong>, sustentando que o valor adjudicado correspondeu ao&nbsp;<strong data-end="1729" data-start="1694">menor pre&ccedil;o ofertado no certame</strong>&nbsp;e permanece inferior ao&nbsp;<strong data-end="1775" data-start="1754">PMVG sem impostos</strong>.</p>

            <p data-end="2136" data-start="1780">Ademais, quando consultada acerca da&nbsp;<strong data-end="1863" data-start="1824">viabilidade de fornecimento do item</strong>&nbsp;ou da&nbsp;<strong data-end="1959" data-start="1870">possibilidade de ades&atilde;o (&ldquo;carona&rdquo;) &agrave; Ata de Registro de Pre&ccedil;os do Minist&eacute;rio da Sa&uacute;de,&nbsp;</strong>atrav&eacute;s do e-mail acostado no evento n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137471741" style="text-indent:0;">00127305074</a></span>, a empresa&nbsp;<strong data-end="2031" data-start="1971">reiterou a impossibilidade de igualar os pre&ccedil;os federais</strong>, apresentando os mesmos fundamentos acima mencionados, conforme consta no&nbsp;<strong data-end="2133" data-start="2106">evento n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei137598101" style="text-indent:0;">00127423416</a></span></strong>.</p>

            <p data-end="2317" data-start="2138">Ressalta-se que o medicamento&nbsp;<strong data-end="2187" data-start="2168">n&atilde;o &eacute; exclusivo</strong>, conforme&nbsp;<strong data-end="2243" data-start="2198">cota&ccedil;&atilde;o acostada no evento n&ordm;&nbsp;<span contenteditable="false" style="text-indent:0;"><a class="ancora_sei" id="lnkSei111566106" style="text-indent:0;">00103173219</a></span></strong>, o que refor&ccedil;a a possibilidade de obten&ccedil;&atilde;o junto a outros fornecedores.</p>

            <p data-end="2498" data-start="2319">A diferen&ccedil;a percentual entre o valor adjudicado (<strong data-end="2379" data-start="2368">R$ 1,04</strong>) e o valor atualmente praticado pelo&nbsp;<strong data-end="2440" data-start="2417">Minist&eacute;rio da Sa&uacute;de</strong>&nbsp;(<strong data-end="2453" data-start="2442">R$ 0,69</strong>) corresponde a aproximadamente&nbsp;<strong data-end="2495" data-start="2485">33,65%</strong>.</p>

            <p cke-dissolved="true" cke-list-level="1" cke-symbol="·">&nbsp;</p>

            <p cke-dissolved="true" cke-list-level="1" cke-symbol="·">Atenciosamente,</p>

            <p cke-dissolved="true" cke-list-level="1" cke-symbol="·">&nbsp;</p>
            """

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

            page.wait_for_timeout(4000)
            frame = page.frame_locator('iframe[name="ifrVisualizacao"]')
            frame.get_by_role("link", name="Enviar Processo").click()
            unidade_input = frame.locator("#txtUnidade")
            unidade_input.wait_for(state="visible", timeout=5000)
            unidade_input.press_sequentially("SESAB/GAB/NAJS", delay=100)
            page.wait_for_timeout(4000)
            opcao_link = frame.get_by_role("link", name="SESAB/GAB/NAJS - Núcleo de")
            opcao_link.wait_for(state="visible", timeout=5000)
            opcao_link.click()
            page.wait_for_timeout(4000)
            page.close()
