from sqlmodel import SQLModel, Field, Relationship

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    expiry: str | None = None
    brand: str | None = None
    weight: float | None = None
    category: str  # It shall be predefined by Platform
    sku: str | None = None
    ratings: list["ProductRating"] = Relationship(back_populates="product")
    # image: str  # Multiple | URL Not Media | One to Many Relationship
    # quantity: int | None = None  # Shall it be managed by Inventory Microservice
    # color: str | None = None  # One to Many Relationship
    # rating: float | None = None  # One to Many Relationship

class ProductRating(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    rating: int
    review: str | None = None
    product: "Product" = Relationship(back_populates="ratings")
    # user_id: int  # One to Many Relationship

class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    expiry: str | None = None
    brand: str | None = None
    weight: float | None = None
    category: str | None = None
    sku: str | None = None
