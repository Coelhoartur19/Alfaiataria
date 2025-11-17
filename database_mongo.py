from pymongo import MongoClient

# URL padrão do MongoDB local
MONGO_URL = "mongodb://localhost:27017/"

# Nome da sua base
DATABASE_NAME = "alfaiataria"

client = MongoClient(MONGO_URL)

# Conexão com o banco
mongo_db = client[DATABASE_NAME]

# Coleções do banco
col_usuarios = mongo_db["usuarios"]
col_produtos = mongo_db["produtos"]
col_grupos = mongo_db["grupos"]
col_vendas = mongo_db["vendas"]
col_avaliacao = mongo_db["avaliacao"]
