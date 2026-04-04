"""
word_to_pdf_dialog.py - Word to PDF Conversion Options Dialog

Provides a modal dialog for configuring Word-to-PDF conversion settings,
including formatting preservation mode, image quality, metadata options,
and a live-updating preview panel that reflects the selected mode.

Features:
    - Two conversion modes: preserve all formatting vs. text-only
    - Collapsible advanced options (image quality, compression, metadata)
    - Dynamic preview panel with dark/light theme support
    - Modern slim scrollbar styled per theme
    - Bilingual support (French / English)
    - Intelligent space management: dialog resizes when advanced panel toggles

Dependencies:
    - PySide6
    - widgets.AnimatedCheckBox (local)

Author: Hyacinthe
Version: 1.0
"""

# Standard imports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QButtonGroup, QLabel,
    QFormLayout, QComboBox, QDialogButtonBox, QTextEdit, QSizePolicy
)

# Local imports
import sys as _sys, os as _os
_PKG_DIR  = _os.path.dirname(_os.path.abspath(__file__))
_ROOT_DIR = _os.path.dirname(_PKG_DIR)
if _ROOT_DIR not in _sys.path:
    _sys.path.insert(0, _ROOT_DIR)

from widgets import AnimatedCheckBox

from translations import TranslationManager

# Constants

# Theme color tokens — dark mode
_DARK = {
    "preview_bg":    "#0d1117",
    "preview_fg":    "#c9d1d9",
    "sb_bg":         "#161b22",
    "sb_handle":     "#30363d",
    "sb_handle_hv":  "#4dabf7",
    "title_active":  "#4dabf7",
    "title_accent":  "#74c0fc",
    "title_muted":   "#6c757d",
    "bullet_active": "#c9d1d9",
    "bullet_muted":  "#495057",
}

# Theme color tokens — light mode
_LIGHT = {
    "preview_bg":    "#f8f9fa",
    "preview_fg":    "#212529",
    "sb_bg":         "#e9ecef",
    "sb_handle":     "#ced4da",
    "sb_handle_hv":  "#4dabf7",
    "title_active":  "#1971c2",
    "title_accent":  "#339af0",
    "title_muted":   "#adb5bd",
    "bullet_active": "#343a40",
    "bullet_muted":  "#ced4da",
}

# Stylesheet for the advanced QGroupBox — dark mode
_ADVANCED_GROUP_DARK = """
    QGroupBox {
        font-weight: bold;
        font-size: 16px;
        color: #6c757d;
        background-color: #1c2128;
        border: 1.5px solid #30363d;
        border-radius: 12px;
        margin-top: 16px;
        padding-top: 16px;
        margin-left: 2px;
    }
    QGroupBox:checked {
        color: #74c0fc;
        background-color: #0a1929;
        border: 1.5px solid #4dabf7;
    }
    QGroupBox:unchecked:hover {
        border: 1.5px solid #495057;
        background-color: #1e2530;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 30px;
        padding: 0 10px;
        color: #6c757d;
    }
    QGroupBox:checked::title {
        color: #74c0fc;
    }
    QGroupBox::indicator {
        width: 18px; height: 18px;
        border-radius: 9px;
        border: 2px solid #30363d;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #2d333b, stop:1 #1c2128);
        margin-right: 6px; margin-top: 3px;
    }
    QGroupBox::indicator:unchecked:hover {
        border: 2px solid #4dabf7;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #1a2d42, stop:0.6 #142236, stop:1 #0d1929);
    }
    QGroupBox::indicator:checked {
        border: 2px solid #4dabf7;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #c8e6ff, stop:0.28 #89c4f4,
            stop:0.36 #4dabf7, stop:0.60 #2980b9, stop:1 #1a5f8a);
    }
    QGroupBox::indicator:checked:hover {
        border: 2px solid #74c0fc;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #e8f4ff, stop:0.28 #a8d8ff,
            stop:0.36 #74c0fc, stop:0.60 #3a9bd5, stop:1 #1e6fa0);
    }
"""

# Stylesheet for the advanced QGroupBox — light mode
_ADVANCED_GROUP_LIGHT = """
    QGroupBox {
        font-weight: bold;
        font-size: 16px;
        color: #868e96;
        background-color: #f8f9fa;
        border: 1.5px solid #dee2e6;
        border-radius: 12px;
        margin-top: 16px;
        padding-top: 16px;
        margin-left: 2px;
    }
    QGroupBox:checked {
        color: #1971c2;
        background-color: #e8f4fd;
        border: 1.5px solid #4dabf7;
    }
    QGroupBox:unchecked:hover {
        border: 1.5px solid #adb5bd;
        background-color: #f1f3f5;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 30px;
        padding: 0 10px;
        color: #868e96;
    }
    QGroupBox:checked::title {
        color: #1971c2;
    }
    QGroupBox::indicator {
        width: 18px; height: 18px;
        border-radius: 9px;
        border: 2px solid #ced4da;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #ffffff, stop:1 #f1f3f5);
        margin-right: 6px; margin-top: 3px;
    }
    QGroupBox::indicator:unchecked:hover {
        border: 2px solid #74c0fc;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #f0f8ff, stop:0.6 #dbeeff, stop:1 #c5e3f7);
    }
    QGroupBox::indicator:checked {
        border: 2px solid #4dabf7;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #ffffff, stop:0.30 #e8f4ff,
            stop:0.36 #4dabf7, stop:0.65 #2980b9, stop:1 #1a6fa3);
    }
    QGroupBox::indicator:checked:hover {
        border: 2px solid #339af0;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 #ffffff, stop:0.30 #f0f8ff,
            stop:0.36 #339af0, stop:0.65 #1a7fd4, stop:1 #0f5a9e);
    }
"""

