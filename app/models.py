from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    sku: str
    quantity: int

class Customer(BaseModel):
    user_id: str
    email: str

class OrderRequest(BaseModel):
    customer: Customer
    items: List[OrderItem]