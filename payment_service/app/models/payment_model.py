# from sqlmodel import SQLModel, Field
# from typing import Optional

# class Payment(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     order_id: int
#     product_name: str
#     quantity: int
#     total_price: float
#     currency: str
#     status: str

# payment_service/app/models/payment_model.py
from sqlmodel import SQLModel, Field
from typing import Optional

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int
    product_name: str
    quantity: int
    total_price: float
    status: str
