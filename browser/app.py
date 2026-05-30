import sys
import os
import json

# Force QtWebEngine to avoid GPU shader issues by using software OpenGL
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
os.environ["QT_OPENGL"] = "software"

from PyQt6.QtCore import QCoreApplication, QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QTabWidget, QProgressBar, 
    QStatusBar, QListWidget, QSplitter, QMenu, QFileDialog, 
    QToolButton, QTabBar, QLabel, QTextEdit, QComboBox, QSlider
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class FullScreenTabMenu(QWidget):
    """Full-screen modern dashboard overlay to manage active browser tabs."""
    def __init__(self, parent=None, active_tabs_list=None, current_index=0, switch_callback=None):
        super().__init__(parent)
        self.switch_callback = switch_callback
        
        # Overlay setups to span across window boundaries flawlessly
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(100, 80, 100, 80)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Transparent visual container background panel 
        bg_panel = QWidget(self)
        bg_panel.setObjectName("MenuPanel")
        
        # Apply strict glassmorphism-like styling to the container panel matching browser mode 
        bg_panel.setStyleSheet("""
            QWidget#MenuPanel {
                background-color: rgba(30, 30, 30, 0.95);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
        """)
        
        panel_layout = QVBoxLayout(bg_panel)
        panel_layout.setContentsMargins(40, 40, 40, 40)
        panel_layout.setSpacing(20)
        
        # Overlay Header Label
        title = QLabel("Global Workspace Engine — Active Streams", bg_panel)
        title.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; font-family: 'Segoe UI';")
        panel_layout.addWidget(title)
        
        # Active Elements Registry List View
        self.list_widget = QListWidget(bg_panel)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #e5e5ea;
                font-size: 16px;
                font-family: 'Segoe UI';
            }
            QListWidget::item {
                padding: 14px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #0a84ff;
                color: #ffffff;
            }
        """)
        
        if active_tabs_list:
            for index, name in enumerate(active_tabs_list):
                self.list_widget.addItem(f"Stream Line {index + 1} :  {name}")
            
            # Highlight currently selected workspace context item
            if 0 <= current_index < len(active_tabs_list):
                self.list_widget.setCurrentRow(current_index)
                
        self.list_widget.itemClicked.connect(self.handle_selection)
        panel_layout.addWidget(self.list_widget)
        
        # Return Escape Control Button Action Strip
        close_btn = QPushButton("Return to Pipeline Workspace (Esc)", bg_panel)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton { 
                background-color: #ff3b30; 
                color: white; 
                border-radius: 6px; 
                padding: 12px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e03b24; }
        """)
        close_btn.clicked.connect(self.close)
        panel_layout.addWidget(close_btn)
        
        main_layout.addWidget(bg_panel)
        bg_panel.setMinimumSize(700, 500)

    def handle_selection(self, item):
        try:
            text = item.text()
            idx = int(text.split("Stream Line ")[1].split(" :")[0]) - 1
            if self.switch_callback:
                self.switch_callback(idx)
        except Exception:
            pass
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)


class ChromiumTabBar(QTabBar):
    """Custom tab component mirroring modern premium layout mechanics."""
    new_tab_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectionBehavior.SelectPreviousTab)
        
        self.add_btn = QToolButton(self)
        self.add_btn.setText("＋")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.new_tab_clicked.emit)
        self.add_btn.setObjectName("FloatingAddButton")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_add_button()

    def tabInserted(self, index):
        super().tabInserted(index)
        self.reposition_add_button()

    def tabRemoved(self, index):
        super().tabRemoved(index)
        self.reposition_add_button()

    def reposition_add_button(self):
        """Calculates exact runtime spatial geometry offsets to float adding action button at the absolute end."""
        if self.count() > 0:
            total_tabs_width = 0
            for i in range(self.count()):
                total_tabs_width += self.tabRect(i).width()
            
            # Position safely past the right edge bounding box boundary limits
            available_width = self.width()
            target_x = min(total_tabs_width + 8, available_width - 35)
            
            self.add_btn.setGeometry(target_x, 6, 28, 24)
            self.add_btn.show()
        else:
            self.add_btn.setGeometry(8, 6, 28, 24)
            self.add_btn.show()


class PremiumBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Premium Enterprise Browser")
        self.setGeometry(50, 50, 1500, 950)
        self.overlay_menu = None

        # File Directories & Settings Cache Management
        self.storage_path = os.path.join(os.getcwd(), ".premium_browser_data")
        os.makedirs(self.storage_path, exist_ok=True)
        self.config_file = os.path.join(self.storage_path, "config.json")
        self.session_file = os.path.join(self.storage_path, "session.json")
        
        # Operational Engines Setup
        self.config = self.load_configuration()
        self.history_list_data = []
        self.is_dark_mode = self.config.get("dark_mode", False)
        self.adblock_enabled = self.config.get("adblock", True)
        self.is_tiled_mode = False

        # Pre-defined Premium User Agents
        self.user_agents = {
            "💻 Desktop (Default)": "",
            "📱 iPhone / iOS": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "🤖 Android Mobile": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
        }

        self.setup_persistent_profile()
        self.init_ui()
        self.setup_shortcuts()
        self.render_bookmarks_bar()
        self.apply_theme()

        # Session Restoration Engine
        self.restore_session()

    def load_configuration(self):
        default_config = {
            "homepage": "https://www.google.com",
            "search_engine": "https://www.google.com/search?q=",
            "dark_mode": False,
            "adblock": True,
            "bookmarks": {"Google": "https://www.google.com", "GitHub": "https://github.com", "YouTube": "https://youtube.com"}
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f: return json.load(f)
            except Exception: return default_config
        return default_config

    def save_configuration(self):
        self.config["dark_mode"] = self.is_dark_mode
        self.config["adblock"] = self.adblock_enabled
        with open(self.config_file, 'w') as f: json.dump(self.config, f, indent=4)

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

        # 1. Navigation Panel Toolbar
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(10, 8, 10, 6)
        self.nav_layout.setSpacing(8)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("⟳")
        self.btn_home = QPushButton("🏠")
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter secure URL, destination hash, or search index mapping...")
        
        # Premium Operational Buttons
        self.btn_tile = QPushButton("🪟 Tile: OFF")
        self.btn_bookmark = QPushButton("⭐")
        self.btn_adblock = QPushButton("🛡️ AdBlock: ON" if self.adblock_enabled else "🛡️ AdBlock: OFF")
        
        # User-Agent Profile Dropdown
        self.ua_combobox = QComboBox()
        self.ua_combobox.addItems(list(self.user_agents.keys()))
        self.ua_combobox.currentIndexChanged.connect(self.change_user_agent_profile)

        self.tab_size_combo = QComboBox()
        self.tab_size_combo.addItems(["Compact", "Normal", "Wide"])
        self.tab_size_combo.setCurrentIndex(1)
        self.tab_size_combo.currentIndexChanged.connect(self.change_tab_size)

        # Tab height control (adjusts the tab bar height)
        self.tab_height_label = QLabel("Tab H:")
        self.tab_height_label.setToolTip("Adjust tab bar height")
        self.tab_height_slider = QSlider(Qt.Orientation.Horizontal)
        self.tab_height_slider.setRange(24, 80)
        self.tab_height_slider.setValue(36)
        self.tab_height_slider.setFixedWidth(110)
        self.tab_height_slider.valueChanged.connect(self.change_tab_height)

        self.btn_menu_overlay = QPushButton("🗂️ Dashboard")
        self.btn_developer = QPushButton("📄 Code")
        self.btn_history = QPushButton("📜 History")
        self.btn_theme = QPushButton("🌙")

        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_reload)
        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.url_bar)
        self.nav_layout.addWidget(self.btn_tile)
        self.nav_layout.addWidget(self.btn_bookmark)
        self.nav_layout.addWidget(self.btn_adblock)
        self.nav_layout.addWidget(self.ua_combobox)
        self.nav_layout.addWidget(self.tab_size_combo)
        self.nav_layout.addWidget(self.tab_height_label)
        self.nav_layout.addWidget(self.tab_height_slider)
        self.nav_layout.addWidget(self.btn_menu_overlay)
        self.nav_layout.addWidget(self.btn_developer)
        self.nav_layout.addWidget(self.btn_history)
        self.nav_layout.addWidget(self.btn_theme)

        # 2. Bookmarks Sub-strip Container
        self.bookmarks_bar = QHBoxLayout()
        self.bookmarks_bar.setContentsMargins(12, 2, 12, 4)
        self.bookmarks_bar.setSpacing(8)
        self.bookmarks_container = QWidget()
        self.bookmarks_container.setLayout(self.bookmarks_bar)

        # 3. Dynamic Structural Master Layout Splitter
        self.master_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.master_splitter.setHandleWidth(1)
        
        # Left Panel: History
        self.history_panel = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(8, 8, 8, 8)
        self.history_list = QListWidget()
        self.btn_clear_history = QPushButton("Clear Session Cache")
        self.history_layout.addWidget(self.history_list)
        self.history_layout.addWidget(self.btn_clear_history)
        self.history_panel.setLayout(self.history_layout)
        self.history_panel.setVisible(False)

        # Center Container: Handles Split Layout System
        self.center_container = QWidget()
        self.center_layout = QHBoxLayout()
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)
        self.center_container.setLayout(self.center_layout)

        # Document Tab Bar Widget
        self.tabs = QTabWidget()
        self.custom_tab_bar = ChromiumTabBar(self)
        self.tabs.setTabBar(self.custom_tab_bar)
        self.change_tab_size()
        self.change_tab_height()
        self.tabs.setDocumentMode(True)
        self.center_layout.addWidget(self.tabs)

        # Hidden Secondary View window loop utilized exclusively for split screen tiling
        self.tiled_view = QWebEngineView()
        self.tiled_view.setVisible(False)
        self.center_layout.addWidget(self.tiled_view)

        # Right Panel: File Downloads Track Activity List
        self.download_panel = QWidget()
        self.download_layout = QVBoxLayout()
        self.download_layout.setContentsMargins(8, 8, 8, 8)
        self.download_label = QLabel("<b>Active Pipelines</b>")
        self.download_list = QListWidget()
        self.download_layout.addWidget(self.download_label)
        self.download_layout.addWidget(self.download_list)
        self.download_panel.setLayout(self.download_layout)
        self.download_panel.setVisible(False)

        self.master_splitter.addWidget(self.history_panel)
        self.master_splitter.addWidget(self.center_container)
        self.master_splitter.addWidget(self.download_panel)
        self.master_splitter.setSizes([220, 1080, 200]) 

        # 4. Premium Live Metrics Status Bar Monitor Layout
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.lbl_performance = QLabel("Network Status: Optimized | Engine: V8 Stable  ")
        self.status_bar.addPermanentWidget(self.lbl_performance)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(140)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Build Main Frame Tree
        self.main_layout.addLayout(self.nav_layout)
        self.main_layout.addWidget(self.bookmarks_container)
        self.main_layout.addWidget(self.master_splitter)

        # Direct Signal Linkage Mappings
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.custom_tab_bar.new_tab_clicked.connect(lambda: self.add_new_tab())
        
        self.btn_back.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.btn_home.clicked.connect(self.navigate_home)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        self.btn_tile.clicked.connect(self.toggle_split_screen_tiling)
        self.btn_menu_overlay.clicked.connect(self.show_full_screen_menu)
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
        QShortcut(QKeySequence("Ctrl+M"), self, self.show_full_screen_menu)
        QShortcut(QKeySequence("F5"), self, lambda: self.current_browser().reload() if self.current_browser() else None)

    def resizeEvent(self, event):
        """Maintains overlay coverage across active layout resize signals dynamically."""
        super().resizeEvent(event)
        if self.overlay_menu and self.overlay_menu.isVisible():
            self.overlay_menu.setGeometry(self.rect())

    def show_full_screen_menu(self):
        """Constructs and displays the dynamic full screen workspace manager overlay view."""
        tab_titles = [self.tabs.tabText(i) for i in range(self.tabs.count())]
        current_idx = self.tabs.currentIndex()
        
        self.overlay_menu = FullScreenTabMenu(
            parent=self, 
            active_tabs_list=tab_titles, 
            current_index=current_idx,
            switch_callback=self.tabs.setCurrentIndex
        )
        self.overlay_menu.setGeometry(self.rect())
        self.overlay_menu.show()
        self.overlay_menu.raise_()

    # --- Premium Feature: Split-Screen Tab Tiling ---

    def toggle_split_screen_tiling(self):
        """Splits the main workspace to render two active website instances side-by-side."""
        self.is_tiled_mode = not self.is_tiled_mode
        if self.is_tiled_mode:
            self.btn_tile.setText("🪟 Tile: ON")
            self.btn_tile.setStyleSheet("background-color: #0a84ff; color: white;")
            
            # Anchor secondary view to a search panel or parallel tab reference target
            self.tiled_view.setUrl(QUrl("https://www.google.com"))
            self.tiled_view.setVisible(True)
            self.center_layout.setSizes([750, 750]) if hasattr(self.center_layout, 'setSizes') else None
        else:
            self.btn_tile.setText("🪟 Tile: OFF")
            self.btn_tile.setStyleSheet("")
            self.tiled_view.setVisible(False)

    # --- Premium Feature: Dynamic User-Agent Switcher Engine ---

    def change_user_agent_profile(self):
        """Forces the active rendering framework to spoof target browser identities on runtime loops."""
        selected_key = self.ua_combobox.currentText()
        agent_string = self.user_agents[selected_key]
        
        # Injects profile rules over current default HTTP Request Header maps
        QWebEngineProfile.defaultProfile().setHttpUserAgent(agent_string)
        self.lbl_performance.setText(f"Profile: {selected_key.split()[1]} Mode  ")
        
        # Soft-reload view frames to apply modifications instantly
        if self.current_browser(): self.current_browser().reload()
        if self.tiled_view.isVisible(): self.tiled_view.reload()

    def change_tab_size(self):
        """Updates tab width sizing for the custom browser tab bar."""
        size_map = {
            0: 90,   # Compact
            1: 130,  # Normal
            2: 180   # Wide
        }
        min_width = size_map.get(self.tab_size_combo.currentIndex(), 130)
        self.custom_tab_bar.setStyleSheet(
            f"QTabBar::tab {{ min-width: {min_width}px; padding: 8px 14px; }}"
        )
        self.custom_tab_bar.updateGeometry()
        self.custom_tab_bar.repaint()

    def change_tab_height(self):
        """Updates the tab bar height based on the slider value."""
        try:
            h = int(self.tab_height_slider.value())
        except Exception:
            h = 36
        # Set explicit fixed height on the tab bar and adjust layout
        self.custom_tab_bar.setFixedHeight(h)
        # Provide a small stylesheet tweak for vertical padding
        self.custom_tab_bar.setStyleSheet(
            self.custom_tab_bar.styleSheet() + f"\nQTabBar::tab {{ padding-top: {max(2, (h-20)//4)}px; padding-bottom: {max(2, (h-20)//4)}px; }}"
        )
        self.custom_tab_bar.updateGeometry()
        self.custom_tab_bar.repaint()

    # --- Crash Protection Session Operations ---

    def save_session_state(self):
        open_urls = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser and isinstance(browser, QWebEngineView):
                url_str = browser.url().toString()
                if url_str and "about:blank" not in url_str: open_urls.append(url_str)
        try:
            with open(self.session_file, 'w') as f: json.dump({"urls": open_urls}, f)
        except Exception: pass

    def restore_session(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    urls = json.load(f).get("urls", [])
                    if urls:
                        for url in urls: self.add_new_tab(QUrl(url), "Restoring Core...")
                        return
            except Exception: pass
        self.add_new_tab(QUrl(self.config.get("homepage")), "Google")

    # --- File System Pipeline Controls ---

    def handle_download_intercept(self, download: QWebEngineDownloadRequest):
        suggested_path = os.path.join(os.path.expanduser("~"), "Downloads", download.suggestedFileName())
        file_path, _ = QFileDialog.getSaveFileName(self, "Download Routing Pipeline File As", suggested_path)
        if file_path:
            download.setDownloadDirectory(os.path.dirname(file_path))
            download.setDownloadFileName(os.path.basename(file_path))
            download.accept()
            
            self.download_panel.setVisible(True)
            self.download_list.addItem(f"0% - {download.downloadFileName()}")
            item_idx = self.download_list.count() - 1
            download.receivedBytesChanged.connect(lambda: self.update_download_ui(download, item_idx))

    def update_download_ui(self, download, idx):
        pct = int((download.receivedBytes() / max(1, download.totalBytes())) * 100)
        self.download_list.item(idx).setText(f"{pct}% - {download.downloadFileName()}")

    # --- Operational Workspace Elements ---

    def view_page_source(self):
        browser = self.current_browser()
        if browser: browser.page().toHtml(self._render_source_window)

    def _render_source_window(self, html):
        source_window = QMainWindow(self)
        source_window.setWindowTitle("Advanced Code Inspector")
        source_window.setGeometry(150, 150, 850, 650)
        txt = QTextEdit()
        txt.setPlainText(html)
        txt.setReadOnly(True)
        source_window.setCentralWidget(txt)
        source_window.show()

    def add_new_tab(self, qurl=None, title="New Tab"):
        if qurl is None: qurl = QUrl(self.config.get("homepage"))
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
            self.setWindowTitle(f"{self.tabs.tabText(index)} - Premium Enterprise Framework")

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
        if self.current_browser(): self.current_browser().setUrl(QUrl(self.config.get("homepage")))

    def update_url_bar(self, qurl, browser):
        url_str = qurl.toString()
        if browser == self.current_browser(): self.url_bar.setText(url_str)
        if url_str and "about:blank" not in url_str:
            if not self.history_list_data or self.history_list_data[-1] != url_str:
                self.history_list_data.append(url_str)
                self.history_list.insertItem(0, url_str)
            self.save_session_state()

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
        if self.tiled_view.isVisible(): self.inject_web_dark_mode(self.tiled_view)

    def apply_theme(self):
        if self.is_dark_mode:
            self.btn_theme.setText("☀️")
            self.setStyleSheet("""
                QMainWindow { background-color: #1c1c1e; }
                QWidget { background-color: #2c2c2e; color: #f2f2f7; font-family: 'Segoe UI', Arial; font-size: 13px; }
                QLineEdit, QComboBox { background-color: #1c1c1e; color: #ffffff; border: 1px solid #3a3a3c; border-radius: 6px; padding: 5px; }
                QPushButton, QToolButton { background-color: #3a3a3c; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover, QToolButton:hover { background-color: #48484a; }
                QTabBar::tab { background: #2c2c2e; color: #aeaeae; padding: 8px 16px; border-right: 1px solid #1c1c1e; }
                QTabBar::tab:selected { background: #1c1c1e; color: #ffffff; }
                QStatusBar { background-color: #1c1c1e; color: #8e8e93; }
                QToolButton#FloatingAddButton {
                    background-color: #0a84ff;
                    color: white;
                    font-size: 14px;
                    border-radius: 4px;
                }
                QToolButton#FloatingAddButton:hover {
                    background-color: #0056b3;
                }
            """)
        else:
            self.btn_theme.setText("🌙")
            self.setStyleSheet("""
                QMainWindow { background-color: #f2f2f7; }
                QWidget { background-color: #ffffff; color: #1c1c1e; font-family: 'Segoe UI', Arial; font-size: 13px; }
                QLineEdit, QComboBox { background-color: #f2f2f7; color: #000000; border: 1px solid #d1d1d6; border-radius: 6px; padding: 5px; }
                QPushButton, QToolButton { background-color: #e5e5ea; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover, QToolButton:hover { background-color: #d1d1d6; }
                QTabBar::tab { background: #e5e5ea; color: #48484a; padding: 8px 16px; border-right: 1px solid #d1d1d6; }
                QTabBar::tab:selected { background: #ffffff; color: #000000; }
                QStatusBar { background-color: #f2f2f7; color: #8e8e93; }
                QToolButton#FloatingAddButton {
                    background-color: #0a84ff;
                    color: white;
                    font-size: 14px;
                    border-radius: 4px;
                }
                QToolButton#FloatingAddButton:hover {
                    background-color: #0056b3;
                }
            """)

    # --- Loading Signal Pipeline Loops ---

    def handle_load_start(self, browser):
        if browser == self.current_browser():
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage("Encrypting payload handshake channels...")

    def update_progress(self, progress, browser):
        if browser == self.current_browser(): self.progress_bar.setValue(progress)
        self.run_security_filters(browser)

    def handle_load_finished(self, ok, browser):
        self.inject_web_dark_mode(browser)
        self.run_security_filters(browser)
        if browser == self.current_browser():
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Secure Ready", 2000)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
    app = QApplication(sys.argv)
    window = PremiumBrowser()
    window.show()
    sys.exit(app.exec())