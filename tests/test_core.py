from pathlib import Path
import csv
import pytest

from episodeflow.core import (
    DEFAULT_TEMPLATE, episode_number, scan_folder, template_name,
    apply_scan, save_history, undo_last, export_csv, missing_episodes
)


@pytest.mark.parametrize("old,number", [
    ("ANIROTA_NRT_4K_002", 2),
    ("ANIROTA_NRT_4K_006_4K", 6),
    ("ANIROTA_NRT_4K_007_4K", 7),
    ("ANIROTA_NRT_4K_008", 8),
    ("ANKANRT001.realesrgan.1_4K", 1),
    ("ANKANRT003_ESRGAN_4x_hevc_nvenc_4K", 3),
    ("ANKANRT009_CUGAN_2x_hevc_nvenc_4K", 9),
    ("ANKANRT156_CUGAN_2x_hevc_nvenc_4K_4K", 156),
    ("My Show - Episode 015 - 1080p", 15),
    ("S01E07", 7),
    ("Bölüm 020", 20),
])
def test_extract(old, number):
    assert episode_number(old) == (number, "")


def test_ambiguous_is_never_guessed():
    assert episode_number("video_013_or_014") == (None, "ambiguous")
    assert episode_number("video-no-number") == (None, "unknown")
    assert episode_number("render_4K_2x") == (None, "unknown")
    assert episode_number("export_10bit_60fps") == (None, "unknown")


def test_template_digits():
    assert template_name(DEFAULT_TEMPLATE, 6, 3) == "ANI_ROTA_006_4K"
    assert template_name("Episode-{episode}-EN", 15, 4) == "Episode-0015-EN"
    assert template_name("Bölüm_{bolum}", 2, 3) == "Bölüm_002"
    with pytest.raises(ValueError):
        template_name("constant_name", 1, 3)
    with pytest.raises(ValueError):
        template_name("A/?{episode}", 1, 3)


def test_preview_no_mutation_and_undo(tmp_path):
    (tmp_path / "ANKANRT001.realesrgan.1_4K.mp4").write_bytes(b"video-1")
    (tmp_path / "ANIROTA_NRT_4K_006_4K.mp4").write_bytes(b"video-6")
    (tmp_path / "unknown.mp4").write_bytes(b"video-u")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    scan = scan_folder(tmp_path)
    assert scan.count("ready") == 2
    assert scan.count("unknown") == 1
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    pairs = apply_scan(scan)
    assert (tmp_path / "ANI_ROTA_001_4K.mp4").read_bytes() == b"video-1"
    assert (tmp_path / "ANI_ROTA_006_4K.mp4").read_bytes() == b"video-6"
    history = tmp_path / "undo.json"
    save_history(pairs, history)
    assert undo_last(history) == 2
    assert not history.exists()
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


def test_conflicting_existing_target_is_never_overwritten(tmp_path):
    (tmp_path / "ANKANRT001.mp4").write_bytes(b"original")
    (tmp_path / "ANI_ROTA_001_4K.mp4").write_bytes(b"do not touch")
    scan = scan_folder(tmp_path)
    assert scan.count("ready") == 0
    assert scan.count("conflict") == 1
    assert (tmp_path / "ANI_ROTA_001_4K.mp4").read_bytes() == b"do not touch"


def test_duplicate_episode_targets_are_blocked(tmp_path):
    (tmp_path / "abc_003.mp4").touch()
    (tmp_path / "xyz_003.mp4").touch()
    scan = scan_folder(tmp_path)
    assert scan.count("conflict") == 2


def test_target_becomes_blocked_if_source_is_blocked(tmp_path):
    # Existing target is already correct, so a second filename must not overwrite it.
    (tmp_path / "ANI_ROTA_001_4K.mp4").touch()
    (tmp_path / "other_001.mp4").touch()
    assert scan_folder(tmp_path).count("conflict") == 1


def test_undo_failure_keeps_history(tmp_path):
    (tmp_path / "file_001.mp4").write_bytes(b"1")
    pairs = apply_scan(scan_folder(tmp_path))
    history = tmp_path / "undo.json"
    save_history(pairs, history)
    (tmp_path / "file_001.mp4").write_bytes(b"new file")
    with pytest.raises(FileExistsError):
        undo_last(history)
    assert history.exists()
    assert (tmp_path / "ANI_ROTA_001_4K.mp4").read_bytes() == b"1"


def test_directory_recursion_and_file_types(tmp_path):
    sub = tmp_path / "inner"
    sub.mkdir()
    (sub / "episode_002.mkv").touch()
    (tmp_path / "episode_001.txt").touch()
    assert len(scan_folder(tmp_path).entries) == 0
    assert len(scan_folder(tmp_path, recursive=True).entries) == 1
    assert len(scan_folder(tmp_path, recursive=True, all_files=True).entries) == 2


def test_missing_range_and_export(tmp_path):
    (tmp_path / "ANKANRT001.mp4").touch()
    (tmp_path / "ANKANRT003.mp4").touch()
    scan = scan_folder(tmp_path)
    assert missing_episodes(scan.entries, 1, 4) == [2, 4]
    file = tmp_path / "preview.csv"
    export_csv(scan, file)
    with file.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["Episode", "Original file", "New file", "Status", "Details"]
    assert len(rows) == 3


def test_case_insensitive_conflicts_even_on_linux(tmp_path):
    (tmp_path / "test_004.mp4").touch()
    (tmp_path / "ani_rota_004_4k.MP4").touch()
    assert scan_folder(tmp_path).count("conflict") == 2


def test_all_locales_have_all_strings():
    from episodeflow.i18n import LABELS, TRANSLATIONS, ORDER
    assert len(LABELS) == len(TRANSLATIONS) == 16
    for code, mapping in TRANSLATIONS.items():
        assert set(mapping) == set(ORDER), code
        assert all(mapping.values())


def test_runtime_failure_rolls_back_all_sources(tmp_path, monkeypatch):
    from pathlib import Path
    (tmp_path / "part_001.mp4").write_bytes(b"one")
    (tmp_path / "part_002.mp4").write_bytes(b"two")
    plan = scan_folder(tmp_path)
    real_rename = Path.rename
    raised = {"value": False}

    def failing_once(path, target):
        if (not raised["value"] and path.name.startswith(".episodeflow-")
                and Path(target).name == "ANI_ROTA_002_4K.mp4"):
            raised["value"] = True
            raise PermissionError("simulated write failure")
        return real_rename(path, target)

    monkeypatch.setattr(Path, "rename", failing_once)
    with pytest.raises(PermissionError):
        apply_scan(plan)
    assert (tmp_path / "part_001.mp4").read_bytes() == b"one"
    assert (tmp_path / "part_002.mp4").read_bytes() == b"two"
    assert not any(p.name.startswith(".episodeflow-") for p in tmp_path.iterdir())
