from .base_chart import BaseChart
from PyQt6.QtGui import QPainter, QPen, QColor
import math

class NorthernChart(BaseChart):
    """Northern style chart implementation"""
    
    def __init__(self, parent=None, input_page=None):
        super().__init__(parent, input_page)
        
    def paintEvent(self, event):
        """Draw the northern style chart"""
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
        
        # Define ring radii
        self.outer_radius = radius
        self.middle_radius = radius * 0.85
        self.inner_radius = radius * 0.7
        self.center_radius = radius * 0.25
        
        # Draw chart elements
        self.draw_rings(painter, cx, cy)
        self.draw_houses(painter, cx, cy, radius)
        if self.points:
            self.draw_planets(painter, cx, cy, self.inner_radius)
            
    def draw_rings(self, painter, cx, cy):
        """Draw the concentric rings of the northern chart"""
        # Draw outer ring (Nakshatras)
        painter.setPen(QPen(self.current_theme['rings']))
        painter.drawEllipse(cx - self.outer_radius, cy - self.outer_radius,
                          self.outer_radius * 2, self.outer_radius * 2)
                          
        # Draw middle ring (Zodiac)
        painter.drawEllipse(cx - self.middle_radius, cy - self.middle_radius,
                          self.middle_radius * 2, self.middle_radius * 2)
                          
        # Draw inner ring (Planets)
        painter.drawEllipse(cx - self.inner_radius, cy - self.inner_radius,
                          self.inner_radius * 2, self.inner_radius * 2)
                          
        # Draw center circle
        painter.drawEllipse(cx - self.center_radius, cy - self.center_radius,
                          self.center_radius * 2, self.center_radius * 2)
            
    def draw_houses(self, painter, cx, cy, radius):
        """Draw houses in northern style"""
        if not self.house_cusps:
            return
            
        pen = QPen(self.current_theme['houses'])
        pen.setWidth(1)
        painter.setPen(pen)
        
        for cusp in self.house_cusps:
            angle = math.radians(90 - float(cusp))
            x1 = cx + self.center_radius * math.cos(angle)
            y1 = cy - self.center_radius * math.sin(angle)
            x2 = cx + self.outer_radius * math.cos(angle)
            y2 = cy - self.outer_radius * math.sin(angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
    def draw_planets(self, painter, cx, cy, radius):
        """Draw planets in northern style"""
        if not self.points:
            return
            
        for planet, data in self.points.items():
            longitude = float(data['longitude'])
            x, y = self.calculate_planet_position(longitude, radius)
            x += cx
            y += cy
            
            # Draw planet symbol
            symbol = self.PLANET_SYMBOLS.get(planet, '?')
            painter.drawText(int(x-10), int(y+10), symbol)
