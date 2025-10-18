from faker import Faker
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Produto
from tqdm import tqdm
import random

fake = Faker("pt_BR")
db: Session = SessionLocal()

db.query(Produto).delete()
db.commit()

TOTAL = 50000

categorias = ["Eletrônicos", "Livros", "Roupas", "Brinquedos", "Esportes", "Alimentos"]

print(f"🔹 Inserindo {TOTAL} produtos no banco...")

for _ in tqdm(range(TOTAL)):
    produto = Produto(
        nome=fake.word().capitalize() + " " + fake.word().capitalize(),
        categoria=random.choice(categorias),
        preco=round(random.uniform(10, 1000), 2),
        estoque=random.randint(1, 500),
    )
    db.add(produto)

db.commit()
db.close()

print("✅ Inserção concluída com sucesso!")
