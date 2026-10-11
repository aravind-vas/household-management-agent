"""Guest sandbox: per-sender toolset policy for a shared-channel agent.

The core idea: when a chat channel is shared between a trusted owner and
untrusted guests, privilege must be resolved from *identity in code* before
any model call. Prompt-level guardrails are a second layer — never the first.

This module is deliberately standalone (stdlib only) so the policy can be
unit-tested, audited, and lifted into any platform adapter that exposes a
``toolsets_for_source(sender)`` style hook.

Real identifiers come from environment variables at runtime and are never
stored by this module.
"""

from __future__ import annotations

import os
import unicodedata
from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence, Tuple

# Research-only toolset: no files, no shell, no memory, no cron, no commerce.
GUEST_TOOLSETS: Tuple[str, ...] = ("web", "browser", "vision")

# Minimal toolset for restricted contacts (e.g. a person who may leave
# notes but must never steer the agent).
PRIVATE_TOOLSETS: Tuple[str, ...] = ("personal_note",)

# The only commands a restricted contact may run.
PRIVATE_COMMANDS = frozenset({"new", "reset", "stop", "help", "whoami"})

ENV_OWNER_ID = "HOUSEHOLD_OWNER_ID"
ENV_PRIVATE_ID = "HOUSEHOLD_PRIVATE_ID"
ENV_PRIVATE_PROFILE = "HOUSEHOLD_PRIVATE_PROFILE"


def normalize_id(raw: Optional[str]) -> str:
    """Canonicalize a sender/phone-style id: strip whitespace and leading '+'."""
    return (raw or "").strip().lstrip("+")


@dataclass(frozen=True)
class GuestSandboxPolicy:
    """Resolves toolsets and message permissions per sender.

    Resolution order (first match wins):

    1. restricted contact  -> minimal toolset + command allowlist
    2. owner               -> ``None`` (full platform toolset resolution)
    3. everyone else       -> guest jail
    """

    owner_id: str
    private_id: Optional[str] = None
    private_profile: Optional[str] = None
    guest_toolsets: Sequence[str] = field(default=GUEST_TOOLSETS)

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "GuestSandboxPolicy":
        env = os.environ if env is None else env
        owner = normalize_id(env.get(ENV_OWNER_ID))
        if not owner:
            raise ValueError(f"{ENV_OWNER_ID} must be set — refusing to guess the owner")
        return cls(
            owner_id=owner,
            private_id=normalize_id(env.get(ENV_PRIVATE_ID)) or None,
            private_profile=(env.get(ENV_PRIVATE_PROFILE) or "").strip() or None,
        )

    # ── toolset resolution ──────────────────────────────────────────────

    def toolsets_for_sender(self, sender_id: Optional[str]) -> Optional[list]:
        """Return the allowed toolsets for a sender.

        ``None`` means "no restriction from this policy" — i.e. the owner,
        who gets the platform's normal toolset resolution.
        """
        uid = normalize_id(sender_id)
        if self.private_id and uid == normalize_id(self.private_id):
            return list(PRIVATE_TOOLSETS)
        if uid == normalize_id(self.owner_id):
            return None
        # Fail closed: unknown senders are treated as guests.
        return list(self.guest_toolsets)

    def is_owner(self, sender_id: Optional[str]) -> bool:
        return normalize_id(sender_id) == normalize_id(self.owner_id)

    # ── restricted-contact message gate ─────────────────────────────────

    def message_allowed(
        self,
        sender_id: Optional[str],
        text: Optional[str],
        sender_profile: Optional[str] = None,
    ) -> bool:
        """Gate messages from the restricted contact.

        Non-restricted senders always pass (their toolset jail is their
        containment). For the restricted contact:

        - the routing profile must match the expected isolated profile,
          otherwise the message is dropped entirely (fail closed);
        - slash commands outside the allowlist are dropped;
        - free text is allowed.
        """
        if not self.private_id:
            return True
        if normalize_id(sender_id) != normalize_id(self.private_id):
            return True

        if self.private_profile and sender_profile != self.private_profile:
            return False

        # NFKC so fullwidth/lookalike slashes cannot smuggle commands past us.
        normalized = unicodedata.normalize("NFKC", text or "").lstrip()
        if normalized.startswith("/"):
            command = normalized.split(None, 1)[0].lstrip("/").lower()
            return command in PRIVATE_COMMANDS
        return True
