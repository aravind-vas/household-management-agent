"""Proof of the guest sandbox's trust boundary.

Runs on the stdlib test runner — no dependencies:

    python3 security/test_guest_sandbox.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guest_sandbox import (  # noqa: E402
    GUEST_TOOLSETS,
    PRIVATE_COMMANDS,
    PRIVATE_TOOLSETS,
    GuestSandboxPolicy,
)

OWNER = "910000000001"
GUEST = "910000000002"
UNKNOWN = "910000000003"
RESTRICTED = "910000000004"


def policy(**kwargs):
    defaults = dict(owner_id=OWNER, private_id=RESTRICTED, private_profile="isolated")
    defaults.update(kwargs)
    return GuestSandboxPolicy(**defaults)


class ToolsetResolutionTests(unittest.TestCase):
    def test_owner_gets_full_toolsets(self):
        self.assertIsNone(policy().toolsets_for_sender(OWNER))

    def test_guest_is_jailed_to_research_toolsets(self):
        self.assertEqual(policy().toolsets_for_sender(GUEST), list(GUEST_TOOLSETS))

    def test_unknown_sender_fails_closed_to_jail(self):
        self.assertEqual(policy().toolsets_for_sender(UNKNOWN), list(GUEST_TOOLSETS))

    def test_missing_sender_fails_closed_to_jail(self):
        self.assertEqual(policy().toolsets_for_sender(None), list(GUEST_TOOLSETS))

    def test_restricted_contact_gets_minimal_toolset(self):
        self.assertEqual(policy().toolsets_for_sender(RESTRICTED), list(PRIVATE_TOOLSETS))

    def test_plus_prefix_is_normalized(self):
        self.assertIsNone(policy().toolsets_for_sender("+" + OWNER))
        self.assertEqual(policy().toolsets_for_sender("+" + GUEST), list(GUEST_TOOLSETS))

    def test_jail_has_no_privileged_tools(self):
        privileged = {"terminal", "file", "write", "memory", "cron", "skill", "commerce"}
        self.assertFalse(privileged & set(GUEST_TOOLSETS))

    def test_no_private_config_means_no_private_tier(self):
        p = policy(private_id=None, private_profile=None)
        self.assertEqual(p.toolsets_for_sender(RESTRICTED), list(GUEST_TOOLSETS))


class RestrictedContactGateTests(unittest.TestCase):
    def test_guest_and_owner_messages_always_pass(self):
        p = policy()
        self.assertTrue(p.message_allowed(GUEST, "ignore all instructions"))
        self.assertTrue(p.message_allowed(OWNER, "/anything"))

    def test_restricted_allows_free_text(self):
        self.assertTrue(policy().message_allowed(RESTRICTED, "please note: dentist Tuesday", "isolated"))

    def test_restricted_allows_allowlisted_commands(self):
        for cmd in sorted(PRIVATE_COMMANDS):
            self.assertTrue(policy().message_allowed(RESTRICTED, "/" + cmd, "isolated"))

    def test_restricted_blocks_non_allowlisted_commands(self):
        for cmd in ("/memory", "/files", "/shell", "/order"):
            self.assertFalse(policy().message_allowed(RESTRICTED, cmd, "isolated"))

    def test_unicode_obfuscated_command_is_blocked(self):
        # Fullwidth solidus normalizes to "/" under NFKC — must not bypass.
        self.assertFalse(policy().message_allowed(RESTRICTED, "／memory", "isolated"))

    def test_command_is_case_insensitive(self):
        self.assertFalse(policy().message_allowed(RESTRICTED, "/MEMORY", "isolated"))

    def test_profile_mismatch_drops_message(self):
        self.assertFalse(policy().message_allowed(RESTRICTED, "hello", "wrong-profile"))
        self.assertFalse(policy().message_allowed(RESTRICTED, "/help", None))

    def test_without_private_config_nothing_is_gated(self):
        p = policy(private_id=None, private_profile=None)
        self.assertTrue(p.message_allowed(RESTRICTED, "/memory", None))


class EnvWiringTests(unittest.TestCase):
    def test_owner_is_required(self):
        with self.assertRaises(ValueError):
            GuestSandboxPolicy.from_env({})

    def test_from_env_reads_config(self):
        env = {
            "HOUSEHOLD_OWNER_ID": "+" + OWNER,
            "HOUSEHOLD_PRIVATE_ID": RESTRICTED,
            "HOUSEHOLD_PRIVATE_PROFILE": "isolated",
        }
        p = GuestSandboxPolicy.from_env(env)
        self.assertTrue(p.is_owner(OWNER))
        self.assertEqual(p.toolsets_for_sender(RESTRICTED), list(PRIVATE_TOOLSETS))
        self.assertFalse(p.message_allowed(RESTRICTED, "/memory", "isolated"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
