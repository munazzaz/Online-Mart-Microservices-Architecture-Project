from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.product_model import Product, ProductUpdate

# Add a New Product to the Database
def add_new_product(product_data: Product, session: Session):
    print("Adding Product to Database")
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data

# Get All Products from the Database
def get_all_products(session: Session):
    all_products = session.exec(select(Product)).all()
    return all_products

# Get a Product by ID
def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Delete Product by ID
def delete_product_by_id(product_id: int, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Delete the Product
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted Successfully"}




# Update Product by ID
def update_product_by_id(product_id: int, to_update_product_data:ProductUpdate, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Update the Product
    hero_data = to_update_product_data.model_dump(exclude_unset=True)
    product.sqlmodel_update(hero_data)
    session.add(product)
    session.commit()
    # session.refresh(product)
    
    # return product
    return {"message": "Product updated successfully"}




# Validate Product by ID
def validate_product_by_id(product_id: int, session: Session) -> Product | None:
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    return product











# from fastapi import HTTPException
# from sqlmodel import Session, select
# from app.models.product_model import Product, ProductUpdate

# def add_new_product(product_data: Product, session: Session):
#     print("Adding Product to Database")
#     session.add(product_data)
#     session.commit()
#     session.refresh(product_data)
#     return product_data

# def get_all_products(session: Session):
#     all_products = session.exec(select(Product)).all()
#     return all_products

# def get_product_by_id(product_id: int, session: Session):
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

# def delete_product_by_id(product_id: int, session: Session):
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     session.delete(product)
#     session.commit()
#     return {"message": "Product Deleted Successfully"}

# def update_product_by_id(product_id: int, to_update_product_data: ProductUpdate, session: Session):
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     update_data = to_update_product_data.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(product, key, value)
    
#     session.add(product)
#     session.commit()
#     session.refresh(product)
#     return product

# def validate_product_by_id(product_id: int, session: Session) -> Product | None:
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     return product
























# from fastapi import HTTPException
# from sqlmodel import Session, select
# from app.models.product_model import Product, ProductUpdate

# def add_new_product(product_data: Product, session: Session):
#     print("Adding Product to Database")
#     session.add(product_data)
#     session.commit()
#     session.refresh(product_data)
#     return product_data

# def get_all_products(session: Session):
#     all_products = session.exec(select(Product)).all()
#     return all_products

# def get_product_by_id(product_id: int, session: Session):
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

# def delete_product_by_id(product_id: int, session: Session):
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     session.delete(product)
#     session.commit()
#     return {"message": "Product Deleted Successfully"}

# def update_product_by_id(product_id: int, to_update_product_data: ProductUpdate, session: Session):
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     update_data = to_update_product_data.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(product, key, value)
    
#     session.add(product)
#     session.commit()
#     session.refresh(product)
#     return product

# def validate_product_by_id(product_id: int, session: Session) -> Product | None:
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     return product

#.proto
# syntax = "proto3";

# package product;

# message Product {
#     int32 id = 1;
#     string name = 2;
#     string description = 3;
#     float price = 4;
# }

# message ProductUpdate {
#     int32 id = 1;
#     string name = 2;
#     string description = 3;
#     float price = 4;
# }
