from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QProgressBar)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
import os
from pathlib import Path
from constants import DOWNLOADS_DIR

class DownloadsView(QWidget):
    def __init__(self, download_manager=None):
        super().__init__()
        self.download_manager = download_manager
        # Use the centralized DOWNLOADS_DIR from constants
        self.downloads_folder = DOWNLOADS_DIR
        self.downloads_folder.mkdir(exist_ok=True, parents=True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📥 Downloads")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(header)
        
        # Downloads folder location
        location_layout = QHBoxLayout()
        location_label = QLabel(f"📁 Folder: {self.downloads_folder}")
        location_label.setFont(QFont("Arial", 10))
        location_label.setStyleSheet("color: #b4bcd4;")
        location_layout.addWidget(location_label)
        
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.clicked.connect(self.open_downloads_folder)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 212, 255, 0.15);
                color: #00D4FF;
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.2);
            }
        """)
        location_layout.addWidget(open_folder_btn)
        location_layout.addStretch()
        layout.addLayout(location_layout)
        
        # Downloads list
        self.downloads_list = QListWidget()
        self.downloads_list.setSpacing(15)
        self.downloads_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: #252525;
            }
        """)
        layout.addWidget(self.downloads_list, 1)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_downloads)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 107, 107, 0.1);
                color: #FF6B6B;
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 107, 107, 0.2);
            }
        """)
        button_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_downloads)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 215, 0, 0.1);
                color: #FFD700;
                border: 1px solid rgba(255, 215, 0, 0.3);
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.2);
            }
        """)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Load downloads on init
        self.refresh_downloads()
    
    def refresh_downloads(self):
        """Refresh the downloads list"""
        self.downloads_list.clear()
        
        try:
            if not self.downloads_folder.exists():
                self.status_label.setText("Downloads folder not found")
                return
            
            # Get all files from downloads folder
            all_files = list(self.downloads_folder.glob("*"))
            
            if not all_files:
                self.status_label.setText("No downloads yet")
                return
            
            # Sort by modification time (newest first)
            files = sorted([f for f in all_files if f.is_file()], 
                          key=lambda x: x.stat().st_mtime, reverse=True)
            
            for file in files:
                item_widget = self.create_download_item(file)
                item = QListWidgetItem()
                
                # Force a larger size hint to prevent text clipping
                hint = item_widget.sizeHint()
                hint.setHeight(max(hint.height(), 90)) # Ensure at least 90px height
                item.setSizeHint(hint)
                
                self.downloads_list.addItem(item)
                self.downloads_list.setItemWidget(item, item_widget)
            
            self.status_label.setText(f"Total downloads: {len(files)}")
        
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            print(f"Error loading downloads: {e}")
    
    def create_download_item(self, file_path):
        """Create a download item widget"""
        widget = QWidget()
        widget.setMinimumHeight(85) # Ensure widget is tall enough
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # File icon and info
        info_layout = QVBoxLayout()
        
        # File name
        name_label = QLabel(f"📄 {file_path.name}")
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        name_label.setStyleSheet("color: #00D4FF;")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # File size and date
        size_mb = file_path.stat().st_size / (1024 * 1024)
        mod_time = file_path.stat().st_mtime
        import time
        time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mod_time))
        
        details_label = QLabel(f"Size: {size_mb:.2f} MB | Modified: {time_str}")
        details_label.setFont(QFont("Arial", 9))
        details_label.setStyleSheet("color: #888;")
        info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout, 1)
        
        # Action buttons
        open_btn = QPushButton("Open")
        open_btn.setMaximumWidth(80)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 212, 255, 0.15);
                color: #00D4FF;
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.2);
            }
        """)
        open_btn.clicked.connect(lambda: self.open_file(file_path))
        layout.addWidget(open_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setMaximumWidth(80)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 107, 107, 0.15);
                color: #FF6B6B;
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 107, 107, 0.2);
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_file(file_path))
        layout.addWidget(delete_btn)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 4px;
            }
        """)
        
        return widget
    
    def open_file(self, file_path):
        """Open a file with default application"""
        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")
    
    def delete_file(self, file_path):
        """Delete a downloaded file"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete:\n{file_path.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                file_path.unlink()
                self.refresh_downloads()
                QMessageBox.information(self, "Success", "File deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete file: {e}")
    
    def open_downloads_folder(self):
        """Open downloads folder in explorer"""
        try:
            os.startfile(self.downloads_folder)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {e}")
    
    def clear_downloads(self):
        """Clear all downloaded files"""
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to delete ALL downloads?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                deleted_count = 0
                for file in self.downloads_folder.glob("*"):
                    if file.is_file():
                        file.unlink()
                        deleted_count += 1
                
                self.refresh_downloads()
                QMessageBox.information(self, "Success", f"Deleted {deleted_count} files")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error clearing downloads: {e}")
