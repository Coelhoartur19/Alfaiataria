from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base

class GrupoUsuario(Base):
    __tablename__ = "grupos_usuarios"

    IDGrupo = Column(Integer, primary_key=True, index=True)
    NomeGrupo = Column(String(60), unique=True, nullable=False)
    Descricao = Column(String(255))

    usuarios = relationship("Usuario", back_populates="grupo")


class Usuario(Base):
    __tablename__ = "usuarios"

    IDUsuario = Column(Integer, primary_key=True, index=True)
    Nome = Column(String(120), nullable=False)
    Email = Column(String(150), unique=True)
    SenhaHash = Column(String(255))
    IDGrupo = Column(Integer, ForeignKey("grupos_usuarios.IDGrupo"), nullable=False)
    CriadoEm = Column(TIMESTAMP)

    grupo = relationship("GrupoUsuario", back_populates="usuarios")


class Cliente(Base):
    __tablename__ = "Clientes"

    IDCliente = Column(Integer, primary_key=True, index=True)
    Nome = Column(String(120), nullable=False)
    CPF = Column(String(11), unique=True)
    CriadoEm = Column(TIMESTAMP)


class Funcionario(Base):
    __tablename__ = "Funcionarios"

    IDFuncionario = Column(Integer, primary_key=True, index=True)
    Nome = Column(String(120), nullable=False)
    CPF = Column(String(11), unique=True)
    Cargo = Column(String(60))
    Salario = Column(Float)
    CriadoEm = Column(TIMESTAMP)


class Produto(Base):
    __tablename__ = "Produtos"

    IDProduto = Column(Integer, primary_key=True, index=True)
    Nome = Column(String(120), nullable=False)
    Categoria = Column(String(80))
    Descricao = Column(Text)
    Preco = Column(Float, nullable=False)
    Estoque = Column(Integer, nullable=False, default=0)


class Venda(Base):
    __tablename__ = "Vendas"

    IDVenda = Column(Integer, primary_key=True, index=True)
    IDCliente = Column(Integer, ForeignKey("Clientes.IDCliente"), nullable=False)
    IDFuncionario = Column(Integer, ForeignKey("Funcionarios.IDFuncionario"), nullable=False)
    DataVenda = Column(TIMESTAMP)
    Total = Column(Float, default=0)

    cliente = relationship("Cliente")
    funcionario = relationship("Funcionario")
    itens = relationship("ItemVenda", back_populates="venda")


class ItemVenda(Base):
    __tablename__ = "ItensVenda"

    IDItem = Column(Integer, primary_key=True, index=True)
    IDVenda = Column(Integer, ForeignKey("Vendas.IDVenda"), nullable=False)
    IDProduto = Column(Integer, ForeignKey("Produtos.IDProduto"), nullable=False)
    Quantidade = Column(Integer, nullable=False)
    PrecoUnitario = Column(Float, nullable=False)

    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")
