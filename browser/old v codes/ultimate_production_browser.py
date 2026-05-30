import sys
import os
import json
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QTabWidget, QProgressBar, 
    QStatusBar, QListWidget, QSplitter, QMenu, QFileDialog, 
    QToolButton, QTabBar, QLabel, QTextEdit
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class ChromiumTabBar(QTabBar):
    """Advanced tab component mirroring Chromium layout properties."""
    new_tab_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectionBehavior.SelectPreviousTab)
        
        # Inline Addition Control Anchor
        self.add_btn = QToolButton(self)
        self.add_btn.setText("＋")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.new_tab_clicked.emit)
        self.add_btn.setStyleSheet("border: none; font-size: 13px; font-weight: bold; padding: 2px 6px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.count() > 0:
            last_tab_rect = self.tabRect(self.count() - 1)
            # Positions button precisely 6px to the right of the trailing tab edge
            self.add_btn.move(last_tab_rect.right() + 6, 5)
            self.add_btn.show()
        else:
            self.add_btn.hide()


class ProductionBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Browser Engine")
        self.setGeometry(100, 100, 1400, 900)

        # File System Initialization
        self.storage_path = os.path.join(os.getcwd(), ".production_browser_data")
        os.makedirs(self.storage_path, exist_ok=True)
        self.config_file = os.path.join(self.storage_path, "config.json")
        self.session_file = os.path.join(self.storage_path, "session.json")
        
        # Core Configurations Setup
        self.config = self.load_configuration()
        self.history_list_data = []
        self.is_dark_mode = self.config.get("dark_mode", False)
        self.adblock_enabled = self.config.get("adblock", True)

        self.setup_persistent_profile()
        self.init_ui()
        self.setup_shortcuts()
        self.render_bookmarks_bar()
        self.apply_theme()

        # Restore Last Session or Load Default Homepage
        self.restore_session()

    def load_configuration(self):
        default_config = {
            "homepage": "https://www.google.com",
            "search_engine": "https://www.google.com/search?q=",
            "dark_mode": False,
            "adblock": True,
            "bookmarks": {"Google": "https://www.google.com", "GitHub": "https://github.com"}
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return default_config
        return default_config

    def save_configuration(self):
        self.config["dark_mode"] = self.is_dark_mode
        self.config["adblock"] = self.adblock_enabled
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def setup_persistent_profile(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setCachePath(os.path.join(self.storage_path, "Cache"))
        profile.setPersistentStoragePath(os.path.join(self.storage_path, "Storage"))
        profile.downloadRequested.connect(self.handle_download_intercept)

    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)

        # 1. Navigation Panel
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(10, 8, 10, 6)
        self.nav_layout.setSpacing(8)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("⟳")
        self.btn_home = QPushButton("🏠")
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter secure URL or query mapping...")
        
        self.btn_bookmark = QPushButton("⭐")
        self.btn_adblock = QPushButton("🛡️ AdBlock: ON" if self.adblock_enabled else "🛡️ AdBlock: OFF")
        self.btn_developer = QPushButton("📄 Code")
        self.btn_history = QPushButton("📜 History")
        self.btn_theme = QPushButton("🌙")

        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_reload)
        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.url_bar)
        self.nav_layout.addWidget(self.btn_bookmark)
        self.nav_layout.addWidget(self.btn_adblock)
        self.nav_layout.addWidget(self.btn_developer)
        self.nav_layout.addWidget(self.btn_history)
        self.nav_layout.addWidget(self.btn_theme)

        # 2. Bookmarks Sub-strip
        self.bookmarks_bar = QHBoxLayout()
        self.bookmarks_bar.setContentsMargins(12, 2, 12, 4)
        self.bookmarks_bar.setSpacing(8)
        self.bookmarks_container = QWidget()
        self.bookmarks_container.setLayout(self.bookmarks_bar)

        # 3. Structural Splitter Framework
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # Left Side: History Panel
        self.history_panel = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(8, 8, 8, 8)
        self.history_list = QListWidget()
        self.btn_clear_history = QPushButton("Clear Caching History")
        self.history_layout.addWidget(self.history_list)
        self.history_layout.addWidget(self.btn_clear_history)
        self.history_panel.setLayout(self.history_layout)
        self.history_panel.setVisible(False)

        # Center Main: Document Mode Tab Widget with Customized Bar
        self.tabs = QTabWidget()
        self.custom_tab_bar = ChromiumTabBar(self)
        self.tabs.setTabBar(self.custom_tab_bar)
        self.tabs.setDocumentMode(True)

        # Right Side: Downloads Activity Monitor
        self.download_panel = QWidget()
        self.download_layout = QVBoxLayout()
        self.download_layout.setContentsMargins(8, 8, 8, 8)
        self.download_label = QLabel("<b>Active Downloads</b>")
        self.download_list = QListWidget()
        self.download_layout.addWidget(self.download_label)
        self.download_layout.addWidget(self.download_list)
        self.download_panel.setLayout(self.download_layout)
        self.download_panel.setVisible(False)

        self.splitter.addWidget(self.history_panel)
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.download_panel)
        self.splitter.setSizes([240, 960, 200]) 

        # 4. Status Systems Block
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(140)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Assemble Core Engine Layers
        self.main_layout.addLayout(self.nav_layout)
        self.main_layout.addWidget(self.bookmarks_container)
        self.main_layout.addWidget(self.splitter)

        # UI Element Event Connectors
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.custom_tab_bar.new_tab_clicked.connect(lambda: self.add_new_tab())
        
        self.btn_back.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.btn_home.clicked.connect(self.navigate_home)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        self.btn_history.clicked.connect(self.toggle_history_panel)
        self.btn_clear_history.clicked.connect(self.clear_history)
        self.history_list.itemDoubleClicked.connect(self.navigate_from_history)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_adblock.clicked.connect(self.toggle_adblock)
        self.btn_bookmark.clicked.connect(self.add_current_bookmark)
        self.btn_developer.clicked.connect(self.view_page_source)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_new_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+H"), self, self.toggle_history_panel)
        QShortcut(QKeySequence("F5"), self, lambda: self.current_browser().reload() if self.current_browser() else None)

    # --- Session Save & Crash Recovery Subsystem ---

    def save_session_state(self):
        """Serializes current runtime tabs onto disk layouts to facilitate automated reboots."""
        open_urls = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser and isinstance(browser, QWebEngineView):
                url_str = browser.url().toString()
                if url_str and "about:blank" not in url_str:
                    open_urls.append(url_str)
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump({"urls": open_urls}, f)
        except Exception:
            pass

    def restore_session(self):
        """Attempts to recompile tab arrays from last terminated execution."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    state = json.load(f)
                    urls = state.get("urls", [])
                    if urls:
                        for url in urls:
                            self.add_new_tab(QUrl(url), "Restoring...")
                        return
            except Exception:
                pass
        self.add_new_tab(QUrl(self.config.get("homepage")), "Google")

    # --- Integrated File Downloads Processing Pipeline ---

    def handle_download_intercept(self, download: QWebEngineDownloadRequest):
        suggested_path = os.path.join(os.path.expanduser("~"), "Downloads", download.suggestedFileName())
        file_path, _ = QFileDialog.getSaveFileName(self, "Download Target Destination", suggested_path)
        if file_path:
            download.setDownloadDirectory(os.path.dirname(file_path))
            download.setDownloadFileName(os.path.basename(file_path))
            download.accept()
            
            self.download_panel.setVisible(True)
            list_item_text = f"0% - {download.downloadFileName()}"
            self.download_list.addItem(list_item_text)
            item_index = self.download_list.count() - 1

            # Monitor background worker progression maps
            download.receivedBytesChanged.connect(
                lambda: self.update_download_progress_ui(download, item_index)
            )

    def update_download_progress_ui(self, download, index):
        pct = int((download.receivedBytes() / max(1, download.totalBytes())) * 100)
        self.download_list.item(index).setText(f"{pct}% - {download.downloadFileName()}")
        if pct >= 100:
            self.status_bar.showMessage(f"Download complete: {download.downloadFileName()}", 4000)

    # --- Developer Layout Tools ---

    def view_page_source(self):
        """Extracts source HTML DOM configurations directly into separate diagnostic windows."""
        browser = self.current_browser()
        if browser:
            browser.page().toHtml(self._render_source_window)

    def _render_source_window(self, html_content):
        source_window = QMainWindow(self)
        source_window.setWindowTitle("Source Inspector View")
        source_window.setGeometry(150, 150, 800, 600)
        text_area = QTextEdit()
        text_area.setPlainText(html_content)
        text_area.setReadOnly(True)
        source_window.setCentralWidget(text_area)
        source_window.show()

    # --- Standard Tab Framework Operations ---

    def add_new_tab(self, qurl=None, title="New Tab"):
        if qurl is None:
            qurl = QUrl(self.config.get("homepage"))

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        browser.customContextMenuRequested.connect(lambda pos: self.create_context_menu(pos, browser))

        i = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, b=browser: self.update_url_bar(qurl, b))
        browser.titleChanged.connect(lambda t, b=browser: self.update_tab_title(t, b))
        browser.loadProgress.connect(lambda p, b=browser: self.update_progress(p, b))
        browser.loadStarted.connect(lambda b=browser: self.handle_load_start(b))
        browser.loadFinished.connect(lambda ok, b=browser: self.handle_load_finished(ok, b))
        
        self.save_session_state()

    def close_tab(self, index):
        if self.tabs.count() < 2: return
        widget = self.tabs.widget(index)
        if widget: widget.deleteLater()
        self.tabs.removeTab(index)
        self.save_session_state()

    def current_browser(self) -> QWebEngineView:
        return self.tabs.currentWidget()

    def tab_changed(self, index):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())
            self.setWindowTitle(f"{self.tabs.tabText(index)} - Production Engine")

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            short_title = title[:14] + "..." if len(title) > 14 else title
            self.tabs.setTabText(index, short_title)

    def navigate_to_url(self):
        browser = self.current_browser()
        if not browser or not self.url_bar.text().strip(): return
        url = self.url_bar.text().strip()

        if "." not in url or " " in url:
            url = f"{self.config.get('search_engine')}{url.replace(' ', '+')}"
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        browser.setUrl(QUrl(url))

    def navigate_home(self):
        if self.current_browser(): 
            self.current_browser().setUrl(QUrl(self.config.get("homepage")))

    def update_url_bar(self, qurl, browser):
        url_str = qurl.toString()
        if browser == self.current_browser():
            self.url_bar.setText(url_str)
        if url_str and "about:blank" not in url_str:
            if not self.history_list_data or self.history_list_data[-1] != url_str:
                self.history_list_data.append(url_str)
                self.history_list.insertItem(0, url_str)
            self.save_session_state()

    # --- Sidebar Panels, Filtering, & Bookmarks Core ---

    def toggle_history_panel(self):
        self.history_panel.setVisible(not self.history_panel.isVisible())

    def clear_history(self):
        self.history_list_data.clear()
        self.history_list.clear()

    def navigate_from_history(self, item):
        if self.current_browser(): self.current_browser().setUrl(QUrl(item.text()))

    def add_current_bookmark(self):
        browser = self.current_browser()
        if browser:
            url = browser.url().toString()
            title = self.tabs.tabText(self.tabs.currentIndex()).replace("...", "")
            if url and url not in self.config["bookmarks"].values():
                self.config["bookmarks"][title] = url
                self.save_configuration()
                self.render_bookmarks_bar()

    def render_bookmarks_bar(self):
        while self.bookmarks_bar.count():
            item = self.bookmarks_bar.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for name, url in self.config["bookmarks"].items():
            btn = QPushButton(name[:12])
            btn.setToolTip(url)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, target_url=url: self.current_browser().setUrl(QUrl(target_url)))
            self.bookmarks_bar.addWidget(btn)
        self.bookmarks_bar.addStretch()

    def toggle_adblock(self):
        self.adblock_enabled = not self.adblock_enabled
        self.btn_adblock.setText("🛡️ AdBlock: ON" if self.adblock_enabled else "🛡️ AdBlock: OFF")
        self.save_configuration()
        if self.current_browser(): self.current_browser().reload()

    def run_security_filters(self, browser):
        if not self.adblock_enabled: return
        js = "document.querySelectorAll('amp-ad, ins.adsbygoogle, div[id^=\"div-gpt-ad\"]').forEach(el => el.remove());"
        browser.page().runJavaScript(js)

    def inject_web_dark_mode(self, browser):
        js_code = """
        (function() {
            var style = document.getElementById('dark-mode-style');
            if (%s) {
                var css = 'html { filter: invert(1) hue-rotate(180deg) !important; } img, video, canvas { filter: invert(1) hue-rotate(180deg) !important; }';
                if (!style) {
                    style = document.createElement('style'); style.id = 'dark-mode-style'; style.type = 'text/css';
                    style.appendChild(document.createTextNode(css)); (document.head || document.documentElement).appendChild(style);
                }
            } else if (style) { style.remove(); }
        })();
        """ % ("true" if self.is_dark_mode else "false")
        browser.page().runJavaScript(js_code)

    def create_context_menu(self, pos, browser):
        menu = QMenu(self)
        act_back = QAction("← Back", self)
        act_forward = QAction("→ Forward", self)
        act_reload = QAction("⟳ Reload", self)
        act_back.triggered.connect(browser.back)
        act_forward.triggered.connect(browser.forward)
        act_reload.triggered.connect(browser.reload)
        menu.addActions([act_back, act_forward, act_reload])
        menu.exec(browser.mapToGlobal(pos))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.save_configuration()
        self.apply_theme()
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser: self.inject_web_dark_mode(browser)

    def apply_theme(self):
        if self.is_dark_mode:
            self.btn_theme.setText("☀️")
            self.setStyleSheet("""
                QMainWindow { background-color: #1c1c1e; }
                QWidget { background-color: #2c2c2e; color: #f2f2f7; font-family: 'Segoe UI', Arial; font-size: 13px; }
                QLineEdit { background-color: #1c1c1e; color: #ffffff; border: 1px solid #3a3a3c; border-radius: 6px; padding: 6px; }
                QPushButton, QToolButton { background-color: #3a3a3c; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover, QToolButton:hover { background-color: #48484a; }
                QTabBar::tab { background: #2c2c2e; color: #aeaeae; padding: 8px 16px; border-right: 1px solid #1c1c1e; }
                QTabBar::tab:selected { background: #1c1c1e; color: #ffffff; }
                QStatusBar { background-color: #1c1c1e; color: #8e8e93; }
            """)
        else:
            self.btn_theme.setText("🌙")
            self.setStyleSheet("""
                QMainWindow { background-color: #f2f2f7; }
                QWidget { background-color: #ffffff; color: #1c1c1e; font-family: 'Segoe UI', Arial; font-size: 13px; }
                QLineEdit { background-color: #f2f2f7; color: #000000; border: 1px solid #d1d1d6; border-radius: 6px; padding: 6px; }
                QPushButton, QToolButton { background-color: #e5e5ea; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover, QToolButton:hover { background-color: #d1d1d6; }
                QTabBar::tab { background: #e5e5ea; color: #48484a; padding: 8px 16px; border-right: 1px solid #d1d1d6; }
                QTabBar::tab:selected { background: #ffffff; color: #000000; }
                QStatusBar { background-color: #f2f2f7; color: #8e8e93; }
            """)

    # --- Execution Caching States Handles ---

    def handle_load_start(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage("Negotiating handshake profile...")

    def update_progress(self, progress, browser):
        if browser == self.current_browser(): self.progress_bar.setValue(progress)
        self.run_security_filters(browser)

    def handle_load_finished(self, ok, browser):
        self.inject_web_dark_mode(browser)
        self.run_security_filters(browser)
        if browser == self.current_browser():
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready" if ok else "Navigation Aborted", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductionBrowser()
    window.show()
    sys.exit(app.exec())