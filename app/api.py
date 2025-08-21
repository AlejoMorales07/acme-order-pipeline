from fastapi import FastAPI, HTTPException, Query
from app.inventory import check_inventory, get_product_by_sku, get_all_products, get_inventory_by_sku
from app.kafka_producer import publish_order_event
from app.models import OrderRequest
from app.orders import get_order_by_id, get_orders_by_user
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/products")
def products(sku: str = Query(None)):
    if sku:
        result = get_product_by_sku(sku)
        if not result["ok"]:
            raise HTTPException(status_code=500 if result["error"] == "internal_server_error" else 404, detail={"error": result["error"], "message": result["message"]})
        return {"products": [result["value"]]}
    else:
        result = get_all_products()
        if not result["ok"]:
            raise HTTPException(status_code=500, detail={"error": result["error"], "message": result["message"]})
    return {"products": result["value"]}

@app.get("/products/{sku}/inventory")
def product_inventory(sku: str):
    result = get_inventory_by_sku(sku)
    if not result["ok"]:
        raise HTTPException(status_code=500 if result["error"] == "internal_server_error" else 404, detail={"error": result["error"], "message": result["message"]})
    return result["value"]

@app.post("/orders")
def create_order(order: OrderRequest):
    result = check_inventory(order.items)
    if not result["ok"]:
        raise HTTPException(status_code=404 if result["error"] == "product_not_found" else 400, detail={"error": result["error"], "message": result["message"]})
    publish_order_event(order)
    return {
        "order_id": "ORD-2024-001234",  # Genera el ID real en tu lógica
        "status": "pending",
        "message": "Order created successfully and queued for processing",
        "estimated_total": 0,  # Calcula el total real
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    result = get_order_by_id(order_id)
    if not result["ok"]:
        print(f"Error fetching order: {result['error']}")
        raise HTTPException(status_code=404 if result["error"] == "order_not_found" else 500, detail={"error": result["error"], "message": result["message"]})
    return result["value"]

@app.get("/users/{user_id}/orders")
def get_user_orders(user_id: str, page: int = 1, limit: int = 10):
    result = get_orders_by_user(user_id, page, limit)
    if not result["ok"]:
        raise HTTPException(status_code=500 if result["error"] == "internal_server_error" else 404, detail={"error": result["error"], "message": result["message"]})
    return result["value"]