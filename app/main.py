from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.domain.order import Order
from app.repository import OrderRepository

app = FastAPI(title="AEM Order Service")
app.state.order_repository = OrderRepository()


class OrderCreateRequest(BaseModel):
    customer_email: EmailStr
    amount: float = Field(gt=0)
    status: str = Field(min_length=1)


class OrderResponse(BaseModel):
    id: int
    customer_email: EmailStr
    amount: float
    status: str
    created_at: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreateRequest) -> Any:
    repository: OrderRepository = app.state.order_repository
    next_id = len(repository.list()) + 1
    order = Order(
        id=next_id,
        customer_email=payload.customer_email,
        amount=payload.amount,
        status=payload.status,
    )
    created = repository.create(order)
    return {
        "id": created.id,
        "customer_email": str(created.customer_email),
        "amount": created.amount,
        "status": created.status,
        "created_at": created.created_at.isoformat(),
    }


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int) -> Any:
    repository: OrderRepository = app.state.order_repository
    try:
        order = repository.get(order_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        ) from exc

    return {
        "id": order.id,
        "customer_email": str(order.customer_email),
        "amount": order.amount,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
    }
