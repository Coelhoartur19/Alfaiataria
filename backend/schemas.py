from pydantic import BaseModel, EmailStr
from typing import Optional, List


# -------------------------------
# USUÁRIOS
# -------------------------------
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    grupo_id: int


class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    grupo_id: int

    class Config:
        from_attributes = True


# -------------------------------
# PRODUTOS
# -------------------------------
class ProdutoBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    preco: float
    estoque: Optional[int] = 0


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoOut(ProdutoBase):
    id: int

    class Config:
        from_attributes = True


# -------------------------------
# GRUPOS
# -------------------------------
class GrupoOut(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------------
# VENDAS
# -------------------------------
class ItemVenda(BaseModel):
    id: int
    quantidade: int
    preco: float
    total: float


class VendaCreate(BaseModel):
    id_usuario: int
    itens: List[ItemVenda]
