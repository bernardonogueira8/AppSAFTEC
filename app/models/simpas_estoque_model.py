from core.base_model import BaseModel
from core.database import _connect_sqlite


class Simpas_estoqueModel(BaseModel):
    table_name = "simpas_estoque"
