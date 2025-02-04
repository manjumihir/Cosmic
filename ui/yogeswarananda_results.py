from PyQt6.QtWidgets import (QWidget, QTextBrowser, QScrollArea, 
                           QWidget, QVBoxLayout, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class YogeswaranandaResultsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use QTextBrowser instead of QTextEdit for better HTML rendering and scrolling
        self.results_text = QTextBrowser()
        self.results_text.setOpenExternalLinks(False)
        self.results_text.setFont(QFont("Segoe UI", 10))
        
        # Style the widget
        self.results_text.setStyleSheet("""
            QTextBrowser {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                padding: 20px;
            }
            QScrollBar:vertical {
                background: #1A1A1A;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 20px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #1A1A1A;
                height: 15px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #404040;
                min-width: 20px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Add to layout
        layout.addWidget(self.results_text)
        
    def set_html_content(self, html_content):
        """Set the HTML content of the results window"""
        self.results_text.setHtml(html_content)
