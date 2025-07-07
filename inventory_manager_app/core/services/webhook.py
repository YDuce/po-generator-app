"""ShipStation webhook handling."""

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any, Optional

import redis
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import structlog

from inventory_manager_app.core.models import OrderRecord, ChannelSheet
from .sheets import SheetsService


class WebhookService:
    """Validate ShipStation webhooks with replay protection."""

    def __init__(
        self,
        secrets: list[str],
        redis_client: redis.Redis,
        db_session: Session,
        window_seconds: int = 300,
    ) -> None:
        self.secrets = secrets
        self.redis = redis_client
        self.db = db_session
        self.window = window_seconds

    def rotate_from_file(self, path: str) -> None:
        """Reload HMAC secrets from an external file."""
        with open(path, "r", encoding="utf-8") as handle:
            self.secrets = [line.strip() for line in handle if line.strip()]

    def verify(self, payload: bytes, signature: str) -> bool:
        if self.redis.get(signature):
            return False
        for secret in self.secrets:
            digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            if hmac.compare_digest(digest, signature):
                self.redis.set(signature, 1, ex=self.window)
                return True
        return False

    def process(
        self,
        payload: bytes,
        signature: str,
        data: dict[str, Any],
        sheets: Optional["SheetsService"] = None,
        request_id: str | None = None,
    ) -> tuple[str, int]:
        """Validate and persist webhook data.

        Parameters
        ----------
        payload: bytes
            Raw request body used for signature verification.
        signature: str
            Value from ``X-ShipStation-Signature`` header.
        data: dict[str, Any]
            Parsed JSON payload.
        sheets: SheetsService | None
            Optional Sheets service used for spreadsheet updates.
        """

        logger = structlog.get_logger(__name__).bind(request_id=request_id)

        if not self.verify(payload, signature):
            logger.warning("Webhook signature verification failed")
            return "invalid signature", 400

        from inventory_manager_app.core.schemas import OrderPayload
        try:
            payload_data = OrderPayload.model_validate(data)
        except Exception as exc:
            logger.warning("invalid payload", errors=str(exc))
            return "invalid payload", 400

        try:
            ordered_date = payload_data.ordered_date
            if ordered_date is None:
                ordered_dt = datetime.now(timezone.utc)
            else:
                ordered_dt = ordered_date

            order = self.db.query(OrderRecord).filter_by(
                order_id=payload_data.order_id
            ).first()
            if order:
                order.channel = payload_data.channel
                order.product_sku = payload_data.product_sku
                order.quantity = payload_data.quantity
                order.ordered_date = ordered_dt
            else:
                order = OrderRecord(
                    order_id=payload_data.order_id,
                    channel=payload_data.channel,
                    product_sku=payload_data.product_sku,
                    quantity=payload_data.quantity,
                    ordered_date=ordered_dt,
                )
                self.db.add(order)
            self.db.commit()

            if sheets:
                try:
                    sheet = (
                        self.db.query(ChannelSheet)
                        .filter_by(channel=payload_data.channel)
                        .first()
                    )
                    if not sheet:
                        logger.error(
                            "channel mapping missing", channel=payload_data.channel
                        )
                        return "unknown channel", 400
                    sheets.append_row(
                        sheet.spreadsheet_id,
                        "A1",
                        [
                            payload_data.order_id,
                            payload_data.product_sku,
                            payload_data.quantity,
                            ordered_dt.isoformat(),
                        ],
                    )
                except Exception as exc:
                    logger.exception("Sheet update failed", error=str(exc))

            return "", 204
        except SQLAlchemyError as exc:
            logger.exception("db error", error=str(exc))
            self.db.rollback()
            return "error", 500
        except Exception as exc:
            logger.exception("Webhook processing error", error=str(exc))
            self.db.rollback()
            return "error", 500
