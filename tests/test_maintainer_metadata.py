"""Regression checks for public maintainer credit and translations."""
from pathlib import Path
import tomllib

from episodeflow.i18n import LABELS, developer_label


ROOT = Path(__file__).resolve().parents[1]


def test_developer_credit_for_every_ui_language():
    assert len(LABELS) == 16
    assert all(developer_label(locale).strip() for locale in LABELS)
    assert developer_label('tr') == 'Geliştirici'
    assert developer_label('en') == 'Developer'
    assert developer_label('unknown') == 'Developer'


def test_profile_and_project_author_are_consistent():
    metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
    assert metadata['project']['authors'] == [{'name': 'Cuma Duran'}]
    assert metadata['project']['urls']['Developer'] == 'https://github.com/cumaduran'
    ui_source = (ROOT / 'src/episodeflow/ui.py').read_text(encoding='utf-8')
    assert 'DEVELOPER_PROFILE = "https://github.com/cumaduran"' in ui_source
    assert 'QDesktopServices.openUrl(QUrl(DEVELOPER_PROFILE))' in ui_source
    assert 'self.developer_btn.clicked.connect(self.open_developer_profile)' in ui_source