# OK button stylesheet
_BTN_OK = """
    QPushButton {
        background-color: #28a745; color: white;
        border: none; padding: 8px 16px;
        border-radius: 6px; font-weight: bold;
    }
    QPushButton:hover   { background-color: #218838; }
    QPushButton:pressed { background-color: #1e7e34; }
"""

# Cancel button stylesheet
_BTN_CANCEL = """
    QPushButton {
        background-color: #B55454; color: white;
        border: none; padding: 8px 16px;
        border-radius: 6px; font-weight: bold;
    }
    QPushButton:hover   { background-color: #A04040; }
    QPushButton:pressed { background-color: #8B3030; }
"""

# Dialog class

class WordToPdfOptionsDialog(QDialog):
    """
    Modal dialog for Word to PDF conversion settings.

    Args:
        parent:      Parent widget (used to detect dark_mode).
        language:    UI language — "fr" (default) or "en".
        has_content: When True, displays an extra info line indicating the
                     document contains formatted content (images, tables...).
    """

    def __init__(self, parent=None, language: str = "fr", has_content: bool = False):
        super().__init__(parent)

        self.language     = language
        self.has_content  = has_content
        self._tm          = TranslationManager(); self._tm.set_language(language)
        self.is_dark_mode: bool = getattr(parent, "dark_mode", False) if parent else False

        self.setWindowTitle(self.translate_text("Options de conversion Word vers PDF"))
        self.setModal(True)
        self._setup_ui()

    # UI construction
    def _setup_ui(self) -> None:
        """Build and wire all top-level widgets into the dialog layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        layout.addWidget(self._build_mode_group())
        layout.addWidget(self._build_preview_group(), stretch=1)
        layout.addWidget(self._build_buttons())

        # Wire radio buttons to the mode-change handler
        self.preserve_all_radio.toggled.connect(self._on_mode_changed)
        self.text_only_radio.toggled.connect(self._on_mode_changed)

    def _build_mode_group(self) -> QGroupBox:
        """Create the conversion-mode section (radio buttons + advanced sub-group)."""
        group  = QGroupBox(self.translate_text("Mode de conversion"))
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        # Animated buttons
        self.mode_group = QButtonGroup(self)

        self.preserve_all_radio = AnimatedCheckBox(
            self.translate_text("✅ Conserver toute la mise en forme (recommandé)")
        )
        self.preserve_all_radio.setChecked(True)

        self.text_only_radio = AnimatedCheckBox(
            self.translate_text("📝 Texte seulement (plus rapide)")
        )

        self.mode_group.addButton(self.preserve_all_radio, 1)
        self.mode_group.addButton(self.text_only_radio,    2)

        # Optional extra info line when the document has formatted content
        info_text = self.translate_text("📋 Sélectionnez le mode de conversion :")
        if self.has_content:
            info_text += "\n" + self.translate_text(
                "ℹ️ Ce document contient du contenu formaté, images, tableaux, etc."
            )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #007acc; font-size: 12.5px; margin: 4px 0;")

        # Collapsible advanced options
        self.advanced_group = self._build_advanced_group()

        layout.addWidget(info_label)
        layout.addWidget(self.preserve_all_radio)
        layout.addWidget(self.text_only_radio)
        layout.addSpacing(6)
        layout.addWidget(self.advanced_group)

        return group

    def _build_advanced_group(self) -> QGroupBox:
        """Create the collapsible advanced-options QGroupBox (quality, compression, metadata)."""
        group = QGroupBox(self.translate_text("Options avancées"))
        group.setCheckable(True)
        group.setChecked(False)

        # Pick the right stylesheet for the current theme
        group.setStyleSheet(
            _ADVANCED_GROUP_DARK if self.is_dark_mode else _ADVANCED_GROUP_LIGHT
        )

        form = QFormLayout(group)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            self.translate_text("Haute qualité (300 DPI)"),
            self.translate_text("Qualité standard (150 DPI)"),
            self.translate_text("Optimisé (96 DPI)"),
        ])

        self.compress_checkbox = AnimatedCheckBox(self.translate_text("Compresser les images"))
        self.compress_checkbox.setChecked(True)

        self.include_metadata_checkbox = AnimatedCheckBox(self.translate_text("Inclure les métadonnées"))
        self.include_metadata_checkbox.setChecked(True)

        form.addRow(self.translate_text("Qualité d'image:"), self.quality_combo)
        form.addWidget(self.compress_checkbox)
        form.addWidget(self.include_metadata_checkbox)

        return group

    def _build_preview_group(self) -> QGroupBox:
        """Create the preview-differences section with a themed, elastic QTextEdit."""
        group = QGroupBox(self.translate_text("Aperçu des différences"))
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_text.setMinimumHeight(90)
        self.preview_text.setStyleSheet(self._build_preview_stylesheet())

        # Populate with initial HTML content
        self._update_preview_html()

        layout.addWidget(self.preview_text)
        return group

    def _build_preview_stylesheet(self) -> str:
        """Return the QTextEdit + slim scrollbar stylesheet for the current theme."""
        c = _DARK if self.is_dark_mode else _LIGHT
        return f"""
            QTextEdit {{
                background-color: {c['preview_bg']};
                color: {c['preview_fg']};
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }}
            QScrollBar:vertical {{
                background: {c['sb_bg']}; width: 8px;
                border-radius: 4px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {c['sb_handle']};
                border-radius: 4px; min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover  {{ background: {c['sb_handle_hv']}; }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical      {{ height: 0; }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical      {{ background: none; }}
            QScrollBar:horizontal {{
                background: {c['sb_bg']}; height: 8px;
                border-radius: 4px; margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {c['sb_handle']};
                border-radius: 4px; min-width: 24px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: {c['sb_handle_hv']}; }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal     {{ width: 0; }}
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal     {{ background: none; }}
        """

    def _build_buttons(self) -> QDialogButtonBox:
        """Create and style the OK / Cancel button box."""
        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        ok = box.button(QDialogButtonBox.Ok)
        if ok:
            ok.setStyleSheet(_BTN_OK)

        cancel = box.button(QDialogButtonBox.Cancel)
        if cancel:
            cancel.setStyleSheet(_BTN_CANCEL)

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        return box

    # Slots
    def _on_mode_changed(self) -> None:
        """Show/hide advanced options and refresh the preview whenever the mode switches."""
        is_preserve = self.preserve_all_radio.isChecked()

        self.advanced_group.setVisible(is_preserve)

        # Give the preview more vertical room when the advanced panel is hidden
        self.preview_text.setMinimumHeight(90 if is_preserve else 110)

        self._update_preview_html()

    # Preview rendering
    def _update_preview_html(self) -> None:
        """Rebuild the preview HTML, visually highlighting the active mode."""
        c           = _DARK if self.is_dark_mode else _LIGHT
        is_preserve = self.preserve_all_radio.isChecked()

        # Localized labels
        title_keep   = self.translate_text("Mode 'Conserver tout'")
        title_text   = self.translate_text("Mode 'Texte seulement'")

        keep_bullets = [
            self.translate_text("• Garde toutes les images, tableaux, couleurs"),
            self.translate_text("• Conserve la mise en page exacte"),
            self.translate_text("• Maintient les en-têtes et pieds de page"),
        ]
        text_bullets = [
            self.translate_text("• Extrait uniquement le texte"),
            self.translate_text("• Formatage minimal"),
            self.translate_text("• Plus rapide pour les longs documents"),
        ]

        if is_preserve:
            # "Keep all" active → highlighted; "text-only" shown in accent color
            color_keep,  color_text   = c["title_active"], c["title_accent"]
            bullets_keep, bullets_text = c["bullet_active"], c["bullet_active"]
            prefix_text = ""
        else:
            # "Text only" active → "keep all" muted, "text-only" highlighted
            color_keep,  color_text   = c["title_muted"], c["title_active"]
            bullets_keep, bullets_text = c["bullet_muted"], c["bullet_active"]
            prefix_text = "▶ "

        def _section(title: str, color: str, bullets: list, bc: str, bottom_gap: str = "10px") -> str:
            """Helper that renders one labeled bullet section."""
            rows = "".join(
                f'<p style="margin:0 0 2px 0; color:{bc};">{b}</p>'
                for b in bullets
            )
            return (
                f'<p style="margin:0 0 6px 0; color:{color}; font-weight:bold;">{title}</p>'
                f'{rows}'
                f'<p style="margin:0 0 {bottom_gap} 0;"></p>'
            )

        html = (
            _section(title_keep,                  color_keep, keep_bullets, bullets_keep)
            + _section(prefix_text + title_text,  color_text, text_bullets, bullets_text, bottom_gap="0")
        )

        self.preview_text.setHtml(html)

    # Helpers
    def translate_text(self, text: str) -> str:
        """Return the translated string for the current language, falling back to the key itself."""
        return self._tm.translate_text(text)

    # Public API
    def get_conversion_mode(self) -> dict:
        """
        Return the user's selected conversion settings.

        Returns:
            dict with keys:
                mode (str):              "preserve_all" | "text_only"
                quality (str):           currently selected quality label
                compress_images (bool):  whether image compression is enabled
                include_metadata (bool): whether metadata inclusion is enabled
        """
        return {
            "mode":             "preserve_all" if self.preserve_all_radio.isChecked() else "text_only",
            "quality":          self.quality_combo.currentText(),
            "compress_images":  self.compress_checkbox.isChecked(),
            "include_metadata": self.include_metadata_checkbox.isChecked(),
        }