from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditRecord:
    order_id: int
    action: str
    at: datetime


@dataclass(frozen=True)
class Notification:
    order_id: int
    type: str
    recipient: str
    message: str
    at: datetime


class AuditRepository:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def create(self, record: AuditRecord) -> AuditRecord:
        self._records.append(record)
        return record

    def list_for_order(self, order_id: int) -> list[AuditRecord]:
        return [record for record in self._records if record.order_id == order_id]


class NotificationRepository:
    def __init__(self) -> None:
        self._notifications: list[Notification] = []

    def create(self, notification: Notification) -> Notification:
        self._notifications.append(notification)
        return notification

    def list_for_order(self, order_id: int) -> list[Notification]:
        return [
            notification
            for notification in self._notifications
            if notification.order_id == order_id
        ]


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self._repository = repository

    def record_order_cancelled(self, order_id: int, occurred_at: datetime) -> AuditRecord:
        return self._repository.create(
            AuditRecord(order_id=order_id, action="order_cancelled", at=occurred_at)
        )


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    def notify_order_cancelled(
        self, order_id: int, customer_email: str, occurred_at: datetime
    ) -> Notification:
        return self._repository.create(
            Notification(
                order_id=order_id,
                type="order_cancelled",
                recipient=customer_email,
                message=f"Order {order_id} was cancelled",
                at=occurred_at,
            )
        )