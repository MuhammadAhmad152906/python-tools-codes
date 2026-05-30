import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QTabWidget, QProgressBar, QStatusBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class AdvancedBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Python Web Browser")
        self.setGeometry(100, 100, 1100, 800)

        # Base layout elements
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.main_widget.setLayout(self.layout)

        # 1. Navigation Bar Setup
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(5, 5, 5, 5)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("🔄")
        self.btn_home = QPushButton("🏠")
        self.btn_new_tab = QPushButton("➕ New Tab")
        self.btn_go = QPushButton("Go")

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter web address...")

        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_reload)
        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.url_bar)
        self.nav_layout.addWidget(self.btn_go)
        self.nav_layout.addWidget(self.btn_new_tab)

        # 2. Tabs Container Setup
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        
        # Connect tab signals
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        # 3. Bottom Status Bar & Progress Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Combine main layouts
        self.layout.addLayout(self.nav_layout)
        self.layout.addWidget(self.tabs)

        # Connect Navigation Buttons
        self.btn_back.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.btn_home.clicked.connect(self.navigate_home)
        self.btn_go.clicked.connect(self.navigate_to_url)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.btn_new_tab.clicked.connect(lambda: self.add_new_tab())

        # Open up an initial starting tab
        self.add_new_tab(QUrl("https://www.google.com"), "Homepage")

    # --- Tab Management Logic ---

    def add_new_tab(self, qurl=None, title="New Tab"):
        """Creates a new tab containing a standalone web engine view."""
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Index tracking for managing specific tabs
        i = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(i)

        # Connect browser signals to handle updates inside this specific tab
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url_bar(qurl, browser))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
        browser.loadProgress.connect(lambda progress, browser=browser: self.update_progress(progress, browser))
        browser.loadStarted.connect(lambda browser=browser: self.handle_load_start(browser))
        browser.loadFinished.connect(lambda _, browser=browser: self.handle_load_finished(browser))

    def close_tab(self, index):
        """Closes the targeted tab, making sure not to close the last remaining tab."""
        if self.tabs.count() < 2:
            return  # Keep at least one tab open
        
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def current_browser(self) -> QWebEngineView:
        """Helper to get the active browser widget from the currently selected tab."""
        return self.tabs.currentWidget()

    def tab_changed(self, index):
        """Triggers when switching tabs; syncs the address bar and window title."""
        browser = self.current_browser()
        if browser:
            qurl = browser.url()
            self.url_bar.setText(qurl.toString())
            self.setWindowTitle(f"{self.tabs.tabText(index)} - Advanced Python Web Browser")
        else:
            self.url_bar.clear()

    def update_tab_title(self, title, browser):
        """Updates the tab text to reflect the actual website title."""
        index = self.tabs.indexOf(browser)
        if index != -1:
            # Truncate text if title is too long
            short_title = title[:15] + "..." if len(title) > 15 else title
            self.tabs.setTabText(index, short_title)
            if browser == self.current_browser():
                self.setWindowTitle(f"{title} - Advanced Python Web Browser")

    # --- Navigation Logic ---

    def navigate_to_url(self):
        """Navigates the active tab to the text present in the URL bar."""
        browser = self.current_browser()
        if not browser:
            return

        url = self.url_bar.text().strip()
        if not url:
            return

        # Simple trick: If it doesn't contain a dot or has spaces, treat it as a Google Search
        if "." not in url or " " in url:
            url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        browser.setUrl(QUrl(url))

    def navigate_home(self):
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl("https://www.google.com"))

    def update_url_bar(self, qurl, browser):
        """Syncs URL bar text only if the update belongs to the current tab view."""
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())

    # --- UI Status & Progress Bars ---

    def handle_load_start(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage("Loading page...")

    def update_progress(self, progress, browser):
        if browser == self.current_browser():
            self.progress_bar.setValue(progress)

    def handle_load_finished(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Done", 3000) # Message disappears after 3 seconds


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedBrowser()
    window.show()
    sys.exit(app.exec())