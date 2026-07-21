"""Stable idempotency keys for provider actions."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def build_idempotency_key(
    *,
    provider: str,
    account_id: str,
    resource_type: str,
    resource_id: str,
    action_type: str,
    payload: Mapping[str, object],
) -> str:
    """Return a stable SHA-256 key for a semantically identical action."""
    canonical_action = {
        "account_id": account_id,
        "action_type": action_type,
        "payload": payload,
        "provider": provider,
        "resource_id": resource_id,
        "resource_type": resource_type,
    }
    encoded_action = json.dumps(
        canonical_action,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(encoded_action).hexdigest()
