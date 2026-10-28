"""Pure Python, preview-first and collision-safe episode renaming engine."""
from __future__ import annotations

import csv
import json
import os
import re
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_TEMPLATE = "ANI_ROTA_*(x)*_4K"
TOKENS = ("*(x)*", "{episode}", "{bolum}", "{number}")
VIDEO_EXTENSIONS = frozenset({".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v", ".ts", ".flv", ".mpg", ".mpeg"})
INVALID_WINDOWS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_WINDOWS = re.compile(r"(?i)^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$")
SEASON_EP = re.compile(r"(?i)S\d{1,3}[_. -]*E(\d{1,4})(?!\d)")
EPISODE_TAG = re.compile(r"(?i)(?:^|[^\w])(?:episode|ep|e|bölüm|bolum|chapter|chap|capitulo|episodio)[\s._#-]*(\d{1,4})(?!\d)")
KNOWN_GROUPS = re.compile(r"(?i)^(?:ANKANRT|ANIROTA(?:[_. -]?NRT)?)[_. -]*(?:4K[_. -]*)?(\d{1,4})(?![0-9kxp])")
THREE_DIGIT = re.compile(r"(?i)(?<!\d)(\d{3,4})(?!\d|[kxp]|bit|fps|hz)")
NUMBER = re.compile(r"(?i)(?<!\d)(\d{1,4})(?!\d|[kxp]|bit|fps|hz)")


@dataclass(frozen=True)
class Entry:
    source: Path
    episode: int | None
    target: Path | None
    status: str  # ready, unchanged, unknown, ambiguous, conflict
    detail: str = ""


@dataclass(frozen=True)
class Scan:
    folder: Path
    entries: tuple[Entry, ...]

    @property
    def ready(self) -> tuple[Entry, ...]:
        return tuple(e for e in self.entries if e.status == "ready")

    def count(self, status: str) -> int:
        return sum(e.status == status for e in self.entries)


def missing_episodes(entries: Iterable[Entry], minimum: int, maximum: int) -> list[int]:
    observed = {e.episode for e in entries if e.episode is not None}
    return [i for i in range(minimum, maximum + 1) if i not in observed]


def episode_number(stem: str, minimum: int = 1, maximum: int = 220) -> tuple[int | None, str]:
    """Prefer explicit markers, known filename families, then padded tokens.

    If two equally strong numbers disagree, skip instead of guessing.
    '4K', '2x', '1080p' and other resolution/scale tokens are ignored.
    """
    for pattern in (SEASON_EP, EPISODE_TAG, KNOWN_GROUPS, THREE_DIGIT, NUMBER):
        candidates = {int(m.group(1)) for m in pattern.finditer(stem)
                      if minimum <= int(m.group(1)) <= maximum}
        if len(candidates) == 1:
            return next(iter(candidates)), ""
        if len(candidates) > 1:
            return None, "ambiguous"
    return None, "unknown"


def template_name(template: str, episode: int, digits: int) -> str:
    if not any(token in template for token in TOKENS):
        raise ValueError("Template must include *(x)* or {episode}.")
    number = str(episode).zfill(digits)
    output = template
    for token in TOKENS:
        output = output.replace(token, number)
    if not output or output.endswith((" ", ".")) or INVALID_WINDOWS.search(output):
        raise ValueError("Template contains invalid Windows filename characters.")
    if RESERVED_WINDOWS.fullmatch(output) or len(output) > 200:
        raise ValueError("Template creates a reserved or excessively long Windows filename.")
    return output


def _key(path: Path) -> str:
    # Case-insensitive comparisons match Windows filesystem expectations.
    return str(path.absolute()).casefold()


def scan_folder(folder: Path | str, template: str = DEFAULT_TEMPLATE, *, digits: int = 3,
                minimum: int = 1, maximum: int = 220, recursive: bool = False,
                all_files: bool = False) -> Scan:
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Select an existing folder.")
    if minimum < 0 or maximum < minimum or digits < 1 or digits > 8:
        raise ValueError("Invalid episode limits or digit width.")
    template_name(template, minimum, digits)
    files = (p for p in (root.rglob("*") if recursive else root.iterdir()) if p.is_file())
    files = sorted((p for p in files if not p.name.startswith(".episodeflow-") and
                    (all_files or p.suffix.lower() in VIDEO_EXTENSIONS)),
                   key=lambda p: str(p).casefold())
    present = {_key(p) for p in (p for p in (root.rglob("*") if recursive else root.iterdir()) if p.exists())}
    entries: list[Entry] = []
    for src in files:
        number, problem = episode_number(src.stem, minimum, maximum)
        if number is None:
            entries.append(Entry(src, None, None, problem))
            continue
        new_name = template_name(template, number, digits) + src.suffix
        if len(new_name) > 255:
            entries.append(Entry(src, number, None, "conflict", "filename-too-long"))
            continue
        dest = src.with_name(new_name)
        if src.name == new_name:
            entries.append(Entry(src, number, dest, "unchanged"))
        else:
            entries.append(Entry(src, number, dest, "ready"))

    # A duplicated episode can only be renamed safely when destinations differ.
    destination_frequency: dict[str, int] = {}
    for item in entries:
        if item.status == "ready" and item.target:
            key = _key(item.target)
            destination_frequency[key] = destination_frequency.get(key, 0) + 1
    entries = [replace(item, status="conflict", detail="duplicate-target")
               if item.status == "ready" and item.target and destination_frequency[_key(item.target)] > 1
               else item for item in entries]

    # If a target exists, it is allowed only when *that same path* is an active
    # rename source. Iterate: once a source is blocked, targets pointing at it
    # become blocked too. This supports swaps/cycles while never overwriting.
    while True:
        moving = {_key(e.source) for e in entries if e.status == "ready"}
        updated = [replace(e, status="conflict", detail="target-exists")
                   if e.status == "ready" and e.target and _key(e.target) in present
                   and _key(e.target) not in moving else e for e in entries]
        if updated == entries:
            break
        entries = updated
    return Scan(root, tuple(entries))


