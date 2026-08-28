"""Tests for SecretStore: keychain-first resolution with an environment fallback."""

from __future__ import annotations

from typing import TYPE_CHECKING

from keyring.errors import KeyringError

from floating_agent.secret_store import SecretStore

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_prefers_keychain_over_environment(mocker: MockerFixture) -> None:
    mocker.patch("floating_agent.secret_store.keyring.get_password", return_value="from-keychain")
    mocker.patch.dict("os.environ", {"TOKEN": "from-env"}, clear=False)
    assert SecretStore().get("TOKEN") == "from-keychain"


def test_falls_back_to_environment_when_keychain_empty(mocker: MockerFixture) -> None:
    mocker.patch("floating_agent.secret_store.keyring.get_password", return_value=None)
    mocker.patch.dict("os.environ", {"TOKEN": "from-env"}, clear=False)
    assert SecretStore().get("TOKEN") == "from-env"


def test_falls_back_when_no_keychain_backend(mocker: MockerFixture) -> None:
    mocker.patch("floating_agent.secret_store.keyring.get_password", side_effect=KeyringError("no backend"))
    mocker.patch.dict("os.environ", {"TOKEN": "from-env"}, clear=False)
    assert SecretStore().get("TOKEN") == "from-env"


def test_returns_none_when_unset(mocker: MockerFixture) -> None:
    mocker.patch("floating_agent.secret_store.keyring.get_password", return_value=None)
    mocker.patch.dict("os.environ", {}, clear=True)
    assert SecretStore().get("MISSING") is None
