from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStackedWidget, QFrame, QPushButton,
    QToolBar, QStyle, QApplication, QTabWidget, QComboBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QPalette, QColor
from .input_page import InputPage
from .sliding_panel import SlidingPanel
from .yogeswarananda_window import YogeswaranandaWindow
from .dasha_display import DashaDisplay
from .results_window import ResultsWindow
from .chart_widgets import NorthernChartWidget
from .eastern_chart_widget import EasternChartWidget
from .sidebar_toolbar import SidebarToolbar
import traceback

class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmic Calculator")
        self.setMinimumSize(1200, 800)
        
        # Initialize settings
        self.settings = QSettings('Cosmic', 'CosmicCalculator')
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create input page first (will be used by sidebar)
        self.input_page = InputPage()
        self.input_page.chart_calculated.connect(self.update_all_views)
        
        # Create and add sidebar with input page
        self.sidebar = SidebarToolbar(self, self.input_page)
        self.main_layout.addWidget(self.sidebar)
        
        # Connect input page signals
        self.input_page.panel_closed.connect(lambda: self.sidebar.toggle_input_panel())
        
        # Create container for main content
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_container)
        
        # Setup rest of UI in content container
        self.setup_ui()
        
        # Restore window state (after UI is setup)
        self.restore_window_state()
        
        # Apply theme
        self.apply_dark_theme()
        
        # Connect signals
        # self.input_page.panel_closed.connect(self.sidebar.collapse)
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Create splitter for main content
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.content_layout.addWidget(self.splitter)
        
        # Create right panel for chart display
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Modern look
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #3b3b3b;
                color: #ffffff;
                padding: 8px 16px;
                border: none;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: #505050;
            }
            QTabBar::tab:hover {
                background: #454545;
            }
        """)
        
        # Create and add the results window
        self.results_window = ResultsWindow()
        self.tab_widget.addTab(self.results_window, "Chart Results")
        
        # Create and add the dasha display
        self.dasha_widget = DashaDisplay()
        self.tab_widget.addTab(self.dasha_widget, "Dasha Periods")
        
        # Create and add the yogeswarananda window
        self.yogeswarananda_window = YogeswaranandaWindow()
        self.tab_widget.addTab(self.yogeswarananda_window, "Yogeswarananda")
        
        # Create chart widget container
        self.chart_container = QWidget()
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create chart widget
        self.chart_widget = EasternChartWidget(parent=self, input_page=self.input_page)
        chart_layout.addWidget(self.chart_widget)
        
        # Add chart tab
        chart_tab_index = self.tab_widget.addTab(self.chart_container, "Birth Chart")
        
        # Create and add style selector to tab bar
        self.style_combo = QComboBox()
        self.style_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.style_combo.setMinimumWidth(120)
        self.style_combo.setMaximumWidth(300)
        self.style_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #663399;
                border-radius: 4px;
                padding: 4px 25px 4px 10px;  
                background: #3b3b3b;
                color: white;
                margin: 4px;
            }
            QComboBox:hover {
                border: 1px solid #7a40b5;
                background: #454545;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                background: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #663399;
                margin-top: 3px;
                width: 14px;
            }
            QComboBox::down-arrow:hover {
                border-top: 8px solid #7a40b5;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
                selection-background-color: #663399;
                selection-color: white;
                border: 1px solid #663399;
                padding: 4px;
            }
        """)
        
        # Add the combo box to the tab bar
        self.tab_widget.setCornerWidget(self.style_combo, Qt.Corner.TopRightCorner)
        
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Store the tab indices for reference
        self.tab_indices = {
            'chart': self.tab_widget.indexOf(self.chart_container),
            'results': self.tab_widget.indexOf(self.results_window),
            'dasha': self.tab_widget.indexOf(self.dasha_widget),
            'yogeswarananda': self.tab_widget.indexOf(self.yogeswarananda_window)
        }
        
        right_layout.addWidget(self.tab_widget)
        
        # Add panels to splitter
        self.splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (proportional to window width)
        total_width = self.width()
        self.splitter.setSizes([int(total_width * 0.7)])
        
    def apply_dark_theme(self):
        """Apply theme to the application"""
        # Get theme from settings or use dark theme as default
        use_dark_theme = self.settings.value('use_dark_theme', True, type=bool)
        
        if use_dark_theme:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        else:
            palette = QApplication.style().standardPalette()
            
        QApplication.instance().setPalette(palette)

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        use_dark_theme = self.settings.value('use_dark_theme', True, type=bool)
        self.settings.setValue('use_dark_theme', not use_dark_theme)
        self.apply_dark_theme()
        
    def restore_window_state(self):
        """Restore window geometry and state from settings"""
        geometry = self.settings.value('window_geometry')
        if geometry:
            self.restoreGeometry(geometry)
            
        state = self.settings.value('window_state')
        if state:
            self.restoreState(state)
            
        splitter_sizes = self.settings.value('splitter_sizes')
        if splitter_sizes and hasattr(self, 'splitter'):
            try:
                self.splitter.setSizes([int(size) for size in splitter_sizes])
            except (TypeError, ValueError):
                # If conversion fails, use default sizes
                self.splitter.setSizes([700])
            
    def save_window_state(self):
        """Save window geometry and state to settings"""
        self.settings.setValue('window_geometry', self.saveGeometry())
        self.settings.setValue('window_state', self.saveState())
        if hasattr(self, 'splitter'):
            self.settings.setValue('splitter_sizes', self.splitter.sizes())
        
    def closeEvent(self, event):
        """Save window state before closing"""
        self.save_window_state()
        super().closeEvent(event)
        
    def update_all_views(self, chart_data):
        """Update all views with new chart data"""
        print("\nDEBUG - ModernMainWindow.update_all_views called")
        print(f"DEBUG - Chart data zodiac system: {chart_data.get('meta', {}).get('zodiac_system', 'Not specified')}")
        
        try:
            # Store current data
            self.current_data = chart_data
            
            # Update chart widget
            if self.chart_widget:
                print("DEBUG - Updating chart widget")
                self.chart_widget.update_data(chart_data)
                self.chart_widget.repaint()
                print("DEBUG - Chart widget updated and repainted")
            else:
                print("DEBUG - No chart widget available")
            
            # Update other views
            if self.results_window:
                print("DEBUG - Updating results window")
                self.results_window.update_data(chart_data)
            
            if self.dasha_widget:
                print("DEBUG - Updating dasha widget")
                self.dasha_widget.update_data(chart_data)
            
            if self.yogeswarananda_window:
                print("DEBUG - Updating yogeswarananda window")
                self.yogeswarananda_window.update_data(chart_data)
                
            print("DEBUG - All views updated")
            
        except Exception as e:
            print(f"ERROR in update_all_views: {str(e)}")
            traceback.print_exc()
            
    def switch_to_results(self):
        """Switch to results view"""
        self.tab_widget.setCurrentWidget(self.results_window)
        
    def switch_to_dashas(self):
        """Switch to dasha periods view"""
        self.tab_widget.setCurrentWidget(self.dasha_widget)
        
    def switch_to_yogeswarananda(self):
        """Switch to yogeswarananda view"""
        self.tab_widget.setCurrentWidget(self.yogeswarananda_window)
        
    def change_chart_style(self, style=None):
        """Change the chart style between Northern and Eastern"""
        if not style:
            style = self.style_combo.currentText()
            
        print(f"\nDEBUG - Changing chart style to: {style}")
            
        # Store current data
        current_data = None
        if hasattr(self, 'current_data'):
            current_data = self.current_data
            print(f"Current data available: {bool(current_data)}")
            
        # Remove current chart widget
        if self.chart_widget:
            self.chart_widget.deleteLater()
        
        # Create new chart widget based on selection
        if "Eastern" in style:
            print("Creating Eastern Chart Widget")
            self.chart_widget = EasternChartWidget(parent=self, input_page=self.input_page)
        else:
            print("Creating Northern Chart Widget")
            self.chart_widget = NorthernChartWidget(parent=self, input_page=self.input_page)
        
        # Add to layout and update with current data
        self.chart_container.layout().addWidget(self.chart_widget)
        if current_data:
            print("Updating new chart widget with current data")
            self.chart_widget.update_data(current_data)
            self.chart_widget.repaint()  # Force immediate repaint
            print("New chart widget updated and repainted")
            
    def update_chart(self, chart_data):
        """Update the chart with new data"""
        if hasattr(self, 'chart_widget'):
            self.chart_widget.update_data(chart_data)
            self.chart_widget.update()
            self.tab_widget.setCurrentWidget(self.chart_container)

    def on_tab_changed(self, index):
        """Handle tab changes"""
        # Disconnect any existing connections
        try:
            self.style_combo.currentTextChanged.disconnect()
        except:
            pass
            
        # Clear current items
        self.style_combo.clear()
        
        # Show combo box for all tabs
        self.style_combo.setVisible(True)
        
        if index == self.tab_indices['chart']:
            # Chart tab options
            self.style_combo.addItems(["Eastern Chart", "Northern Chart"])
            self.style_combo.setCurrentText("Eastern Chart" if isinstance(self.chart_widget, EasternChartWidget) else "Northern Chart")
            self.style_combo.currentTextChanged.connect(self.change_chart_style)
            self.style_combo.setToolTip("Select chart style")
            
        elif index == self.tab_indices['results']:
            # Results tab options
            self.style_combo.addItems(["View Options", "Export PDF", "Print Results"])
            self.style_combo.currentTextChanged.connect(self.handle_results_options)
            self.style_combo.setToolTip("Results options")
            
        elif index == self.tab_indices['dasha']:
            # Dasha tab options
            self.style_combo.addItems(["All Dashas", "Current Dasha", "Future Dashas", "Export Timeline"])
            self.style_combo.currentTextChanged.connect(self.handle_dasha_options)
            self.style_combo.setToolTip("Dasha view options")
            
        elif index == self.tab_indices['yogeswarananda']:
            # Yogeswarananda tab options
            self.style_combo.addItems(["Show Calculations", "Export Analysis", "Print Report"])
            self.style_combo.currentTextChanged.connect(self.handle_yogeswarananda_options)
            self.style_combo.setToolTip("Yogeswarananda options")
            
    def handle_results_options(self, option):
        """Handle options selected in the results tab"""
        if option == "Export PDF":
            # Add PDF export functionality
            pass
        elif option == "Print Results":
            # Add print functionality
            pass
        # Reset to default after handling
        self.style_combo.setCurrentIndex(0)
        
    def handle_dasha_options(self, option):
        """Handle options selected in the dasha tab"""
        if option == "All Dashas":
            self.dasha_widget.expand_all_items()
        elif option == "Current Dasha":
            self.dasha_widget.show_current_dasha()
        elif option == "Future Dashas":
            self.dasha_widget.show_future_dashas()
        elif option == "Export Timeline":
            # TODO: Implement export timeline functionality
            pass
        # Reset to default after handling
        self.style_combo.setCurrentIndex(0)
        
    def handle_yogeswarananda_options(self, option):
        """Handle options selected in the yogeswarananda tab"""
        if option == "Show Calculations":
            # This will be handled by the existing show_calculations method
            self.yogeswarananda_window.toggle_calculations()
        elif option == "Export Analysis":
            # Add export functionality
            pass
        elif option == "Print Report":
            # Add print functionality
            pass
        # Reset to default after handling
        self.style_combo.setCurrentIndex(0)
