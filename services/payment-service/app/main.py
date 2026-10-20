
import os
import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Numeric,
    DateTime,
    text,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-service")

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


# MODELE SQLALCHEMY
class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)


# SCHEMAS PYDANTIC
class PaymentIn(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    currency: Literal["EUR", "USD"] = "EUR"


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    amount: Decimal
    currency: str
    status: str
    created_at: datetime


# INITIALISATION
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    logger.info("Payment Service initialized")
    yield


app = FastAPI(
    title="Resilience Alpha - Payment Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

Instrumentator().instrument(app).expose(app)


# HEALTHCHECK
@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except SQLAlchemyError:
        logger.exception("Database healthcheck failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


# CREATION D'UN PAIEMENT
@app.post(
    "/payments",
    response_model=PaymentOut,
    status_code=201
)
def create_payment(payload: PaymentIn):
    payment = Payment(
        id=str(uuid.uuid4()),
        amount=payload.amount,
        currency=payload.currency,
        status="accepted",
        created_at=datetime.now(timezone.utc)
    )

    try:
        with Session.begin() as session:
            session.add(payment)
            session.flush()

            result = PaymentOut.model_validate(payment)

        return result

    except SQLAlchemyError:
        logger.exception("Payment creation failed")
        raise HTTPException(
            status_code=503,
            detail="Payment service temporarily unavailable"
        )


# HISTORIQUE DES PAIEMENTS
@app.get("/payments", response_model=list[PaymentOut])
def list_payments(
    limit: int = Query(default=50, ge=1, le=100)
):
    try:
        with Session() as session:
            payments = session.scalars(
                select(Payment)
                .order_by(Payment.created_at.desc())
                .limit(limit)
            ).all()

            return [
                PaymentOut.model_validate(payment)
                for payment in payments
            ]

    except SQLAlchemyError:
        logger.exception("Payment listing failed")
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve payments"
        )


# DETAIL D'UN PAIEMENT
@app.get(
    "/payments/{payment_id}",
    response_model=PaymentOut
)
def get_payment(payment_id: uuid.UUID):
    try:
        with Session() as session:
            payment = session.get(Payment, str(payment_id))

            if payment is None:
                raise HTTPException(
                    status_code=404,
                    detail="Payment not found"
                )

            return PaymentOut.model_validate(payment)

    except SQLAlchemyError:
        logger.exception("Payment lookup failed")
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve payment"
        )
