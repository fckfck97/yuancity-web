import logging
from typing import Any, Dict, Iterable, List, Optional

from exponent_server_sdk import PushClient, PushMessage, PushServerError

from apps.user.models import ExpoPushToken, UserAccount

logger = logging.getLogger(__name__)

CHUNK = 95  # Expo recomienda < 100 por batch


def _chunks(seq: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def send_push(
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    *,
    user: Optional[UserAccount] = None,
    badge: Optional[int] = None,
) -> None:
    """
    Envía notificaciones push mediante Expo.
    - Si se pasa `user`, sólo se envía a sus tokens activos.
    - Si `user` es None, se envía a todos los tokens activos.
    """

    qs = (
        user.push_tokens.filter(active=True)
        if user
        else ExpoPushToken.objects.filter(active=True)
    )
    tokens = list(qs.values_list("token", flat=True))
    if not tokens:
        logger.info("Sin tokens para enviar push: %s", title)
        return

    payload_data = data or {}

    for batch in _chunks(tokens, CHUNK):
        messages = []
        for token in batch:
            payload = {"to": token, "title": title, "body": body, "data": payload_data}
            if badge is not None:
                payload["badge"] = badge
            messages.append(PushMessage(**payload))

        try:
            tickets = PushClient().publish_multiple(messages)
        except PushServerError as exc:
            logger.error(
                "PushServerError: %s | response=%s | errors=%s",
                exc,
                getattr(exc, "response_data", None),
                getattr(exc, "errors", None),
            )
            continue
        except Exception as exc:  # pragma: no cover
            logger.exception("Error genérico al enviar push: %s", exc)
            continue

        # Limpia tokens inválidos
        for ticket, target in zip(tickets, batch):
            if (
                ticket.get("status") == "error"
                and ticket.get("details", {}).get("error") == "DeviceNotRegistered"
            ):
                ExpoPushToken.objects.filter(token=target).update(active=False)
                logger.info("Token desactivado: %s", target)
