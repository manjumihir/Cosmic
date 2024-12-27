from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BaseSidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setup_ui()
        
    def setup_ui(self):
        # Create a scroll area for the content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create the content widget
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        
        scroll.setWidget(content)
        self.main_layout.addWidget(scroll)
        
    def add_section(self, title):
        # Add a section header
        header = QLabel(title)
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff; padding: 5px;")
        self.content_layout.addWidget(header)
        
        # Create a grid layout for the section content
        grid = QGridLayout()
        grid.setSpacing(10)
        self.content_layout.addLayout(grid)
        return grid
        
    def add_button(self, grid, text, row, col, callback=None):
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setMinimumHeight(40)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b3b;
                border: none;
                border-radius: 5px;
                color: #ffffff;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
        """)
        if callback:
            button.clicked.connect(callback)
        grid.addWidget(button, row, col)
        return button

class ChartsSidePanel(BaseSidePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_charts_ui()
        
    def setup_charts_ui(self):
        # Divisional Charts Section
        div_grid = self.add_section("Divisional Charts")
        charts = ["D-1", "D-2", "D-3", "D-4", "D-7", "D-9", "D-10", "D-12", "D-16", "D-20", "D-24", "D-27", "D-30", "D-40", "D-45", "D-60"]
        for i, chart in enumerate(charts):
            self.add_button(div_grid, chart, i // 4, i % 4)
            
        # Specialized Charts Section
        spec_grid = self.add_section("Specialized Charts")
        spec_charts = ["Chalit Chart", "Bhava Chalit", "Moon Chart", "Navamsa", "Composite"]
        for i, chart in enumerate(spec_charts):
            self.add_button(spec_grid, chart, i // 3, i % 3)
            
        # Transit Charts Section
        transit_grid = self.add_section("Transit Charts")
        transit_types = ["Current Transit", "Date Transit", "Progressive", "Solar Return"]
        for i, transit in enumerate(transit_types):
            self.add_button(transit_grid, transit, i // 2, i % 2)

class HelpSidePanel(BaseSidePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_help_ui()
        
    def setup_help_ui(self):
        # Quick Start Section
        quick_grid = self.add_section("Quick Start")
        quick_topics = ["Getting Started", "Basic Navigation", "Chart Reading", "Calculations"]
        for i, topic in enumerate(quick_topics):
            self.add_button(quick_grid, topic, i, 0)
            
        # Documentation Section
        doc_grid = self.add_section("Documentation")
        doc_topics = ["User Guide", "Chart Types", "Calculations", "API Reference"]
        for i, topic in enumerate(doc_topics):
            self.add_button(doc_grid, topic, i // 2, i % 2)
            
        # Support Section
        support_grid = self.add_section("Support")
        support_options = ["FAQ", "Contact Support", "Report Bug", "Feature Request"]
        for i, option in enumerate(support_options):
            self.add_button(support_grid, option, i // 2, i % 2)

class PreferencesSidePanel(BaseSidePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_preferences_ui()
        
    def setup_preferences_ui(self):
        # Display Settings Section
        display_grid = self.add_section("Display Settings")
        display_options = ["Theme", "Chart Style", "Font Size", "Colors", "Layout"]
        for i, option in enumerate(display_options):
            self.add_button(display_grid, option, i // 2, i % 2)
            
        # Calculation Settings Section
        calc_grid = self.add_section("Calculation Settings")
        calc_options = ["Ayanamsa", "House System", "Zodiac Type", "Aspects"]
        for i, option in enumerate(calc_options):
            self.add_button(calc_grid, option, i // 2, i % 2)
            
        # Advanced Settings Section
        adv_grid = self.add_section("Advanced Settings")
        adv_options = ["API Configuration", "Data Sources", "Cache Settings", "Export Options"]
        for i, option in enumerate(adv_options):
            self.add_button(adv_grid, option, i // 2, i % 2)

class ReportSidePanel(BaseSidePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_report_ui()
        
    def setup_report_ui(self):
        # Basic Reports Section
        basic_grid = self.add_section("Basic Reports")
        basic_reports = ["Birth Chart", "Planetary Positions", "House Positions", "Aspects"]
        for i, report in enumerate(basic_reports):
            self.add_button(basic_grid, report, i // 2, i % 2)
            
        # Advanced Reports Section
        adv_grid = self.add_section("Advanced Reports")
        adv_reports = ["Dasha Analysis", "Transit Report", "Yogas", "Strength Analysis"]
        for i, report in enumerate(adv_reports):
            self.add_button(adv_grid, report, i // 2, i % 2)
            
        # Custom Reports Section
        custom_grid = self.add_section("Custom Reports")
        custom_options = ["Create New", "Load Template", "Export Report", "Share Report"]
        for i, option in enumerate(custom_options):
            self.add_button(custom_grid, option, i // 2, i % 2)

class ResearchSidePanel(BaseSidePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_research_ui()
        
    def setup_research_ui(self):
        # Data Analysis Section
        analysis_grid = self.add_section("Data Analysis")
        analysis_options = ["Pattern Search", "Statistical Analysis", "Correlation Study", "Event Analysis"]
        for i, option in enumerate(analysis_options):
            self.add_button(analysis_grid, option, i // 2, i % 2)
            
        # Research Tools Section
        tools_grid = self.add_section("Research Tools")
        tool_options = ["Data Collection", "Chart Comparison", "Time Search", "Location Search"]
        for i, option in enumerate(tool_options):
            self.add_button(tools_grid, option, i // 2, i % 2)
            
        # Results Section
        results_grid = self.add_section("Results")
        result_options = ["Save Results", "Export Data", "Generate Report", "Share Findings"]
        for i, option in enumerate(result_options):
            self.add_button(results_grid, option, i // 2, i % 2)
