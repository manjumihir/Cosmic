import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui.eastern_chart_widget import EasternChartWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eastern Chart Test")
        self.setGeometry(100, 100, 800, 800)
        
        # Create and set the eastern chart widget
        self.chart = EasternChartWidget(self)
        self.setCentralWidget(self.chart)
        
        # Test data
        self.test_data = {
            'points': {
                'Sun': {'longitude': 0, 'latitude': 0, 'sign': 'Aries'},
                'Moon': {'longitude': 45, 'latitude': 0, 'sign': 'Taurus'},
                'Mars': {'longitude': 90, 'latitude': 0, 'sign': 'Cancer'},
                'Mercury': {'longitude': 135, 'latitude': 0, 'sign': 'Leo'},
                'Jupiter': {'longitude': 180, 'latitude': 0, 'sign': 'Libra'},
                'Venus': {'longitude': 225, 'latitude': 0, 'sign': 'Scorpio'},
                'Saturn': {'longitude': 270, 'latitude': 0, 'sign': 'Capricorn'},
                'Rahu': {'longitude': 315, 'latitude': 0, 'sign': 'Aquarius'},
                'Ketu': {'longitude': 135, 'latitude': 0, 'sign': 'Leo'}
            },
            'houses': {
                1: {'longitude': 0, 'sign': 'Aries'},
                2: {'longitude': 30, 'sign': 'Taurus'},
                3: {'longitude': 60, 'sign': 'Gemini'},
                4: {'longitude': 90, 'sign': 'Cancer'},
                5: {'longitude': 120, 'sign': 'Leo'},
                6: {'longitude': 150, 'sign': 'Virgo'},
                7: {'longitude': 180, 'sign': 'Libra'},
                8: {'longitude': 210, 'sign': 'Scorpio'},
                9: {'longitude': 240, 'sign': 'Sagittarius'},
                10: {'longitude': 270, 'sign': 'Capricorn'},
                11: {'longitude': 300, 'sign': 'Aquarius'},
                12: {'longitude': 330, 'sign': 'Pisces'}
            }
        }
        
        # Update chart with test data
        self.chart.update_data(self.test_data)

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