def _validate_mapping(pairs: list[tuple[Path, Path]]) -> None:
    if not pairs:
        raise ValueError("No files are ready to rename.")
    from_keys = [_key(source) for source, _ in pairs]
    to_keys = [_key(target) for _, target in pairs]
    if len(set(from_keys)) != len(from_keys) or len(set(to_keys)) != len(to_keys):
        raise ValueError("Duplicate names in the rename operation.")
    source_keys = set(from_keys)
    for source, target in pairs:
        if not source.is_file():
            raise FileNotFoundError(f"Source is missing: {source}")
        if source.parent.resolve() != target.parent.resolve():
            raise ValueError("Moving files between folders is not supported.")
        if _key(target) not in source_keys and target.exists():
            raise FileExistsError(f"Destination already exists: {target}")
        # On case-insensitive Windows, even mixed-case existing names must be protected.
        for item in target.parent.iterdir():
            if _key(item) == _key(target) and _key(item) not in source_keys:
                raise FileExistsError(f"Destination already exists: {item}")


def _atomic_batch(pairs: list[tuple[Path, Path]]) -> None:
    """Two-phase rename. Recover renamed files on ordinary OS exceptions.

    OS interruption/power failure cannot be made atomic across all files; see README.
    """
    _validate_mapping(pairs)
    staged: list[tuple[Path, Path, Path]] = []
    try:
        for source, target in pairs:
            temp = source.with_name(f".episodeflow-{uuid.uuid4().hex}.tmp")
            while temp.exists():
                temp = source.with_name(f".episodeflow-{uuid.uuid4().hex}.tmp")
            source.rename(temp)
            staged.append((source, temp, target))
        for _, temp, target in staged:
            if target.exists():
                raise FileExistsError(f"Destination appeared during rename: {target}")
            temp.rename(target)
    except Exception:
        # Re-stage already completed destinations, then restore originals.
        for source, temp, target in reversed(staged):
            if target.exists() and not temp.exists():
                try:
                    target.rename(temp)
                except OSError:
                    pass
        for source, temp, _ in reversed(staged):
            if temp.exists() and not source.exists():
                try:
                    temp.rename(source)
                except OSError:
                    pass
        raise


def apply_scan(scan: Scan) -> list[tuple[Path, Path]]:
    pairs = [(e.source, e.target) for e in scan.ready if e.target is not None]
    _atomic_batch(pairs)
    return pairs


def history_file() -> Path:
    base = os.getenv("APPDATA")
    folder = Path(base) if base else Path.home() / ".episodeflow"
    return folder / "EpisodeFlow" / "last_operation.json" if base else folder / "last_operation.json"


def save_history(pairs: list[tuple[Path, Path]], path: Path | None = None) -> None:
    dest = path or history_file()
    dest.parent.mkdir(parents=True, exist_ok=True)
    obj = {"version": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
           "pairs": [{"old": str(source), "new": str(target)} for source, target in pairs]}
    temp = dest.with_suffix(".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(dest)


def undo_last(path: Path | None = None) -> int:
    journal = path or history_file()
    obj = json.loads(journal.read_text(encoding="utf-8"))
    if obj.get("version") != 1 or not isinstance(obj.get("pairs"), list):
        raise ValueError("Invalid undo history.")
    pairs = [(Path(item["new"]), Path(item["old"])) for item in obj["pairs"]]
    _atomic_batch(pairs)
    journal.unlink()
    return len(pairs)


def _csv_safe(value: str) -> str:
    return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r")) else value


def export_csv(scan: Scan, destination: Path | str) -> None:
    with Path(destination).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Episode", "Original file", "New file", "Status", "Details"])
        for row in scan.entries:
            writer.writerow([row.episode or "", _csv_safe(str(row.source)),
                             _csv_safe(str(row.target or "")), row.status, row.detail])
