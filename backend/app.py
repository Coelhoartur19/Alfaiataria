from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .database import Base, engine, SessionLocal
from . import models
from .database_mongo import col_usuarios
from .schemas import UsuarioCreate, UsuarioOut, ProdutoBase, ProdutoOut
from . import security

# ---------------------------------------------------------
# IMPORTAR ROTEADORES
# ---------------------------------------------------------
from .routers import grupos

# ---------------------------------------------------------
# CRIAR APP (DEVE VIR ANTES DE QUALQUER include_router)
# ---------------------------------------------------------
app = FastAPI(title="API Loja Alfaiataria")

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Criar tabelas no MySQL (se ainda não existirem)
# ---------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# Dependência do banco
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# INCLUIR ROTEADORES (AGORA SIM, APP EXISTE)
# ---------------------------------------------------------
app.include_router(grupos.router)

# ---------------------------------------------------------
# ROTA RAIZ
# ---------------------------------------------------------
@app.get("/")
def raiz():
    return {"status": "API Loja Online", "versao": "2.0"}

# ---------------------------------------------------------
# LOGIN (MongoDB)
# ---------------------------------------------------------
class LoginRequest(BaseModel):
    usuario: str
    senha: str

@app.post("/api/login")
def login(request: LoginRequest):
    usuario = col_usuarios.find_one({"email": request.usuario})

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    senha_salva = usuario.get("senha")
    if senha_salva != request.senha:
        raise HTTPException(status_code=401, detail="Senha incorreta")

    return {
        "mensagem": f"Login realizado com sucesso, {usuario['nome']}!",
        "usuario": {
            "nome": usuario["nome"],
            "email": usuario["email"],
            "grupo": usuario.get("grupo", "Usuário")
        }
    }

# ---------------------------------------------------------
# PRODUTOS (MySQL)
# ---------------------------------------------------------
@app.get("/api/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(models.Produto).all()

    return [
        {
            "id": p.IDProduto,
            "nome": p.Nome,
            "categoria": p.Categoria,
            "preco": p.Preco,
            "estoque": p.Estoque,
        }
        for p in produtos
    ]

@app.post("/api/produtos")
def adicionar_produto(produto: ProdutoBase, db: Session = Depends(get_db)):
    try:
        novo = models.Produto(
            Nome=produto.nome,
            Categoria=produto.categoria,
            Preco=produto.preco,
            Estoque=produto.estoque or 0
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)

        return {
            "message": "Produto adicionado com sucesso!",
            "produto": {
                "id": novo.IDProduto,
                "nome": novo.Nome,
                "categoria": novo.Categoria,
                "preco": novo.Preco,
                "estoque": novo.Estoque
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao adicionar produto: {e}")

@app.delete("/api/produtos/{produto_id}")
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.IDProduto == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()

    return {"message": "Produto excluído com sucesso!"}

# ---------------------------------------------------------
# USUÁRIOS (MySQL)
# ---------------------------------------------------------
@app.get("/api/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()

    return [
        {
            "id": u.IDUsuario,
            "nome": u.Nome,
            "email": u.Email,
            "grupo_id": u.IDGrupo
        }
        for u in usuarios
    ]

class UsuarioCreateIn(BaseModel):
    nome: str
    email: str
    senha: str
    grupo_id: int

@app.post("/api/usuarios")
def adicionar_usuario(payload: UsuarioCreateIn, db: Session = Depends(get_db)):

    grupo = db.query(models.GrupoUsuario).filter(
        models.GrupoUsuario.IDGrupo == payload.grupo_id
    ).first()

    if not grupo:
        raise HTTPException(status_code=400, detail="Grupo informado não existe!")

    existe = db.query(models.Usuario).filter(models.Usuario.Email == payload.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    try:
        novo = models.Usuario(
            Nome=payload.nome,
            Email=payload.email,
            SenhaHash=security.hash_password(payload.senha),
            IDGrupo=payload.grupo_id
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)

        return {
            "message": "Usuário cadastrado com sucesso!",
            "id": novo.IDUsuario
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar: {e}")

@app.delete("/api/usuarios/{id}")
def excluir_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.IDUsuario == id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(usuario)
    db.commit()

    return {"message": "Usuário excluído com sucesso!"}
