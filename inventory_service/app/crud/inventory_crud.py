# from fastapi import HTTPException
# from sqlmodel import Session, select
# from app.models.inventory_model import InventoryItem, InventoryItemUpdate

# def add_new_inventory_item(item_data: InventoryItem, session: Session):
#     session.add(item_data)
#     session.commit()
#     session.refresh(item_data)
#     return item_data

# def get_all_inventory_items(session: Session):
#     return session.exec(select(InventoryItem)).all()

# def get_inventory_item_by_id(inventory_item_id: int, session: Session):
#     item = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_item_id)).one_or_none()
#     if item is None:
#         raise HTTPException(status_code=404, detail="Inventory item not found")
#     return item

# def delete_inventory_item_by_id(inventory_item_id: int, session: Session):
#     item = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_item_id)).one_or_none()
#     if item is None:
#         raise HTTPException(status_code=404, detail="Inventory item not found")
#     session.delete(item)
#     session.commit()
#     return {"message": "Inventory Item Deleted Successfully"}

# def update_inventory_item_by_id(item_id: int, to_update_item_data: InventoryItemUpdate, session: Session):
#     item = session.exec(select(InventoryItem).where(InventoryItem.id == item_id)).one_or_none()
#     if item is None:
#         raise HTTPException(status_code=404, detail="Inventory item not found")
#     item_data = to_update_item_data.dict(exclude_unset=True)
#     for key, value in item_data.items():
#         setattr(item, key, value)
#     session.add(item)
#     session.commit()
#     return item

# from fastapi import HTTPException
# from sqlmodel import Session, select
# from app.models.inventory_model import Inventory, InventoryCreate, InventoryUpdate

# # Add a New Inventory to the Database
# def add_new_inventory(inventory_data: InventoryCreate, session: Session):
#     inventory = Inventory.from_orm(inventory_data)
#     session.add(inventory)
#     session.commit()
#     session.refresh(inventory)
#     return inventory

# # Get All Inventory from the Database
# def get_all_inventory(session: Session):
#     all_inventory = session.exec(select(Inventory)).all()
#     return all_inventory

# # Get an Inventory by ID
# def get_inventory_by_id(inventory_id: int, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
#     if inventory is None:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     return inventory

# # Update Inventory by ID
# def update_inventory_by_id(inventory_id: int, to_update_inventory_data: InventoryUpdate, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
#     if inventory is None:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     inventory_data = to_update_inventory_data.dict(exclude_unset=True)
#     for key, value in inventory_data.items():
#         setattr(inventory, key, value)
#     session.add(inventory)
#     session.commit()
#     session.refresh(inventory)
#     return inventory

# # Delete Inventory by ID
# def delete_inventory_by_id(inventory_id: int, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
#     if inventory is None:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     session.delete(inventory)
#     session.commit()
#     return {"message": "Inventory deleted successfully"}

import requests
from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.inventory_model import Inventory, InventoryCreate, InventoryUpdate

def add_new_inventory(inventory_data: InventoryCreate, session: Session):
    validate_product_id(inventory_data.product_id)
    inventory = Inventory.from_orm(inventory_data)
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory

def validate_product_id(product_id: int):
    try:
        response = requests.get(f"http://product_service:8000/manage-products/{product_id}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Product ID {product_id} validation failed: {e}")


# Get All Inventory from the Database
def get_all_inventory(session: Session):
    all_inventory = session.exec(select(Inventory)).all()
    return all_inventory

# Get an Inventory by ID
def get_inventory_by_id(inventory_id: int, session: Session):
    inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

# Update Inventory by ID
def update_inventory_by_id(inventory_id: int, to_update_inventory_data: InventoryUpdate, session: Session):
    inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    inventory_data = to_update_inventory_data.dict(exclude_unset=True)
    for key, value in inventory_data.items():
        setattr(inventory, key, value)
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory

# Delete Inventory by ID
def delete_inventory_by_id(inventory_id: int, session: Session):
    inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    session.delete(inventory)
    session.commit()
    return {"message": "Inventory deleted successfully"}

def get_inventory_by_product_id(product_id: int, session: Session) -> Inventory:
    statement = select(Inventory).where(Inventory.product_id == product_id)
    results = session.exec(statement)
    return results.first()

# from fastapi import HTTPException
# from sqlmodel import Session, select
# from app.models.inventory_model import Inventory, InventoryCreate, InventoryUpdate

# # Add a New Inventory to the Database
# def add_new_inventory(inventory_data: InventoryCreate, session: Session):
#     db_inventory = Inventory.from_orm(inventory_data)
#     session.add(db_inventory)
#     session.commit()
#     session.refresh(db_inventory)
#     return db_inventory

# # Get All Inventory from the Database
# def get_all_inventory(session: Session):
#     result = session.exec(select(Inventory))
#     return result.all()

# # Get Inventory by ID
# def get_inventory_by_id(inventory_id: int, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
#     if not inventory:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     return inventory

# # Update Inventory by ID
# def update_inventory_by_id(inventory_id: int, to_update_inventory_data: InventoryUpdate, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
#     if not inventory:
#         raise HTTPException(status_code=404, detail="Inventory not found")

#     inventory_data = to_update_inventory_data.dict(exclude_unset=True)
#     for key, value in inventory_data.items():
#         setattr(inventory, key, value)
#     session.add(inventory)
#     session.commit()
#     session.refresh(inventory)
#     return inventory

# # Delete Inventory by ID
# def delete_inventory_by_id(inventory_id: int, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.id == inventory_id)).one_or_none()
#     if not inventory:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     session.delete(inventory)
#     session.commit()
#     return {"message": "Inventory Deleted Successfully"}

# # Delete Inventory by Product ID
# def delete_inventory_by_product_id(product_id: int, session: Session):
#     inventory = session.exec(select(Inventory).where(Inventory.product_id == product_id)).one_or_none()
#     if not inventory:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     session.delete(inventory)
#     session.commit()
#     return {"message": "Inventory Deleted Successfully"}

# # Validate Product ID
# def validate_product_id(product_id: int):
#     # Implement logic to validate if the product_id exists in the product service
#     pass
