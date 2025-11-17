from sqlalchemy import Column, Integer, String, ForeignKey, Double, Text, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from .database import Base


# ---------------------------------------
# TABELA: grupos_usuarios
# ---------------------------------------
class GrupoUsuario(Base):
    __tablename__ = "grupos_usuarios"

    IDGrupo = Column(Integer, primary_key=True, autoincrement=True)
    NomeGrupo = Column(String(60), unique=True, nullable=False)
    Descricao = Column(String(255))

    usuarios = relationship("Usuario", back_populates="grupo")


# ---------------------------------------
# TABELA: usuarios
# ---------------------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    IDUsuario = Column(Integer, primary_key=True, autoincrement=True)
    Nome = Column(String(120), nullable=False)
    Email = Column(String(150), unique=True)
    SenhaHash = Column(String(255))
    IDGrupo = Column(Integer, ForeignKey("grupos_usuarios.IDGrupo"), nullable=False)
    CriadoEm = Column(TIMESTAMP)

    grupo = relationship("GrupoUsuario", back_populates="usuarios")


# ---------------------------------------
# TABELA: Produtos
# ---------------------------------------
class Produto(Base):
    __tablename__ = "Produtos"

    IDProduto = Column(Integer, primary_key=True, autoincrement=True)
    Nome = Column(String(120), nullable=False)
    Categoria = Column(String(80))
    Descricao = Column(Text)
    Preco = Column(Double, nullable=False)
    Estoque = Column(Integer, nullable=False, default=0)


# ---------------------------------------
# TABELA: Vendas
# ---------------------------------------
class Venda(Base):
    __tablename__ = "Vendas"

    IDVenda = Column(Integer, primary_key=True, autoincrement=True)
    IDUsuarioCliente = Column(Integer, ForeignKey("usuarios.IDUsuario"), nullable=False)
    IDUsuarioAtendente = Column(Integer, ForeignKey("usuarios.IDUsuario"), nullable=False)
    DataVenda = Column(TIMESTAMP)
    Total = Column(Double, nullable=False, default=0)


# ---------------------------------------
# TABELA: ItensVenda
# ---------------------------------------
class ItemVenda(Base):
    __tablename__ = "ItensVenda"

    IDItem = Column(Integer, primary_key=True, autoincrement=True)
    IDVenda = Column(Integer, ForeignKey("Vendas.IDVenda"), nullable=False)
    IDProduto = Column(Integer, ForeignKey("Produtos.IDProduto"), nullable=False)
    Quantidade = Column(Integer, nullable=False)
    PrecoUnitario = Column(Double, nullable=False)


# ---------------------------------------
# TABELA: MovimentacoesEstoque
# ---------------------------------------
class MovimentacaoEstoque(Base):
    __tablename__ = "MovimentacoesEstoque"

    IDMovimentacao = Column(Integer, primary_key=True, autoincrement=True)
    IDProduto = Column(Integer, ForeignKey("Produtos.IDProduto"), nullable=False)
    TipoMovimentacao = Column(Enum("Entrada", "Saída"), nullable=False)
    Quantidade = Column(Integer, nullable=False)
    DataMovimentacao = Column(TIMESTAMP)


# ---------------------------------------
# TABELA: AvisosEstoque
# ---------------------------------------
class AvisoEstoque(Base):
    __tablename__ = "AvisosEstoque"

    IDAviso = Column(Integer, primary_key=True, autoincrement=True)
    IDProduto = Column(Integer, ForeignKey("Produtos.IDProduto"), nullable=False)
    Mensagem = Column(String(255), nullable=False)
    DataAviso = Column(TIMESTAMP)
