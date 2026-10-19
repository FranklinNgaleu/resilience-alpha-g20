import os
from unittest import result
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Numeric, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from prometheus_fastapi_instrumentator import Instrumentator

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

class PaymentIn(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="EUR", pattern="^(EUR|USD)$")

app = FastAPI(title="Resilience Alpha - Payment Demo", version="0.1.0")
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def init_db():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}

@app.post("/payments", status_code=201)
def create_payment(payload: PaymentIn):
    payment = Payment(
        id=str(uuid.uuid4()),
        amount=payload.amount,
        currency=payload.currency,
        status="accepted",
        created_at=datetime.now(timezone.utc)
    )

    with Session.begin() as session:
        session.add(payment)
        session.flush()

        result = {
            "id": payment.id,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "status": payment.status
        }
    return result


@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    with Session() as session:
        payment = session.get(Payment, payment_id)
        if payment is None:
            raise HTTPException(404, "Payment not found")
        return {"id": payment.id, "amount": str(payment.amount), "currency": payment.currency, "status": payment.status}
