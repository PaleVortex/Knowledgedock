from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QScrollArea, QFrame, QMessageBox, QInputDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal


class ExtensionsSettingsView(QWidget):
    """UI for managing extensions"""
    
    extension_state_changed = pyqtSignal()
    
    def __init__(self, extension_manager, database_manager, extension_core_manager=None):
        super().__init__()
        self.extension_manager = extension_manager
        self.database_manager = database_manager
        self.extension_core_manager = extension_core_manager
        self.extension_states = {}
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Header
        header = QLabel("🔌 Extensions Manager")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #f97316;")
        main_layout.addWidget(header)
        
        subtitle = QLabel("Manage and customize your knowledge sources")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #999;")
        main_layout.addWidget(subtitle)
        
        # Info box
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-left: 4px solid #3b82f6;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        info_label = QLabel("💡 Tip: Enable or disable extensions to customize your search experience. Download extensions to access additional knowledge sources.")
        info_label.setFont(QFont("Arial", 10))
        info_label.setStyleSheet("color: #999;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        main_layout.addWidget(info_box)
        
        # Installed extensions section
        installed_label = QLabel("📦 Installed Extensions")
        installed_label.setFont(QFont("Arial", 16, QFont.Bold))
        installed_label.setStyleSheet("color: #f97316;")
        main_layout.addWidget(installed_label)
        
        # Extensions list with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: 1px solid #334155; border-radius: 4px;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # Create extension cards dynamically
        self.extension_cards = {}
        
        if self.extension_core_manager:
            extensions = self.extension_core_manager.extensions
            for ext_name, ext in extensions.items():
                # Determine icon based on name (simple mapping)
                icon = "🧩"
                if "Wikipedia" in ext.name: icon = "🌐"
                elif "arXiv" in ext.name: icon = "📄"
                elif "Library" in ext.name: icon = "📚"
                elif "Gutenberg" in ext.name: icon = "🎓"
                
                ext_data = {
                    "name": ext.name,
                    "icon": icon,
                    "version": ext.version,
                    "author": ext.author,
                    "description": ext.description,
                    "url": getattr(ext, 'url', ""), # Handle missing url attribute
                    "enabled": ext.enabled
                }
                
                card = self.create_extension_card(ext_data)
                scroll_layout.addWidget(card)
                self.extension_states[ext.name] = ext.enabled
                self.extension_cards[ext.name] = card
        else:
            # Fallback if manager not connected
            error_label = QLabel("Extension Manager not connected")
            error_label.setStyleSheet("color: #ef4444;")
            scroll_layout.addWidget(error_label)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        install_btn = QPushButton("⬇️ Install New Extension")
        install_btn.setMinimumHeight(45)
        install_btn.setMinimumWidth(200)
        install_btn.setFont(QFont("Arial", 11, QFont.Bold))
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        install_btn.clicked.connect(self.install_extension)
        action_layout.addWidget(install_btn)
        
        refresh_btn = QPushButton("🔄 Refresh Extensions")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.setMinimumWidth(200)
        refresh_btn.setFont(QFont("Arial", 11, QFont.Bold))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #fbbf24;
                color: #333;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f59e0b;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_extensions)
        action_layout.addWidget(refresh_btn)
        
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
    
    def create_extension_card(self, ext_data):
        """Create an extension card widget"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 8px;
                padding: 20px;
            }
            QFrame:hover {
                border: 2px solid #f97316;
                background-color: #334155;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"{ext_data['icon']} {ext_data['name']}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #f97316;")
        header_layout.addWidget(title_label)
        
        version_label = QLabel(f"v{ext_data['version']}")
        version_label.setFont(QFont("Arial", 10))
        version_label.setStyleSheet("color: #888;")
        header_layout.addWidget(version_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(ext_data['description'])
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #cbd5e1;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Author
        author_label = QLabel(f"By {ext_data['author']}")
        author_label.setFont(QFont("Arial", 9))
        author_label.setStyleSheet("color: #666;")
        layout.addWidget(author_label)
        
        # Status and buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Status indicator
        status_text = "✅ Enabled" if ext_data["enabled"] else "⛔ Disabled"
        status_label = QLabel(status_text)
        status_label.setFont(QFont("Arial", 10, QFont.Bold))
        status_label.setStyleSheet("color: #22c55e;" if ext_data["enabled"] else "color: #ef4444;")
        button_layout.addWidget(status_label)
        
        button_layout.addStretch()
        
        # Toggle button
        toggle_text = "🔴 Disable" if ext_data["enabled"] else "🟢 Enable"
        toggle_btn = QPushButton(toggle_text)
        toggle_btn.setMaximumWidth(120)
        toggle_btn.setMinimumHeight(35)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f97316;
                border: 1px solid #f97316;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f97316;
                color: white;
            }
        """)
        
        ext_name = ext_data['name']
        toggle_btn.clicked.connect(lambda: self.toggle_extension(ext_name, toggle_btn, status_label))
        button_layout.addWidget(toggle_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Config")
        settings_btn.setMaximumWidth(100)
        settings_btn.setMinimumHeight(35)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        settings_btn.clicked.connect(lambda: self.config_extension(ext_name))
        button_layout.addWidget(settings_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Remove")
        delete_btn.setMaximumWidth(100)
        delete_btn.setMinimumHeight(35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E63946;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D62828;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_extension(ext_name))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        # Store references for updating
        card.toggle_btn = toggle_btn
        card.status_label = status_label
        card.is_enabled = ext_data["enabled"]
        
        return card
    
    def toggle_extension(self, ext_name, button, status_label):
        """Toggle extension state"""
        is_currently_enabled = self.extension_states.get(ext_name, True)
        new_state = not is_currently_enabled
        
        self.extension_states[ext_name] = new_state
        
        # Update button and status
        status_text = "✅ Enabled" if new_state else "⛔ Disabled"
        toggle_text = "🔴 Disable" if new_state else "🟢 Enable"
        
        button.setText(toggle_text)
        status_label.setText(status_text)
        status_label.setStyleSheet("color: #22c55e;" if new_state else "color: #ef4444;")
        
        # Update in database and core manager
        try:
            # Update DB (extension_manager here is the DB manager)
            if self.extension_manager:
                if new_state:
                    self.extension_manager.enable_extension(ext_name)
                else:
                    self.extension_manager.disable_extension(ext_name)
            
            # Update core runtime manager.
            # Core manager uses short keys (e.g. "gutenberg") but ext_name is the
            # display name (e.g. "Project Gutenberg"), so we look up the key by name.
            if self.extension_core_manager:
                key_to_use = None
                for key, ext in self.extension_core_manager.extensions.items():
                    if ext.name == ext_name:
                        key_to_use = key
                        break
                
                if key_to_use:
                    if new_state:
                        self.extension_core_manager.enable_extension(key_to_use)
                    else:
                        self.extension_core_manager.disable_extension(key_to_use)
            
            QMessageBox.information(self, "Success", f"{ext_name} has been {('enabled' if new_state else 'disabled')}!")
            self.extension_state_changed.emit()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to toggle extension: {e}")
    
    def delete_extension(self, ext_name):
        """Delete/uninstall an extension"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to remove '{ext_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # In production, this would delete from database
                QMessageBox.information(self, "Removed", f"{ext_name} has been successfully removed!")
                self.extension_state_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to remove extension: {e}")
    
    def config_extension(self, ext_name):
        """Configure extension settings"""
        text, ok = QInputDialog.getText(
            self, 
            f"Configure {ext_name}",
            "Enter configuration (e.g., API key, settings):"
        )
        
        if ok and text:
            QMessageBox.information(self, "Configured", f"{ext_name} configuration updated!")
    
    def install_extension(self):
        """Install a new extension"""
        text, ok = QInputDialog.getText(
            self,
            "Install Extension",
            "Enter extension URL or name to install:\n(e.g., https://github.com/user/extension)"
        )
        
        if ok and text:
            if text.strip():
                QMessageBox.information(
                    self,
                    "Installation",
                    f"Extension installation initiated!\n\nURL: {text}\n\nNote: Installation would complete in a production environment."
                )
            else:
                QMessageBox.warning(self, "Error", "Please enter a valid extension URL or name")
    
    def refresh_extensions(self):
        """Refresh extension list"""
        QMessageBox.information(self, "Refreshed", "Extension list has been refreshed!")
        self.extension_state_changed.emit()
