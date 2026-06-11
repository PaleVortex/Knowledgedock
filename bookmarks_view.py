from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QScrollArea, QGridLayout, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import webbrowser

class BookmarkCard(QWidget):
    def __init__(self, bookmark_data, on_remove_callback=None):
        super().__init__()
        self.bookmark_data = bookmark_data
        self.on_remove_callback = on_remove_callback
        self.init_ui()
    
    def init_ui(self):
        bookmark_id, title, url, source, resource_type, added_date, cover_url, description = self.bookmark_data
        
        card = QWidget()
        card.setMaximumWidth(280)
        card.setMinimumHeight(200)
        card.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 1px solid #333;
                padding: 10px;
            }
            QWidget:hover {
                border: 1px solid #FF6B6B;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #FF6B6B;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Source
        source_label = QLabel(f"Source: {source}")
        source_label.setFont(QFont("Arial", 9))
        source_label.setStyleSheet("color: #999;")
        layout.addWidget(source_label)
        
        # Type
        type_label = QLabel(f"Type: {resource_type}")
        type_label.setFont(QFont("Arial", 9))
        type_label.setStyleSheet("color: #999;")
        layout.addWidget(type_label)
        
        # Description
        if description:
            desc_label = QLabel(description[:100] + "..." if len(description) > 100 else description)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setStyleSheet("color: #ccc;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        layout.addSpacing(5)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        open_btn = QPushButton("Open")
        open_btn.setMaximumWidth(80)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        open_btn.clicked.connect(lambda: webbrowser.open(url))
        button_layout.addWidget(open_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setMaximumWidth(80)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #888;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_bookmark(url))
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Replace self layout
        self_layout = QVBoxLayout(self)
        self_layout.addWidget(card)
        self_layout.setContentsMargins(0, 0, 0, 0)
    
    def remove_bookmark(self, url):
        if self.on_remove_callback:
            self.on_remove_callback(url)


class BookmarksView(QWidget):
    def __init__(self, bookmark_manager):
        super().__init__()
        self.bookmark_manager = bookmark_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("My Bookmarks")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(header)
        
        # Search
        search_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search bookmarks...")
        search_input.setMinimumHeight(40)
        search_input.setMaximumWidth(400)
        search_input.textChanged.connect(lambda text: self.search_bookmarks(text))
        search_layout.addWidget(search_input)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        
        # Bookmarks grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(15)
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll)
        
        # Load bookmarks
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """Load and display all bookmarks"""
        # Clear existing widgets
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        bookmarks = self.bookmark_manager.get_all_bookmarks()
        
        if not bookmarks:
            empty_label = QLabel("No bookmarks yet. Start exploring!")
            empty_label.setFont(QFont("Arial", 14))
            empty_label.setStyleSheet("color: #999;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
        else:
            for idx, bookmark in enumerate(bookmarks):
                card = BookmarkCard(bookmark, on_remove_callback=self.on_remove_bookmark)
                self.grid_layout.addWidget(card, idx // 4, idx % 4)
            
            self.grid_layout.setRowStretch(len(bookmarks) // 4 + 1, 1)
    
    def search_bookmarks(self, query):
        """Search and display filtered bookmarks"""
        # Clear existing widgets
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not query.strip():
            self.load_bookmarks()
            return
        
        bookmarks = self.bookmark_manager.search_bookmarks(query)
        
        if not bookmarks:
            empty_label = QLabel("No bookmarks found.")
            empty_label.setFont(QFont("Arial", 14))
            empty_label.setStyleSheet("color: #999;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
        else:
            for idx, bookmark in enumerate(bookmarks):
                card = BookmarkCard(bookmark, on_remove_callback=self.on_remove_bookmark)
                self.grid_layout.addWidget(card, idx // 4, idx % 4)
            
            self.grid_layout.setRowStretch(len(bookmarks) // 4 + 1, 1)
    
    def on_remove_bookmark(self, url):
        """Remove bookmark and refresh view"""
        self.bookmark_manager.remove_bookmark(url)
        self.load_bookmarks()
    
    def refresh(self):
        """Refresh bookmarks display"""
        self.load_bookmarks()
