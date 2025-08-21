import random

def simulate_payment(order_id, amount):
    # Simula fallo de pago aleatorio
    if random.random() < 0.1:
        return False
    return True