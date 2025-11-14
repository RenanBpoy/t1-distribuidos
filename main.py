from fastapi import FastAPI
from database import Base, write_engine
from routers import produto

app = FastAPI()

Base.metadata.create_all(bind=write_engine)

app.include_router(produto.router)

@app.get("/")
def raiz():
    return {"mensagem": "API de produtos funcionando com PostgreSQL (Neon)!"}
