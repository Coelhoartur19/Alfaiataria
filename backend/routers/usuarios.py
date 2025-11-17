from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import SessionLocal
from .. import models, schemas, security, crud
from ..database import Base
from ..database import engine
from ..database import SessionLocal
from ..database import Base

from ..database import SessionLocal
from ..database import engine

from ..database import SessionLocal
from ..database import engine

from ..database import SessionLocal 
from ..database import engine

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/usuarios", response_model=List[schemas.UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    resultado = []
    for u in usuarios:
        resultado.append({
            "id": u.IDUsuario,
            "nome": u.Nome,
            "email": u.Email,
            "grupo_id": u.IDGrupo
        })
    return resultado

@router.post("/usuarios", response_model=schemas.UsuarioOut)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.criar_usuario(db, usuario)




@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
def criar_usuario(payload: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # verifica grupo
    grupo = db.query(models.GrupoUsuario).filter(models.GrupoUsuario.IDGrupo == payload.grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=400, detail="Grupo informado não existe!")

    # verifica email unico
    existe = db.query(models.Usuario).filter(models.Usuario.Email == payload.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email já está em uso")

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
        return {"message": "Usuário criado com sucesso!", "id": novo.IDUsuario}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar usuário: {e}")

@router.delete("/usuarios/{id}")
def excluir_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.IDUsuario == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return {"message": "Usuário excluído com sucesso!"}
