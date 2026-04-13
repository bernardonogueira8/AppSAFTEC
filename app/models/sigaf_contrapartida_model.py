from core.base_model import BaseModel
from core.database import _connect_sqlite

class Sigaf_contrapartidaModel(BaseModel):
    def __init__(self, db_connection=None):
        # A conexão com o banco de dados é injetada no modelo
        self.db = db_connection or _connect_sqlite()

    def buscar_credenciais(self, system_name="SIGAF"):
        """Busca as credenciais salvas para o sistema especificado."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT username, password FROM sei_dma WHERE system_name = ? LIMIT 1",
            (system_name,),
        )
        return cursor.fetchone()  # Retorna uma tupla (user, pass) ou None se não achar

    def salvar_credenciais(self, username, password, system_name="SIGAF"):
        """Insere ou atualiza os dados no SQLite."""
        cursor = self.db.cursor()

        # Primeiro, verificamos se já existe um registro para esse sistema
        cursor.execute("SELECT id FROM sei_dma WHERE system_name = ?", (system_name,))
        registro = cursor.fetchone()

        if registro:
            # CORREÇÃO: Usar registro para extrair o ID numérico da tupla
            cursor.execute(
                "UPDATE sei_dma SET username = ?, password = ?, system_name = ? WHERE id = ? ",
                (username, password, system_name, registro[0]),
            )
        else:
            # Se não existe, inserimos (INSERT) normalmente
            cursor.execute(
                "INSERT INTO sei_dma (username, password, system_name) VALUES (?, ?, ?)",
                (username, password, system_name),
            )
        self.db.commit()
