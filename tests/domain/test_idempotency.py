from floating_agent.domain.idempotency import build_idempotency_key


def test_idempotency_key_is_independent_from_payload_order() -> None:
    first = build_idempotency_key(
        provider="mail",
        account_id="demo-account",
        resource_type="message",
        resource_id="message-1",
        action_type="archive",
        payload={"label": "inbox", "read": True},
    )
    second = build_idempotency_key(
        provider="mail",
        account_id="demo-account",
        resource_type="message",
        resource_id="message-1",
        action_type="archive",
        payload={"read": True, "label": "inbox"},
    )

    assert first == second


def test_idempotency_key_changes_with_action_payload() -> None:
    base = {
        "provider": "mail",
        "account_id": "demo-account",
        "resource_type": "message",
        "resource_id": "message-1",
        "action_type": "label",
    }

    assert build_idempotency_key(**base, payload={"label": "follow-up"}) != build_idempotency_key(
        **base,
        payload={"label": "archive"},
    )
