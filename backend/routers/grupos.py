from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import GrupoUsuario

router = APIRouter(prefix="/api/grupos", tags=["Grupos"])

@router.get("/")
def listar_grupos(db: Session = Depends(get_db)):
    grupos = db.query(GrupoUsuario).all()

    return {
        "grupos": [
            {
                "id": g.IDGrupo,
                "nome": g.NomeGrupo,
                "descricao": g.Descricao
            }
            for g in grupos
        ]
    }
