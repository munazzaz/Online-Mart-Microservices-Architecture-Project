from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime



from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class OrderCreate(SQLModel):
    id: Optional[int] = None
    user_id: int
    product_id: int
    product_name: str
    quantity: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    product_id: int
    product_name: str
    quantity: int
    total_price: float
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
class OrderUpdate(SQLModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None

