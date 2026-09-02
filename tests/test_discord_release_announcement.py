import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "discord_release_announcement.py"


def asset(name):
    return {
        "name": name,
        "browser_download_url": f"https://github.com/PattrnData/Outlaw-Tools-Releases/releases/download/v0.2.2/{name}",
        "size": 123,
        "state": "uploaded",
        "digest": "sha256:" + "a" * 64,
    }


def release(tag="v0.2.2", release_id=379679455, prerelease=False, draft=False):
    return {
        "action": "published",
        "release": {
            "id": release_id,
            "tag_name": tag,
            "name": f"Outlaw Tools {tag} - Resource Clarity",
            "body": "## Changes\n\n- Better resource clarity.\n- Safer routes.\n\nLong details follow.",
            "draft": draft,
            "prerelease": prerelease,
            "html_url": f"https://github.com/PattrnData/Outlaw-Tools-Releases/releases/tag/{tag}",
            "assets": [
                asset("OutlawTools-Setup.exe"),
                asset("OutlawTools-Setup.exe.sha256"),
                asset("OutlawTools-linux-x86_64.tar.gz"),
                asset("OutlawTools-linux-x86_64.tar.gz.sha256"),
            ],
        },
    }


class DiscordReleaseAnnouncementTests(unittest.TestCase):
    def run_script(self, payload):
        with tempfile.TemporaryDirectory() as td:
            event = Path(td) / "event.json"
            receipt = Path(td) / "receipt.json"
            out = Path(td) / "payload.json"
            event.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--event",
                    str(event),
                    "--receipt",
                    str(receipt),
                    "--payload-out",
                    str(out),
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            return result, json.loads(receipt.read_text()), json.loads(out.read_text())

    def test_current_style_v022_builds_no_ping_payload_and_receipt(self):
        result, receipt, payload = self.run_script(release())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["allowed_mentions"], {"parse": []})
        self.assertNotIn("@everyone", payload["content"])
        self.assertNotIn("@here", payload["content"])
        self.assertIn("v0.2.2", payload["content"])
        self.assertIn("OutlawTools-Setup.exe", payload["content"])
        self.assertIn("OutlawTools-linux-x86_64.tar.gz", payload["content"])
        self.assertIn("https://www.orbitaloutlaws.tv/tools", payload["content"])
        self.assertIn("#tool-feedback", payload["content"])
        self.assertEqual(receipt["release"]["id"], 379679455)
        self.assertEqual(receipt["release"]["tag"], "v0.2.2")
        self.assertEqual(receipt["discord"]["message_id"], "DRY_RUN_NO_MESSAGE")
        self.assertEqual(receipt["discord"]["target"], "DISCORD_OUTLAW_TOOLS_RELEASES_WEBHOOK_URL")
        self.assertEqual(receipt["idempotency_key"], "release:379679455:v0.2.2")
        self.assertTrue(all(check["present"] for check in receipt["asset_checks"]))

    def test_synthetic_future_prerelease_is_marked_explicitly(self):
        result, receipt, payload = self.run_script(release(tag="v0.3.0-beta.1", release_id=400000001, prerelease=True))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(receipt["release"]["prerelease"])
        self.assertIn("Prerelease: yes", payload["content"])
        self.assertEqual(receipt["idempotency_key"], "release:400000001:v0.3.0-beta.1")

    def test_draft_release_is_rejected_before_payload(self):
        with tempfile.TemporaryDirectory() as td:
            event = Path(td) / "event.json"
            receipt = Path(td) / "receipt.json"
            event.write_text(json.dumps(release(draft=True)), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--event", str(event), "--receipt", str(receipt), "--dry-run"],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("draft release", result.stderr.lower())

    def test_missing_required_stable_asset_is_rejected(self):
        payload = release()
        payload["release"]["assets"] = [a for a in payload["release"]["assets"] if a["name"] != "OutlawTools-Setup.exe.sha256"]
        with tempfile.TemporaryDirectory() as td:
            event = Path(td) / "event.json"
            receipt = Path(td) / "receipt.json"
            event.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--event", str(event), "--receipt", str(receipt), "--dry-run"],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OutlawTools-Setup.exe.sha256", result.stderr)


if __name__ == "__main__":
    unittest.main()
