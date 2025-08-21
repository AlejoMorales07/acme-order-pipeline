import psycopg2
from app.models import OrderItem
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)



def get_db_conn():
    return psycopg2.connect(
        dbname="ecommerce_inventory",
        user="postgres",
        password="postgres123",
        host="localhost",
        port=5432
    )

def check_inventory(items: list[OrderItem]):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        for item in items:
            
            cur.execute("SELECT id FROM product WHERE sku=%s", (item.sku,))
            product = cur.fetchone()
            if not product:
                return {"ok": False,"error": "product_not_found", "message": "Product not found"}
            cur.execute("SELECT available_quantity, reserved_quantity FROM inventory WHERE product_id=%s", (product[0],))
            result = cur.fetchone()
            if not result:
                return {"ok": False, "error": "inventory_not_found", "message": "Inventory not found"}
            available_quantity, reserved_quantity = result
            if available_quantity - reserved_quantity < item.quantity:
                return {"ok": False, "error": "insufficient_inventory", "message": "Insufficient inventory"}
        return {"ok": True}
    except Exception as e:
        logging.error(f"Error checking inventory: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

def get_product_by_sku(sku: str):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, sku, name, price FROM product WHERE sku=%s", (sku,))
        row = cur.fetchone()
        if row:
            return {
                "ok": True,
                "value": {
                    "id": row[0],
                    "sku": row[1],
                    "name": row[2],
                    "price": row[3],
                }
            }
        return {"ok": False, "error": "product_not_found", "message": "Product not found"}
    except Exception as e:
        logging.error(f"Error fetching product by SKU: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

def get_all_products():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, sku, name, price FROM product")
        rows = cur.fetchall()
        return {
            "ok": True,
            "value": [
                {"id": r[0], "sku": r[1], "name": r[2], "price": r[3]}
                for r in rows
            ]
        }
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

def get_inventory_by_sku(sku: str):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, sku, name FROM product WHERE sku=%s", (sku,))
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "product_not_found", "message": "Product not found"}
        cur.execute("SELECT available_quantity, reserved_quantity FROM inventory WHERE product_id=%s", (row[0],))
        inventory = cur.fetchone()
        if inventory:
            return { "ok": True, "value":{"sku": row[1], "product_name": row[2], "available_quantity": inventory[0], "reserved_quantity": inventory[1]}}
        return {"ok": False, "error": "inventory_not_found", "message": "Inventory not found for the given SKU"}
    except Exception as e:
        logging.error(f"Error fetching inventory: {e}")
        return {"ok": False, "error": "internal_server_error", "message": str(e)}
    finally:
        cur.close()
        conn.close()