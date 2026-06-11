import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# helper copied from main for resource path resolution
def get_resource_path(relative_path) -> str:
    base_path: os.Any | str = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About Knowledgedock")
        self.setFixedSize(500, 450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }
            QLabel {
                color: #f1f5f9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 25)
        layout.setSpacing(20)
        
        # Cover Image Header
        cover_label = QLabel()
        cover_path: str = get_resource_path(os.path.join("assets", "cover.png"))
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            scaled_pix: QPixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
            cover_label.setPixmap(scaled_pix)
        else:
            cover_label.setText("KNOWLEDGEDOCK")
            cover_label.setAlignment(Qt.AlignCenter)
            cover_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #3b82f6; padding: 40px;")            
        layout.addWidget(cover_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 0, 30, 0)
        content_layout.setSpacing(10)
        
        title = QLabel("Knowledgedock")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3b82f6;")
        content_layout.addWidget(title)
        
        version = QLabel("Version 2.1.0 Blue")
        version.setFont(QFont("Segoe UI", 10))
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #94a3b8;")
        content_layout.addWidget(version)
        
        description = QLabel("A modern knowledge explorer powered by open data. "
                            "Search across various digital libraries and encyclopedias "
                            "in one unified interface.")
        description.setFont(QFont("Segoe UI", 10))
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #cbd5e1; margin-top: 10px;")
        content_layout.addWidget(description)
        
        # Copyright
        copyright = QLabel("© 2026 Knowledgedock Contributors")
        copyright.setFont(QFont("Segoe UI", 9))
        copyright.setAlignment(Qt.AlignCenter)
        copyright.setStyleSheet("color: #64748b; margin-top: 20px;")
        content_layout.addWidget(copyright)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Close button
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(100, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
            }
        """)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = AboutDialog()
    dialog.show()
    sys.exit(app.exec_())
