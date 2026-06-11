from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QScrollArea, QFrame
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
import webbrowser


class TrendingLoader(QThread):
    """Load trending items in a separate thread"""
    trending_loaded = pyqtSignal(list)
    
    def __init__(self, extension_manager):
        super().__init__()
        self.extension_manager = extension_manager
    
    def run(self):
        try:
            if self.extension_manager:
                trending = self.extension_manager.get_trending_all(limit=6)
                self.trending_loaded.emit(trending)
        except Exception as e:
            print(f"Error loading trending: {e}")
            self.trending_loaded.emit([])


class HomeView(QWidget):
    # Signals for navigation
    browse_requested = pyqtSignal()
    bookmarks_requested = pyqtSignal()
    projects_requested = pyqtSignal()
    extensions_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    search_requested = pyqtSignal(str)
    
    def __init__(self, extension_manager=None, bookmark_manager=None):
        super().__init__()
        self.extension_manager = extension_manager
        self.bookmark_manager = bookmark_manager
        self.trending_items = []
        self.trending_loader = None
        self.stats_counts = {'bookmarks': 0, 'extensions': 4, 'sources': 4, 'status': 'Active'}
        self.init_ui()
        # Load trending data
        self.load_trending_data()
        self.refresh_stats()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Hero section
        hero = self.create_hero_section()
        main_layout.addWidget(hero)
        
        # Main content with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(40, 40, 40, 40)
        scroll_layout.setSpacing(40)
        
        # Stats section
        stats_section = self.create_stats_section()
        scroll_layout.addWidget(stats_section)
        
        # Trending section
        self.trending_container = QWidget()
        self.trending_layout = QVBoxLayout(self.trending_container)
        self.trending_layout.setContentsMargins(0, 0, 0, 0)
        self.trending_layout.setSpacing(20)
        scroll_layout.addWidget(self.trending_container)
        
        # Features section
        features_section = self.create_features_section()
        scroll_layout.addWidget(features_section)
        
        # Quick access section
        quickaccess_section = self.create_quick_access_section()
        scroll_layout.addWidget(quickaccess_section)
        
        # Sources section
        sources_section = self.create_sources_section()
        scroll_layout.addWidget(sources_section)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
    
    def load_trending_data(self):
        """Load trending data from extensions in a background thread"""
        if self.extension_manager:
            # If a previous loader is still running, stop it safely first
            if self.trending_loader and self.trending_loader.isRunning():
                try:
                    self.trending_loader.trending_loaded.disconnect()
                except TypeError:
                    pass
                self.trending_loader.quit()
                self.trending_loader.wait(2000)
            self.trending_loader = TrendingLoader(self.extension_manager)
            self.trending_loader.trending_loaded.connect(self.on_trending_loaded)
            self.trending_loader.start()

    def closeEvent(self, event):
        """Safely stop background threads before widget is destroyed"""
        if self.trending_loader and self.trending_loader.isRunning():
            try:
                self.trending_loader.trending_loaded.disconnect()
            except TypeError:
                pass
            self.trending_loader.quit()
            self.trending_loader.wait(3000)
        super().closeEvent(event)
    
    def on_trending_loaded(self, trending_items):
        """Called when trending data is loaded"""
        # Guard: if the widget was destroyed while the thread was running, bail out
        if not self.isVisible() and not self.isActiveWindow():
            return
        self.trending_items = trending_items
        self.display_trending(trending_items)
    
    def display_trending(self, items):
        """Display trending items in the UI"""
        # Clear previous items
        while self.trending_layout.count():
            item = self.trending_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not items:
            return

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🔥 Trending Now")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #06b6d4; letter-spacing: 0.5px;")
        header_layout.addWidget(title)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setToolTip("Refresh Trending")
        refresh_btn.clicked.connect(self.load_trending_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(6, 182, 212, 0.1);
                color: #06b6d4;
                border: 1px solid rgba(6, 182, 212, 0.3);
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: rgba(249, 115, 22, 0.3);
            }
        """)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()
        self.trending_layout.addLayout(header_layout)
        
        # Horizontal scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(240)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                height: 8px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        content_layout.setAlignment(Qt.AlignLeft)
        
        for item in items:
            resource = item.get('resource')
            extension = item.get('extension')
            if resource:
                card = self.create_trending_card(resource, extension)
                content_layout.addWidget(card)
        
        scroll.setWidget(content_widget)
        self.trending_layout.addWidget(scroll)

    def create_trending_card(self, resource, extension):
        """Create a card for a trending item"""
        card = QFrame()
        card.setFixedSize(160, 220)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 41, 59, 0.4);
                border-radius: 12px;
                border: 1px solid rgba(249, 115, 22, 0.1);
            }}
            QFrame:hover {{
                background-color: rgba(30, 41, 59, 0.6);
                border: 1px solid #06b6d4;
            }}
        """)
        
        # Add click event to open details/browser
        # Note: We need a way to trigger search or details view. 
        # For now, we can emit a search signal with the title
        pass 
        # Since QFrame doesn't have clicked signal, we can install event filter or use QPushButton
        # Using a transparent button overlay is a common trick
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(5)
        
        # Icon/Cover placeholder
        icon_label = QLabel("📚")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI", 32))
        layout.addWidget(icon_label)
        
        # Title
        title_text = resource.title if hasattr(resource, 'title') else "Unknown"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet("color: #e0e6ed;")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(60) # Limit height
        layout.addWidget(title)
        
        # Author
        author_text = resource.author if hasattr(resource, 'author') else "Unknown"
        author = QLabel(author_text)
        author.setFont(QFont("Segoe UI", 8))
        author.setStyleSheet("color: #999;")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)
        
        layout.addStretch()
        
        # Source badge
        source = QLabel(extension)
        source.setFont(QFont("Segoe UI", 8, QFont.Bold))
        source.setStyleSheet("color: #FFD700; background-color: rgba(255, 215, 0, 0.1); border-radius: 4px; padding: 2px 6px;")
        source.setAlignment(Qt.AlignCenter)
        layout.addWidget(source, 0, Qt.AlignCenter)
        
        return card
    
    def refresh_stats(self):
        """Refresh statistics section with latest data"""
        try:
            # Get updated bookmark count
            bookmarks_count = 0
            if self.bookmark_manager:
                try:
                    bookmarks_count = len(self.bookmark_manager.get_all_bookmarks())
                except:
                    bookmarks_count = 0
            
            # Get extension counts
            extensions_count = 0
            sources_count = 0
            
            if self.extension_manager:
                try:
                    # extension_manager in HomeView is the Core manager from main.py
                    extensions_count = len(self.extension_manager.extensions)
                    # Count enabled extensions as active sources
                    sources_count = sum(1 for ext in self.extension_manager.extensions.values() if ext.enabled)
                except Exception as ext_error:
                    print(f"Error counting extensions: {ext_error}")
                    extensions_count = 0
                    sources_count = 0
            
            # Find and update the stats cards
            self.stats_counts = {
                'bookmarks': bookmarks_count,
                'extensions': extensions_count,
                'sources': sources_count,
                'status': 'Active'
            }
            
            # Update UI if cards exist
            if hasattr(self, 'stats_cards'):
                if 'bookmarks' in self.stats_cards:
                    self.stats_cards['bookmarks'].value_label.setText(str(bookmarks_count))
                if 'extensions' in self.stats_cards:
                    self.stats_cards['extensions'].value_label.setText(str(extensions_count))
                if 'sources' in self.stats_cards:
                    self.stats_cards['sources'].value_label.setText(str(sources_count))
        except Exception as e:
            print(f"Error refreshing stats: {e}")
    
    def create_hero_section(self):
        """Create the hero banner at the top with modern glassmorphism"""
        hero = QFrame()
        hero.setMaximumHeight(300)
        hero.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9333ea, stop:0.5 #7c3aed, stop:1 #0891b2);
                border: none;
                border-radius: 0px;
            }
        """)
        
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(20)
        
        # Main title
        title = QLabel("Knowledgedock")
        title.setFont(QFont("Segoe UI", 44, QFont.Bold))
        title.setStyleSheet("color: white; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # Tagline
        tagline = QLabel("Your Gateway to Knowledge • Search Wikipedia, arXiv, Open Library & Project Gutenberg")
        tagline.setFont(QFont("Segoe UI", 13))
        tagline.setStyleSheet("color: rgba(255, 255, 255, 0.95);")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)
        
        layout.addStretch()
        
        # CTA Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        explore_btn = QPushButton("Explore Knowledge")
        explore_btn.setMinimumHeight(48)
        explore_btn.setMinimumWidth(200)
        explore_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        explore_btn.setCursor(Qt.PointingHandCursor)
        explore_btn.clicked.connect(self.browse_requested.emit)
        explore_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #ea580c;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.95);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.85);
            }
        """)
        button_layout.addWidget(explore_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return hero
    
    def create_stats_section(self):
        """Create statistics cards with modern design"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(25)
        
        title = QLabel("Your Activity")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #06b6d4; letter-spacing: 0.5px;")
        layout.addWidget(title)
        
        # Get actual stats
        bookmarks_count = self.stats_counts.get('bookmarks', 0)
        extensions_count = self.stats_counts.get('extensions', 0)
        sources_count = self.stats_counts.get('sources', 0)
        
        # Stats grid
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(20)
        
        self.stats_cards = {}
        
        stats = [
            ("Bookmarks", str(bookmarks_count), "#f97316"),
            ("Extensions", str(extensions_count), "#3b82f6"),
            ("Sources", str(sources_count), "#fbbf24"),
            ("Status", "Active", "#22c55e")
        ]
        
        for stat_title, stat_value, color in stats:
            card = self.create_stat_card_modern(stat_title, stat_value, color)
            self.stats_cards[stat_title.lower()] = card
            stats_grid.addWidget(card)
        
        layout.addLayout(stats_grid)
        return frame
    
    def create_stat_card_modern(self, title, value, color):
        """Create modern glassmorphic stat card"""
        card = QFrame()
        card.setMinimumHeight(140)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 41, 59, 0.4);
                border-radius: 12px;
                border: 1px solid rgba({self._hex_to_rgb(color)[0]}, {self._hex_to_rgb(color)[1]}, {self._hex_to_rgb(color)[2]}, 0.3);
                padding: 24px;
            }}
            QFrame:hover {{
                background-color: rgba(30, 41, 59, 0.6);
                border: 1px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        card.value_label = value_label
        
        return card
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_features_section(self):
        """Create features overview with modern cards"""
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent; border: none;")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(25)
        
        title = QLabel("Key Features")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #06b6d4; letter-spacing: 0.5px;")
        layout.addWidget(title)
        
        features_grid = QGridLayout()
        features_grid.setSpacing(20)
        features_grid.setColumnStretch(0, 1)
        features_grid.setColumnStretch(1, 1)
        features_grid.setColumnStretch(2, 1)
        
        features = [
            ("🌐 Multi-Source Search", "Search across 4 powerful knowledge sources simultaneously"),
            ("📥 Smart Downloads", "Download PDFs, books, and papers directly"),
            ("❤️ Bookmarking System", "Save and organize your favorite resources"),
            ("⚙️ Custom Extensions", "Install and manage custom knowledge sources"),
            ("🔍 Advanced Search", "Filter and sort results by relevance and source"),
            ("📱 Responsive Design", "Works seamlessly on all screen sizes")
        ]
        
        for i, (feature_title, feature_desc) in enumerate(features):
            card = self.create_feature_card_modern(feature_title, feature_desc)
            features_grid.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(features_grid)
        return frame
    
    def create_feature_card_modern(self, title, description):
        """Create modern feature card with glassmorphism"""
        card = QFrame()
        card.setMinimumHeight(180)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.3);
                border-radius: 12px;
                border: 1px solid rgba(59, 130, 246, 0.15);
                padding: 24px;
            }
            QFrame:hover {
                background-color: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(59, 130, 246, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: #3b82f6;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #b4bcd4;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        return card
    
    def create_quick_access_section(self):
        """Create quick access buttons with modern styling"""
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent; border: none;")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(25)
        
        title = QLabel("Quick Access")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #06b6d4; letter-spacing: 0.5px;")
        layout.addWidget(title)
        
        button_grid = QHBoxLayout()
        button_grid.setSpacing(20)
        
        quick_buttons = [
            ("Browse All", "#3b82f6", self.browse_requested),
            ("My Bookmarks", "#fbbf24", self.bookmarks_requested),
            ("Extensions", "#f97316", self.extensions_requested),
            ("Settings", "#22c55e", self.settings_requested)
        ]
        
        for btn_text, btn_color, signal in quick_buttons:
            btn = QPushButton(btn_text)
            btn.setMinimumHeight(54)
            btn.setMinimumWidth(180)
            btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: linear-gradient(135deg, {btn_color} 0%, rgba({self._hex_to_rgb(btn_color)[0]}, {self._hex_to_rgb(btn_color)[1]}, {self._hex_to_rgb(btn_color)[2]}, 0.8) 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: linear-gradient(135deg, {btn_color} 0%, {btn_color} 100%);
                }}
                QPushButton:pressed {{
                    background: linear-gradient(135deg, rgba({self._hex_to_rgb(btn_color)[0]}, {self._hex_to_rgb(btn_color)[1]}, {self._hex_to_rgb(btn_color)[2]}, 0.6) 0%, rgba({self._hex_to_rgb(btn_color)[0]}, {self._hex_to_rgb(btn_color)[1]}, {self._hex_to_rgb(btn_color)[2]}, 0.5) 100%);
                }}
            """)
            btn.clicked.connect(signal.emit)
            button_grid.addWidget(btn)
        
        layout.addLayout(button_grid)
        return frame
    
    def create_sources_section(self):
        """Create sources information with modern cards"""
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent; border: none;")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(25)
        
        title = QLabel("Connected Sources")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #06b6d4; letter-spacing: 0.5px;")
        layout.addWidget(title)
        
        sources_grid = QGridLayout()
        sources_grid.setSpacing(20)
        sources_grid.setColumnStretch(0, 1)
        sources_grid.setColumnStretch(1, 1)
        
        sources = [
            ("Wikipedia", "Free encyclopedia with millions of articles", "https://wikipedia.org"),
            ("arXiv", "Research papers and preprints in science", "https://arxiv.org"),
            ("Open Library", "Free library with millions of books", "https://openlibrary.org"),
            ("Project Gutenberg", "Over 70,000 free ebooks", "https://gutenberg.org")
        ]
        
        for i, (source_title, source_desc, source_url) in enumerate(sources):
            card = self.create_source_card_modern(source_title, source_desc, source_url)
            sources_grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(sources_grid)
        return frame
    
    def create_source_card_modern(self, title, description, url):
        """Create modern source information card"""
        card = QFrame()
        card.setMinimumHeight(200)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.3);
                border-radius: 12px;
                border: 1px solid rgba(59, 130, 246, 0.15);
                padding: 28px;
            }
            QFrame:hover {
                background-color: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(59, 130, 246, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_label.setStyleSheet("color: #3b82f6;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #b4bcd4;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        visit_btn = QPushButton("Visit Source →")
        visit_btn.setMinimumHeight(40)
        visit_btn.setCursor(Qt.PointingHandCursor)
        visit_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        visit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(59, 130, 246, 0.15);
                color: #3b82f6;
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3b82f6;
                color: white;
                border: 1px solid #3b82f6;
            }
            QPushButton:pressed {
                background-color: rgba(59, 130, 246, 0.8);
            }
        """)
        visit_btn.clicked.connect(lambda: webbrowser.open(url))
        layout.addWidget(visit_btn)
        
        return card
