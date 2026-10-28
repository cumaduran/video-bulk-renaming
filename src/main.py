"""Application entrypoint for source runs and PyInstaller."""
import sys
import tempfile
from pathlib import Path


def self_test() -> int:
    # Verify the bundled Qt UI modules can be imported as part of the smoke test.
    from episodeflow.ui import MainWindow  # noqa: F401
    from episodeflow.core import scan_folder, apply_scan, undo_last, save_history
    with tempfile.TemporaryDirectory() as location:
        root = Path(location)
        (root / "ANKANRT006_4K.mp4").write_bytes(b"sample")
        batch = scan_folder(root)
        if len(batch.ready) != 1:
            return 1
        changes = apply_scan(batch)
        journal = root / "history.json"
        save_history(changes, journal)
        if undo_last(journal) != 1:
            return 1
        return 0 if (root / "ANKANRT006_4K.mp4").read_bytes() == b"sample" else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
    from episodeflow.ui import MainWindow, resource_path
    app = QApplication(sys.argv)
    app.setApplicationName("EpisodeFlow")
    app.setOrganizationName("EpisodeFlow")
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(str(resource_path("assets/episodeflow.ico"))))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
