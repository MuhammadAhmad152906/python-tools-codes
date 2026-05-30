import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QTabWidget, QProgressBar, 
    QStatusBar, QListWidget, QSplitter
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class UltimateBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ultimate Python Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Track history data and dark mode state
        self.history_list_data = []
        self.is_dark_mode = False

        # Main Layout Container
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)

        # 1. Navigation Bar Setup
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(5, 5, 5, 5)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("🔄")
        self.btn_home = QPushButton("🏠")
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter web address...")
        
        self.btn_go = QPushButton("Go")
        self.btn_new_tab = QPushButton("➕ New Tab")
        self.btn_history = QPushButton("📜 History")
        self.btn_theme = QPushButton("🌙 Dark Mode")

        # Add everything to navigation layout
        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_reload)
        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.url_bar)
        self.nav_layout.addWidget(self.btn_go)
        self.nav_layout.addWidget(self.btn_new_tab)
        self.nav_layout.addWidget(self.btn_history)
        self.nav_layout.addWidget(self.btn_theme)

        # 2. Splitter for Side History Panel + Main View
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # History Sidebar Setup
        self.history_panel = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(5, 5, 5, 5)
        
        self.history_list = QListWidget()
        self.btn_clear_history = QPushButton("Clear History")
        
        self.history_layout.addWidget(self.history_list)
        self.history_layout.addWidget(self.btn_clear_history)
        self.history_panel.setLayout(self.history_layout)
        self.history_panel.setVisible(False) # Hidden by default

        # Tabs Setup
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)

        # Assemble the horizontal splitter
        self.splitter.addWidget(self.history_panel)
        self.splitter.addWidget(self.tabs)
        # Set initial sizes (History panel width 250, Browser view takes the rest)
        self.splitter.setSizes([250, 950]) 

        # 3. Bottom Status & Progress Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Combine Layouts
        self.main_layout.addLayout(self.nav_layout)
        self.main_layout.addWidget(self.splitter)

        # --- Event Configurations & Signals ---
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        self.btn_back.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.btn_home.clicked.connect(self.navigate_home)
        self.btn_go.clicked.connect(self.navigate_to_url)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.btn_new_tab.clicked.connect(lambda: self.add_new_tab())
        
        # New features buttons mapping
        self.btn_history.clicked.connect(self.toggle_history_panel)
        self.btn_clear_history.clicked.connect(self.clear_history)
        self.history_list.itemDoubleClicked.connect(self.navigate_from_history)
        self.btn_theme.clicked.connect(self.toggle_theme)

        # Load home page tab
        self.add_new_tab(QUrl("https://www.google.com"), "Homepage")

    # --- Tab Logic ---

    def add_new_tab(self, qurl=None, title="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, b=browser: self.update_url_bar(qurl, b))
        browser.titleChanged.connect(lambda t, b=browser: self.update_tab_title(t, b))
        browser.loadProgress.connect(lambda p, b=browser: self.update_progress(p, b))
        browser.loadStarted.connect(lambda b=browser: self.handle_load_start(b))
        browser.loadFinished.connect(lambda _, b=browser: self.handle_load_finished(b))

    def close_tab(self, index):
        if self.tabs.count() < 2:
            return
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def current_browser(self) -> QWebEngineView:
        return self.tabs.currentWidget()

    def tab_changed(self, index):
        browser = self.current_browser()
        if browser:
            qurl = browser.url()
            self.url_bar.setText(qurl.toString())
            self.setWindowTitle(f"{self.tabs.tabText(index)} - Ultimate Python Web Browser")
        else:
            self.url_bar.clear()

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            short_title = title[:15] + "..." if len(title) > 15 else title
            self.tabs.setTabText(index, short_title)
            if browser == self.current_browser():
                self.setWindowTitle(f"{title} - Ultimate Python Web Browser")

    # --- Navigation Logic ---

    def navigate_to_url(self):
        browser = self.current_browser()
        if not browser: return

        url = self.url_bar.text().strip()
        if not url: return

        if "." not in url or " " in url:
            url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        browser.setUrl(QUrl(url))

    def navigate_home(self):
        if self.current_browser():
            self.current_browser().setUrl(QUrl("https://www.google.com"))

    def update_url_bar(self, qurl, browser):
        url_str = qurl.toString()
        if browser == self.current_browser():
            self.url_bar.setText(url_str)
        
        # Append to History system if it's a completely fresh site hit
        if url_str and (not self.history_list_data or self.history_list_data[-1] != url_str):
            if "about:blank" not in url_str:
                self.history_list_data.append(url_str)
                self.history_list.addItem(url_str)

    # --- History Feature Logic ---

    def toggle_history_panel(self):
        """Collapses or expands the history panel."""
        self.history_panel.setVisible(not self.history_panel.isVisible())

    def clear_history(self):
        self.history_list_data.clear()
        self.history_list.clear()

    def navigate_from_history(self, item):
        """Navigates to the history link when you double-click it."""
        if self.current_browser():
            self.current_browser().setUrl(QUrl(item.text()))

    # --- Theme / Dark Mode Logic ---

    def toggle_theme(self):
        """Switches the UI application styles between Dark and Light mode."""
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            self.btn_theme.setText("☀️ Light Mode")
            dark_stylesheet = """
                QMainWindow { background-color: #121212; }
                QWidget { background-color: #1e1e1e; color: #ffffff; font-family: Arial; }
                QLineEdit { background-color: #2d2d2d; color: #ffffff; border: 1px solid #3d3d3d; border-radius: 4px; padding: 4px; }
                QPushButton { background-color: #333333; color: #ffffff; border: 1px solid #444444; border-radius: 4px; padding: 5px 10px; }
                QPushButton:hover { background-color: #444444; }
                QPushButton:pressed { background-color: #555555; }
                QTabBar::tab { background: #2d2d2d; color: #aaaaaa; padding: 8px 15px; border: 1px solid #1e1e1e; }
                QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 2px solid #3daee9; }
                QListWidget { background-color: #2d2d2d; color: #ffffff; border: 1px solid #3d3d3d; }
                QStatusBar { background-color: #121212; color: #888888; }
                QProgressBar { border: 1px solid #444444; border-radius: 3px; text-align: center; color: white; }
                QProgressBar::chunk { background-color: #3daee9; }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            self.btn_theme.setText("🌙 Dark Mode")
            self.setStyleSheet("") # Restores native OS window styles

    # --- Loading Status UI Updates ---

    def handle_load_start(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage("Loading...")

    def update_progress(self, progress, browser):
        if browser == self.current_browser():
            self.progress_bar.setValue(progress)

    def handle_load_finished(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltimateBrowser()
    window.show()
    sys.exit(app.exec())