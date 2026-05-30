import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QTabWidget, QProgressBar, 
    QStatusBar, QListWidget, QSplitter, QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class ProBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pro Browser")
        self.setGeometry(100, 100, 1200, 850)

        # State management
        self.history_list_data = []
        self.is_dark_mode = False

        # Main Layout Setup
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)

        # 1. Sleek Navigation Bar
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(8, 6, 8, 6)
        self.nav_layout.setSpacing(6)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("⟳")
        self.btn_home = QPushButton("🏠")
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search Google or type a URL...")
        
        self.btn_new_tab = QPushButton("＋")
        self.btn_history = QPushButton("📜 History")
        self.btn_theme = QPushButton("🌙")

        # Set tooltip hints
        self.btn_back.setToolTip("Back")
        self.btn_forward.setToolTip("Forward")
        self.btn_reload.setToolTip("Reload (F5)")
        self.btn_new_tab.setToolTip("New Tab (Ctrl+T)")
        self.btn_history.setToolTip("Toggle History (Ctrl+H)")
        self.btn_theme.setToolTip("Toggle Dark Mode")

        # Assemble Navbar
        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_reload)
        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.url_bar)
        self.nav_layout.addWidget(self.btn_new_tab)
        self.nav_layout.addWidget(self.btn_history)
        self.nav_layout.addWidget(self.btn_theme)

        # 2. Main Area Splitter (History Panel + Tabs)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # Modern Side History Panel
        self.history_panel = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(8, 8, 8, 8)
        self.history_layout.setSpacing(8)
        
        self.history_list = QListWidget()
        self.btn_clear_history = QPushButton("Clear Browsing Data")
        
        self.history_layout.addWidget(self.history_list)
        self.history_layout.addWidget(self.btn_clear_history)
        self.history_panel.setLayout(self.history_layout)
        self.history_panel.setVisible(False) 

        # Modern Document-Mode Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True) # Allow dragging tabs around

        self.splitter.addWidget(self.history_panel)
        self.splitter.addWidget(self.tabs)
        self.splitter.setSizes([260, 940]) 

        # 3. Micro Status Bar & Progress Indicator
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(140)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Attach Layouts
        self.main_layout.addLayout(self.nav_layout)
        self.main_layout.addWidget(self.splitter)

        # Connect Logic & Handlers
        self.setup_connections()
        self.setup_shortcuts()

        # Load Light Styles by Default
        self.apply_theme()

        # Open Startup Tab
        self.add_new_tab(QUrl("https://www.google.com"), "Google")

    def setup_connections(self):
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        self.btn_back.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.btn_home.clicked.connect(self.navigate_home)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.btn_new_tab.clicked.connect(lambda: self.add_new_tab())
        
        self.btn_history.clicked.connect(self.toggle_history_panel)
        self.btn_clear_history.clicked.connect(self.clear_history)
        self.history_list.itemDoubleClicked.connect(self.navigate_from_history)
        self.btn_theme.clicked.connect(self.toggle_theme)

    def setup_shortcuts(self):
        """Registers global hotkeys for power-user navigation."""
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_new_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+H"), self, self.toggle_history_panel)
        QShortcut(QKeySequence("F5"), self, lambda: self.current_browser().reload() if self.current_browser() else None)
        QShortcut(QKeySequence("Ctrl+R"), self, lambda: self.current_browser().reload() if self.current_browser() else None)

    # --- Core Tab Management ---

    def add_new_tab(self, qurl=None, title="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Inject custom right-click menus directly into the web view instance
        browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        browser.customContextMenuRequested.connect(lambda pos: self.create_custom_context_menu(pos, browser))

        i = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(i)

        # Hook updates
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_url_bar(qurl, b))
        browser.titleChanged.connect(lambda t, b=browser: self.update_tab_title(t, b))
        browser.loadProgress.connect(lambda p, b=browser: self.update_progress(p, b))
        browser.loadStarted.connect(lambda b=browser: self.handle_load_start(b))
        browser.loadFinished.connect(lambda ok, b=browser: self.handle_load_finished(ok, b))

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
            self.url_bar.setText(browser.url().toString())
            self.setWindowTitle(f"{self.tabs.tabText(index)} - Pro Browser")
        else:
            self.url_bar.clear()

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            short_title = title[:18] + "..." if len(title) > 18 else title
            self.tabs.setTabText(index, short_title)
            if browser == self.current_browser():
                self.setWindowTitle(f"{title} - Pro Browser")

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
        
        if url_str and (not self.history_list_data or self.history_list_data[-1] != url_str):
            if "about:blank" not in url_str:
                self.history_list_data.append(url_str)
                self.history_list.insertItem(0, url_str) # Show newest history at the top

    def toggle_history_panel(self):
        self.history_panel.setVisible(not self.history_panel.isVisible())

    def clear_history(self):
        self.history_list_data.clear()
        self.history_list.clear()

    def navigate_from_history(self, item):
        if self.current_browser():
            self.current_browser().setUrl(QUrl(item.text()))

    # --- Custom Web Context Menu ---

    def create_custom_context_menu(self, pos, browser):
        """Generates a clean right-click drop menu anywhere on the website web-view."""
        menu = QMenu(self)
        
        act_back = QAction("←  Back", self)
        act_forward = QAction("→  Forward", self)
        act_reload = QAction("⟳  Reload", self)
        act_copy = QAction("📋 Copy Page URL", self)

        act_back.triggered.connect(browser.back)
        act_forward.triggered.connect(browser.forward)
        act_reload.triggered.connect(browser.reload)
        act_copy.triggered.connect(lambda: QApplication.clipboard().setText(browser.url().toString()))

        menu.addAction(act_back)
        menu.addAction(act_forward)
        menu.addAction(act_reload)
        menu.addSeparator()
        menu.addAction(act_copy)
        
        menu.exec(browser.mapToGlobal(pos))

    # --- Web Page + System Deep Theme Injection ---

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        
        # Inject JavaScript to convert existing website content themes seamlessly on click
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser:
                self.inject_web_dark_mode(browser)

    def inject_web_dark_mode(self, browser):
        """Forces open web pages to render structural CSS filters simulating native dark styling."""
        if self.is_dark_mode:
            # Smart filter inversion inversion trick to make content look naturally dark
            js_code = """
            (function() {
                var css = 'html { filter: invert(1) hue-rotate(180deg) !important; } img, video, canvas { filter: invert(1) hue-rotate(180deg) !important; }';
                var head = document.head || document.getElementsByTagName('head')[0];
                var style = document.getElementById('dark-mode-style');
                if (!style) {
                    style = document.createElement('style');
                    style.id = 'dark-mode-style';
                    style.type = 'text/css';
                    style.appendChild(document.createTextNode(css));
                    head.appendChild(style);
                }
            })();
            """
        else:
            js_code = """
            (function() {
                var style = document.getElementById('dark-mode-style');
                if (style) { style.remove(); }
            })();
            """
        browser.page().runJavaScript(js_code)

    def apply_theme(self):
        """Applies advanced global CSS skin variations for modern layouts."""
        if self.is_dark_mode:
            self.btn_theme.setText("☀️")
            self.setStyleSheet("""
                QMainWindow { background-color: #1c1c1e; }
                QWidget { background-color: #2c2c2e; color: #f2f2f7; font-family: 'Segoe UI', Arial; font-size: 13px; }
                QLineEdit { background-color: #1c1c1e; color: #ffffff; border: 1px solid #3a3a3c; border-radius: 6px; padding: 6px 10px; }
                QLineEdit:focus { border: 1px solid #0a84ff; }
                QPushButton { background-color: #3a3a3c; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover { background-color: #48484a; }
                QPushButton:pressed { background-color: #636366; }
                QTabBar::tab { background: #2c2c2e; color: #aeaeae; padding: 8px 16px; border-right: 1px solid #1c1c1e; }
                QTabBar::tab:selected { background: #1c1c1e; color: #ffffff; font-weight: bold; }
                QTabBar::close-button { image: url(close.png); subcontrol-position: right; } /* Minimal default fallback close icon */
                QListWidget { background-color: #1c1c1e; border: 1px solid #3a3a3c; border-radius: 6px; padding: 4px; }
                QStatusBar { background-color: #1c1c1e; color: #8e8e93; }
                QProgressBar::chunk { background-color: #0a84ff; border-radius: 3px; }
                QMenu { background-color: #2c2c2e; border: 1px solid #3a3a3c; padding: 4px; }
                QMenu::item:selected { background-color: #0a84ff; color: white; }
            """)
        else:
            self.btn_theme.setText("🌙")
            self.setStyleSheet("""
                QMainWindow { background-color: #f2f2f7; }
                QWidget { background-color: #ffffff; color: #1c1c1e; font-family: 'Segoe UI', Arial; font-size: 13px; }
                QLineEdit { background-color: #f2f2f7; color: #000000; border: 1px solid #d1d1d6; border-radius: 6px; padding: 6px 10px; }
                QLineEdit:focus { border: 1px solid #007aff; background-color: #ffffff; }
                QPushButton { background-color: #e5e5ea; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover { background-color: #d1d1d6; }
                QPushButton:pressed { background-color: #c7c7cc; }
                QTabBar::tab { background: #e5e5ea; color: #48484a; padding: 8px 16px; border-right: 1px solid #d1d1d6; }
                QTabBar::tab:selected { background: #ffffff; color: #000000; font-weight: bold; }
                QListWidget { background-color: #f2f2f7; border: 1px solid #d1d1d6; border-radius: 6px; padding: 4px; }
                QStatusBar { background-color: #f2f2f7; color: #8e8e93; }
                QProgressBar::chunk { background-color: #007aff; border-radius: 3px; }
                QMenu { background-color: #ffffff; border: 1px solid #d1d1d6; padding: 4px; }
                QMenu::item:selected { background-color: #007aff; color: white; }
            """)

    # --- Status Logic Filters ---

    def handle_load_start(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage("Connecting...")

    def update_progress(self, progress, browser):
        if browser == self.current_browser():
            self.progress_bar.setValue(progress)

    def handle_load_finished(self, ok, browser):
        # Reinject Dark web layout rules if page refreshed/changed structures
        self.inject_web_dark_mode(browser)
        
        if browser == self.current_browser():
            self.progress_bar.setVisible(False)
            if ok:
                self.status_bar.showMessage("Done", 2000)
            else:
                self.status_bar.showMessage("Error loading page", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProBrowser()
    window.show()
    sys.exit(app.exec())