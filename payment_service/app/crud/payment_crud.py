# payment_service/app/crud/payment_crud.py
from sqlmodel import Session
from app.models.payment_model import Payment
from typing import Optional

def create_payment(payment_data: Payment, session: Session) -> Payment:
    session.add(payment_data)
    session.commit()
    session.refresh(payment_data)
    return payment_data

def get_payment_by_order_id(order_id: int, session: Session) -> Optional[Payment]:
    return session.query(Payment).filter(Payment.order_id == order_id).first()

def update_payment_status(payment_id: int, status: str, session: Session) -> Payment:
    payment = session.get(Payment, payment_id)
    if payment:
        payment.status = status
        session.add(payment)
        session.commit()
        session.refresh(payment)
    return payment
