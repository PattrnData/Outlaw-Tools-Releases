# Outlaw Tools Third-Party Notices

Outlaw Tools is developed by Orbital Outlaws. It uses the third-party projects and data services listed below. Their inclusion does not imply endorsement of Outlaw Tools by their authors.

## Runtime libraries

| Project | Purpose | Licence | Source |
| --- | --- | --- | --- |
| Pillow | Image processing | HPND | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) |
| OpenCV | Image matching and processing | Apache-2.0 | [opencv/opencv](https://github.com/opencv/opencv) |
| NumPy | Numerical arrays | BSD-3-Clause | [numpy/numpy](https://github.com/numpy/numpy) |
| MSS | Screen capture | MIT | [BoboTiG/python-mss](https://github.com/BoboTiG/python-mss) |
| Keyboard | Global hotkeys | MIT | [boppreh/keyboard](https://github.com/boppreh/keyboard) |
| RapidOCR | Fast local text recognition | Apache-2.0 | [RapidAI/RapidOCR](https://github.com/RapidAI/RapidOCR) |
| ONNX Runtime | GPU inference runtime | MIT | [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) |

The full licence text and copyright notices for each project are available from its linked upstream repository and installed package metadata.

## Optional Windows Own-PC Sync

Windows sync uses aiortc, aioice, PyAV, Supabase Auth, keyring and their pinned
dependencies. Full upstream notices and retained sources are included under
`third-party/own-pc-sync-runtime/` in the application bundle. The source-built
FFmpeg/PyAV libraries, exact sources and rebuild instructions are under
`third-party/own-pc-sync-native/`.

FFmpeg is dynamically linked under LGPL-2.1-or-later, without GPL/nonfree features.
Users may replace the external FFmpeg libraries with compatible versions and
reverse-engineer Outlaw Tools as needed to debug modifications to those libraries.
No application term restricts these third-party licence rights. See the bundled
`NOTICE.txt` for replacement instructions. All third-party rights remain with
their respective owners; the application's proprietary licence does not cover them.

## Bundled fonts

Workspace button icons are rasterized from Lucide (ISC), including Feather-derived icons (MIT). Full notices are included in `assets/workspace-icons/LICENSE.txt`; the source is [Lucide](https://github.com/lucide-icons/lucide).

Orbitron, Barlow, Chakra Petch, and Kaushan Script are distributed under the SIL Open Font License 1.1. Their canonical project and licence information is available from [Google Fonts](https://github.com/google/fonts).

## Game and economy data

| Provider | Use | Licence or terms | Source |
| --- | --- | --- | --- |
| Dumper's Repo | Build-aligned game mechanics | Apache-2.0 | [Sinedrone-Sentinel/dumpers_repo](https://github.com/Sinedrone-Sentinel/dumpers_repo) |
| SCMDb | Mining locations, prevalence and paired crafting item/recipe data | Licence not declared by upstream; read-only data service and build-pinned bundled snapshot | [KrovaxCode/SCMDB_DATA](https://github.com/KrovaxCode/SCMDB_DATA) |
| scunpacked-data | Build-pinned extracted ship, ship-item, and FPS equipment data | No licence declared by upstream | [StarCitizenWiki/scunpacked-data](https://github.com/StarCitizenWiki/scunpacked-data) |
| ScDataDumper | Generator credited by scunpacked-data; not distributed by Outlaw Tools | MIT | [octfx/ScDataDumper](https://github.com/octfx/ScDataDumper) |
| UEX Corp | Economy and terminal data | Licence not declared by upstream; used as a read-only data service | [UEX API](https://uexcorp.space/api/documentation/) |
| Star Citizen Wiki API | Blueprint item images | Community API used as a credited read-only image service | [API guide](https://api.star-citizen.wiki/developers) |

scunpacked-data credits ScDataDumper as its current generator. Its extracted Star Citizen game data remains with Cloud Imperium Games, Roberts Space Industries, and other applicable rights holders. No upstream licence or credit listed here grants additional rights to that game data.

Other provider data remains the property of its respective provider and upstream rights holders.

Crafting projections use SCMDb's paired item and recipe data. Exact source revisions and game builds are recorded in the active reference metadata, the bundled `reference-sources.json`, and the reference-channel manifest. Outlaw Tools calculates and labels its own estimates from those facts; attribution does not imply endorsement or a grant of rights.

## Star Citizen disclaimer

Outlaw Tools is an unofficial fan-made tool and is not affiliated with or endorsed by Cloud Imperium Games or Roberts Space Industries. Star Citizen and related marks belong to their respective owners.
