# backend/crud.py
from sqlalchemy.orm import Session
from . import models, schemas, security

# Produtos
def listar_produtos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Produto).offset(skip).limit(limit).all()

def criar_produto(db: Session, produto: schemas.ProdutoCreate):
    db_obj = models.Produto(
        Nome=produto.Nome,
        Categoria=produto.Categoria,
        Descricao=produto.Descricao,
        Preco=produto.Preco,
        Estoque=produto.Estoque or 0
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def buscar_produto(db: Session, id_produto: int):
    return db.query(models.Produto).filter(models.Produto.IDProduto == id_produto).first()

def atualizar_produto(db: Session, id_produto: int, produto: schemas.ProdutoCreate):
    db_obj = buscar_produto(db, id_produto)
    if db_obj:
        db_obj.Nome = produto.Nome
        db_obj.Categoria = produto.Categoria
        db_obj.Descricao = produto.Descricao
        db_obj.Preco = produto.Preco
        db_obj.Estoque = produto.Estoque
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
    return db.query(models.Grupo).all()

def buscar_grupo_por_id(db: Session, id_grupo: int):
    return db.query(models.Grupo).filter(models.Grupo.IDGrupo == id_grupo).first()

# Usuarios
def listar_usuarios(db: Session):
    return db.query(models.Usuario).all()

def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed = security.hash_password(usuario.Senha)
    db_obj = models.Usuario(
        Nome=usuario.Nome,
        Email=usuario.Email,
        IDGrupo=usuario.IDGrupo,
        SenhaHash=hashed
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def buscar_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.Email == email).first()

def buscar_usuario_por_id(db: Session, id_usuario: int):
    return db.query(models.Usuario).filter(models.Usuario.IDUsuario == id_usuario).first()
