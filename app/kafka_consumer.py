from kafka import KafkaConsumer
import json
from app.inventory import get_db_conn
from app.payment import simulate_payment
from app.orders import save_order

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
        print(msg)
    # for msg in consumer:
    #     order = msg.value
    #     # Simular pago
    #     total_amount = sum([item["quantity"] * 10 for item in order["items"]])  # Suponiendo precio fijo
    #     payment_ok = simulate_payment(order["customer_id"], total_amount)
    #     if not payment_ok:
    #         print(f"Pago fallido para orden {order}")
    #         continue
    #     # Actualizar inventario
    #     conn = get_db_conn()
    #     cur = conn.cursor()
    #     for item in order["items"]:
    #         cur.execute(
    #             "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
    #             (item["quantity"], item["product_id"], item["quantity"])
    #         )
    #     conn.commit()
    #     cur.close()
    #     conn.close()
    #     # Guardar orden en MongoDB
    #     save_order(order, total_amount)
    #     print(f"Orden procesada y guardada: {order}")