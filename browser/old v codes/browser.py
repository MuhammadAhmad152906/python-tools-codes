import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and initial dimensions
        self.setWindowTitle("Simple Python Web Browser")
        self.setGeometry(100, 100, 1024, 768)

        # Main layout container
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Create navigation bar layout
        self.nav_layout = QHBoxLayout()

        # Navigation buttons
        self.btn_back = QPushButton("← Back")
        self.btn_forward = QPushButton("Forward →")
        self.btn_reload = QPushButton("🔄 Reload")
        self.btn_go = QPushButton("Go")

        # URL Address Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL here (e.g., https://google.com)")

        # Assemble the navigation bar
        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_reload)
        self.nav_layout.addWidget(self.url_bar)
        self.nav_layout.addWidget(self.btn_go)

        # Create the Web View component
        self.browser = QWebEngineView()
        
        # Add navigation and browser components to the main layout
        self.layout.addLayout(self.nav_layout)
        self.layout.addWidget(self.browser)

        # Connect button signals to browser functions
        self.btn_back.clicked.connect(self.browser.back)
        self.btn_forward.clicked.connect(self.browser.forward)
        self.btn_reload.clicked.connect(self.browser.reload)
        self.btn_go.clicked.connect(self.navigate_to_url)
        
        # Allow pressing 'Enter' in the URL bar to navigate
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Update the address bar text automatically when the page changes
        self.browser.urlChanged.connect(self.update_url_bar)

        # Set default home page
        self.browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        """Navigates to the URL entered in the address bar."""
        url = self.url_bar.text().strip()

        # Automatically prepend 'http://' if the user forgets it
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        self.browser.setUrl(QUrl(url))

    def update_url_bar(self, qurl):
        """Updates the address bar with the current active URL."""
        self.url_bar.setText(qurl.toString())


# Application initialization
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyBrowser()
    window.show()
    sys.exit(app.exec())