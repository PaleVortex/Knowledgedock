from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QLineEdit, QScrollArea, QFrame,
    QSplitter, QInputDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

class ProjectsView(QWidget):
    """UI for managing research projects and collections"""
    
    project_selected = pyqtSignal(int)  # Emits project_id when selected
    resource_clicked = pyqtSignal(str, str) # Emits url, title to open in reader
    
    def __init__(self, project_manager):
        super().__init__()
        self.project_manager = project_manager
        self.current_project_id = None
        self.init_ui()
        self.load_projects()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(30, 27, 75, 0.6), stop:1 rgba(15, 23, 42, 0.6));
                border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        title = QLabel("📁 Research Projects")
        title.setStyleSheet("color: #f8fafc; font-size: 22px; font-weight: bold; background: transparent; border: none;")
        
        new_project_btn = QPushButton("+ New Project")
        new_project_btn.setCursor(Qt.PointingHandCursor)
        new_project_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
                color: white; border: none;
                border-radius: 6px; padding: 10px 20px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #60a5fa, stop:1 #3b82f6); }
        """)
        new_project_btn.clicked.connect(self.create_new_project)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(new_project_btn)
        
        main_layout.addWidget(header)
        
        # Splitter for Projects List vs Project Details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Projects List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        self.projects_list = QListWidget()
        self.projects_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(15, 23, 42, 0.4); 
                border: 1px solid rgba(59, 130, 246, 0.15);
                border-radius: 8px; 
                color: #e2e8f0; 
                font-size: 15px;
                outline: none;
            }
            QListWidget::item { 
                padding: 14px 16px; 
                border-bottom: 1px solid rgba(255, 255, 255, 0.05); 
                margin: 2px 4px;
                border-radius: 6px;
            }
            QListWidget::item:hover { 
                background-color: rgba(59, 130, 246, 0.1); 
                color: #60a5fa; 
            }
            QListWidget::item:selected { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(59, 130, 246, 0.25), stop:1 transparent); 
                color: #3b82f6; 
                border-left: 4px solid #3b82f6; 
                font-weight: bold; 
            }
        """)
        self.projects_list.currentItemChanged.connect(self.on_project_selected)
        left_layout.addWidget(QLabel("Your Collections", styleSheet="color:#94a3b8; font-weight:bold;"))
        left_layout.addWidget(self.projects_list)
        
        # Right side: Project Details (Kanban/List view)
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(20, 20, 20, 20)
        
        project_header_layout = QHBoxLayout()
        self.project_title = QLabel("Select a project")
        self.project_title.setStyleSheet("color: #f8fafc; font-size: 28px; font-weight: bold; letter-spacing: 0.5px;")
        
        self.delete_project_btn = QPushButton("🗑️ Delete")
        self.delete_project_btn.setStyleSheet("""
            QPushButton { background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background-color: rgba(239, 68, 68, 0.2); }
        """)
        self.delete_project_btn.clicked.connect(self.delete_current_project)
        self.delete_project_btn.hide()
        
        project_header_layout.addWidget(self.project_title)
        project_header_layout.addStretch()
        project_header_layout.addWidget(self.delete_project_btn)
        
        self.right_layout.addLayout(project_header_layout)

        self.project_desc = QLabel("")
        self.project_desc.setStyleSheet("color: #94a3b8; font-size: 15px; font-style: italic;")
        
        self.resources_list = QListWidget()
        self.resources_list.setSpacing(10)
        self.resources_list.setStyleSheet("""
            QListWidget {
                background-color: transparent; border: none; outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                margin-bottom: 4px;
            }
            QListWidget::item:selected, QListWidget::item:hover { 
                background-color: transparent; 
            }
        """)
        self.resources_list.itemDoubleClicked.connect(self.on_resource_double_clicked)
        
        self.right_layout.addWidget(self.project_desc)
        self.right_layout.addSpacing(20)
        self.right_layout.addWidget(QLabel("Resources", styleSheet="color:#94a3b8; font-weight:bold;"))
        self.right_layout.addWidget(self.resources_list)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter, 1)
        
    def load_projects(self):
        """Load all projects into the left sidebar"""
        self.projects_list.clear()
        projects = self.project_manager.get_all_projects()
        
        for p in projects:
            p_id, name, desc, status, created, updated = p
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, p_id)
            item.setData(Qt.UserRole + 1, desc)
            self.projects_list.addItem(item)
            
        if self.projects_list.count() > 0:
            self.projects_list.setCurrentRow(0)
            
    def create_new_project(self):
        """Show dialog to create a new project"""
        name, ok = QInputDialog.getText(self, "New Project", "Project Name:")
        if ok and name.strip():
            desc, ok_desc = QInputDialog.getText(self, "New Project", "Description (optional):")
            # Always try to create, desc is optional
            desc_text = desc.strip() if ok_desc else ""
            if self.project_manager.create_project(name.strip(), desc_text):
                self.load_projects()
            else:
                QMessageBox.warning(self, "Error", "Failed to create project. Name might already exist.")
                
    def on_project_selected(self, current, previous):
        """Handle selection change in the projects list"""
        if not current:
            return
            
        self.current_project_id = current.data(Qt.UserRole)
        name = current.text()
        desc = current.data(Qt.UserRole + 1)
        
        self.project_title.setText(name)
        self.project_desc.setText(desc if desc else "No description provided.")
        self.delete_project_btn.show()
        
        self.load_project_resources()
        
    def load_project_resources(self):
        """Load resources for the currently selected project"""
        if not self.current_project_id:
            return
            
        self.resources_list.clear()
        resources = self.project_manager.get_project_resources(self.current_project_id)
        
        for r in resources:
            r_id, url, title, status, added = r
            
            # Create a rich item layout using a styled frame
            item_widget = QFrame()
            item_widget.setMinimumHeight(85)
            item_widget.setObjectName("ResourceCard")
            item_widget.setStyleSheet("""
                QFrame#ResourceCard {
                    background-color: rgba(30, 41, 59, 0.5);
                    border: 1px solid rgba(59, 130, 246, 0.15);
                    border-radius: 10px;
                }
                QFrame#ResourceCard:hover {
                    background-color: rgba(30, 41, 59, 0.8);
                    border: 1px solid rgba(59, 130, 246, 0.4);
                }
            """)
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 12, 15, 12)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #f1f5f9; font-weight: 600; font-size: 16px; border: none; background: transparent;")
            title_label.setWordWrap(True)
            
            # Status combo box
            status_combo = QComboBox()
            status_combo.addItems(["To Read", "Reading", "Synthesized"])
            status_combo.setStyleSheet("""
                QComboBox {
                    background-color: rgba(15, 23, 42, 0.8);
                    color: #cbd5e1;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                    margin-right: 10px;
                }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView {
                    background-color: #1e293b;
                    color: white;
                    selection-background-color: #3b82f6;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                }
            """)
            
            idx = 0
            if status == 'reading': idx = 1
            elif status == 'synthesized': idx = 2
            status_combo.setCurrentIndex(idx)
            
            # The lambda captures r_id by default value to avoid late binding issues
            status_combo.currentIndexChanged.connect(
                lambda idx, rid=r_id: self.update_resource_status(rid, idx)
            )
            
            btn_read = QPushButton("Read Now")
            btn_read.setCursor(Qt.PointingHandCursor)
            btn_read.setStyleSheet("""
                QPushButton { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #059669, stop:1 #047857);
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 6px; 
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #059669);
                }
            """)
            btn_read.clicked.connect(lambda checked, u=url, t=title: self.resource_clicked.emit(u, t))
            
            item_layout.addWidget(title_label, 1)
            item_layout.addWidget(status_combo)
            item_layout.addWidget(btn_read)
            
            list_item = QListWidgetItem(self.resources_list)
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.UserRole, url) # Store URL for double-click
            list_item.setData(Qt.UserRole + 1, title)
            
            self.resources_list.addItem(list_item)
            self.resources_list.setItemWidget(list_item, item_widget)
            
    def update_resource_status(self, resource_id, combo_idx):
        status_map = {0: 'to_read', 1: 'reading', 2: 'synthesized'}
        new_status = status_map.get(combo_idx, 'to_read')
        self.project_manager.update_resource_status(resource_id, new_status)
        
    def on_resource_double_clicked(self, item):
        url = item.data(Qt.UserRole)
        title = item.data(Qt.UserRole + 1)
        self.resource_clicked.emit(url, title)
    def update_resource_status(self, resource_id, combo_idx):
        status_map = {0: 'to_read', 1: 'reading', 2: 'synthesized'}
        new_status = status_map.get(combo_idx, 'to_read')
        self.project_manager.update_resource_status(resource_id, new_status)
        
    def on_resource_double_clicked(self, item):
        url = item.data(Qt.UserRole)
        title = item.data(Qt.UserRole + 1)
        self.resource_clicked.emit(url, title)

    def delete_current_project(self):
        if not self.current_project_id:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete project '{self.project_title.text()}'?\nAll its resources will be removed from this project.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if hasattr(self.project_manager, 'delete_project') and self.project_manager.delete_project(self.current_project_id):
                self.current_project_id = None
                self.project_title.setText("Select a project")
                self.project_desc.setText("")
                self.delete_project_btn.hide()
                self.resources_list.clear()
                self.load_projects()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete project.")
