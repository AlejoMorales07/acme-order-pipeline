from pymongo import MongoClient

def get_mongo_conn():
    client = MongoClient("mongodb://admin:admin123@localhost:27017/")
    db = client["ecommerce_orders"]
    return db

def get_order_by_id(order_id):
    try:
        db = get_mongo_conn()
        order = db.orders.find_one({"order_id": order_id})
        if order:
            order.pop("_id", None)
            return {"ok": True, "value": order}
        return {"ok": False, "error": "order_not_found", "message": "Order not found"}
    except Exception as e:
        print(f"Error fetching order by ID: {e}")
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
        print(f"Error fetching orders by user: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}