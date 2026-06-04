"""`python -m floating_agent` → launch the native overlay."""

from __future__ import annotations

import sys

from floating_agent.overlay.app import run

if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
