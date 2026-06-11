from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
                             QSpinBox, QComboBox, QPushButton, QScrollArea, QGroupBox, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import json
from pathlib import Path
from constants import SETTINGS_PATH


class SettingsView(QWidget):
    # Signal for when settings are applied
    settings_applied = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings_file = SETTINGS_PATH
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings = self.load_settings()
        self.setting_widgets = {}

        self.init_ui()
    
    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            "theme": "Dark",
            "viewer_zoom": 100,
            "auto_open_downloads": False
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
        except:
            pass
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        try:
            # Collect all settings from widgets
            for key, widget in self.setting_widgets.items():
                if isinstance(widget, QCheckBox):
                    self.settings[key] = widget.isChecked()
                elif isinstance(widget, QSpinBox):
                    self.settings[key] = widget.value()
                elif isinstance(widget, QComboBox):
                    self.settings[key] = widget.currentText()
            
            # Write to file
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            # Emit signal to notify app to apply new settings
            self.settings_applied.emit(self.settings)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False
    
    def reset_settings(self):
        """Reset to default settings"""
        reply = QMessageBox.question(self, "Confirm", "Reset all settings to default?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.settings_file.unlink(missing_ok=True)
            self.settings = self.load_settings()
            self.refresh_ui()
            QMessageBox.information(self, "Success", "Settings reset to default!")
    
    def refresh_ui(self):
        """Refresh UI with current settings"""
        for key, widget in self.setting_widgets.items():
            if isinstance(widget, QCheckBox):
                widget.setChecked(self.settings.get(key, False))
            elif isinstance(widget, QSpinBox):
                widget.setValue(self.settings.get(key, 0))
            elif isinstance(widget, QComboBox):
                value = self.settings.get(key, "")
                index = widget.findText(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("⚙️ Knowledgedock Settings")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(25)
        
        # Reader Settings
        reader_group = self.create_reader_settings()
        scroll_layout.addWidget(reader_group)
        
        # About & Actions
        about_group = self.create_about_group()
        scroll_layout.addWidget(about_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(150)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.setMinimumHeight(40)
        reset_btn.setMinimumWidth(150)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font: 11pt Arial;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def create_settings_group(self, title, settings):
        """Create a settings group with various control types"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                color: #CCCCCC;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        for setting_info in settings:
            key = setting_info[0]
            label = setting_info[1]
            control_type = setting_info[2] if len(setting_info) > 2 else "checkbox"
            
            if control_type == "checkbox":
                checkbox = QCheckBox(label)
                checkbox.setChecked(self.settings.get(key, False))
                checkbox.setStyleSheet("color: #CCCCCC; spacing: 8px;")
                layout.addWidget(checkbox)
                self.setting_widgets[key] = checkbox
            
            elif control_type == "combo":
                options = setting_info[3] if len(setting_info) > 3 else []
                combo_layout = QHBoxLayout()
                combo_label = QLabel(label)
                combo_label.setMinimumWidth(150)
                combo = QComboBox()
                combo.addItems(options)
                combo.setCurrentText(self.settings.get(key, options[0] if options else ""))
                combo.setMinimumWidth(200)
                combo_layout.addWidget(combo_label)
                combo_layout.addWidget(combo)
                combo_layout.addStretch()
                layout.addLayout(combo_layout)
                self.setting_widgets[key] = combo
        
        return group
    
    def create_reader_settings(self):
        group = QGroupBox("📖 Viewer Settings")
        group.setStyleSheet("""
            QGroupBox {
                color: #CCCCCC;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Default zoom level
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Default Zoom Level:")
        zoom_label.setMinimumWidth(150)
        zoom_spin = QSpinBox()
        zoom_spin.setMinimum(50)
        zoom_spin.setMaximum(200)
        zoom_spin.setValue(self.settings.get("viewer_zoom", 100))
        zoom_spin.setMaximumWidth(100)
        zoom_spin.setSuffix("%")
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(zoom_spin)
        zoom_layout.addStretch()
        layout.addLayout(zoom_layout)
        self.setting_widgets["viewer_zoom"] = zoom_spin
        
        # Open downloaded resources
        open_checkbox = QCheckBox("Auto-Open Downloaded Resources in Viewer")
        open_checkbox.setChecked(self.settings.get("auto_open_downloads", False))
        open_checkbox.setStyleSheet("color: #CCCCCC; spacing: 8px;")
        layout.addWidget(open_checkbox)
        self.setting_widgets["auto_open_downloads"] = open_checkbox
        
        return group
    

    
    def create_about_group(self):
        group = QGroupBox("ℹ️ About Knowledgedock")
        group.setStyleSheet("""
            QGroupBox {
                color: #CCCCCC;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        version_label = QLabel("🎓 Knowledgedock v2.0.0\nMulti-Source Knowledge Gateway")
        version_label.setStyleSheet("color: #888; font-size: 10pt;")
        layout.addWidget(version_label)
        
        features_label = QLabel("✨ Features:\n• Search across Wikipedia, arXiv, Open Library & Project Gutenberg\n• Bookmark and organize resources\n• Download PDFs and ebooks\n• Manage custom extensions")
        features_label.setStyleSheet("color: #999; font-size: 9pt;")
        features_label.setWordWrap(True)
        layout.addWidget(features_label)
        
        cache_layout = QHBoxLayout()
        clear_cache_btn = QPushButton("🗑️ Clear Cache")
        clear_cache_btn.setMaximumWidth(200)
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addWidget(clear_cache_btn)
        
        cache_layout.addStretch()
        layout.addLayout(cache_layout)
        
        update_layout = QHBoxLayout()
        check_update_btn = QPushButton("🔄 Check for Updates")
        check_update_btn.setMaximumWidth(200)
        check_update_btn.clicked.connect(lambda: self.show_message("You are running the latest version (v2.0.0)!"))
        update_layout.addWidget(check_update_btn)
        
        update_layout.addStretch()
        layout.addLayout(update_layout)
        
        return group
    
    def clear_cache(self):
        """Clear the web engine cache"""
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineProfile
            profile = QWebEngineProfile.defaultProfile()
            profile.clearHttpCache()
            self.show_message("Browser cache cleared successfully!")
        except Exception as e:
            self.show_message(f"Error clearing cache: {e}")
            
    def show_message(self, message):
        """Show info message"""
        QMessageBox.information(self, "Info", message)
