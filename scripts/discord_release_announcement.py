#!/usr/bin/env python3
"""Build and optionally send Outlaw Tools release announcements to Discord."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import parse, request

REQUIRED_ASSETS = (
    "OutlawTools-Setup.exe",
    "OutlawTools-Setup.exe.sha256",
    "OutlawTools-linux-x86_64.tar.gz",
    "OutlawTools-linux-x86_64.tar.gz.sha256",
)
TOOLS_PAGE_URL = "https://www.orbitaloutlaws.tv/tools"
DEFAULT_WEBHOOK_ENV = "DISCORD_OUTLAW_TOOLS_RELEASES_WEBHOOK_URL"
DRY_RUN_MESSAGE_ID = "DRY_RUN_NO_MESSAGE"


class ReleaseAnnouncementError(RuntimeError):
    """Raised for release data that must not be announced."""


def load_release_event(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    release = data.get("release") if isinstance(data, dict) else None
    if not isinstance(release, dict):
        raise ReleaseAnnouncementError("event JSON does not contain a release object")
    return data


def validate_release(release: dict[str, Any]) -> None:
    if release.get("draft"):
        raise ReleaseAnnouncementError("draft release will not be announced")
    if not release.get("id"):
        raise ReleaseAnnouncementError("release id is required for idempotency")
    if not release.get("tag_name"):
        raise ReleaseAnnouncementError("release tag_name is required")


def required_asset_map(release: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets = release.get("assets") or []
    by_name = {asset.get("name"): asset for asset in assets if isinstance(asset, dict)}
    missing = [name for name in REQUIRED_ASSETS if name not in by_name]
    if missing:
        raise ReleaseAnnouncementError("missing required stable release asset(s): " + ", ".join(missing))
    return {name: by_name[name] for name in REQUIRED_ASSETS}


def verify_url(url: str, timeout: float = 10.0) -> dict[str, Any]:
    if not url.startswith(("https://", "http://")):
        return {"url_resolves": False, "status": None, "error": "unsupported URL scheme"}
    req = request.Request(url, method="HEAD", headers={"User-Agent": "outlaw-tools-release-discord-action"})
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return {"url_resolves": 200 <= response.status < 400, "status": response.status, "error": None}
    except Exception as exc:  # noqa: BLE001 - receipt must preserve URL-check failure reason
        return {"url_resolves": False, "status": None, "error": exc.__class__.__name__}


def build_asset_checks(asset_map: dict[str, dict[str, Any]], check_urls: bool) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for name in REQUIRED_ASSETS:
        asset = asset_map[name]
        url = asset.get("browser_download_url") or ""
        check: dict[str, Any] = {
            "name": name,
            "present": True,
            "browser_download_url": url,
            "state": asset.get("state"),
            "size": asset.get("size"),
            "digest": asset.get("digest"),
            "url_checked": check_urls,
        }
        if check_urls:
            check.update(verify_url(url))
        else:
            check.update({"url_resolves": None, "status": None, "error": None})
        checks.append(check)
    failures = [check for check in checks if check_urls and not check.get("url_resolves")]
    if failures:
        names = ", ".join(check["name"] for check in failures)
        raise ReleaseAnnouncementError(f"required release asset URL(s) did not resolve: {names}")
    return checks


def short_notes(body: str | None, limit: int = 700) -> str:
    text = (body or "").replace("\r\n", "\n").strip()
    if not text:
        return "See the GitHub release notes for details."
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    notes = "\n".join(lines[:8])
    if len(notes) > limit:
        notes = notes[: limit - 1].rstrip() + "…"
    return notes


def build_discord_payload(release: dict[str, Any], asset_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    tag = str(release["tag_name"])
    name = str(release.get("name") or tag)
    prerelease = "yes" if release.get("prerelease") else "no"
    windows = asset_map["OutlawTools-Setup.exe"]["browser_download_url"]
    windows_sha = asset_map["OutlawTools-Setup.exe.sha256"]["browser_download_url"]
    linux = asset_map["OutlawTools-linux-x86_64.tar.gz"]["browser_download_url"]
    linux_sha = asset_map["OutlawTools-linux-x86_64.tar.gz.sha256"]["browser_download_url"]
    content = (
        f"Outlaw Tools {tag} is live.\n"
        f"Release: {name}\n"
        f"Prerelease: {prerelease}\n"
        f"\nShort notes:\n{short_notes(release.get('body'))}\n"
        f"\nDownloads:\n"
        f"- Windows: {windows}\n"
        f"- Windows SHA256: {windows_sha}\n"
        f"- Linux: {linux}\n"
        f"- Linux SHA256: {linux_sha}\n"
        f"\nTools page: {TOOLS_PAGE_URL}\n"
        f"Support: share issues and feedback in #tool-feedback."
    )
    return {"content": content, "allowed_mentions": {"parse": []}}


def webhook_wait_url(webhook_url: str) -> str:
    parts = parse.urlsplit(webhook_url)
    query = dict(parse.parse_qsl(parts.query, keep_blank_values=True))
    query["wait"] = "true"
    return parse.urlunsplit((parts.scheme, parts.netloc, parts.path, parse.urlencode(query), parts.fragment))


def post_to_discord(webhook_url: str, payload: dict[str, Any]) -> str:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        webhook_wait_url(webhook_url),
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "outlaw-tools-release-discord-action"},
    )
    with request.urlopen(req, timeout=20) as response:
        response_body = response.read().decode("utf-8")
    message = json.loads(response_body)
    message_id = message.get("id")
    if not message_id:
        raise ReleaseAnnouncementError("Discord webhook did not return a message id")
    return str(message_id)


def build_receipt(
    event: dict[str, Any],
    payload: dict[str, Any],
    asset_checks: list[dict[str, Any]],
    message_id: str,
    webhook_env: str,
    dry_run: bool,
) -> dict[str, Any]:
    release = event["release"]
    content_hash = hashlib.sha256(payload["content"].encode("utf-8")).hexdigest()
    return {
        "receipt_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_action": event.get("action"),
        "trigger_policy": "release.published only; release.edited intentionally disabled until safe update persistence exists",
        "idempotency_key": f"release:{release['id']}:{release['tag_name']}",
        "release": {
            "id": release["id"],
            "tag": release["tag_name"],
            "name": release.get("name"),
            "draft": bool(release.get("draft")),
            "prerelease": bool(release.get("prerelease")),
            "html_url": release.get("html_url"),
        },
        "discord": {
            "target": webhook_env,
            "message_id": message_id,
            "wait_true": True,
            "dry_run": dry_run,
            "allowed_mentions": payload["allowed_mentions"],
        },
        "content_sha256": content_hash,
        "asset_checks": asset_checks,
        "live_side_effects": {
            "discord_webhook_called": not dry_run,
            "broad_mentions_enabled": False,
            "secret_values_committed": False,
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post an Outlaw Tools GitHub release announcement to Discord.")
    parser.add_argument("--event", type=Path, required=True, help="GitHub release event JSON path, usually GITHUB_EVENT_PATH")
    parser.add_argument("--receipt", type=Path, required=True, help="Path to write the structured receipt JSON")
    parser.add_argument("--payload-out", type=Path, help="Optional path to write the Discord payload JSON")
    parser.add_argument("--dry-run", action="store_true", help="Validate and write artifacts without calling Discord")
    parser.add_argument("--check-urls", action="store_true", help="Resolve required asset browser_download_url values")
    parser.add_argument("--webhook-env", default=DEFAULT_WEBHOOK_ENV, help="Environment variable containing the Discord webhook URL")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        event = load_release_event(args.event)
        release = event["release"]
        validate_release(release)
        asset_map = required_asset_map(release)
        asset_checks = build_asset_checks(asset_map, check_urls=args.check_urls)
        payload = build_discord_payload(release, asset_map)
        if args.payload_out:
            args.payload_out.parent.mkdir(parents=True, exist_ok=True)
            args.payload_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if args.dry_run:
            message_id = DRY_RUN_MESSAGE_ID
        else:
            webhook_url = os.environ.get(args.webhook_env)
            if not webhook_url:
                raise ReleaseAnnouncementError(f"required webhook environment variable is not set: {args.webhook_env}")
            message_id = post_to_discord(webhook_url, payload)
        receipt = build_receipt(event, payload, asset_checks, message_id, args.webhook_env, args.dry_run)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        mode = "dry-run" if args.dry_run else "sent"
        print(f"{mode}: release {release['tag_name']} -> receipt {args.receipt}")
        return 0
    except ReleaseAnnouncementError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
