from fastapi import APIRouter, HTTPException, Depends
from mysql.connector import MySQLConnection
from backend.database_mysql import get_db
from backend.schemas import ProdutoCreate, ProdutoOut

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])


# ---------------------------------------------------------
# LISTAR PRODUTOS
# ---------------------------------------------------------
@router.get("/", response_model=list[ProdutoOut])
def listar(db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, categoria, preco FROM produtos")
    produtos = cursor.fetchall()
    cursor.close()

    return produtos


# ---------------------------------------------------------
# BUSCAR PRODUTO POR ID
# ---------------------------------------------------------
@router.get("/{produto_id}", response_model=ProdutoOut)
def buscar(produto_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, categoria, preco FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()
    cursor.close()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


# ---------------------------------------------------------
# CRIAR PRODUTO
# ---------------------------------------------------------
@router.post("/", response_model=ProdutoOut)
def criar(produto: ProdutoCreate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    sql = """
        INSERT INTO produtos (nome, categoria, preco)
        VALUES (%s, %s, %s)
    """
    valores = (produto.nome, produto.categoria, produto.preco)
    cursor.execute(sql, valores)
    db.commit()

    novo_id = cursor.lastrowid
    cursor.close()

    return {
        "id": novo_id,
        "nome": produto.nome,
        "categoria": produto.categoria,
        "preco": produto.preco
    }


# ---------------------------------------------------------
# ATUALIZAR PRODUTO
# ---------------------------------------------------------
@router.put("/{produto_id}", response_model=ProdutoOut)
def atualizar(produto_id: int, produto: ProdutoCreate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()

    # Verificar se existe
    cursor.execute("SELECT id FROM produtos WHERE id = %s", (produto_id,))
    if not cursor.fetchone():
        cursor.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    sql = """
        UPDATE produtos
        SET nome = %s, categoria = %s, preco = %s
        WHERE id = %s
    """
    valores = (produto.nome, produto.categoria, produto.preco, produto_id)
    cursor.execute(sql, valores)
    db.commit()
    cursor.close()

    return {
        "id": produto_id,
        "nome": produto.nome,
        "categoria": produto.categoria,
        "preco": produto.preco
    }


# ---------------------------------------------------------
# REMOVER PRODUTO
# ---------------------------------------------------------
@router.delete("/{produto_id}")
def remover(produto_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
    db.commit()

    if cursor.rowcount == 0:
        cursor.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    cursor.close()
    return {"message": "Produto removido com sucesso!"}
