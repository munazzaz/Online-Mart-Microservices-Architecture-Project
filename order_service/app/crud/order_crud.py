from sqlmodel import Session, select
from app.models.order_model import Order, OrderUpdate

def create_order(order: Order, session: Session) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def get_order_by_id(order_id: int, session: Session) -> Order:
    return session.exec(select(Order).where(Order.id == order_id)).first()

def update_order_by_id(order_id: int, to_update_order_data: OrderUpdate, session: Session) -> Order:
    db_order = get_order_by_id(order_id, session)
    for key, value in to_update_order_data.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order

def delete_order_by_id(order_id: int, session: Session) -> None:
    db_order = get_order_by_id(order_id, session)
    session.delete(db_order)
    session.commit()
