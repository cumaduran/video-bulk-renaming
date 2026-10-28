"""Modern, translated, accessible Qt desktop UI for EpisodeFlow."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QSettings, QUrl
from PySide6.QtGui import QColor, QBrush, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QScrollArea, QSizePolicy, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QHeaderView, QAbstractItemView
)
from .core import (DEFAULT_TEMPLATE, Scan, scan_folder, missing_episodes,
                   export_csv, apply_scan, save_history, undo_last, history_file)
from .i18n import LABELS, developer_label, translate


DEVELOPER_PROFILE = "https://github.com/cumaduran"
DEVELOPER_HANDLE = "@cumaduran"


def resource_path(name: str) -> Path:
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS) / name
    return Path(__file__).resolve().parents[2] / name


DARK = """
QWidget { background: #0b1120; color: #e9f1ff; font-family: 'Segoe UI', 'Noto Sans', sans-serif; font-size: 13px; }
QFrame#surface, QFrame#stat, QFrame#side { background: #131e31; border: 1px solid #26364d; border-radius: 17px; }
QFrame#topbar { background: transparent; }
QLabel[role='title'] { font-size: 24px; font-weight: 800; color: #ffffff; }
QLabel[role='subtitle'] { font-size: 13px; color: #91a4c1; }
QLabel[role='label'] { color: #c7d4e8; font-size: 12px; font-weight: 700; }
QLabel[role='metric'] { font-size: 29px; color: #f1f8ff; font-weight: 800; }
QLabel[role='muted'] { color: #94a9c4; font-size: 12px; }
QLabel[role='accent'] { color: #53e6d1; font-size: 12px; font-weight: 700; }
QLabel#pill { background: #153a43; border-radius: 11px; padding: 7px 13px; color: #64e8d7; font-size: 11px; font-weight: 700; }
QLineEdit, QSpinBox, QComboBox { background: #0e1728; color: #eaf2ff; border: 1px solid #334763; padding: 10px 12px; border-radius: 10px; selection-background-color: #087c88; min-height: 19px; }
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid #46e1cf; }
QLineEdit:disabled, QComboBox:disabled { color: #8292a7; }
QComboBox QAbstractItemView { background: #18253a; color: #ecf2ff; selection-background-color: #197b82; border: 1px solid #334763; padding: 5px; }
QPushButton { background: #24364e; border: 1px solid #334d66; border-radius: 10px; padding: 11px 13px; font-weight: 700; color: #eaf2ff; min-height: 18px; }
QPushButton:hover { background: #304a66; border-color: #57dcd1; }
QPushButton#developerProfile { background: transparent; color: #64e8d7; border: 1px solid #285e66; padding: 6px 12px; min-height: 16px; }
QPushButton#developerProfile:hover { background: #153a43; border-color: #53e6d1; }
QPushButton:disabled { background: #1d2939; color: #677a93; border-color: #2b3b50; }
QPushButton[variant='primary'] { background: #30d6c5; border-color: #30d6c5; color: #062e34; }
QPushButton[variant='primary']:hover { background: #75f7e8; border-color: #75f7e8; }
QPushButton[variant='primary']:disabled { background: #286264; color: #7caaac; border-color: #286264; }
QPushButton[variant='outline'] { background: #12333c; border: 1px solid #29666a; color: #64f1e1; }
QCheckBox { spacing: 9px; color: #d0dcef; }
QCheckBox::indicator { width: 17px; height: 17px; border: 1px solid #506580; border-radius: 5px; background: #0c1626; }
QCheckBox::indicator:checked { background: #22bfaf; border-color: #22bfaf; }
QTableWidget { background: #131e31; color: #dbe7fa; border: none; gridline-color: transparent; selection-background-color: #203d50; alternate-background-color: #162338; }
QTableWidget::item { padding: 9px 6px; border-bottom: 1px solid #223148; }
QHeaderView::section { background: #18263b; border: none; border-bottom: 1px solid #354761; color: #93aacc; font-size: 11px; padding: 12px 7px; font-weight: 800; }
QScrollBar:vertical { background: #0e1728; width: 9px; border: none; }
QScrollBar::handle:vertical { background: #39506c; border-radius: 4px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QStatusBar { background: #0b1120; color: #8da1be; border-top: 1px solid #24354e; }
QToolTip { background: #20334c; color: white; border: 1px solid #355c72; padding: 8px; }
"""

LIGHT = """
QWidget { background: #f2f6fc; color: #17283d; font-family: 'Segoe UI', 'Noto Sans', sans-serif; font-size: 13px; }
QFrame#surface, QFrame#stat, QFrame#side { background: #ffffff; border: 1px solid #d9e4ef; border-radius: 17px; }
QFrame#topbar { background: transparent; }
QLabel[role='title'] { font-size: 24px; font-weight: 800; color: #192b43; }
QLabel[role='subtitle'] { font-size: 13px; color: #677e98; }
QLabel[role='label'] { color: #485c75; font-size: 12px; font-weight: 700; }
QLabel[role='metric'] { font-size: 29px; color: #1a3551; font-weight: 800; }
QLabel[role='muted'] { color: #73849b; font-size: 12px; }
QLabel[role='accent'] { color: #057f79; font-size: 12px; font-weight: 700; }
QLabel#pill { background: #dff7f1; border-radius: 11px; padding: 7px 13px; color: #067c71; font-size: 11px; font-weight: 700; }
QLineEdit, QSpinBox, QComboBox { background: #f7f9fd; color: #1d3046; border: 1px solid #c8d6e5; padding: 10px 12px; border-radius: 10px; selection-background-color: #8adcd2; min-height: 19px; }
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid #119b94; }
QComboBox QAbstractItemView { background: white; color: #25394e; selection-background-color: #b5ece3; border: 1px solid #d5dfeb; padding: 5px; }
QPushButton { background: #e7eef6; border: 1px solid #d1dfea; border-radius: 10px; padding: 11px 13px; font-weight: 700; color: #25405e; min-height: 18px; }
QPushButton:hover { background: #d8eaf2; border-color: #33b3aa; }
QPushButton#developerProfile { background: transparent; color: #087d75; border: 1px solid #9edbd2; padding: 6px 12px; min-height: 16px; }
QPushButton#developerProfile:hover { background: #e3f6f3; border-color: #0dafa4; }
QPushButton:disabled { color: #9caabb; background: #f0f4f7; }
QPushButton[variant='primary'] { background: #0dafa4; color: #ffffff; border-color: #0dafa4; }
QPushButton[variant='primary']:hover { background: #078d87; border-color: #078d87; }
QPushButton[variant='primary']:disabled { background: #a7d9d5; border-color: #a7d9d5; }
QPushButton[variant='outline'] { background: #e3f6f3; color: #087d75; border-color: #9edbd2; }
QCheckBox { spacing: 9px; color: #425873; }
QCheckBox::indicator { width: 17px; height: 17px; border: 1px solid #9aaec4; border-radius: 5px; background: #ffffff; }
QCheckBox::indicator:checked { background: #1aafa6; border-color: #1aafa6; }
QTableWidget { background: #ffffff; color: #1f374d; border: none; gridline-color: transparent; selection-background-color: #c3f0eb; alternate-background-color: #f6f9fd; }
QTableWidget::item { padding: 9px 6px; border-bottom: 1px solid #e5ebf2; }
QHeaderView::section { background: #f0f5fa; border: none; border-bottom: 1px solid #dae5ef; color: #5f7994; font-size: 11px; padding: 12px 7px; font-weight: 800; }
QScrollBar:vertical { background: #eff3f8; width: 9px; border: none; }
QScrollBar::handle:vertical { background: #bbcadb; border-radius: 4px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QStatusBar { background: #f2f6fc; color: #73849b; border-top: 1px solid #dbe6f0; }
"""


def text_label(role: str, text: str = "") -> QLabel:
    label = QLabel(text)
    label.setProperty("role", role)
    return label


def make_button(variant: str = "", text: str = "") -> QPushButton:
    button = QPushButton(text)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    if variant:
        button.setProperty("variant", variant)
    return button


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prefs = QSettings("EpisodeFlow", "EpisodeFlow")
        self.lang = str(self.prefs.value("language", "tr"))
        if self.lang not in LABELS:
            self.lang = "tr"
        self.dark = str(self.prefs.value("dark", "true")).lower() != "false"
        self.scan_result: Scan | None = None
        self.setWindowTitle("EpisodeFlow — Episode Batch Renamer")
        self.resize(1280, 810)
        self.setMinimumSize(1040, 660)
        self.setAcceptDrops(True)
        self.setWindowIcon(QIcon(str(resource_path("assets/episodeflow.ico"))))
        self._build_ui()
        self.apply_theme()
        self.retranslate()
        self._refresh_undo()
        self.statusBar().showMessage(self.t("welcome"))

    def t(self, key: str, **kwargs) -> str:
        return translate(self.lang, key, **kwargs)

    def _build_ui(self):
        shell = QWidget()
        self.setCentralWidget(shell)
        root = QVBoxLayout(shell)
        root.setContentsMargins(26, 22, 26, 16)
        root.setSpacing(18)

        header = QFrame()
        header.setObjectName("topbar")
        h = QHBoxLayout(header)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(14)
        brand = QLabel()
        pix = QPixmap(str(resource_path("assets/episodeflow-logo.png")))
        brand.setPixmap(pix.scaled(62, 62, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        brand.setFixedSize(66, 66)
        h.addWidget(brand)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(4)
        self.brand_title = text_label("title", "EpisodeFlow")
        self.brand_subtitle = text_label("subtitle")
        brand_text.addWidget(self.brand_title)
        brand_text.addWidget(self.brand_subtitle)
        h.addLayout(brand_text)
        h.addStretch(1)
        self.offline = QLabel()
        self.offline.setObjectName("pill")
        h.addWidget(self.offline)
        self.language_select = QComboBox()
        self.language_select.setAccessibleName("Language")
        self.language_select.setMinimumWidth(164)
        for code, label in LABELS.items():
            self.language_select.addItem(label, code)
        self.language_select.setCurrentIndex(max(0, self.language_select.findData(self.lang)))
        self.language_select.currentIndexChanged.connect(self.change_language)
        h.addWidget(self.language_select)
        self.theme_btn = make_button()
        self.theme_btn.setFixedWidth(52)
        self.theme_btn.clicked.connect(self.toggle_theme)
        h.addWidget(self.theme_btn)
        self.help_btn = make_button(text="?")
        self.help_btn.setFixedWidth(45)
        self.help_btn.clicked.connect(self.show_help)
        h.addWidget(self.help_btn)
        root.addWidget(header)

        main = QHBoxLayout()
        main.setSpacing(18)
        root.addLayout(main, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedWidth(372)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        side = QFrame()
        side.setObjectName("side")
        side.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        scroll.setWidget(side)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(20, 22, 20, 22)
        sl.setSpacing(12)
        main.addWidget(scroll)

        self.folder_label = text_label("label")
        sl.addWidget(self.folder_label)
        folderrow = QHBoxLayout()
        folderrow.setSpacing(7)
        self.folder_edit = QLineEdit(str(self.prefs.value("folder", "")))
        self.folder_edit.setClearButtonEnabled(True)
        self.folder_edit.textChanged.connect(self.invalidate)
        folderrow.addWidget(self.folder_edit, 1)
        self.browse_btn = make_button()
        self.browse_btn.clicked.connect(self.choose_folder)
        folderrow.addWidget(self.browse_btn)
        sl.addLayout(folderrow)
        self.folder_hint = text_label("muted")
        self.folder_hint.setWordWrap(True)
        sl.addWidget(self.folder_hint)
        sl.addSpacing(7)
        self.pattern_label = text_label("label")
        sl.addWidget(self.pattern_label)
        self.pattern_edit = QLineEdit(str(self.prefs.value("pattern", DEFAULT_TEMPLATE)))
        self.pattern_edit.setClearButtonEnabled(True)
        self.pattern_edit.textChanged.connect(self.invalidate)
        sl.addWidget(self.pattern_edit)
        self.pattern_hint = text_label("muted")
        self.pattern_hint.setWordWrap(True)
        sl.addWidget(self.pattern_hint)
        sl.addSpacing(5)

        opt = QGridLayout()
        opt.setHorizontalSpacing(12)
        opt.setVerticalSpacing(5)
        self.digits_label = text_label("label")
        self.min_label = text_label("label")
        self.max_label = text_label("label")
        opt.addWidget(self.digits_label, 0, 0)
        opt.addWidget(self.min_label, 0, 1)
        opt.addWidget(self.max_label, 0, 2)
        self.digits_spin = QSpinBox()
        self.digits_spin.setRange(1, 8)
        self.digits_spin.setValue(int(self.prefs.value("digits", 3)))
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 9999)
        self.min_spin.setValue(int(self.prefs.value("min", 1)))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(0, 9999)
        self.max_spin.setValue(int(self.prefs.value("max", 220)))
        for idx, w in enumerate((self.digits_spin, self.min_spin, self.max_spin)):
            opt.addWidget(w, 1, idx)
            w.valueChanged.connect(self.invalidate)
        sl.addLayout(opt)
        sl.addSpacing(6)
        self.recursive_box = QCheckBox()
        self.recursive_box.setChecked(str(self.prefs.value("recursive", "false")).lower() == "true")
        self.recursive_box.toggled.connect(self.invalidate)
        sl.addWidget(self.recursive_box)
        self.allfiles_box = QCheckBox()
        self.allfiles_box.setChecked(str(self.prefs.value("allfiles", "false")).lower() == "true")
        self.allfiles_box.toggled.connect(self.invalidate)
        sl.addWidget(self.allfiles_box)
        sl.addSpacing(12)
        self.scan_btn = make_button("primary")
        self.scan_btn.clicked.connect(self.preview)
        sl.addWidget(self.scan_btn)
        self.rename_btn = make_button("outline")
        self.rename_btn.clicked.connect(self.execute)
        sl.addWidget(self.rename_btn)
        self.undo_btn = make_button()
        self.undo_btn.clicked.connect(self.undo)
        sl.addWidget(self.undo_btn)
        self.export_btn = make_button()
        self.export_btn.clicked.connect(self.export)
        sl.addWidget(self.export_btn)
        sl.addStretch(1)
        self.help_label = text_label("muted")
        self.help_label.setWordWrap(True)
        sl.addWidget(self.help_label)

        right = QVBoxLayout()
        right.setSpacing(14)
        main.addLayout(right, 1)
        stats = QHBoxLayout()
        stats.setSpacing(10)
        self.stat_widgets = []
        for _ in range(4):
            sf = QFrame()
            sf.setObjectName("stat")
            sf.setMinimumHeight(90)
            sv = QVBoxLayout(sf)
            sv.setContentsMargins(15, 12, 15, 12)
            sv.setSpacing(5)
            val = text_label("metric", "0")
            txt = text_label("muted")
            sv.addWidget(val)
            sv.addWidget(txt)
            stats.addWidget(sf, 1)
            self.stat_widgets.append((val, txt))
        right.addLayout(stats)

        previewframe = QFrame()
        previewframe.setObjectName("surface")
        pv = QVBoxLayout(previewframe)
        pv.setContentsMargins(15, 16, 15, 16)
        pv.setSpacing(12)
        previewtoolbar = QHBoxLayout()
        self.preview_title = text_label("label")
        previewtoolbar.addWidget(self.preview_title)
        previewtoolbar.addStretch(1)
        self.search = QLineEdit()
        self.search.setMinimumWidth(180)
        self.search.setMaximumWidth(320)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.filter_rows)
        previewtoolbar.addWidget(self.search)
        pv.addLayout(previewtoolbar)
        self.table = QTableWidget(0, 4)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(False)
        self.table.setColumnWidth(0, 72)
        self.table.setColumnWidth(3, 148)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(43)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        pv.addWidget(self.table, 1)
        self.missing = text_label("accent")
        self.missing.setWordWrap(True)
        pv.addWidget(self.missing)
        right.addWidget(previewframe, 1)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(12)
        self.footer = text_label("muted")
        self.footer.setWordWrap(True)
        footer_row.addWidget(self.footer, 1)
        self.developer_label = text_label("muted")
        footer_row.addWidget(self.developer_label)
        self.developer_btn = make_button(text=f"↗  {DEVELOPER_HANDLE}")
        self.developer_btn.setObjectName("developerProfile")
        self.developer_btn.setToolTip(DEVELOPER_PROFILE)
        self.developer_btn.setAccessibleName("GitHub: " + DEVELOPER_HANDLE)
        self.developer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.developer_btn.clicked.connect(self.open_developer_profile)
        footer_row.addWidget(self.developer_btn)
        root.addLayout(footer_row)
        self._update_stats()

    def retranslate(self):
        self.brand_subtitle.setText(self.t("subtitle"))
        self.offline.setText(self.t("offline"))
        self.folder_label.setText(self.t("folder"))
        self.folder_edit.setPlaceholderText(self.t("folder_hint"))
        self.folder_hint.setText(self.t("folder_hint"))
        self.browse_btn.setText(self.t("browse"))
        self.pattern_label.setText(self.t("pattern"))
        self.pattern_hint.setText(self.t("pattern_hint"))
        self.digits_label.setText(self.t("digits"))
        self.min_label.setText(self.t("range_start"))
        self.max_label.setText(self.t("range_end"))
        self.recursive_box.setText(self.t("recursive"))
        self.allfiles_box.setText(self.t("all_files"))
        self.scan_btn.setText("✦  " + self.t("scan"))
        self.rename_btn.setText("✓  " + self.t("rename"))
        self.undo_btn.setText("↶  " + self.t("undo"))
        self.export_btn.setText("↧  " + self.t("export"))
        self.search.setPlaceholderText(self.t("filter"))
        self.preview_title.setText(self.t("scan"))
        self.footer.setText(self.t("footer"))
        self.developer_label.setText(developer_label(self.lang) + ":")
        self.help_label.setText(self.t("help_text"))
        self.help_btn.setToolTip(self.t("help"))
        self.theme_btn.setToolTip(self.t("theme_light") if self.dark else self.t("theme_dark"))
        self.theme_btn.setText("☀" if self.dark else "☾")
        self.table.setHorizontalHeaderLabels([self.t("episode"), self.t("original"), self.t("new"), self.t("status")])
        for (_, label), key in zip(self.stat_widgets, ("total", "ready", "skipped", "issues")):
            label.setText(self.t(key))
        self._fill_table()
        self._refresh_undo()
        self._update_stats()

    def change_language(self):
        code = self.language_select.currentData()
        if code and code != self.lang:
            self.lang = code
            self.prefs.setValue("language", self.lang)
            self.retranslate()
            # Layout is kept left-to-right to avoid filename columns changing order.

    def apply_theme(self):
        QApplication.instance().setStyleSheet(DARK if self.dark else LIGHT)
        self.theme_btn.setText("☀" if self.dark else "☾")
        self.theme_btn.setToolTip(self.t("theme_light") if self.dark else self.t("theme_dark"))

    def toggle_theme(self):
        self.dark = not self.dark
        self.prefs.setValue("dark", self.dark)
        self.apply_theme()
        self._fill_table()

    def choose_folder(self):
        start = self.folder_edit.text().strip() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, self.t("choose_folder"), start)
        if folder:
            self.folder_edit.setText(folder)

    def invalidate(self):
        if self.scan_result is not None:
            self.scan_result = None
            self.table.setRowCount(0)
            self.missing.setText("")
            self._update_stats()
        self.rename_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

    def _save_preferences(self):
        for key, value in {
            "folder": self.folder_edit.text(), "pattern": self.pattern_edit.text(),
            "digits": self.digits_spin.value(), "min": self.min_spin.value(),
            "max": self.max_spin.value(), "recursive": self.recursive_box.isChecked(),
            "allfiles": self.allfiles_box.isChecked(),
        }.items():
            self.prefs.setValue(key, value)

    def preview(self):
        folder = self.folder_edit.text().strip().strip('"')
        if not folder:
            QMessageBox.warning(self, self.t("error_title"), self.t("folder_required"))
            return
        self._save_preferences()
        try:
            self.scan_result = scan_folder(
                folder, self.pattern_edit.text(), digits=self.digits_spin.value(),
                minimum=self.min_spin.value(), maximum=self.max_spin.value(),
                recursive=self.recursive_box.isChecked(), all_files=self.allfiles_box.isChecked())
        except (ValueError, OSError) as exc:
            self.invalidate()
            QMessageBox.warning(self, self.t("error_title"), str(exc))
            return
        self._fill_table()
        self._update_stats()
        self.rename_btn.setEnabled(bool(self.scan_result.ready))
        self.export_btn.setEnabled(bool(self.scan_result.entries))
        self.statusBar().showMessage(self.t("scan_ready", count=len(self.scan_result.entries)))

    def _status_text(self, status: str) -> str:
        return self.t(status if status in ("ready", "unknown", "ambiguous", "conflict", "unchanged") else "issues")

    def _fill_table(self):
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(0)
        if self.scan_result:
            rows = self.scan_result.entries
            self.table.setRowCount(len(rows))
            color = {"ready": "#37cdb8" if self.dark else "#078b80",
                     "unchanged": "#89a6c8" if self.dark else "#576d87",
                     "conflict": "#ff8b90" if self.dark else "#cf4254",
                     "unknown": "#ffbf75" if self.dark else "#a66b23",
                     "ambiguous": "#ffbf75" if self.dark else "#a66b23"}
            for i, e in enumerate(rows):
                columns = [str(e.episode).zfill(self.digits_spin.value()) if e.episode is not None else "—",
                           e.source.name, e.target.name if e.target else "—", self._status_text(e.status)]
                for col, value in enumerate(columns):
                    cell = QTableWidgetItem(value)
                    cell.setToolTip(e.detail or (str(e.target) if e.target else str(e.source)))
                    if col == 0:
                        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if col == 3:
                        cell.setForeground(QBrush(QColor(color.get(e.status, "#b8cad9"))))
                    self.table.setItem(i, col, cell)
        self.table.setUpdatesEnabled(True)
        self.filter_rows()

    def filter_rows(self):
        phrase = self.search.text().strip().casefold()
        for i in range(self.table.rowCount()):
            pieces = [self.table.item(i, j).text().casefold() for j in range(4) if self.table.item(i, j)]
            self.table.setRowHidden(i, phrase not in " ".join(pieces))

    def _update_stats(self):
        entries = self.scan_result.entries if self.scan_result else ()
        total = len(entries)
        ready = sum(e.status == "ready" for e in entries)
        skipped = sum(e.status in ("unknown", "ambiguous", "unchanged") for e in entries)
        issues = sum(e.status == "conflict" for e in entries)
        for (value, _), number in zip(self.stat_widgets, (total, ready, skipped, issues)):
            value.setText(str(number))
        if self.scan_result and entries:
            missing = missing_episodes(entries, self.min_spin.value(), self.max_spin.value())
            if missing:
                if len(missing) > 25:
                    display = ", ".join(map(str, missing[:25])) + f" … (+{len(missing) - 25})"
                else:
                    display = ", ".join(map(str, missing))
                self.missing.setText(self.t("missing_count", list=display))
            else:
                self.missing.setText(self.t("missing_none"))
        else:
            self.missing.setText("")

    def execute(self):
        if not self.scan_result or not self.scan_result.ready:
            QMessageBox.information(self, self.t("error_title"), self.t("nothing_ready"))
            return
        count = len(self.scan_result.ready)
        answer = QMessageBox.question(self, self.t("confirm_title"), self.t("confirm_body", count=count),
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            pairs = apply_scan(self.scan_result)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, self.t("error_title"), str(exc))
            self.preview()
            return
        try:
            save_history(pairs)
        except OSError as exc:
            QMessageBox.warning(self, self.t("error_title"), f"Renamed, but undo history could not be saved: {exc}")
        QMessageBox.information(self, self.t("done_title"), self.t("rename_done", count=len(pairs)))
        self._refresh_undo()
        self.preview()
        self.statusBar().showMessage(self.t("renamed_notice"))

    def _refresh_undo(self):
        self.undo_btn.setEnabled(history_file().exists())

    def undo(self):
        if not history_file().exists():
            QMessageBox.information(self, self.t("error_title"), self.t("undo_missing"))
            return
        answer = QMessageBox.question(self, self.t("confirm_title"), self.t("undo") + "?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            count = undo_last()
        except (OSError, ValueError, KeyError) as exc:
            QMessageBox.critical(self, self.t("error_title"), str(exc))
            return
        QMessageBox.information(self, self.t("done_title"), self.t("undo_done", count=count))
        self._refresh_undo()
        self.preview()

    def export(self):
        if not self.scan_result or not self.scan_result.entries:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, self.t("export"),
                                                   str(Path.home() / "EpisodeFlow-preview.csv"), "CSV (*.csv)")
        if not file_path:
            return
        try:
            export_csv(self.scan_result, file_path)
        except OSError as exc:
            QMessageBox.critical(self, self.t("error_title"), str(exc))
            return
        self.statusBar().showMessage(self.t("csv_saved"))

    def open_developer_profile(self):
        """Open the developer's profile only when the user clicks the footer link."""
        QDesktopServices.openUrl(QUrl(DEVELOPER_PROFILE))

    def show_help(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle(self.t("about"))
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setText(self.t("about_text") + "\n\n" + self.t("help_text"))
        dialog.setInformativeText(
            f'{developer_label(self.lang)}: '
            f'<a href="{DEVELOPER_PROFILE}">{DEVELOPER_HANDLE}</a>'
        )
        dialog.setTextFormat(Qt.TextFormat.RichText)
        dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        profile_button = dialog.addButton(f"↗ GitHub {DEVELOPER_HANDLE}", QMessageBox.ButtonRole.ActionRole)
        profile_button.clicked.connect(self.open_developer_profile)
        dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(Path(u.toLocalFile()).is_dir() for u in event.mimeData().urls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            folder = Path(url.toLocalFile())
            if folder.is_dir():
                self.folder_edit.setText(str(folder))
                self.preview()
                event.acceptProposedAction()
                return
