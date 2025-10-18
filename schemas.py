from pydantic import BaseModel

class ProdutoBase(BaseModel):
    nome: str
    categoria: str
    preco: float
    estoque: int

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int

    class Config:
        orm_mode = True
