from kafka import KafkaConsumer
import json
from app.inventory import get_db_conn
from app.payment import simulate_payment
from app.orders import save_order
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="order-processors"
)

def process_orders():
    for msg in consumer:
        order = msg.value
        total_amount = sum([item["quantity"] * 10 for item in order["items"]]) 
        payment_ok = simulate_payment()
        if not payment_ok:
            payment_info = {
                "status": "failed",
                "error": "payment_failed",
                "message": "Payment processing failed. Inventory has been released.",
            }
            save_order(order, total_amount, status="failed", payment_info=payment_info)
            logging.warning({
                "order_id": order.get("order_id"),
                "status": "failed",
                "error": "payment_failed",
                "message": "Payment processing failed. Inventory has been released.",
                "created_at": datetime.utcnow().isoformat() + "Z"
            })
            continue
        conn = get_db_conn()
        cur = conn.cursor()
        for item in order["items"]:
            cur.execute("SELECT id FROM product WHERE sku=%s", (item["sku"],))
            product = cur.fetchone()
            if not product:
                logging.error(f"Product not found: {item['sku']}")
                continue
            cur.execute(
                "UPDATE inventory SET available_quantity = available_quantity - %s WHERE product_id = %s AND available_quantity >= %s",
                (item["quantity"], product[0], item["quantity"])
            )
        conn.commit()
        cur.close()
        conn.close()
        payment_info = {
            "status": "completed",
            "transaction_id": f"txn_{order.get('order_id')}"
        }
        save_order(
            order,
            total_amount,
            status="confirmed",
            payment_info=payment_info
        )
        logging.info(f"Order processed and saved: {order}")


if __name__ == "__main__":
    process_orders()