from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QSpinBox, QComboBox, QToolBar, QMessageBox, QFrame, 
                             QScrollArea, QSplitter, QTextEdit)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import sys
import os

class CustomWebEnginePage(QWebEnginePage):
    """Custom WebEnginePage to intercept navigation requests"""
    read_now_requested = pyqtSignal()

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() == "action" and url.path() == "read_now":
            self.read_now_requested.emit()
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class ReaderView(QWidget):
    back_requested = pyqtSignal()
    bookmark_requested = pyqtSignal(str, str, str)  # title, url, extension_name

    # Signal for adding to project: title, url, extension_name
    add_to_project_requested = pyqtSignal(str, str, str)
    
    def __init__(self, annotation_manager=None):
        super().__init__()
        self.annotation_manager = annotation_manager
        self.current_resource = None
        self.web_view = None
        self.zoom_level = 100
        self.init_ui()
    
    def init_ui(self):
        # Main layout is horizontal: Sidebar | Main Content
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar (Left) ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-right: 1px solid #334155;
            }
            QLabel {
                color: #b4bcd4;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)
        
        # Sidebar Sections
        self.create_sidebar_category(sidebar_layout, "Table of Contents", [
            "Overview", "View 2 Editions", "Details", "Reviews", "Lists", "Related Books"
        ], active_item="Overview")
        
        self.create_sidebar_category(sidebar_layout, "Metadata", ["Author", "Publisher", "Year"])
        self.create_sidebar_category(sidebar_layout, "Notes", ["My Notes", "Highlights"])
        
        sidebar_layout.addStretch()
        
        # Status/Ready/Footer tiny text in sidebar
        footer_label = QLabel("Ready")
        footer_label.setStyleSheet("color: #666; font-size: 11px;")
        sidebar_layout.addWidget(footer_label)
        
        main_layout.addWidget(self.sidebar)
        
        # --- Main Content Area (Right) ---
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1e293b;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header Bar
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-bottom: 1px solid #334155;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setSpacing(15)
        
        # Back Button
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(80, 32)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #3b82f6;
                border: 1px solid #334155;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2a2e3b;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        # Title
        self.title_label = QLabel("No resource loaded")
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: #f1f5f9;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Zoom Controls Group
        zoom_widget = QWidget()
        zoom_widget.setStyleSheet("""
            QWidget {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 4px;
            }
            QPushButton {
                border: none;
                background: transparent;
                color: #8b949e;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #3b82f6;
                background-color: rgba(59, 130, 246, 0.1);
            }
            QLabel {
                color: #c9d1d9;
                border: none;
                padding: 0 5px;
            }
        """)
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(2, 2, 2, 2)
        zoom_layout.setSpacing(0)
        
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(30, 28)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setFixedWidth(50)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 28)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)
        
        header_layout.addWidget(zoom_widget)
        
        # Action Icons (Download, Bookmark, Share/Reload)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.download_btn = self.create_icon_button("⬇", "Download")
        self.download_btn.clicked.connect(self.download_current)

        self.bookmark_btn = self.create_icon_button("🔖", "Bookmark")
        self.bookmark_btn.clicked.connect(self.bookmark_current)  # Fixed: was never connected

        self.project_btn = self.create_icon_button("📁", "Add to Project")
        self.project_btn.clicked.connect(self.request_add_to_project)

        self.refresh_btn = self.create_icon_button("🔄", "Reload")
        self.refresh_btn.clicked.connect(self.reload_page)

        actions_layout.addWidget(self.download_btn)
        actions_layout.addWidget(self.bookmark_btn)
        actions_layout.addWidget(self.project_btn)
        actions_layout.addWidget(self.refresh_btn)
        
        header_layout.addLayout(actions_layout)
        
        content_layout.addWidget(header)
        
        # Content Splitter (Web View | Annotation Sidebar)
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # Web View
        self.web_view = QWebEngineView()
        self.page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.page)
        self.page.read_now_requested.connect(self.read_current_resource)
        self.web_view.setStyleSheet("background-color: #ffffff;") 
        
        self.content_splitter.addWidget(self.web_view)
        
        # Annotation Sidebar (Right)
        self.annotation_sidebar = self.create_annotation_sidebar()
        self.annotation_sidebar.hide() # Hidden by default until "Read Now" is clicked
        self.content_splitter.addWidget(self.annotation_sidebar)
        
        # Initial proportions (70% web, 30% notes)
        self.content_splitter.setSizes([700, 300])
        
        content_layout.addWidget(self.content_splitter, 1) # Set stretch factor
        
        main_layout.addWidget(content_widget)

    def read_current_resource(self):
        """Load the current resource URL directly in the web view"""
        if not self.current_resource:
            return
            
        url = self.current_resource['url']
        if url and url != '#':
            # Use QTimer.singleShot to avoid re-entrancy issues with WebEngine navigation
            QTimer.singleShot(0, lambda: self.web_view.setUrl(QUrl(url)))
            
            # Show the annotation sidebar & load notes for this URL
            self.annotation_sidebar.show()
            self.load_annotations(url)

    def create_annotation_sidebar(self):
        """Builds the sidebar for taking notes on the current resource"""
        sidebar = QWidget()
        sidebar.setMinimumWidth(250)
        sidebar.setStyleSheet("background-color: #f8fafc; border-left: 1px solid #cbd5e1;")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("Resource Notes")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; border: none;")
        layout.addWidget(header)
        
        # Text Editor
        self.notes_editor = QTextEdit()
        self.notes_editor.setPlaceholderText("Capture your thoughts, ideas, and synthesis here while reading...")
        self.notes_editor.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #94a3b8;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: #334155;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        layout.addWidget(self.notes_editor, 1) # Give it stretch
        
        # Actions Layout (Save and AI)
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save Button
        save_btn = QPushButton("Save Notes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        save_btn.clicked.connect(self.save_annotation)
        
        # AI Summarize Button
        ai_btn = QPushButton("✨ AI Summarize")
        ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        ai_btn.clicked.connect(self.summarize_resource)
        
        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(ai_btn)
        
        layout.addLayout(actions_layout)
        
        # Info label about database storage
        from constants import DB_PATH
        db_info_label = QLabel(f"Notes are saved locally at:\n{DB_PATH.resolve()}")
        db_info_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic; margin-top: 5px;")
        db_info_label.setWordWrap(True)
        layout.addWidget(db_info_label)
        
        return sidebar
        
    def summarize_resource(self):
        """Placeholder for AI Summarization logic"""
        QMessageBox.information(
            self, 
            "AI Summarization", 
            "AI Summarization is not yet configured. Please set up an API key in Settings."
        )

    def load_annotations(self, url):
        """Fetch existing notes for this URL from the database"""
        if not self.annotation_manager:
            return
            
        self.current_annotation_id = None
        self.notes_editor.clear()
        
        annotations = self.annotation_manager.get_annotations_for_resource(url)
        if annotations:
            # We assume 1 global note per resource for the MVP
            # annotations[0] holds: (id, note_text, highlight_text, created_date, updated_date)
            first_note = annotations[0]
            self.current_annotation_id = first_note[0]
            self.notes_editor.setPlainText(first_note[1] or "")
            
    def save_annotation(self):
        """Save the current text in the notes editor"""
        if not self.annotation_manager or not self.current_resource:
            return
            
        url = self.current_resource.get('url', '')
        if not url or url == '#':
            return
            
        text = self.notes_editor.toPlainText()
        
        if self.current_annotation_id:
            if self.annotation_manager.update_annotation(self.current_annotation_id, text):
                QMessageBox.information(self, "Saved", "Notes updated successfully.")
        else:
            if self.annotation_manager.add_annotation(url, note_text=text):
                # Reload to get the new ID
                self.load_annotations(url)
                QMessageBox.information(self, "Saved", "Notes created successfully.")


    def create_sidebar_category(self, layout, title, items, active_item=None):
        """Helper to create sidebar sections"""
        # Category Header
        header = QPushButton(title)
        header.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #8b949e;
            }
        """)
        header.setCursor(Qt.PointingHandCursor)
        layout.addWidget(header)
        
        # Items
        items_widget = QWidget()
        items_layout = QVBoxLayout(items_widget)
        items_layout.setContentsMargins(10, 5, 0, 10)
        items_layout.setSpacing(2)
        
        for item in items:
            btn = QPushButton(f"•  {item}")
            is_active = (item == active_item)
            
            color = "#3b82f6" if is_active else "#94a3b8"
            bg = "rgba(59, 130, 246, 0.1)" if is_active else "transparent"
            border_left = "2px solid #3b82f6" if is_active else "2px solid transparent"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {color};
                    border: none;
                    border-left: {border_left};
                    padding: 6px 10px;
                    text-align: left;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    color: #3b82f6;
                    background-color: rgba(59, 130, 246, 0.05);
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            items_layout.addWidget(btn)
            
        layout.addWidget(items_widget)

    def create_icon_button(self, icon, tooltip):
        btn = QPushButton(icon)
        btn.setFixedSize(36, 36)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #3b82f6;
                border-color: #3b82f6;
            }
        """)
        return btn

    def load_resource(self, resource, resource_title, extension_name):
        """Load a resource in the reader"""
        is_dict = isinstance(resource, dict)
        url = resource.get('url', '#') if is_dict else getattr(resource, 'url', '#')
        
        self.current_resource = {
            'resource': resource,
            'title': resource_title,
            'extension': extension_name,
            'url': url
        }
        
        self.title_label.setText(f"{resource_title} — {extension_name}")
        
        # Generate HTML display from resource
        html_content = self._generate_resource_html(resource, resource_title, extension_name)
        self.web_view.setHtml(html_content)
    
    def _generate_resource_html(self, resource, title, extension_name):
        """Generate HTML content from a resource object"""
        if isinstance(resource, dict):
            author = resource.get('author', 'Unknown Author')
            description = resource.get('description', 'No description available')
            url = resource.get('url', '#')
            cover_url = resource.get('cover_url', None)
        else:
            author = getattr(resource, 'author', 'Unknown Author')
            description = getattr(resource, 'description', 'No description available')
            url = getattr(resource, 'url', '#')
            cover_url = getattr(resource, 'cover_url', None)
        
        # Use a cleaner, "paper-like" design or clean web design
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    background-color: #f6f8fa;
                    color: #24292f;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    padding: 40px;
                    margin: 0;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background: white;
                    padding: 60px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                    border: 1px solid #d0d7de;
                }}
                .header-section {{
                    display: flex;
                    gap: 40px;
                    margin-bottom: 40px;
                    border-bottom: 1px solid #d0d7de;
                    padding-bottom: 40px;
                }}
                .cover {{
                    width: 200px;
                    height: 300px;
                    object-fit: cover;
                    border-radius: 4px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    background-color: #eee;
                    display: block;
                }}
                .info {{
                    flex: 1;
                }}
                h1 {{
                    margin-top: 0;
                    font-size: 32px;
                    margin-bottom: 8px;
                    color: #1a1f3a;
                }}
                .author {{
                    font-size: 18px;
                    color: #3b82f6;
                    margin-bottom: 24px;
                }}
                .actions {{
                    display: flex;
                    gap: 12px;
                    margin-bottom: 30px;
                }}
                .btn {{
                    padding: 10px 20px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 14px;
                }}
                .btn-primary {{
                    background-color: #3b82f6;
                    color: white;
                }}
                .btn-outline {{
                    background-color: #f6f8fa;
                    color: #24292f;
                    border: 1px solid #d0d7de;
                }}
                .description {{
                    font-size: 16px;
                    color: #57606a;
                }}
                h3 {{
                    font-size: 18px;
                    margin-bottom: 10px;
                    color: #24292f;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header-section">
                    <img class="cover" src="{cover_url or 'https://via.placeholder.com/200x300?text=No+Cover'}" alt="Cover">
                    
                    <div class="info">
                        <h1>{title}</h1>
                        <div class="author">by {author}</div>
                        
                        <div class="actions">
                            <a href="action:read_now" class="btn btn-primary">Read Now</a>
                            <a href="{url}" class="btn btn-outline">View on {extension_name}</a>
                        </div>
                        
                        <div class="description">
                            <h3>Overview</h3>
                            <p>{description}</p>
                        </div>
                    </div>
                </div>
                
                <div class="details">
                     <!-- More details -->
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def reload_page(self):
        """Reload the current page in the web view"""
        if self.web_view:
            self.web_view.reload()  # Fixed: was commented out

    def zoom_in(self):
        """Zoom in using QWebEngineView's setZoomFactor (zoomIn/zoomOut do not exist in PyQt5)"""
        if self.zoom_level < 200:
            self.zoom_level += 10
            self.web_view.setZoomFactor(self.zoom_level / 100.0)  # Fixed: was zoomIn(1) which crashes
            self.zoom_label.setText(f"{self.zoom_level}%")

    def zoom_out(self):
        """Zoom out using QWebEngineView's setZoomFactor"""
        if self.zoom_level > 50:
            self.zoom_level -= 10
            self.web_view.setZoomFactor(self.zoom_level / 100.0)  # Fixed: was zoomOut(1) which crashes
            self.zoom_label.setText(f"{self.zoom_level}%")

    def request_add_to_project(self):
        """Emit signal to add current resource to a project"""
        if not self.current_resource:
            QMessageBox.information(self, "No Resource", "No resource is currently loaded.")
            return
            
        url = self.current_resource.get('url', '')
        title = self.current_resource.get('title', 'Unknown Resource')
        
        if not url or url == '#':
            QMessageBox.warning(self, "Cannot Save", 
                              "This resource doesn't have a valid URL to save.")
            return
            
        extension = self.current_resource.get('extension', 'Unknown')
        self.add_to_project_requested.emit(title, url, extension)
        
    def download_current(self):
        """Download the current resource using the appropriate DownloadHelper method"""
        if not self.current_resource:
            QMessageBox.warning(self, "No Resource", "Please load a resource first")
            return

        try:
            from download_helper import DownloadHelper
            title = self.current_resource.get('title', 'download')
            url = self.current_resource.get('url', '')
            extension = self.current_resource.get('extension', '').lower()
            resource = self.current_resource.get('resource')

            if not url or url == '#':
                QMessageBox.warning(self, "Download Failed", "No valid URL available for this resource.")
                return

            helper = DownloadHelper()

            # Route to the correct source-specific method
            if 'arxiv' in extension:
                # Extract arXiv ID from URL (e.g. arxiv.org/abs/1234.56789)
                arxiv_id = url.rstrip('/').split('/')[-1]
                success, message = helper.download_pdf_from_arxiv(arxiv_id)
            elif 'gutenberg' in extension:
                book_id = url.rstrip('/').split('/')[-1]
                success, message = helper.download_from_gutenberg(book_id, format_type='epub')
            elif 'openlibrary' in extension or 'library' in extension:
                # Open Library URLs contain the book key like /works/OL123W
                from urllib.parse import urlparse
                path = urlparse(url).path
                success, message = helper.download_book_from_openlibrary(path)
            elif 'wikipedia' in extension:
                article_title = title.replace(' ', '_')
                success, message = helper.download_wikipedia_article(article_title)
            elif 'doaj' in extension:
                success, message = helper.download_file(url, f"{helper.clean_filename(title)}.html")
            else:
                # Generic fallback — attempt to save as PDF if it looks like one
                import urllib.parse
                parsed_url = urllib.parse.urlparse(url)
                if parsed_url.path.lower().endswith('.pdf'):
                    filename = f"{helper.clean_filename(title)}.pdf"
                else:
                    filename = f"{helper.clean_filename(title)}.html"
                success, message = helper.download_file(url, filename)

            if success:
                QMessageBox.information(self, "Download Complete", message)
            else:
                QMessageBox.warning(self, "Download Failed", message)

        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"An error occurred:\n{e}")


    def bookmark_current(self):
        """Bookmark the currently loaded resource"""
        if not self.current_resource:
            QMessageBox.warning(self, "Nothing to Bookmark", "Please load a resource first.")
            return
        # Emit signal so main window can handle it via the shared BookmarkManager
        self.bookmark_requested.emit(
            self.current_resource.get('title', 'Untitled'),
            self.current_resource.get('url', ''),
            self.current_resource.get('extension', '')
        )
        QMessageBox.information(self, "Bookmarked", f"'{self.current_resource.get('title')}' has been bookmarked!")

    def clear(self):
        self.current_resource = None
        self.title_label.setText("No resource loaded")
        self.web_view.setHtml("<html><body style='background-color: #f6f8fa;'></body></html>")
