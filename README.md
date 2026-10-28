# EpisodeFlow

<p align="center"><img src="assets/episodeflow-logo.png" alt="EpisodeFlow icon" width="148"></p>

**Developer:** [@cumaduran](https://github.com/cumaduran) (Cuma Duran). The app includes a clickable developer profile link in the footer and About dialog.

**EpisodeFlow** is a polished, offline-first desktop application that batch-renames video episode files using the episode numbers already found in their existing filenames. It is designed for mixed naming conventions from different encoders, upscalers, and archives.

> Example: `ANKANRT156_CUGAN_2x_hevc_nvenc_4K_4K.mp4` → `ANI_ROTA_156_4K.mp4`.

EpisodeFlow is **not** a video converter. It only changes filenames. Your video bytes, codec, quality, and metadata inside the file are not modified.

## Features

- Modern Windows GUI using **Qt for Python (PySide6)**, with dark and light themes, drag-and-drop folder selection, a searchable preview, and application icon.
- **16 interface languages:** Turkish, English, German, French, Spanish, Italian, Portuguese, Dutch, Polish, Russian, Arabic, Simplified Chinese, Japanese, Korean, Hindi, and Indonesian.
- Automatic episode number extraction from known patterns (`ANKANRT001`, `ANIROTA_NRT_4K_006`) and general markers (`Episode 12`, `S01E07`, `Bölüm 008`).
- Custom filename pattern with `*(x)*`, `{episode}`, `{bolum}`, or `{number}` as the episode placeholder.
- Adjustable minimum/maximum episode number and zero-padding (e.g. `1` → `001`, or `0001`).
- Recognizes common video formats; optional scan of all file types and subfolders.
- Preview-before-commit, name conflict detection (including Windows case-insensitive collisions), CSV export, and undo of the **most recent successful batch**.
- Local processing without accounts, online services, telemetry, or network access.
- GitHub Actions pipeline to **build a self-contained Windows `.exe`** and attach it to tagged GitHub releases.

## Install: ready-made Windows executable

When this repository has been pushed to GitHub:

1. Open the repository's **Actions** tab.
2. Select **Build Windows EXE** and click **Run workflow** (or push to `main` to build automatically).
3. Open the completed run and download the `EpisodeFlow-Windows-...` artifact.
4. Extract the artifact and double-click **`EpisodeFlow.exe`**.

To publish a download-ready release, run **Actions → Build Windows EXE → Run workflow**, enter `v1.0.0` in **Release tag**, and click **Run workflow**. The workflow builds the EXE, runs a smoke test, and publishes `EpisodeFlow.exe`, `EpisodeFlow-Windows.zip`, and `SHA256SUMS.txt` under **Releases**. Leave Release tag empty to only build a run artifact. An alternative is to push a version tag as shown below.

**Note:** EXE builds require a successful Windows Actions run. A `.zip` of source files is not a compiled Windows EXE.

**No Python installation is needed to run the packaged EXE.** An unsigned EXE can trigger Microsoft SmartScreen on first launch; review the publisher/source and sign releases for public distribution.

## Usage

1. Open **EpisodeFlow** and pick the directory containing your videos (or drag the folder into the window).
2. Enter a naming pattern. The default is `ANI_ROTA_*(x)*_4K`.
3. Set the number of **Digits** (default: `3`) and episode range (default: **1–220**).
4. Optionally enable **Include subfolders** or **All file types**.
5. Click **Preview names**. Review the old name, proposed name, extracted episode, and status for every file.
6. Click **Rename files** and confirm. Only entries marked **Ready** are changed.
7. If needed, click **Undo last batch** to restore the previous filenames. The undo journal is stored in your user profile, not inside your video directory.

| Original name | New name with default pattern |
| --- | --- |
| `ANIROTA_NRT_4K_002.mp4` | `ANI_ROTA_002_4K.mp4` |
| `ANKANRT001.realesrgan.1_4K.mp4` | `ANI_ROTA_001_4K.mp4` |
| `ANKANRT003_ESRGAN_4x_hevc_nvenc_4K.mp4` | `ANI_ROTA_003_4K.mp4` |
| `ANKANRT156_CUGAN_2x_hevc_nvenc_4K_4K.mp4` | `ANI_ROTA_156_4K.mp4` |

The application automatically preserves each file's extension. The pattern should **not** include `.mp4` or any other extension. The application extracts episode numbers **from filenames, not from the media contents**.

### Status meanings

- **Ready:** can be safely renamed.
- **Already correct:** no change is necessary.
- **Number not found:** no episode number within the chosen range was detected.
- **Multiple numbers:** the name is ambiguous; it is deliberately skipped.
- **Name conflict:** a proposed target already exists, or more than one file would receive the same name.

### Safety details

EpisodeFlow stages all files in a batch under unique temporary filenames before finalizing destination names. This supports filename swaps/cycles and prevents intentional overwrites. On an ordinary rename error it attempts to roll back the entire batch. A forced shutdown, power loss, filesystem permissions error, external concurrent edits, or hardware failure can interrupt any multi-file filesystem operation; keep backups of valuable data. If the program is interrupted, look for `.episodeflow-*.tmp` files in the affected folders before doing anything else.

The **Undo** action handles only the latest successful batch whose history was saved, and will refuse to overwrite a newly existing file. Renaming another batch replaces the previous undo journal. CSV exports may contain absolute local paths; review them before sharing. Use a copy of your files for the first trial.

## Developer setup

Requirements: **Python 3.12+**, Windows 10/11 recommended for the packaged app, and Git.

```powershell
cd C:\Projects\video-bulk-renaming
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

Run unit tests:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Build a standalone EXE **on Windows**:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
# Output: dist\EpisodeFlow.exe
```

PyInstaller builds binaries for the operating system it runs on, so Linux/macOS cannot directly create this Windows EXE; the included GitHub Actions workflow runs on `windows-latest` for that reason.

## Publish to GitHub

The included helper script publishes this folder to a **private** GitHub repository by default (requires Git, GitHub CLI, and `gh auth login`):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_github.ps1
# For a PUBLIC repository instead:
# powershell -ExecutionPolicy Bypass -File .\scripts\publish_github.ps1 -Public
```

You can also use GitHub CLI commands directly:

```powershell
cd C:\Projects\video-bulk-renaming
git init
git add .
git commit -m "feat: initial EpisodeFlow release"
git branch -M main
gh repo create video-bulk-renaming --private --source . --remote origin --push
```

Alternatively, create an empty repository on GitHub and run:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/video-bulk-renaming.git
git push -u origin main
```

After pushing, **Actions → Build Windows EXE** automatically packages a Windows executable. For a public repository users can access downloads under [`Releases`](https://github.com/cumaduran/video-bulk-renaming/releases) after you actually create the repo and publish the first version. A private repository's releases are accessible only to authorized GitHub users.

**Easiest Release path (GitHub website):** go to **Actions → Build Windows EXE → Run workflow**, select `main`, type `v1.0.0` in the `Release tag` field, then press **Run workflow**. Once green, check **Releases** on the repository home page.

**Alternative (Git CLI):** To publish a versioned Release using a pushed Git tag:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

The release workflow requires repository Actions permissions to create release assets (`contents: write`). No PAT needs to be committed into source control. Verify **Actions** are enabled in the repository and the workflow finished successfully. The workflow refuses to overwrite an existing published Release when you manually request a tag that is already released.

### One-command release from a Windows terminal

After pushing your source to GitHub and authenticating with GitHub CLI, you may instead run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_release.ps1 -Version v1.0.0
```

This helper triggers the GitHub Actions release build for `v1.0.0`; **it does not build an EXE on your own computer**. View the Actions run for progress. Each subsequent release should use a new version (`v1.0.1`, `v1.1.0`, etc.).

## Maintainer

Created and maintained by **[@cumaduran](https://github.com/cumaduran)**. This repository is intended to live at [`cumaduran/video-bulk-renaming`](https://github.com/cumaduran/video-bulk-renaming); the repository URL only becomes live after the owner publishes it.

## Repository structure

```text
video-bulk-renaming/
├── .github/workflows/    # tests, build, release
├── assets/               # app icon (.png and .ico)
├── examples/             # anonymized, filename-only regression samples
├── scripts/              # Windows build and launch scripts
├── src/episodeflow/      # rename engine, translations, Qt UI
├── src/main.py           # application entry point
├── tests/                # unit + sample regression tests
├── README.md             # this guide (English)
├── QUICKSTART_TR.md      # Turkish quick start
└── LICENSE, SECURITY.md, CONTRIBUTING.md, ...
```

## Development and contribution

- The renaming engine (`src/episodeflow/core.py`) does not depend on Qt, and has unit tests for extraction, collision prevention, preview, undo, and sample filenames.
- UI strings live in `src/episodeflow/i18n.py`; translations use the same key set for every locale.
- CI tests run on Windows and Ubuntu; Windows builds are generated separately on Windows runners.
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## Release safety checklist

Please review [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) before distributing an EXE publicly.

## License and third-party notices

EpisodeFlow source code is released under the **MIT License**. The UI uses **PySide6 / Qt**, which has separate LGPL/GPL/commercial licensing requirements. If you distribute modified or bundled Qt binaries, review the applicable Qt licensing obligations (including required notices and replacement/relinking rights). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This repository is not affiliated with any anime series, codec vendor, or Qt Company.
