from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from . import models

# Cria as tabelas, se não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Loja")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "API Loja Online"}


@app.get("/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(models.Produto).all()
    return produtos


@app.get("/clientes")
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()


@app.get("/funcionarios")
def listar_funcionarios(db: Session = Depends(get_db)):
    return db.query(models.Funcionario).all()
