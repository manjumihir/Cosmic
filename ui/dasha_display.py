from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
from utils.astro_calc import DashaCalculator

class DashaDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Create tree widget with headers
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Dasha', 'Start Date', 'End Date', 'Duration'])
        self.tree.setColumnWidth(0, 200)  # Wider column for dasha names
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 150)
        self.tree.setColumnWidth(3, 100)
        
        # Style the tree widget
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                border: none;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #262626;
                color: #ffffff;
                padding: 5px;
                border: none;
            }
        """)
        
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
    def update_data(self, chart_data):
        """Update the dasha display with new chart data"""
        if not chart_data:
            return
            
        # Clear existing items
        self.tree.clear()
        
        # Get moon longitude from chart data
        moon_longitude = None
        if 'points' in chart_data and 'Moon' in chart_data['points']:
            moon_data = chart_data['points']['Moon']
            if isinstance(moon_data, dict) and 'longitude' in moon_data:
                moon_longitude = moon_data['longitude']
        
        if moon_longitude is None:
            print("Error: Moon longitude not found in chart data")
            return
            
        # Get birth time from chart data
        birth_time = None
        if 'datetime' in chart_data:
            birth_time = datetime.strptime(chart_data['datetime'], '%Y-%m-%d %H:%M:%S')
            birth_time = birth_time.astimezone()  # Convert to local timezone
        else:
            print("Error: Birth time not found in chart data")
            return
            
        # Calculate dashas
        dasha_calc = DashaCalculator()
        dashas = dasha_calc.calculate_dashas(birth_time, moon_longitude)
        
        # Add dashas to tree
        self.add_dasha_to_tree(dashas)
        
    def add_dasha_to_tree(self, dashas):
        """Add dasha periods to the tree widget"""
        # Get timezone-aware current time
        current_time = datetime.now().astimezone()
        
        # Color definitions
        colors = {
            'past': {
                'main': '#4a5568',  # Dark gray
                'antar': '#718096',  # Medium gray
                'pratyantar': '#a0aec0',  # Light gray
                'text': '#ffffff'  # White text
            },
            'present': {
                'main': '#2c5282',  # Deep blue
                'antar': '#3182ce',  # Medium blue
                'pratyantar': '#4299e1',  # Light blue
                'text': '#ffffff'  # White text
            },
            'future': {
                'main': '#2f855a',  # Deep green
                'antar': '#38a169',  # Medium green
                'pratyantar': '#48bb78',  # Light green
                'text': '#ffffff'  # White text
            }
        }
        
        for dasha in dashas:
            # Create main dasha item
            main_item = QTreeWidgetItem(self.tree)
            main_item.setText(0, dasha['lord'])
            main_item.setText(1, dasha['start_date'].strftime('%Y-%m-%d'))
            main_item.setText(2, dasha['end_date'].strftime('%Y-%m-%d'))
            main_item.setText(3, dasha['duration_str'])
            
            # Determine dasha timing
            is_current = dasha['start_date'] <= current_time <= dasha['end_date']
            is_past = dasha['end_date'] < current_time
            is_future = dasha['start_date'] > current_time
            
            # Apply colors based on timing
            color_set = colors['present'] if is_current else colors['past'] if is_past else colors['future']
            for col in range(4):
                main_item.setBackground(col, QColor(color_set['main']))
                main_item.setForeground(col, QColor(color_set['text']))
            
            if is_current:
                main_item.setExpanded(True)  # Auto-expand current dasha
            
            # Add antardashas (sub-periods)
            if 'sub_dashas' in dasha:
                for antardasha in dasha['sub_dashas']:
                    antar_item = QTreeWidgetItem(main_item)
                    antar_item.setText(0, f"⤷ {antardasha['lord'].split('-')[1]}")
                    antar_item.setText(1, antardasha['start_date'].strftime('%Y-%m-%d'))
                    antar_item.setText(2, antardasha['end_date'].strftime('%Y-%m-%d'))
                    antar_item.setText(3, antardasha['duration_str'])
                    
                    # Determine antardasha timing
                    is_current_antar = antardasha['start_date'] <= current_time <= antardasha['end_date']
                    is_past_antar = antardasha['end_date'] < current_time
                    is_future_antar = antardasha['start_date'] > current_time
                    
                    # Apply colors based on timing
                    color_set = colors['present'] if is_current_antar else colors['past'] if is_past_antar else colors['future']
                    for col in range(4):
                        antar_item.setBackground(col, QColor(color_set['antar']))
                        antar_item.setForeground(col, QColor(color_set['text']))
                    
                    if is_current_antar:
                        antar_item.setExpanded(True)
                    
                    # Add pratyantar dashas (sub-sub-periods)
                    if 'sub_dashas' in antardasha:
                        for pratyantar in antardasha['sub_dashas']:
                            prat_item = QTreeWidgetItem(antar_item)
                            prat_item.setText(0, f"  ⤷ {pratyantar['lord'].split('-')[2]}")
                            prat_item.setText(1, pratyantar['start_date'].strftime('%Y-%m-%d'))
                            prat_item.setText(2, pratyantar['end_date'].strftime('%Y-%m-%d'))
                            prat_item.setText(3, pratyantar['duration_str'])
                            
                            # Determine pratyantar timing
                            is_current_prat = pratyantar['start_date'] <= current_time <= pratyantar['end_date']
                            is_past_prat = pratyantar['end_date'] < current_time
                            is_future_prat = pratyantar['start_date'] > current_time
                            
                            # Apply colors based on timing
                            color_set = colors['present'] if is_current_prat else colors['past'] if is_past_prat else colors['future']
                            for col in range(4):
                                prat_item.setBackground(col, QColor(color_set['pratyantar']))
                                prat_item.setForeground(col, QColor(color_set['text']))
    
    def handle_dasha_options(self, option):
        """Handle different dasha view options"""
        if option == "All Dashas":
            # Expand all items
            self.expand_all_items()
        elif option == "Current Dasha":
            # Show only current dasha
            self.show_current_dasha()
        elif option == "Future Dashas":
            # Show future dashas
            self.show_future_dashas()
            
    def expand_all_items(self):
        """Expand all items in the tree"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setExpanded(True)
            
    def show_current_dasha(self):
        """Show only the current dasha"""
        current_time = datetime.now().astimezone()
        
        # First collapse all items
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self.collapse_all_children(item)
            item.setExpanded(False)
        
        # Then expand only the current dasha
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            start_date = datetime.strptime(item.text(1), '%Y-%m-%d').astimezone()
            end_date = datetime.strptime(item.text(2), '%Y-%m-%d').astimezone()
            
            if start_date <= current_time <= end_date:
                item.setExpanded(True)
                # Also expand current antardasha if exists
                for j in range(item.childCount()):
                    antar_item = item.child(j)
                    antar_start = datetime.strptime(antar_item.text(1), '%Y-%m-%d').astimezone()
                    antar_end = datetime.strptime(antar_item.text(2), '%Y-%m-%d').astimezone()
                    
                    if antar_start <= current_time <= antar_end:
                        antar_item.setExpanded(True)
                        break
                break
    
    def collapse_all_children(self, item):
        """Recursively collapse all children of an item"""
        for i in range(item.childCount()):
            child = item.child(i)
            self.collapse_all_children(child)
            child.setExpanded(False)
            
    def show_future_dashas(self):
        """Show future dashas"""
        current_time = datetime.now().astimezone()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            start_date = datetime.strptime(item.text(1), '%Y-%m-%d').astimezone()
            is_future = start_date > current_time
            item.setExpanded(is_future)
