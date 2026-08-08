"""Secret resolution — OS keychain first, environment variable as a fallback."""

from __future__ import annotations

import os

import keyring
from keyring.errors import KeyringError

SERVICE_NAME = "floating-agent"


class SecretStore:
    """Resolves named secrets, preferring the OS keychain over the environment.

    The security guarantee is "no plaintext secrets on disk": a secret stored in
    the OS keychain (via ``keyring``) is used in preference to any environment
    variable of the same name. The environment stays supported as a fallback for
    CI and headless setups where no keychain backend is available.
    """

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        self._service_name = service_name

    def get(self, name: str) -> str | None:
        """Return the secret ``name`` from the keychain, else the environment."""
        value = self._from_keychain(name)
        if value is not None:
            return value
        return os.environ.get(name)

    def _from_keychain(self, name: str) -> str | None:
        """Read from the OS keychain, tolerating the absence of a backend."""
        try:
            return keyring.get_password(self._service_name, name)
        except KeyringError:
            return None
