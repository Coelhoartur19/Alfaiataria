from sqlalchemy.orm import Session
from . import models, schemas, security


# ---------------------------------------------------------
# PRODUTOS (MySQL)
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# GRUPOS
# ---------------------------------------------------------
def listar_grupos(db: Session):
    return db.query(models.GrupoUsuario).all()


def buscar_grupo_por_id(db: Session, id_grupo: int):
    return db.query(models.GrupoUsuario).filter(models.GrupoUsuario.IDGrupo == id_grupo).first()


# ---------------------------------------------------------
# USUÁRIOS (MySQL)
# ---------------------------------------------------------
def listar_usuarios(db: Session):
    return db.query(models.Usuario).all()


def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    """Cria usuário com hash e grupo correto."""
    hashed = security.hash_password(usuario.senha)

    db_obj = models.Usuario(
        Nome=usuario.nome,
        Email=usuario.email,
        SenhaHash=hashed,
        IDGrupo=usuario.grupo_id
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return db_obj


def buscar_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.Email == email).first()


def buscar_usuario_por_id(db: Session, id_usuario: int):
    return db.query(models.Usuario).filter(models.Usuario.IDUsuario == id_usuario).first()


# ---------------------------------------------------------
# VENDAS
# ---------------------------------------------------------
def criar_venda(db: Session, venda: schemas.VendaCreate):

    # Calcula total
    total = sum(item.preco * item.quantidade for item in venda.itens)

    # Cria venda principal
    nova_venda = models.Venda(
        IDUsuarioCliente=venda.id_usuario,
        IDUsuarioAtendente=venda.id_usuario,
        Total=total
    )
    db.add(nova_venda)
    db.commit()
    db.refresh(nova_venda)

    # Cria itens da venda
    for item in venda.itens:
        novo_item = models.ItemVenda(
            IDVenda=nova_venda.IDVenda,
            IDProduto=item.id,
            Quantidade=item.quantidade,
            PrecoUnitario=item.preco
        )
        db.add(novo_item)

    db.commit()
    return nova_venda
