from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QGridLayout, QScrollArea, QComboBox, QMessageBox,
                             QListWidget, QListWidgetItem, QProgressDialog, QCompleter)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QStringListModel
from PyQt5.QtNetwork import QNetworkAccessManager
import requests
from urllib.request import urlopen
from io import BytesIO
from download_helper import DownloadHelper


class SearchWorker(QThread):
    """Worker thread for searching extensions"""
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, extension_manager, query, limit=20):
        super().__init__()
        self.extension_manager = extension_manager
        self.query = query
        self.limit = limit
    
    def run(self):
        try:
            if not self.query.strip():
                self.error_occurred.emit("Please enter a search query")
                return
            
            results = self.extension_manager.search_all(self.query, self.limit)
            self.results_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(f"Search error: {str(e)}")


class DownloadWorker(QThread):
    """Worker thread for downloading resources"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, download_func, *args):
        super().__init__()
        self.download_func = download_func
        self.args = args
        self._cancelled = False
    
    def cancel(self):
        """Request cooperative cancellation — safe alternative to terminate()"""
        self._cancelled = True
    
    def run(self):
        if self._cancelled:
            return
        try:
            # Call the download function with provided args and progress callback
            success, message = self.download_func(*self.args, progress_callback=self.progress.emit)
            if self._cancelled:
                self.finished.emit(False, "Download cancelled")
            else:
                self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, str(e))


class BrowserView(QWidget):
    def __init__(self, bookmark_manager=None, extension_manager=None, reader_view=None):
        super().__init__()
        self.bookmark_manager = bookmark_manager
        self.extension_manager = extension_manager
        self.reader_view = reader_view  # Reference to reader view for loading content
        self.search_worker = None
        self.current_results = []
        self.download_helper = DownloadHelper()
        
        # Popular search suggestions
        self.popular_searches = [
            "Python", "Machine Learning", "Quantum Computing", "Relativity",
            "Artificial Intelligence", "Climate Change", "COVID-19", "DNA",
            "Black Holes", "COVID", "Einstein", "Philosophy", "Biology",
            "Physics", "Chemistry", "History", "Mathematics", "Literature",
            "Art History", "Psychology", "Economics", "Technology", "Space"
        ]
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Browse Resources")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(header)
        
        # Search and filters
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Wikipedia, arXiv, Open Library, Project Gutenberg...")
        self.search_input.setMinimumHeight(40)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Set up autocomplete with popular searches
        completer = QCompleter(self.popular_searches)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.search_input.setCompleter(completer)
        
        # Show suggestions when search input is focused
        self.search_input.focusInEvent = lambda e: self.show_suggestions_panel()
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setMinimumHeight(40)
        self.search_btn.setMaximumWidth(100)
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # Source filter
        filter_layout = QHBoxLayout()
        
        source_label = QLabel("Source:")
        filter_layout.addWidget(source_label)
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["All Sources", "Wikipedia", "arXiv", "Open Library", "Project Gutenberg"])
        self.source_combo.setMinimumHeight(35)
        self.source_combo.setMaximumWidth(200)
        filter_layout.addWidget(self.source_combo)
        
        self.results_count_label = QLabel("Results: 0")
        self.results_count_label.setStyleSheet("color: #888;")
        filter_layout.addWidget(self.results_count_label)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Suggestions panel (shown by default) - uses scroll area
        self.suggestions_scroll = QScrollArea()
        self.suggestions_scroll.setWidgetResizable(True)
        self.suggestions_scroll.setStyleSheet("border: none;")
        
        self.suggestions_panel = QWidget()
        suggestions_layout = QVBoxLayout(self.suggestions_panel)
        suggestions_layout.setContentsMargins(0, 10, 0, 10)
        suggestions_layout.setSpacing(10)
        
        sugg_title = QLabel("Popular Searches")
        sugg_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sugg_title.setStyleSheet("color: #FFD700;")
        suggestions_layout.addWidget(sugg_title)
        
        # Grid of suggestion buttons
        suggestion_grid = QGridLayout()
        suggestion_grid.setSpacing(10)
        
        for i, search_term in enumerate(self.popular_searches):
            btn = QPushButton(search_term)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 200, 255, 0.1);
                    color: #b4bcd4;
                    border: 1px solid rgba(100, 200, 255, 0.2);
                    border-radius: 6px;
                    padding: 10px 15px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(100, 200, 255, 0.25);
                    color: #00D4FF;
                    border: 1px solid rgba(100, 200, 255, 0.5);
                }
            """)
            btn.clicked.connect(lambda checked, term=search_term: self.search_suggestion(term))
            suggestion_grid.addWidget(btn, i // 4, i % 4)
        
        suggestions_layout.addLayout(suggestion_grid)
        suggestions_layout.addStretch()
        
        self.suggestions_scroll.setWidget(self.suggestions_panel)
        layout.addWidget(self.suggestions_scroll, 1)
        
        # Results list (hidden by default) - takes full space when shown
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #0a0a0a;
                color: #CCCCCC;
                border: 1px solid #333;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #1a1a1a;
            }
            QListWidget::item:hover {
                background-color: #1a1a1a;
            }
            QListWidget::item:selected {
                background-color: #FF6B6B;
            }
        """)
        self.results_list.hide()
        layout.addWidget(self.results_list, 1)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def show_suggestions_panel(self):
        """Show suggestions panel"""
        if not self.search_input.text():
            self.suggestions_scroll.show()
            self.results_list.hide()
    
    def on_search_text_changed(self, text):
        """Handle search text changes"""
        if text.strip():
            self.suggestions_scroll.hide()
        else:
            self.suggestions_scroll.show()
            self.results_list.hide()
    
    def search_suggestion(self, term):
        """Search when a suggestion is clicked"""
        self.search_input.setText(term)
        self.perform_search()
    
    def perform_search(self):
        """Perform search using extension manager"""
        if not self.extension_manager:
            QMessageBox.warning(self, "Error", "Extension manager not initialized")
            return
        
        query = self.search_input.text().strip()
        if not query:
            self.status_label.setText("Please enter a search query")
            return
        
        self.search_btn.setEnabled(False)
        self.search_btn.setText("Searching...")
        self.status_label.setText("Searching all sources...")
        self.results_list.clear()
        
        # Create and start search worker
        self.search_worker = SearchWorker(self.extension_manager, query, 50)
        self.search_worker.results_ready.connect(self.display_results)
        self.search_worker.error_occurred.connect(self.handle_search_error)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
    
    def display_results(self, results):
        """Display search results"""
        self.results_list.clear()
        self.current_results = results
        
        # Show results list, hide suggestions
        self.suggestions_scroll.hide()
        self.results_list.show()
        
        if not results:
            self.status_label.setText("No results found")
            self.results_count_label.setText("Results: 0")
            return
        
        for result_dict in results:
            # Extract the actual resource and extension info
            resource = result_dict.get('resource')
            extension_name = result_dict.get('extension', 'Unknown')
            
            if resource:
                item_widget = self.create_result_item(resource, extension_name)
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.results_list.addItem(item)
                self.results_list.setItemWidget(item, item_widget)
        
        self.status_label.setText("")
        self.results_count_label.setText(f"Results: {len(results)}")
    
    def create_result_item(self, resource, extension_name):
        """Create a result item widget from a Resource object"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        # Title and source
        header_layout = QHBoxLayout()
        
        title_label = QLabel(resource.title if hasattr(resource, 'title') else 'Unknown')
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        
        source_label = QLabel(extension_name)
        source_label.setFont(QFont("Arial", 9))
        source_label.setStyleSheet("color: #FFD700;")
        source_label.setMaximumWidth(120)
        header_layout.addWidget(source_label)
        layout.addLayout(header_layout)
        
        # Author
        author = resource.author if hasattr(resource, 'author') else 'Unknown'
        author_label = QLabel(f"By: {author}")
        author_label.setFont(QFont("Arial", 10))
        author_label.setStyleSheet("color: #999;")
        layout.addWidget(author_label)
        
        # Description
        description = resource.description if hasattr(resource, 'description') else ''
        desc_label = QLabel((description or '')[:200])
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(desc_label)
        
        # Buttons - use elastic sizing instead of fixed width
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        open_btn = QPushButton("📖 Read in App")
        open_btn.setMinimumHeight(36)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3BBFB8;
            }
        """)
        # Load content in reader instead of browser
        title_text = resource.title if hasattr(resource, 'title') else 'Unknown'
        open_btn.clicked.connect(lambda: self.open_in_reader(resource, title_text, extension_name))
        button_layout.addWidget(open_btn)
        
        download_btn = QPushButton("⬇️ Download")
        download_btn.setMinimumHeight(36)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        
        title = resource.title if hasattr(resource, 'title') else 'resource'
        download_btn.clicked.connect(lambda: self.download_resource(resource, title, extension_name))
        button_layout.addWidget(download_btn)
        
        bookmark_btn = QPushButton("❤️ Bookmark")
        bookmark_btn.setMinimumHeight(36)
        
        url = resource.url if hasattr(resource, 'url') else ''
        is_bookmarked = False
        if self.bookmark_manager:
            is_bookmarked = self.bookmark_manager.is_bookmarked(url)
        
        if is_bookmarked:
            bookmark_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)
        else:
            bookmark_btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #FF6B6B;
                }
            """)
        
        bookmark_btn.clicked.connect(
            lambda: self.toggle_bookmark(resource, extension_name, bookmark_btn)
        )
        button_layout.addWidget(bookmark_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 4px;
            }
        """)
        
        return widget
    
    
    def open_in_reader(self, resource, title, extension_name):
        """Open a resource in the in-app reader and switch to reader view"""
        if self.reader_view:
            self.reader_view.load_resource(resource, title, extension_name)
            # Find the main window and switch to reader view
            main_window = self.window()
            if hasattr(main_window, 'show_reader'):
                main_window.show_reader()
        else:
            QMessageBox.information(self, "Reader", f"Opening: {title} from {extension_name}")
    
    def toggle_bookmark(self, resource, extension_name, button):
        """Toggle bookmark state"""
        if not self.bookmark_manager:
            return
        
        url = resource.url if hasattr(resource, 'url') else ''
        title = resource.title if hasattr(resource, 'title') else 'Unknown'
        source_type = resource.source_type if hasattr(resource, 'source_type') else 'Web'
        description = resource.description if hasattr(resource, 'description') else ''
        
        if self.bookmark_manager.is_bookmarked(url):
            self.bookmark_manager.remove_bookmark(url)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #FF6B6B;
                }
            """)
        else:
            self.bookmark_manager.add_bookmark(
                title, url, extension_name, source_type,
                description=description
            )
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)
    
    def handle_search_error(self, error):
        """Handle search errors"""
        self.status_label.setText(f"Error: {error}")
        self.results_count_label.setText("Results: 0")
    
    def on_search_finished(self):
        """Called when search finishes"""
        self.search_btn.setEnabled(True)
        self.search_btn.setText("Search")
    
    def download_resource(self, resource, title, source):
        """Download a resource"""
        try:
            url = resource.url if hasattr(resource, 'url') else None
            resource_id = resource.id if hasattr(resource, 'id') else None
            
            if not url and not resource_id:
                QMessageBox.warning(self, "Error", "Cannot download: No URL or ID available")
                return
            
            # Create progress dialog
            self.progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowTitle(f"Downloading {title}")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setAutoReset(False)
            self.progress_dialog.setStyleSheet("""
                QProgressDialog {
                    background-color: #0a0a0a;
                    color: #CCCCCC;
                }
                QProgressBar {
                    background-color: #222;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #FF6B6B;
                }
            """)
            
            # Determine download method based on source
            if source == "arXiv":
                self.download_worker = DownloadWorker(
                    self.download_helper.download_pdf_from_arxiv, 
                    resource_id
                )
            elif source == "Open Library":
                self.download_worker = DownloadWorker(
                    self.download_helper.download_book_from_openlibrary, 
                    resource_id
                )
            elif source == "Project Gutenberg":
                self.download_worker = DownloadWorker(
                    self.download_helper.download_from_gutenberg, 
                    resource_id, 
                    'epub'
                )
            elif source == "Wikipedia":
                self.download_worker = DownloadWorker(
                    self.download_helper.download_wikipedia_article, 
                    title
                )
            else:
                # Default fallback
                filename = f"{title}.pdf" # Simple filename fallback
                self.download_worker = DownloadWorker(
                    self.download_helper.download_file, 
                    url, 
                    filename
                )
            
            self.download_worker.progress.connect(self.progress_dialog.setValue)
            self.download_worker.finished.connect(self.on_download_finished)
            
            # Safe cooperative cancellation — terminate() is unsafe and causes crashes
            self.progress_dialog.canceled.connect(self.download_worker.cancel)
            
            # Show dialog and start thread
            self.progress_dialog.show()
            self.download_worker.start()
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Download setup error: {str(e)}")
            
    def on_download_finished(self, success, message):
        """Handle download completion"""
        if self.progress_dialog:
            self.progress_dialog.close()
            
        if success:
            reply = QMessageBox.information(
                self,
                "Download Complete",
                f"{message}\n\nWould you like to open the downloads folder?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.download_helper.open_downloads_folder()
        else:
            QMessageBox.warning(self, "Download Failed", message)

