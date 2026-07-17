from datetime import datetime, timezone
from bson import ObjectId
from app.database_mongo import reviews_collection


def create_review(product_id: int, user_name: str, rating: int, comment: str | None) -> dict:
    doc = {
        "product_id": product_id,
        "user_name": user_name,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.now(timezone.utc),
    }
    result = reviews_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def list_reviews(product_id: int) -> list[dict]:
    return list(reviews_collection.find({"product_id": product_id}).sort("created_at", -1))


def get_rating_summary(product_id: int) -> dict:
    pipeline = [
        {"$match": {"product_id": product_id}},
        {
            "$group": {
                "_id": "$product_id",
                "average_rating": {"$avg": "$rating"},
                "review_count": {"$sum": 1},
            }
        },
    ]
    result = list(reviews_collection.aggregate(pipeline))
    if not result:
        return {"average_rating": None, "review_count": 0}
    return {
        "average_rating": round(result[0]["average_rating"], 2),
        "review_count": result[0]["review_count"],
    }


def serialize_review(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "product_id": doc["product_id"],
        "user_name": doc["user_name"],
        "rating": doc["rating"],
        "comment": doc.get("comment"),
        "created_at": doc["created_at"],
    }
