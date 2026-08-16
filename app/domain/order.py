from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field, field_validator


class Order(BaseModel):
    id: int = Field(gt=0)
    customer_email: EmailStr
    amount: float = Field(gt=0)
    status: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed = {"pending", "paid", "shipped", "cancelled"}
        if normalized not in allowed:
            raise ValueError("status must be one of: pending, paid, shipped, cancelled")
        return normalized
