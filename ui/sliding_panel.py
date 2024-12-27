from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QPushButton, QSplitter, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QSize
from PyQt6.QtGui import QPainter, QPen, QColor

class SlidingPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Setup layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # State variables
        self.is_expanded = True
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.check_hover_state)
        
        # Fixed sizes
        self.expanded_width = 800
        self.collapsed_width = 20
        
        # Enable mouse tracking for hover detection
        self.setMouseTracking(True)
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)  
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def addWidget(self, widget):
        """Add a widget to the panel's layout"""
        self.layout.addWidget(widget)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
    def enterEvent(self, event):
        """Handle mouse enter events"""
        self.hover_timer.start(200)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        self.hover_timer.start(500)
        super().leaveEvent(event)
        
    def check_hover_state(self):
        """Check if mouse is still over panel and expand/collapse accordingly"""
        pos = self.mapFromGlobal(self.cursor().pos())
        if self.rect().contains(pos):
            self.expand()
        else:
            self.collapse()
            
    def expand(self):
        """Expand the panel with animation"""
        if not self.is_expanded:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.expanded_width)
            self.animation.start()
            self.setMaximumWidth(self.expanded_width)
            self.is_expanded = True
            if isinstance(self.parent(), QSplitter):
                sizes = self.parent().sizes()
                sizes[0] = self.expanded_width
                self.parent().setSizes(sizes)
            
    def collapse(self):
        """Collapse the panel with animation"""
        if self.is_expanded:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()
            self.setMaximumWidth(self.collapsed_width)
            self.is_expanded = False
            if isinstance(self.parent(), QSplitter):
                sizes = self.parent().sizes()
                sizes[0] = self.collapsed_width
                self.parent().setSizes(sizes)
            
    def paintEvent(self, event):
        """Custom paint event to draw panel with slight transparency"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent background
        painter.setBrush(QColor(240, 240, 240, 250))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
        # Draw subtle border
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.rect())

class DragHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(20)
        self.hovered = False
        self.dots_color = QColor(150, 150, 150)
        
    def setHovered(self, hovered):
        """Set hover state and update appearance"""
        if self.hovered != hovered:
            self.hovered = hovered
            self.dots_color = QColor(200, 200, 200) if hovered else QColor(150, 150, 150)
            self.update()
            
    def paintEvent(self, event):
        """Draw the handle with dots pattern"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw dots
        pen = QPen(self.dots_color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        center_x = self.width() // 2
        dot_spacing = 8
        
        for i in range(5):
            y = (self.height() // 2) - (2 * dot_spacing) + (i * dot_spacing)
            painter.drawPoint(center_x, y)
