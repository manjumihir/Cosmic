from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QWidget
from PyQt6.QtCore import Qt
from .chart_widgets import NorthernChartWidget
from .eastern_chart_widget import EasternChartWidget

class ChartDialog(QDialog):
    def __init__(self, chart_widget=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Birth Chart")
        self.setMinimumSize(600, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create chart style selector
        style_layout = QHBoxLayout()
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Northern Chart", "Eastern Chart"])
        self.style_combo.currentTextChanged.connect(self.change_chart_style)
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()
        layout.addLayout(style_layout)
        
        # Create or use provided chart widget
        if chart_widget is None:
            self.chart_widget = NorthernChartWidget(parent=self)
        else:
            self.chart_widget = chart_widget
        
        layout.addWidget(self.chart_widget)
        self.setLayout(layout)
        
        # Make sure the dialog stays on top using the correct flag
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    
    def change_chart_style(self, style):
        # Store current data if it exists
        current_data = None
        if hasattr(self.chart_widget, 'chart_data'):
            current_data = self.chart_widget.chart_data
        
        # Remove current chart widget
        if self.chart_widget:
            self.chart_widget.setParent(None)
            self.chart_widget.deleteLater()
        
        # Create new chart widget based on selection
        if style == "Eastern Chart":
            self.chart_widget = EasternChartWidget(parent=self)
        else:
            self.chart_widget = NorthernChartWidget(parent=self)
        
        # Restore data if it existed
        if current_data:
            self.chart_widget.update_data(current_data)
        
        # Add new widget to layout
        self.layout().addWidget(self.chart_widget)
    
    def update_data(self, chart_data):
        """Update the chart with new data"""
        if self.chart_widget:
            self.chart_widget.update_data(chart_data)