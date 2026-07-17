# Catalog API — MySQL + MongoDB + Postman

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?logo=mongodb&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-collection-FF6C37?logo=postman&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)

API de catálogo de produtos usando **persistência políglota**: dados estruturados e relacionais no MySQL, dados flexíveis e de alto volume de escrita no MongoDB.

## Por que dois bancos?

| Dado                | Banco     | Motivo                                                                      |
|----------------------|-----------|---------------------------------------------------------------------------------|
| Produtos (catálogo)      | MySQL      | Estrutura fixa, relações claras, integridade transacional (preço, estoque)         |
| Avaliações (reviews)       | MongoDB     | Schema flexível (nem toda review tem comentário), alto volume de escrita, sem necessidade de JOIN complexo |

A API consulta os dois bancos e junta o resultado na camada de aplicação: `GET /products/{id}` retorna o produto (MySQL) já com `average_rating` e `review_count` calculados via **aggregation pipeline** do MongoDB.

## Stack

- **FastAPI** para a API REST
- **SQLAlchemy + PyMySQL** para o catálogo de produtos (MySQL)
- **PyMongo** para as avaliações (MongoDB), com `$group`/`$avg` para calcular a média de rating
- **Postman** — coleção pronta em `postman_collection.json`

## Estrutura

```
app/
├── main.py                  # endpoints, junta dados dos dois bancos
├── models.py                  # Product (SQLAlchemy / MySQL)
├── schemas.py                   # Pydantic (request/response)
├── database_mysql.py              # conexao MySQL
├── database_mongo.py                # conexao MongoDB
└── reviews_repository.py              # logica de reviews isolada (insert, list, aggregate)
```

## Como rodar

Precisa de um MySQL e um MongoDB rodando (local via Docker, ou serviços gerenciados como PlanetScale/MongoDB Atlas free tier).

```bash
git clone <seu-repo>
cd catalog-api
pip install -r requirements.txt

export MYSQL_URL="mysql+pymysql://user:senha@localhost:3306/catalogo_db"
export MONGO_URL="mongodb://localhost:27017"
export MONGO_DB="catalogo_reviews"

uvicorn app.main:app --reload
```

### Subindo os bancos rapidamente com Docker

```bash
docker run -d --name mysql-catalog -e MYSQL_ROOT_PASSWORD=senha -e MYSQL_DATABASE=catalogo_db -p 3306:3306 mysql:8
docker run -d --name mongo-catalog -p 27017:27017 mongo:7
```

## Testando com Postman

1. Abre o Postman
2. **Import** → seleciona `postman_collection.json`
3. Ajusta a variável de coleção `base_url` se a API não estiver em `localhost:8000`
4. Roda as requisições da pasta **Products** primeiro (pra ter um `id` válido), depois **Reviews**

A coleção já inclui casos de erro esperados (rating inválido → 422, produto inexistente → 404) pra validar que a API rejeita entradas ruins corretamente.

## Endpoints

| Método | Rota                        | Banco             | Descrição                                  |
|--------|------------------------------|--------------------|------------------------------------------------|
| POST   | `/products`                    | MySQL                | Cria um produto                                    |
| GET    | `/products`                      | MySQL + MongoDB         | Lista produtos com média de avaliação                 |
| GET    | `/products/{id}`                   | MySQL + MongoDB           | Detalhe do produto com média e contagem de reviews       |
| POST   | `/products/{id}/reviews`             | MongoDB                     | Cria uma avaliação                                            |
| GET    | `/products/{id}/reviews`               | MongoDB                       | Lista avaliações do produto                                       |

## Testes realizados

Validado o fluxo completo (criação de produtos, cálculo de média de rating, listagem, 404 em produto inexistente, 422 em rating fora do intervalo 1-5) usando SQLite como substituto local do MySQL e `mongomock` como substituto local do MongoDB — mesma lógica de negócio, sem precisar de servidores externos para testar. Em produção, a aplicação usa os drivers reais (`pymysql`, `pymongo`).

---

© 2026 Gabriel Teramae Chan
