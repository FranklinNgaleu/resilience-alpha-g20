
import os
import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

import httpx
import jwt
from jwt import InvalidTokenError

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Numeric,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    text,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from prometheus_fastapi_instrumentator import Instrumentator


# ============================================================
# CONFIGURATION
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-service")

DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]

ANOMALY_DETECTOR_URL = os.getenv(
    "ANOMALY_DETECTOR_URL",
    "http://anomaly-detector:8001"
).rstrip("/")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


# ============================================================
# MODELE SQLALCHEMY
# ============================================================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

class PaymentAnomaly(Base):
    __tablename__ = "payment_anomalies"

    id = Column(String, primary_key=True)
    payment_id = Column(
        String,
        ForeignKey("payments.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    is_anomaly = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    severity = Column(String(20), nullable=False)
    model = Column(String(100), nullable=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=False)


# ============================================================
# SCHEMAS PYDANTIC
# ============================================================

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

class PaymentAnomalyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payment_id: str
    is_anomaly: bool | None
    score: float | None
    severity: str
    model: str | None
    analyzed_at: datetime


# ============================================================
# INITIALISATION
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    logger.info("Payment Service initialized")
    yield


app = FastAPI(
    title="Resilience Alpha - Payment Service",
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# ============================================================
# AUTHENTIFICATION JWT
# ============================================================

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"],
            issuer="resilience-alpha-auth",
            audience="resilience-alpha-payment"
        )

        user_email = payload.get("sub")

        if not user_email:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return user_email

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ============================================================
# METRIQUES PROMETHEUS
# ============================================================

Instrumentator().instrument(app).expose(app)


# ============================================================
# HEALTHCHECK
# ============================================================

@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "ok",
            "service": "payment-service"
        }

    except SQLAlchemyError:
        logger.exception("Database healthcheck failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


# ============================================================
# ANALYSE IA DES TRANSACTIONS
# ============================================================

def analyze_payment(
    amount: Decimal,
    currency: str,
    created_at: datetime
) -> dict:

    transaction = {
        "amount": float(amount),
        "currency": currency,
        "timestamp": created_at.isoformat(),
        "frequency": 1.0,
    }

    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.post(
                f"{ANOMALY_DETECTOR_URL}/detect",
                json=transaction
            )

            response.raise_for_status()
            analysis = response.json()

        if not isinstance(analysis, dict) or not isinstance(
            analysis.get("is_anomaly"), bool
        ):
            raise ValueError("Invalid anomaly detector response")

        logger.info(
            "AI prediction completed: anomaly=%s, severity=%s",
            analysis.get("is_anomaly"),
            analysis.get("severity")
        )

        return analysis

    except (
        httpx.RequestError,
        httpx.HTTPStatusError,
        ValueError
    ):
        logger.exception("Anomaly detector unavailable or invalid response")

        return {
            "is_anomaly": None,
            "score": None,
            "severity": "unknown",
            "model": "unavailable"
        }


# ============================================================
# CREATION D'UN PAIEMENT
# ============================================================

@app.post(
    "/payments",
    response_model=PaymentOut,
    status_code=201,
    dependencies=[Depends(get_current_user)]
)
def create_payment(payload: PaymentIn):

    payment = Payment(
        id=str(uuid.uuid4()),
        amount=payload.amount,
        currency=payload.currency,
        status="accepted",
        created_at=datetime.now(timezone.utc)
    )

    # Enregistrer d'abord le paiement dans PostgreSQL.
    try:
        with Session.begin() as session:
            session.add(payment)
            session.flush()

            result = PaymentOut.model_validate(payment)

    except SQLAlchemyError:
        logger.exception("Payment creation failed")
        raise HTTPException(
            status_code=503,
            detail="Payment service temporarily unavailable"
        )

    # Analyser ensuite le paiement avec Isolation Forest.
    # L'indisponibilite de l'IA ne doit pas annuler
    # une transaction deja enregistree.
    analysis = analyze_payment(
        amount=payment.amount,
        currency=payment.currency,
        created_at=payment.created_at
    )

    anomaly = PaymentAnomaly(
        id=str(uuid.uuid4()),
        payment_id=payment.id,
        is_anomaly=analysis.get("is_anomaly"),
        score=analysis.get("score"),
        severity=analysis.get("severity") or "unknown",
        model=analysis.get("model"),
        analyzed_at=datetime.now(timezone.utc),
    )

    try:
        with Session.begin() as session:
            session.add(anomaly)

        logger.info(
            "AI analysis saved for payment %s",
            payment.id,
        )

    except SQLAlchemyError:
        logger.exception(
            "Unable to save AI analysis for payment %s",
            payment.id,
        )

    logger.info(
        "Anomaly analysis for payment %s: %s",
        payment.id,
        analysis
    )

    if analysis["is_anomaly"] is True:
        logger.warning(
            "Suspicious payment detected: id=%s, severity=%s, score=%s",
            payment.id,
            analysis.get("severity"),
            analysis.get("score")
        )

    elif analysis["is_anomaly"] is None:
        logger.warning(
            "Payment %s accepted without completed AI analysis",
            payment.id
        )

    return result


# ============================================================
# HISTORIQUE DES PAIEMENTS
# ============================================================

@app.get(
    "/payments",
    response_model=list[PaymentOut],
    dependencies=[Depends(get_current_user)]
)
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


# ============================================================
# DETAIL D'UN PAIEMENT
# ============================================================
@app.get(
    "/payments/anomalies",
    response_model=list[PaymentAnomalyOut],
    dependencies=[Depends(get_current_user)],
)
def list_payment_anomalies(
    limit: int = Query(default=50, ge=1, le=100),
    only_suspicious: bool = False,
):
    try:
        with Session() as session:
            query = select(PaymentAnomaly)

            if only_suspicious:
                query = query.where(
                    PaymentAnomaly.is_anomaly.is_(True)
                )

            analyses = session.scalars(
                query.order_by(
                    PaymentAnomaly.analyzed_at.desc()
                ).limit(limit)
            ).all()

            return [
                PaymentAnomalyOut.model_validate(analysis)
                for analysis in analyses
            ]

    except SQLAlchemyError:
        logger.exception("Unable to retrieve AI analyses")
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve AI analyses",
        )


@app.get(
    "/payments/{payment_id}",
    response_model=PaymentOut,
    dependencies=[Depends(get_current_user)]
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
