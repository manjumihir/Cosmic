from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
import math

class BaseChart(QWidget):
    """Base class for all chart types (Eastern, Northern, Southern, etc.)"""
    
    ZODIAC_SYMBOLS = {
        'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
        'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
        'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
    }
    
    PLANET_SYMBOLS = {
        'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
        'Jupiter': '♃', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋'
    }

    def __init__(self, parent=None, input_page=None):
        super().__init__(parent)
        self.input_page = input_page
        self.chart_data = None
        self.transit_data = None
        self.show_transits = False
        self.points = None
        self.houses = None
        self.house_cusps = None
        self.setup_ui()
        self.setup_themes()
        
    def setup_ui(self):
        """Setup basic UI elements common to all charts"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls container
        self.controls_container = QWidget()
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Settings button and menu
        self.create_settings_button()
        self.create_settings_menu()
        
        self.main_layout.addWidget(self.controls_container)
        
    def create_settings_button(self):
        """Create the settings button"""
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        self.controls_layout.addWidget(self.settings_button)
        
    def create_settings_menu(self):
        """Create the settings menu with common options"""
        self.settings_menu = QMenu(self)
        self.setup_theme_menu()
        self.setup_calculation_menu()
        self.settings_button.setMenu(self.settings_menu)
        
    def setup_themes(self):
        """Setup color themes"""
        self.themes = {
            'Light': {
                'background': QColor(255, 255, 255),
                'rings': QColor(128, 0, 128),
                'text': QColor(0, 0, 0),
                'houses': QColor(100, 100, 100),
                'planet_ring': QColor(255, 223, 0),
                'panel_text': QColor(0, 0, 0),
                'panel_background': QColor(240, 240, 240),
            },
            'Dark': {
                'background': QColor(25, 0, 40),
                'rings': QColor(128, 0, 128),
                'text': QColor(255, 255, 255),
                'houses': QColor(128, 128, 128),
                'planet_ring': QColor(255, 255, 180),
                'panel_text': QColor(255, 255, 255),
                'panel_background': QColor(0, 0, 0),
            }
        }
        self.current_theme = self.themes['Light']
        
    def update_data(self, chart_data):
        """Update chart with new data"""
        self.chart_data = chart_data
        if isinstance(chart_data, dict) and 'points' in chart_data:
            self.points = {k: v for k, v in chart_data['points'].items() 
                         if k not in ['Uranus', 'Neptune', 'Pluto']}
            self.houses = chart_data.get('houses', {})
            self.house_cusps = [
                float(chart_data['houses'][i]['longitude'])
                for i in range(1, 13)
            ]
        self.update()
        
    def paintEvent(self, event):
        """Base paint event - override in child classes"""
        raise NotImplementedError("Subclasses must implement paintEvent")
        
    def draw_planets(self, painter, cx, cy, radius):
        """Base method for drawing planets - override in child classes"""
        raise NotImplementedError("Subclasses must implement draw_planets")
        
    def draw_houses(self, painter, cx, cy, radius):
        """Base method for drawing houses - override in child classes"""
        raise NotImplementedError("Subclasses must implement draw_houses")
        
    def calculate_planet_position(self, longitude, radius):
        """Calculate planet position - common across all chart types"""
        angle = math.radians(90 - longitude)
        x = radius * math.cos(angle)
        y = -radius * math.sin(angle)
        return x, y
