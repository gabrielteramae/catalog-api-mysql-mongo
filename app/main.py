from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database_mysql import engine, get_db
from app.schemas import ProductCreate, ProductRead, ProductWithRating, ReviewCreate, ReviewRead
from app.reviews_repository import create_review, list_reviews, get_rating_summary, serialize_review

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catalog API",
    description="Catalogo de produtos (MySQL) com avaliacoes (MongoDB)",
    version="1.0.0",
)


@app.post("/products", response_model=ProductRead, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products", response_model=list[ProductWithRating])
def list_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    result = []
    for p in products:
        summary = get_rating_summary(p.id)
        result.append(
            ProductWithRating(
                id=p.id, name=p.name, category=p.category,
                price=float(p.price), stock=p.stock,
                average_rating=summary["average_rating"],
                review_count=summary["review_count"],
            )
        )
    return result


@app.get("/products/{product_id}", response_model=ProductWithRating)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Product not found")
    summary = get_rating_summary(product_id)
    return ProductWithRating(
        id=p.id, name=p.name, category=p.category,
        price=float(p.price), stock=p.stock,
        average_rating=summary["average_rating"],
        review_count=summary["review_count"],
    )


@app.post("/products/{product_id}/reviews", response_model=ReviewRead, status_code=201)
def add_review(product_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Product not found")
    doc = create_review(product_id, review.user_name, review.rating, review.comment)
    return serialize_review(doc)


@app.get("/products/{product_id}/reviews", response_model=list[ReviewRead])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Product not found")
    docs = list_reviews(product_id)
    return [serialize_review(d) for d in docs]
