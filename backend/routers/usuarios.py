from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import SessionLocal
from .. import models, schemas, security

router = APIRouter()

# Dependência do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------
# LISTAR USUÁRIOS
# -----------------------------------------------
@router.get("/usuarios", response_model=List[schemas.UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()

    return [
        schemas.UsuarioOut(
            id=u.IDUsuario,
            nome=u.Nome,
            email=u.Email,
            grupo_id=u.IDGrupo
        )
        for u in usuarios
    ]

# -----------------------------------------------
# CRIAR USUÁRIO
# -----------------------------------------------
@router.post("/usuarios", response_model=schemas.UsuarioOut, status_code=201)
def criar_usuario(payload: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    
    # Verifica grupo existente
    grupo = db.query(models.GrupoUsuario).filter(
        models.GrupoUsuario.IDGrupo == payload.grupo_id
    ).first()

    if not grupo:
        raise HTTPException(status_code=400, detail="Grupo informado não existe!")

    # Verifica e-mail único
    existe = db.query(models.Usuario).filter(
        models.Usuario.Email == payload.email
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    # Cria o usuário
    novo = models.Usuario(
        Nome=payload.nome,
        Email=payload.email,
        SenhaHash=security.hash_password(payload.senha),
        IDGrupo=payload.grupo_id
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    # Retorno no formato certo do schema
    return schemas.UsuarioOut(
        id=novo.IDUsuario,
        nome=novo.Nome,
        email=novo.Email,
        grupo_id=novo.IDGrupo
    )

# -----------------------------------------------
# EXCLUIR USUÁRIO
# -----------------------------------------------
@router.delete("/usuarios/{id}", status_code=200)
def excluir_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IDUsuario == id
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(usuario)
    db.commit()

    return {"message": "Usuário excluído com sucesso!"}
