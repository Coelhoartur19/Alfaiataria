from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from .database import Base, engine, SessionLocal
from . import models
from .schemas import ProdutoBase, UsuarioCreate, UsuarioOut
from . import security

# Roteadores
from .routers import vendas, grupos, usuarios, produtos


# ---------------------------------------------------------
# INICIAR APP
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

# Criar tabelas no MySQL
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# DEPENDÊNCIA DO BANCO
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# INCLUIR ROTEADORES
# ---------------------------------------------------------
app.include_router(vendas.router, prefix="/api")
app.include_router(grupos.router)
app.include_router(usuarios.router, prefix="/api")
app.include_router(produtos.router, prefix="/api")


# ---------------------------------------------------------
# ROTA RAIZ
# ---------------------------------------------------------
@app.get("/")
def raiz():
    return {"status": "API Loja Online", "versao": "2.0"}


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
class LoginRequest(BaseModel):
    usuario: str   # email
    senha: str

@app.post("/api/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):

    usuario = db.query(models.Usuario).filter(
        models.Usuario.Email == request.usuario
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not security.verify_password(request.senha, usuario.SenhaHash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    return {
        "mensagem": f"Login realizado com sucesso, {usuario.Nome}!",
        "usuario": {
            "id": usuario.IDUsuario,
            "nome": usuario.Nome,
            "email": usuario.Email,
            "grupo_id": usuario.IDGrupo
        }
    }


# ---------------------------------------------------------
# PRODUTOS - LISTAR
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


# ---------------------------------------------------------
# PRODUTOS - CADASTRAR
# ---------------------------------------------------------
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

        return {"message": "Produto adicionado com sucesso!", "produto": {
            "id": novo.IDProduto,
            "nome": novo.Nome,
            "categoria": novo.Categoria,
            "preco": novo.Preco,
            "estoque": novo.Estoque
        }}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao adicionar produto: {e}")

# ---------------------------------------------------------
# PRODUTOS - EXCLUIR (substitua a sua implementação por esta)
# ---------------------------------------------------------
@app.delete("/api/produtos/{produto_id}")
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.IDProduto == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    try:
        db.delete(produto)
        db.commit()
        return {"message": "Produto excluído com sucesso!"}
    except IntegrityError as ie:
        db.rollback()
        # Mensagem mais clara para frontend — o texto pode ser ajustado
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir este produto: já existe(m) venda(s) vinculada(s) a ele."
        )
    except Exception as e:
        db.rollback()
        # fallback genérico
        raise HTTPException(status_code=500, detail=f"Erro ao excluir produto: {e}")



# ---------------------------------------------------------
# USUÁRIOS - LISTAR
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


# ---------------------------------------------------------
# USUÁRIOS - CADASTRAR
# ---------------------------------------------------------
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

        return {"message": "Usuário cadastrado com sucesso!", "id": novo.IDUsuario}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar: {e}")


# ---------------------------------------------------------
# USUÁRIOS - EXCLUIR
# ---------------------------------------------------------
@app.delete("/api/usuarios/{id}")
def excluir_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.IDUsuario == id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(usuario)
    db.commit()

    return {"message": "Usuário excluído com sucesso!"}
