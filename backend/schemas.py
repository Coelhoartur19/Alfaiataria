from pydantic import BaseModel, EmailStr
from typing import Optional


# -------------------------------------
# USUÁRIOS
# -------------------------------------
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
        from_attributes = True  # Pydantic V2


# -------------------------------------
# PRODUTOS
# -------------------------------------
class ProdutoBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    preco: float
    estoque: Optional[int] = 0


class ProdutoOut(ProdutoBase):
    id: int

    class Config:
        from_attributes = True


# -------------------------------------
# GRUPOS
# -------------------------------------
class GrupoOut(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None

    class Config:
        from_attributes = True

# -------------------------------------
# LOGIN
# -------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class LoginResponse(BaseModel):
    mensagem: str
    id: str
    nome: str
    email: str
    grupo: str
