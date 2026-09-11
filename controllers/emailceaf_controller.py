from core import ft, threading, pd
import time # Apenas para simular o tempo de processamento
from models.emailceaf_model import EmailceafModel

class EmailceafController:
    """
    Controller for emailceaf page
    """

    def __init__(self, page, db_connection=None, model=None):
        self.page = page
        self.model = model or EmailceafModel(db_connection)

        # --- Callbacks de UI (Substituídos pela View) ---
        self.on_progress = lambda pct: None
        self.on_status   = lambda msg: None
        self.on_done     = lambda output_dir: None
        self.on_error    = lambda msg: None

        # --- Variáveis de Estado da Automação ---
        self._file_path = None
        self._pasta1_path = None
        self._pasta2_path = None
        self._tipo_programacao = "complementar" # Valor padrão

    def get_title(self):
        return "Automação: Programação Regular e Complementar de E-mails CEAF"
    
    def load_saved_credentials(self, system_name):
        try:
            return self.model.buscar_credenciais(system_name)
        except Exception as e:
            self._show_snack(f"Erro ao buscar: {e}")
            return None

    def save_credentials(self, username, password, system_name):
        if not username or not password:
            self._show_snack("Preencha e-mail e senha!")
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

    # --- Setters para receber os dados da View ---
    def set_file_path(self, path):
        self._file_path = path

    def set_pasta1_path(self, path):
        self._pasta1_path = path

    def set_pasta2_path(self, path):
        self._pasta2_path = path

    def set_tipo_programacao(self, tipo):
        self._tipo_programacao = tipo

    # --- Lógica Principal de Processamento ---
    def start_processing(self):
        """
        Executa a automação pesada. 
        Como é chamada pelo run_in_executor na View, não vai travar a interface.
        """
        try:
            # 1. Validação de segurança no backend
            if not self._file_path:
                raise ValueError("A planilha de controle não foi informada.")
            if not self._pasta1_path:
                raise ValueError("A Pasta 1 não foi informada.")
            if self._tipo_programacao == "regular" and not self._pasta2_path:
                raise ValueError("A Pasta 2 é obrigatória para programação regular.")

            # 2. Início do Processo
            self.on_status("Iniciando leitura da planilha controle...")
            self.on_progress(0.1)
            
            # EXEMPLO: Aqui você leria o Excel usando o pandas
            # df_controle = pd.read_excel(self._file_path)
            time.sleep(1) # Simulação de tempo
            
            # 3. Leitura da Pasta 1
            self.on_status(f"Processando arquivos da pasta 1 ({self._tipo_programacao})...")
            self.on_progress(0.3)
            time.sleep(1) # Simulação de tempo
            
            # 4. Leitura da Pasta 2 (Se aplicável)
            if self._tipo_programacao == "regular":
                self.on_status("Processando arquivos da pasta 2...")
                self.on_progress(0.4)
                time.sleep(1) # Simulação de tempo
            
            # 5. Loop de Envio de E-mails
            self.on_status("Iniciando disparos de e-mail...")
            total_emails = 5 # Simulação: df_controle.shape[0]
            
            for i in range(total_emails):
                # AQUI ENTRA A LÓGICA DO SEU MODEL PARA ENVIAR O EMAIL
                time.sleep(0.5) 
                
                # Cálculo de progresso de 40% a 95%
                base_pct = 0.4
                pct = base_pct + ((i + 1) / total_emails) * 0.55
                
                self.on_progress(pct)
                self.on_status(f"Enviando e-mail {i+1} de {total_emails}...")

            # 6. Finalização
            self.on_status("Gerando relatórios e finalizando...")
            self.on_progress(1.0)
            time.sleep(0.5)
            
            # Aciona o término na View informando a pasta que o usuário poderá abrir 
            # (Pode ser a pasta 1 ou uma pasta de logs específica que você criar)
            self.on_done(self._pasta1_path)

        except Exception as e:
            # Em caso de qualquer erro, avisa a View
            self.on_error(str(e))