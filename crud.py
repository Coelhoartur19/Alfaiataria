# backend/crud.py
from sqlalchemy.orm import Session
from . import models, schemas, security

# Produtos (MySQL)
def listar_produtos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Produto).offset(skip).limit(limit).all()

def criar_produto(db: Session, produto: schemas.ProdutoBase):
    db_obj = models.Produto(
        Nome=produto.nome,
        Categoria=produto.categoria,
        Descricao="",
        Preco=produto.preco,
        Estoque=produto.estoque or 0
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def buscar_produto(db: Session, id_produto: int):
    return db.query(models.Produto).filter(models.Produto.IDProduto == id_produto).first()

def atualizar_produto(db: Session, id_produto: int, produto: schemas.ProdutoBase):
    db_obj = buscar_produto(db, id_produto)
    if db_obj:
        db_obj.Nome = produto.nome
        db_obj.Categoria = produto.categoria
        db_obj.Preco = produto.preco
        db_obj.Estoque = produto.estoque
        db.commit()
        db.refresh(db_obj)
    return db_obj

def remover_produto(db: Session, id_produto: int):
    db_obj = buscar_produto(db, id_produto)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

# Grupos
def listar_grupos(db: Session):
    return db.query(models.GrupoUsuario).all()

def buscar_grupo_por_id(db: Session, id_grupo: int):
    return db.query(models.GrupoUsuario).filter(models.GrupoUsuario.IDGrupo == id_grupo).first()

# Usuarios (MySQL)
def listar_usuarios(db: Session):
    return db.query(models.Usuario).all()

def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed = security.hash_password(usuario.senha)
    db_obj = models.Usuario(
        Nome=usuario.nome,
        Email=usuario.email,
        IDGrupo=usuario.grupo_id,
        SenhaHash=hashed
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    novo = models.Usuario(
        NomeUsuario=usuario.NomeUsuario,
        Email=usuario.Email,
        Senha=usuario.Senha,
        IDGrupo=3  # CLIENTE fixo
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def buscar_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.Email == email).first()

def buscar_usuario_por_id(db: Session, id_usuario: int):
    return db.query(models.Usuario).filter(models.Usuario.IDUsuario == id_usuario).first()
