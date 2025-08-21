from pymongo import MongoClient
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_mongo_conn():
    client = MongoClient("mongodb://admin:admin123@mongodb:27017/")
    db = client["ecommerce_orders"]
    return db

def save_order(order, total_amount, status="confirmed", payment_info=None):
    db = get_mongo_conn()
    if db.orders.find_one({"order_id": order.get("order_id")}):
        logging.warning(f"Duplicate order detected: {order.get('order_id')}")
        return
    order_doc = {
        "order_id": order.get("order_id"),
        "customer": order.get("customer"),
        "items": order.get("items"),
        "total_amount": total_amount,
        "pricing": {
            "subtotal": total_amount,
            "tax": round(total_amount * 0.08, 2),  
            "total": round(total_amount * 1.08, 2)
        },
        "payment": payment_info or {},
        "status": status,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    db.orders.insert_one(order_doc)

def get_next_order_number():
    db = get_mongo_conn()
    counter = db.counters.find_one_and_update(
        {"_id": "order_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

def generate_order_id():
    number = get_next_order_number()
    return f"ORD-2024-{number:06d}"

def get_order_by_id(order_id):
    try:
        db = get_mongo_conn()
        order = db.orders.find_one({"order_id": order_id})
        if order:
            order.pop("_id", None)
            return {"ok": True, "value": order}
        return {"ok": False, "error": "order_not_found", "message": "Order not found"}
    except Exception as e:
        logging.error(f"Error fetching order by ID: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}

def get_orders_by_user(user_id, page=1, limit=10):
    try:
        db = get_mongo_conn()
        skip = (page - 1) * limit
        orders = list(db.orders.find({"customer.user_id": user_id}).skip(skip).limit(limit))
        for o in orders:
            o.pop("_id", None)
        return {"ok": True, "value": {"orders": orders, "pagination": {"page": page, "limit": limit, "total": len(orders)}}}
    except Exception as e:
        logging.error(f"Error fetching orders by user: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}