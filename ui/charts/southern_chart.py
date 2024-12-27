from .base_chart import BaseChart
from PyQt6.QtGui import QPainter, QPen, QColor
import math

class SouthernChart(BaseChart):
    """Southern style chart implementation"""
    
    def __init__(self, parent=None, input_page=None):
        super().__init__(parent, input_page)
        
    def paintEvent(self, event):
        """Draw the southern style chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set background
        painter.fillRect(self.rect(), self.current_theme['background'])
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        cx = width // 2
        cy = height // 2
        radius = min(width, height) // 2 - 40
        
        # Draw chart elements
        self.draw_houses(painter, cx, cy, radius)
        if self.points:
            self.draw_planets(painter, cx, cy, radius)
            
    def draw_houses(self, painter, cx, cy, radius):
        """Draw houses in southern style"""
        if not self.house_cusps:
            return
            
        # Draw house lines
        pen = QPen(self.current_theme['houses'])
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Draw houses in southern style (you can implement specific southern style here)
        for i in range(12):
            angle = i * 30
            rad = math.radians(angle)
            x = cx + radius * math.cos(rad)
            y = cy + radius * math.sin(rad)
            painter.drawLine(cx, cy, int(x), int(y))
            
    def draw_planets(self, painter, cx, cy, radius):
        """Draw planets in southern style"""
        if not self.points:
            return
            
        planet_radius = radius * 0.85
        for planet, data in self.points.items():
            longitude = float(data['longitude'])
            x, y = self.calculate_planet_position(longitude, planet_radius)
            x += cx
            y += cy
            
            # Draw planet symbol
            symbol = self.PLANET_SYMBOLS.get(planet, '?')
            painter.drawText(int(x-10), int(y+10), symbol)
