from core.logger import get_logger
from core import ft, pd, threading, sync_playwright
from models.sigaf_contrapartida_model import Sigaf_contrapartidaModel

logger = get_logger("App")

class SigafContrapartidaController:
    """
    Controller for sigaf_contrapartida page
    """
    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or Sigaf_contrapartidaModel(db_connection)

    def get_title(self):
        return "SIGAF: Repasse de Contrapartida"

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
            self._show_snack(f"Credenciais do {system_name} prontas!")
            return True  # Retorna Verdadeiro, permite avançar
        except Exception as e:
            logger.error(f"Erro ao salvar: {e}")
            return False

    def _show_snack(self, message):
        """Método auxiliar para exibir alertas rápidos na tela"""
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.overlay.append(snack)
        self.page.update()
        
    def _show_snack_erro(self, message):
        """Exibe um alerta de erro que só fecha no clique"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            duration=3600000, 
            action="Fechar",
            on_action=lambda e: self._close_snack(snack),
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    def _close_snack(self, snack):
        snack.open = False
        self.page.update()

    def start_automation(self, number_cib_input, caminho_arquivo_input, system_name):
        credentials = self.load_saved_credentials(system_name)

        if not credentials:
            self._show_snack("Credenciais não encontradas. Salve-as primeiro!")
            return

        if not number_cib_input or not caminho_arquivo_input:
            self._show_snack("Preencha o número da CIB e selecione o arquivo!")
            return

        self._show_snack("Iniciando automação Playwright...")

        automacao_thread = threading.Thread(
            target=self._run_playwright_script,
            args=(
                credentials[0],
                credentials[1],
                number_cib_input,
                caminho_arquivo_input,
            ),
        )
        automacao_thread.start()

    def _format_df(self, caminho_arquivo, number_cib):
        df = pd.read_excel(caminho_arquivo).copy()
        #df = pd.read_excel("c:/Users/bernardo.silva/Downloads/PLANILHA_PARA_CHAMADO.xlsx").copy()
        #number_cib = '2'
        colunas_necessarias = [
            "DATA",
            "MUNICIPIO",
            "COMPETENCIA",
            "Nº NOB",
            "VALOR",
        ]
        if not all(col in df.columns for col in colunas_necessarias):
            raise ValueError("A planilha não possui as colunas necessárias.")
        df.loc[:, "DESCRIÇÃO"] = (
            "REPASSE FINANCEIRO AO FUNDO MUNICIPAL DE SAÚDE CONFORME RES CIB/BA Nº "
            + number_cib
            + " COMPETÊNCIA "
            + df["COMPETENCIA"].astype(str)
            + " -  NOB  "
            + df["Nº NOB"].astype(str)
        )
        df.loc[:, "VALOR_STR"] = df["VALOR"].apply(
            lambda x: "{:.2f}".format(x).replace(".", ",")
        )
        df.loc[:, "MUNICIPIO_BUSCA"] = (
            "PREFEITURA MUNICIPAL DE " + df["MUNICIPIO"].str.upper()
        )
        df['DATA'] = df['DATA'].apply(lambda x: x.replace(month=x.day, day=x.month) if pd.notna(x) else x)
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("CABACEIRA DO PARAGUACU", "CABACEIRAS DO PARAGUAÇU")
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("MUQUEM DO SAO FRANCISCO", "MUQUÉM DE SÃO FRANCISCO")
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("MARAGOJIPE", "MARAGOGIPE")
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("São Felix", "São Félix")
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("SANTA CRUZ CABRALIA", "SANTA CRUZ")
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("SANTA CRUZ DA VITORIA", "SANTA CRUZ DA")
        df["MUNICIPIO"] = df["MUNICIPIO"].str.replace("SANTA TERESINHA", "SANTA TEREZINHA")
        
        return df

    def _run_playwright_script(self, username, password, number_cib, caminho_arquivo):
        """
        Executa a rotina de automação no sistema SEI.
        """
        self._show_snack(f"Iniciando automação: {username} | CIB: {number_cib}")
        info_linha = "Preparando dados..."
        try:
            df = self._format_df(caminho_arquivo, number_cib)
            # Inicializa o Playwright de forma síncrona
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=False, slow_mo=500)
                page = browser.new_page()
                info_linha = self.open_browser(page, username, password, df)
                browser.close()
                self._show_snack("Automação concluída com sucesso!")
                logger.info("Automação concluída com sucesso!")

        except Exception as e:
            # Aqui garantimos que a mensagem de erro seja clara e o Snack fique parado
            mensagem_completa = f"Erro crítico: {str(e)}\nÚltimo status: {info_linha}"
            logger.error(mensagem_completa)
            self._show_snack_erro(mensagem_completa)
            raise e

    def open_browser(self, page, username, password, df):
        page.goto("http://homologa2.sigaf.sesab.ba.gov.br/")
        page.locator("#login").click()
        page.locator("#login").fill(username)
        page.locator('input[name="senha"]').click()
        page.locator('input[name="senha"]').fill(password)
        with page.expect_popup() as page3_info:
            page.get_by_role("button", name="Login de usuário").click()
        page3 = page3_info.value
        page.goto(
            "http://homologa2.sigaf.sesab.ba.gov.br/?page=meta/view&id_view=tb_lancamento_1&_menu_acessado=406"
        )
        ultima_linha_processada = "Iniciando iteração no DataFrame"
        
        for index, row in df.iterrows():
            # Atualizamos o status a cada iteração
            ultima_linha_processada = f"Linha {index + 2}/{len(df)+1}: {row['MUNICIPIO']}"
            logger.info(ultima_linha_processada)
            try:
                page.wait_for_timeout(1000)
                page.get_by_role("button", name="Adicionar Lançamento").click()
                
                page.locator('input[name="dia_dth_lancamento**246,0;201___dta//0/0"]').fill(
                    row["DATA"].strftime("%d")
                )
                page.locator('input[name="mes_dth_lancamento**246,0;201___dta//0/0"]').fill(
                    row["DATA"].strftime("%m")
                )
                page.locator('input[name="ano_dth_lancamento**246,0;201___dta//0/0"]').fill(
                    row["DATA"].strftime("%Y")
                )
                page.locator('input[name="dsc_lancamento**246,0;201___str//0/0"]').fill(
                    row["DESCRIÇÃO"]
                )
                page.locator(
                    'select[name="cod_lancamento_tipo**246,0;201___int//0/0"]'
                ).select_option("6")
                page.locator('input[name="vlr_lancamento**246,0;201___rea//0/0"]').fill(
                    row["VALOR_STR"]
                )
                page.wait_for_timeout(1000)
                logger.info(
                    f"Adicionando lançamento para o município: {row['MUNICIPIO']} | Valor: {row['VALOR_STR']}"
                )
                with page.expect_popup() as page4_info:
                    page.locator(
                        '[id="cod_unidade_saude**246,0;201___nfm//0/0_seleciona"]'
                    ).click()
                page4 = page4_info.value
                page4.get_by_role("textbox").click()
                page4.get_by_role("textbox").fill(
                    "PREFEITURA MUNICIPAL DE " + row["MUNICIPIO"].upper()
                )
                page4.get_by_role("button", name="Buscar").click()
                page4.locator("#ctr_item_listagem_0").check()
                page4.locator("#link_listagem #btn_lista_selecao_selecionar").click()
                page4.get_by_role("button", name="Selecionar").click()
                page4.close()
                try:
                    page.once("dialog", lambda dialog: dialog.dismiss())
                except:
                    pass
                page.wait_for_timeout(1000)
                page.get_by_role("button", name="Adicionar").click()
                logger.info(f"Progresso: {row['MUNICIPIO']} processado.")

            except Exception as error:
                raise Exception(f"Falha ao processar Município '{row['MUNICIPIO']}'. Detalhes: {error}")

        return ultima_linha_processada