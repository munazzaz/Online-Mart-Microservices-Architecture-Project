# from sqlmodel import SQLModel, Field, Relationship

# # Inventory Microservice Models
# class InventoryItem(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     product_id: int
#     variant_id: int | None = None
#     quantity: int
#     status: str 


# # class InventoryItemUpdate(SQLModel):
# #     pass


# from sqlmodel import SQLModel, Field

# class InventoryItem(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     product_id: int  # Foreign key to product service
#     quantity: int
#     location: str

# class InventoryItemUpdate(SQLModel):
#     quantity: int | None = None
#     location: str | None = None

# from sqlmodel import SQLModel, Field

# class InventoryItem(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     product_id: int
#     quantity: int
#     stock_status: str

# class InventoryItemUpdate(SQLModel):
#     quantity: int | None = None
#     stock_status: str | None = None

# from sqlmodel import SQLModel, Field

# class Inventory(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     product_id: int
#     quantity: int
#     stock_status: str

# class InventoryCreate(SQLModel):
#     product_id: int
#     quantity: int
#     stock_status: str

# class InventoryUpdate(SQLModel):
#     quantity: int
#     stock_status: str

from sqlmodel import SQLModel, Field

class Inventory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: int
    quantity: int
    stock_status: str

class InventoryCreate(SQLModel):
    product_id: int
    quantity: int
    stock_status: str

class InventoryUpdate(SQLModel):
    quantity: int
    stock_status: str

# from sqlmodel import SQLModel, Field

# class Inventory(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     product_id: int
#     quantity: int
#     stock_status: str

# class InventoryCreate(SQLModel):
#     product_id: int
#     quantity: int
#     stock_status: str

# class InventoryUpdate(SQLModel):
#     quantity: int | None = None
#     stock_status: str | None = None


