"""Regression for the 161 real-world filenames supplied by the project requester."""
from pathlib import Path
from episodeflow.core import episode_number


def test_real_world_name_patterns():
    sample = Path(__file__).resolve().parents[1] / "examples" / "sample_filenames.txt"
    names = [line.strip() for line in sample.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(names) == 161
    extracted = []
    for name in names:
        result, reason = episode_number(Path(name).stem)
        assert reason == "", (name, reason)
        extracted.append(result)
    assert len(set(extracted)) == 161
    assert sorted(set(range(1, 162)) - set(extracted)) == [41, 43, 144, 157]


def test_real_world_161_files_bulk_rename_and_undo(tmp_path):
    from episodeflow.core import scan_folder, apply_scan, save_history, undo_last
    sample = Path(__file__).resolve().parents[1] / "examples" / "sample_filenames.txt"
    names = [name for name in sample.read_text(encoding="utf-8").splitlines() if name]
    for i, name in enumerate(names):
        (tmp_path / name).write_bytes(str(i).encode("ascii"))
    batch = scan_folder(tmp_path)
    assert len(batch.entries) == len(batch.ready) == 161
    pairs = apply_scan(batch)
    assert len(pairs) == 161
    assert all((tmp_path / f"ANI_ROTA_{n:03d}_4K.mp4").exists() for n in
               range(1, 162) if n not in (41, 43, 144, 157))
    journal = tmp_path / "journal.json"
    save_history(pairs, journal)
    assert undo_last(journal) == 161
    assert all((tmp_path / name).exists() for name in names)
