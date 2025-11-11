# backend/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# Produtos
class ProdutoBase(BaseModel):
    Nome: str
    Categoria: Optional[str] = None
    Descricao: Optional[str] = None
    Preco: float
    Estoque: Optional[int] = 0

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoOut(ProdutoBase):
    IDProduto: int
    class Config:
        orm_mode = True

# Grupos
class GrupoBase(BaseModel):
    NomeGrupo: str
    Descricao: Optional[str] = None

class GrupoOut(GrupoBase):
    IDGrupo: int
    class Config:
        orm_mode = True

# Usuarios
class UsuarioBase(BaseModel):
    Nome: str
    Email: Optional[EmailStr] = None
    IDGrupo: int

class UsuarioCreate(UsuarioBase):
    Senha: str

class UsuarioOut(UsuarioBase):
    IDUsuario: int
    class Config:
        orm_mode = True

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
