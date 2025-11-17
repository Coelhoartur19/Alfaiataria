from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas import VendaCreate
from ..crud import criar_venda

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/vendas")
def registrar_venda(venda: VendaCreate, db: Session = Depends(get_db)):
    try:
        nova = criar_venda(db, venda)
        return {"mensagem": "Venda registrada!", "id_venda": nova.IDVenda}

    except Exception as e:
        raise HTTPException(400, f"Erro ao registrar venda: {e}")
