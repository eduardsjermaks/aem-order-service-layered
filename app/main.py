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


class OrderUpdateRequest(BaseModel):
    customer_email: EmailStr
    amount: float = Field(gt=0)
    status: str = Field(min_length=1)


class OrderResponse(BaseModel):
    id: int
    customer_email: EmailStr
    amount: float
    status: str
    created_at: str


def serialize_order(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "customer_email": str(order.customer_email),
        "amount": order.amount,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
    }


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
    return serialize_order(created)


@app.get("/orders", response_model=list[OrderResponse])
def list_orders() -> Any:
    repository: OrderRepository = app.state.order_repository
    return [serialize_order(order) for order in repository.list()]


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

    return serialize_order(order)


@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, payload: OrderUpdateRequest) -> Any:
    repository: OrderRepository = app.state.order_repository
    try:
        order = repository.get(order_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        ) from exc

    updated = Order(
        id=order.id,
        customer_email=payload.customer_email,
        amount=payload.amount,
        status=payload.status,
        created_at=order.created_at,
    )
    repository.update(order_id, updated)
    return serialize_order(updated)


@app.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int) -> Any:
    repository: OrderRepository = app.state.order_repository
    try:
        order = repository.get(order_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        ) from exc

    cancelled = Order(
        id=order.id,
        customer_email=order.customer_email,
        amount=order.amount,
        status="cancelled",
        created_at=order.created_at,
    )
    repository.update(order_id, cancelled)
    return serialize_order(cancelled)
