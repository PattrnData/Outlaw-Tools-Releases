# Outlaw Tools downloads

Public release downloads for **Outlaw Tools**, the Orbital Outlaws desktop companion for Star Citizen.

- Canonical product page: https://www.orbitaloutlaws.tv/tools
- Features and roadmap: https://www.orbitaloutlaws.tv/tools#features and https://www.orbitaloutlaws.tv/tools#roadmap
- Releases: https://github.com/PattrnData/Outlaw-Tools-Releases/releases

The source repository remains private. This repository is only for public release notes, installers, Linux packages, and checksum assets.

## Current release

- Latest release: https://github.com/PattrnData/Outlaw-Tools-Releases/releases/latest
- Windows: https://github.com/PattrnData/Outlaw-Tools-Releases/releases/latest/download/OutlawTools-Setup.exe
- Linux: https://github.com/PattrnData/Outlaw-Tools-Releases/releases/latest/download/OutlawTools-linux-x86_64.tar.gz

The installer/package filenames keep stable `OutlawTools-*` names for compatibility with the website download buttons and updater-facing release paths. The product name is **Outlaw Tools**.

## Discord release announcements

Published GitHub releases are announced to the existing Discord `#tools-releases` channel by `.github/workflows/discord-release.yml`.

Repository setup required before the workflow can post live:

- Add the Discord webhook as an Actions secret named `DISCORD_OUTLAW_TOOLS_RELEASES_WEBHOOK_URL`.
- Verify that the webhook targets `#tools-releases`; the workflow does not commit or print the raw webhook URL.
- Set the repository variable `OUTLAW_TOOLS_DISCORD_RELEASES_ENABLED` to `true` only after the webhook target has been verified. Until then, the workflow validates and uploads dry-run artifacts but does not call Discord.
- Keep the workflow trigger on `release.published` only. `release.edited` is intentionally not enabled until a future idempotent update path can safely edit or reconcile the prior Discord message.

The checked helper script validates that the release is not a draft, records prerelease status explicitly, requires these stable assets, posts with `?wait=true`, disables broad mentions through `allowed_mentions: {"parse": []}`, and writes a structured receipt artifact:

- `OutlawTools-Setup.exe`
- `OutlawTools-Setup.exe.sha256`
- `OutlawTools-linux-x86_64.tar.gz`
- `OutlawTools-linux-x86_64.tar.gz.sha256`

Local dry-run example:

```bash
python3 scripts/discord_release_announcement.py \
  --event tests/fixtures/release_v0.2.2.json \
  --receipt /tmp/outlaw-tools-discord-receipt.json \
  --payload-out /tmp/outlaw-tools-discord-payload.json \
  --dry-run
```
