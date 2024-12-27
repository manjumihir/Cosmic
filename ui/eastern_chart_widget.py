from PyQt6 import QtWidgets, QtGui, QtSvg, QtCore
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QMenu)
from PyQt6.QtCore import Qt, QPointF, QPoint, QRect, QRectF, QSettings
from PyQt6.QtGui import (QPainter, QPen, QColor, QFont, QFontMetrics, QPainterPath,
                      QAction, QActionGroup, QBrush)
from .eastern_chart_functions import EasternChartFunctions, EnhancedPlanetDisplay
import math
import traceback


class EasternChartWidget(EasternChartFunctions):
    def __init__(self, parent=None, input_page=None):
        super().__init__(parent, input_page)
            
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create controls container and align right
        self.controls_container = QWidget()
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Create Settings Button
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
        
        # Create Settings Menu
        self.settings_menu = QMenu(self)
        
        # Planet Style submenu
        self.style_menu = QMenu("Planet Style", self)
        self.style_group = QActionGroup(self)
        self.style_group.setExclusive(True)
        
        for style in ['basic', 'geometric', 'enhanced', 'labeled', 'text']:
            action = QAction(style.capitalize(), self.style_group)
            action.setCheckable(True)
            action.setData(style)
            self.style_menu.addAction(action)
            if style == 'text':  # Set default
                action.setChecked(True)
        
        # Theme submenu
        self.theme_menu = QMenu("Theme", self)
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        for theme in ['Light', 'Dark', 'Classic']:
            action = QAction(theme, self.theme_group)
            action.setCheckable(True)
            action.setData(theme)
            self.theme_menu.addAction(action)
            if theme == 'Dark':  # Set default
                action.setChecked(True)
        
        # Add Calculation Settings submenu
        self.calc_settings_menu = QMenu("Calculation Settings", self)
        
        # Calculation Type
        self.calc_type_menu = QMenu("Calculation Type", self)
        self.calc_type_group = QActionGroup(self)
        self.calc_type_group.setExclusive(True)
        for calc_type in ["Geocentric", "Topocentric"]:
            action = QAction(calc_type, self.calc_type_group)
            action.setCheckable(True)
            action.setData(calc_type)
            self.calc_type_menu.addAction(action)
            if calc_type == "Geocentric":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.calc_type_menu)
        
        # Zodiac System
        self.zodiac_menu = QMenu("Zodiac System", self)
        self.zodiac_group = QActionGroup(self)
        self.zodiac_group.setExclusive(True)
        for system in ["Tropical", "Sidereal"]:
            action = QAction(system, self.zodiac_group)
            action.setCheckable(True)
            action.setData(system)
            self.zodiac_menu.addAction(action)
            if system == "Sidereal":  # Set default
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.zodiac_menu)
        
        # Ayanamsa (enabled only for Sidereal)
        self.ayanamsa_menu = QMenu("Ayanamsa", self)
        self.ayanamsa_group = QActionGroup(self)
        self.ayanamsa_group.setExclusive(True)
        for ayanamsa in ["Lahiri", "Raman", "Krishnamurti", "Fagan/Bradley", "True Chitrapaksha", "Yukteswar"]:
            action = QAction(ayanamsa, self.ayanamsa_group)
            action.setCheckable(True)
            action.setData(ayanamsa)
            self.ayanamsa_menu.addAction(action)
            if ayanamsa == "Lahiri":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.ayanamsa_menu)
        
        # House System
        self.house_menu = QMenu("House System", self)
        self.house_group = QActionGroup(self)
        self.house_group.setExclusive(True)
        house_systems = [
            "Placidus", "Koch", "Equal (Asc)", "Equal (MC)", "Whole Sign",
            "Campanus", "Regiomontanus", "Porphyry", "Morinus", "Meridian",
            "Alcabitius", "Azimuthal", "Polich/Page (Topocentric)", "Vehlow Equal"
        ]
        for system in house_systems:
            action = QAction(system, self.house_group)
            action.setCheckable(True)
            action.setData(system)
            self.house_menu.addAction(action)
            if system == "Placidus":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.house_menu)
        
        # Node Type
        self.node_menu = QMenu("Node Type", self)
        self.node_group = QActionGroup(self)
        self.node_group.setExclusive(True)
        for node_type in ["True Node (Rahu/Ketu)", "Mean Node (Rahu/Ketu)"]:
            action = QAction(node_type, self.node_group)
            action.setCheckable(True)
            action.setData(node_type)
            self.node_menu.addAction(action)
            if node_type == "True Node (Rahu/Ketu)":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.node_menu)
        
        # Add all menus to settings menu
        self.settings_menu.addMenu(self.style_menu)
        self.settings_menu.addMenu(self.theme_menu)
        self.settings_menu.addMenu(self.calc_settings_menu)
        
        # Connect action groups to handlers
        self.style_group.triggered.connect(self.handle_style_change)
        self.theme_group.triggered.connect(self.handle_theme_change)
        self.zodiac_group.triggered.connect(self.handle_zodiac_change)
        self.calc_type_group.triggered.connect(self.handle_calc_type_change)
        self.ayanamsa_group.triggered.connect(self.handle_ayanamsa_change)
        self.house_group.triggered.connect(self.handle_house_system_change)
        self.node_group.triggered.connect(self.handle_node_change)
        
        # Connect button to menu
        self.settings_button.clicked.connect(self.show_settings_menu)
        
        # Add settings button to controls layout
        self.controls_layout.addWidget(self.settings_button)
        
        # Add controls to main layout at the bottom
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.controls_container)
        
        # Flag to indicate we should draw text in first paint event
        self.should_draw_text = True
        
    def update_data(self, chart_data):
        """Update the chart with new data"""
        try:
            print("DEBUG - Updating eastern chart data")
            self.chart_data = chart_data
            
            # Update menu selections based on chart data
            meta = chart_data.get('meta', {})
            if meta:
                # Update calculation type
                calc_type = meta.get('calculation_type')
                if calc_type:
                    for action in self.calc_type_group.actions():
                        if action.data() == calc_type:
                            action.setChecked(True)
                
                # Update zodiac system
                zodiac = meta.get('zodiac_system')
                if zodiac:
                    for action in self.zodiac_group.actions():
                        if action.data() == zodiac:
                            action.setChecked(True)
                
                # Update ayanamsa
                ayanamsa = meta.get('ayanamsa')
                if ayanamsa:
                    for action in self.ayanamsa_group.actions():
                        if action.data() == ayanamsa:
                            action.setChecked(True)
                
                # Enable/disable ayanamsa menu based on zodiac
                self.ayanamsa_menu.setEnabled(zodiac == "Sidereal")
                
                # Update house system
                house_system = meta.get('house_system')
                if house_system:
                    for action in self.house_group.actions():
                        if action.data() == house_system:
                            action.setChecked(True)
                
                # Update node type
                node_type = meta.get('node_type')
                if node_type:
                    for action in self.node_group.actions():
                        if action.data() == node_type:
                            action.setChecked(True)
            
            # Extract points and houses directly from the dictionary
            if 'points' in chart_data:
                # Initialize points dictionary, excluding outer planets
                self.points = {k: v for k, v in chart_data['points'].items() 
                             if k not in ['Uranus', 'Neptune', 'Pluto']}
                
                # Store the full houses data
                self.houses = chart_data.get('houses', {})
                
                # Update house cusps using numeric indices
                self.house_cusps = []
                for i in range(1, 13):
                    if i in self.houses:
                        self.house_cusps.append(float(self.houses[i]['longitude']))
                    else:
                        print(f"Warning: Missing house {i} in chart data")
                        self.house_cusps.append(0.0)  # Default value
                
                # Debugging: Log the house_cusps list
                print(f"House Cusps: {self.house_cusps}")
                
            self.update()
            print("DEBUG - Eastern chart update complete")
            
        except Exception as e:
            print(f"Error updating eastern chart: {str(e)}")
            traceback.print_exc()
        
    def change_theme(self, theme):
        """Change the chart's color theme"""
        super().change_theme(theme)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), self.themes[self.current_theme]['background'])

        # Get dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 20

        # Calculate square size based on 30° chord length
        square_size = radius * 2 * math.sin(math.radians(15)) * 0.95  # ≈ radius * 0.5176, reduced by 15%

        # Draw outer circle for nakshatra
        painter.setPen(QPen(self.themes[self.current_theme]['rings'], max(1, int(radius / 200))))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Draw middle circle for zodiac
        middle_radius = radius * 0.95
        painter.drawEllipse(QPointF(center_x, center_y), middle_radius, middle_radius)

        # Draw inner circle for house signs
        inner_radius = radius * 0.9
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)

        # Draw nakshatra lines and names
        self.draw_nakshatra_lines(painter, center_x, center_y, radius)
        self.draw_nakshatras(painter, center_x, center_y, radius)

        # Call to draw house cusps
        self.draw_house_cusps(painter, center_x, center_y, radius)

        # Calculate square corners
        half_size = square_size / 2
        left = center_x - half_size
        right = center_x + half_size
        top = center_y - half_size
        bottom = center_y + half_size

        # Draw the extended lines
        painter.setPen(QPen(self.themes[self.current_theme]['rings'], max(1, int(radius / 200))))
        
        # Calculate line length using chord formula: 2 * sqrt(R² - d²)
        # where R is inner_radius and d is half_size
        line_length = 2 * math.sqrt(inner_radius**2 - half_size**2)
        half_line = line_length / 2

        # Draw vertical lines
        # Left vertical line
        p1 = QPoint(int(center_x - half_size), int(center_y - half_line))
        p2 = QPoint(int(center_x - half_size), int(center_y + half_line))
        painter.drawLine(p1, p2)
        
        # Right vertical line
        p1 = QPoint(int(center_x + half_size), int(center_y - half_line))
        p2 = QPoint(int(center_x + half_size), int(center_y + half_line))
        painter.drawLine(p1, p2)
        
        # Draw horizontal lines
        # Top horizontal line
        p1 = QPoint(int(center_x - half_line), int(center_y - half_size))
        p2 = QPoint(int(center_x + half_line), int(center_y - half_size))
        painter.drawLine(p1, p2)
        
        # Bottom horizontal line
        p1 = QPoint(int(center_x - half_line), int(center_y + half_size))
        p2 = QPoint(int(center_x + half_line), int(center_y + half_size))
        painter.drawLine(p1, p2)

        # Draw diagonal lines from square corners to circle edge
        # Calculate the angles for the corners (45, 135, 225, 315 degrees)
        corner_angles = [45, 135, 225, 315]
        
        # Square corners
        corners = [
            (right, top),    # Top-right
            (left, top),     # Top-left
            (left, bottom),  # Bottom-left
            (right, bottom)  # Bottom-right
        ]
        
        # Draw diagonal lines from each corner
        for (x, y), angle in zip(corners, corner_angles):
            # Calculate end point on circle
            angle_rad = math.radians(angle)
            end_x = center_x + inner_radius * math.cos(angle_rad)
            end_y = center_y - inner_radius * math.sin(angle_rad)
            
            # Draw the diagonal line
            p1 = QPoint(int(x), int(y))
            p2 = QPoint(int(end_x), int(end_y))
            painter.drawLine(p1, p2)

        # Draw degree markers
        self.draw_degree_markers(painter, center_x, center_y, radius)

        # Draw house signs only (no duplicate zodiac signs)
        painter.setPen(self.themes[self.current_theme]['text'])
        self.draw_house_signs(painter, center_x, center_y, middle_radius)

        # Draw zodiac sign names and angles
        start_angle = math.radians(75)
        zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        for i in range(12):
            angle_rad = start_angle - (i * (2 * math.pi / 12))
            if i in [0, 3, 6, 9]:
                angle_rad -= math.radians(5)
            adjusted_angle = angle_rad + (math.pi)
            # Calculate text width for centering
            text_width = painter.fontMetrics().horizontalAdvance(zodiac_signs[i])
            label_x = center_x + (inner_radius * math.cos(adjusted_angle)) - (text_width / 2)  # Center the label over the left edge
            label_y = center_y + (inner_radius * math.sin(adjusted_angle))
            # painter.drawText(int(label_x), int(label_y), zodiac_signs[i])

        # Draw each planet
        if hasattr(self, 'points'):
            for planet, data in self.points.items():
                # Calculate position based on longitude
                longitude = data.get('longitude', 0)
                angle = math.radians(longitude + 75)  # Adjust longitude by adding 75 degrees to align with fixed zodiac
                
                # Calculate degree information
                zodiac_index = int(longitude / 30)
                degrees = int(longitude % 30)
                minutes = int((longitude % 1) * 60)
                
                # Get zodiac sign abbreviation
                zodiac_signs = ["AR", "TA", "GE", "CN", "LE", "VI", "LI", "SC", "SG", "CP", "AQ", "PI"]
                zodiac_abbr = zodiac_signs[zodiac_index]
                
                # Calculate positions
                arrow_start = inner_radius * .90  # Increased from 0.90 to 0.95 to touch inner circle
                arrow_end = inner_radius * 1  # Increased from 0.85 to 0.90 for slightly longer arrow
                
                # Calculate arrow start and end points
                arrow_start_x = center_x + arrow_start * math.cos(angle)
                arrow_start_y = center_y - arrow_start * math.sin(angle)
                arrow_end_x = center_x + arrow_end * math.cos(angle)
                arrow_end_y = center_y - arrow_end * math.sin(angle)
                
                # Calculate planet position (moved more inward)
                planet_radius = inner_radius * 0.82  # Adjusted from 0.70 to 0.50
                planet_x = center_x + planet_radius * math.cos(angle)
                planet_y = center_y - planet_radius * math.sin(angle)
                
                # Calculate text position to be along the line
                
                if planet:
                    #####################################################################################
                    arrow_length = inner_radius * 1 # Length to the outer circle
                    angle_rad = angle  # Use the angle calculated earlier
                    
                    # Calculate the square's corners and midpoints
                    square_size = middle_radius * 0.26  # Size of the square
                    point_radius = inner_radius * 0.53  # Radius around points where arrows should stop
                    square_top_left = (center_x + square_size, center_y + square_size)
                    square_top_right = (center_x - square_size, center_y + square_size)
                    square_bottom_left = (center_x + square_size, center_y - square_size)
                    square_bottom_right = (center_x - square_size , center_y - square_size)
                    
                    # Calculate midpoints of each side
                    mid_top = (center_x, center_y + square_size)
                    mid_bottom = (center_x, center_y - square_size)
                    mid_left = (center_x + square_size, center_y)
                    mid_right = (center_x - square_size, center_y)
                    
                    # Determine the zodiac sign based on the angle
                    arrow_x = center_x + arrow_length * math.cos(angle)
                    arrow_y = center_y - arrow_length * math.sin(angle) 
                    
                    start_angle = math.radians(75)
                    zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
                    adjusted_angle = angle_rad + (math.pi)
                    zodiac_index = int((adjusted_angle - start_angle) / (2 * math.pi / 12)) % 12
                    
                    # Set arrow origin based on zodiac index
                    if zodiac_index == 0:  # Aries
                        arrow_origin_x = arrow_x
                        arrow_origin_y = mid_top[1]
                    elif zodiac_index == 1:  # Taurus
                        arrow_origin_x = square_top_left[0]
                        arrow_origin_y = square_top_left[1]
                    elif zodiac_index == 2:  # Gemini
                        arrow_origin_x = square_top_left[0]
                        arrow_origin_y = square_top_left[1]
                    elif zodiac_index == 3:  # Cancer
                        arrow_origin_x = mid_left[0]
                        arrow_origin_y = arrow_y
                    elif zodiac_index == 4:  # Leo
                        arrow_origin_x = square_bottom_left[0]
                        arrow_origin_y = square_bottom_left[1]
                    elif zodiac_index == 5:  # Virgo
                        arrow_origin_x = square_bottom_left[0]
                        arrow_origin_y = square_bottom_left[1]
                    elif zodiac_index == 6:  # Libra
                        arrow_origin_x = arrow_x
                        arrow_origin_y = mid_bottom[1]
                    elif zodiac_index == 7:  # Scorpio
                        arrow_origin_x = square_bottom_right[0]
                        arrow_origin_y = square_bottom_right[1]
                    elif zodiac_index == 8:  # Sagittarius
                        arrow_origin_x = square_bottom_right[0]
                        arrow_origin_y = square_bottom_right[1]
                    elif zodiac_index == 9:  # Capricorn
                        arrow_origin_x = mid_right[0]
                        arrow_origin_y = arrow_y
                    elif zodiac_index == 10:  # Aquarius
                        arrow_origin_x = square_top_right[0]
                        arrow_origin_y = square_top_right[1]
                    elif zodiac_index == 11:  # Pisces
                        arrow_origin_x = square_top_right[0]
                        arrow_origin_y = square_top_right[1]
                    
                    text_x = arrow_origin_x + (arrow_x - arrow_origin_x) * 0.5
                    text_y = arrow_origin_y + (arrow_y - arrow_origin_y) * 0.5
                    
                    # Retrieve the color for the planet's text
                    planet_color = self.planet_display.PLANET_COLORS[planet]  # Fallback to black if not found
                    
                    # Set pen for the line using the planet's color
                    painter.setPen(QPen(planet_color, 1))  # Set pen for the line using planet color
                    
                    dx = arrow_origin_x - arrow_x
                    dy = arrow_origin_y - arrow_y
                    
                    # Calculate the length of the vector
                    length = math.sqrt(dx * dx + dy * dy)
                    
                    if length > 0:
                        dx = dx / length
                        dy = dy / length
                        # Adjust the arrow endpoint to stop at the radius from the origin point
                        arrow_origin_x = arrow_origin_x - dx * point_radius
                        arrow_origin_y = arrow_origin_y - dy * point_radius
                    
                    painter.drawLine(QPoint(int(arrow_origin_x), int(arrow_origin_y)), QPoint(int(arrow_x), int(arrow_y)))  # Line from arrow origin to outer circle

                    # Draw arrowhead
                    arrowhead_size = 10  # Size of the arrowhead
                    angle_offset = math.radians(30)  # Angle for the arrowhead
                    
                    # Calculate the points for the arrowhead
                    p1_x = arrow_x - arrowhead_size * math.cos(angle - angle_offset)
                    p1_y = arrow_y + arrowhead_size * math.sin(angle - angle_offset)
                    p2_x = arrow_x - arrowhead_size * math.cos(angle + angle_offset)
                    p2_y = arrow_y + arrowhead_size * math.sin(angle + angle_offset)
                    
                    # Draw the arrowhead
                    painter.drawLine(QPoint(int(arrow_x), int(arrow_y)), QPoint(int(p1_x), int(p1_y)))
                    painter.drawLine(QPoint(int(arrow_x), int(arrow_y)), QPoint(int(p2_x), int(p2_y)))
                    
                    #########################################################################################
                    
                    # Set up planet color
                    planet_color = self.planet_display.PLANET_COLORS.get(planet, Qt.GlobalColor.white)
                    painter.setPen(QPen(QColor(planet_color), 1))
                    
                    print(f"\nDEBUG - Drawing planet {planet}")
                    print(f"Current style: {self.planet_display._style}")
                    
                    if self.planet_display._style == "text":
                        # For text style, display planet name with degree
                        display_name = "Asc" if planet == "Ascendant" else planet
                        planet_text = f"{display_name} {degrees:02d}{zodiac_abbr}{minutes:02d}"
                        print(f"Drawing text style: {planet_text}")
                        
                        # Draw text at text position
                        painter.save()
                        font = painter.font()
                        font.setPointSize(int(radius * 0.0425))
                        painter.setFont(font)
                        
                        painter.translate(text_x, text_y)
                        # Calculate text angle directly from the line's direction vector
                        text_angle = math.degrees((math.atan2(-dy, dx)))  # Negative because we want to follow the line direction
                        if 90 < text_angle < 270:
                            text_angle += 180
                        painter.rotate(-text_angle)
                        
                        text_width = painter.fontMetrics().horizontalAdvance(planet_text)
                        text_rect = QRect(int(-text_width/2), -10, int(text_width), 20)
                        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, planet_text)
                        painter.restore()
                        
                        # Draw arrow from inner circle to degree point
                        # painter.drawLine(QPoint(int(arrow_start_x), int(arrow_start_y)), 
                        #               QPoint(int(arrow_end_x), int(arrow_end_y)))
                    else:
                        # Draw planet symbol at planet position
                        print(f"Drawing symbol style: {self.planet_display.PLANET_SYMBOLS.get(planet, '?')}")
                        self.planet_display.draw_planet(painter, planet, int(planet_x), int(planet_y), 
                                                      int(radius / 11.36))
                        
                        # Draw degree text at text position
                        degree_text = f"{degrees:02d}{zodiac_abbr}{minutes:02d}"
                        
                        painter.save()
                        font = painter.font()
                        font.setPointSize(int(radius * 0.035))
                        painter.setFont(font)
                        
                        painter.translate(text_x, text_y)
                        # Use same angle for degree text
                        text_angle = math.degrees((math.atan2(-dy, dx)))
                        if 90 < text_angle < 270:
                            text_angle += 180
                        painter.rotate(-text_angle)
                        
                        text_width = painter.fontMetrics().horizontalAdvance(degree_text)
                        text_rect = QRect(int(-text_width/2), -10, int(text_width), 20)
                        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, degree_text)
                        painter.restore()
                        
                        # Draw arrow from inner circle to degree point
                        # painter.drawLine(QPoint(int(arrow_start_x), int(arrow_start_y)), 
                        #               QPoint(int(arrow_end_x), int(arrow_end_y)))
                    
                    # Draw arrowhead
                    arrow_size = 10
                    angle_degrees = math.degrees(angle)
                    p1_x = arrow_end_x - arrow_size * math.cos(math.radians(angle_degrees + 25))
                    p1_y = arrow_end_y + arrow_size * math.sin(math.radians(angle_degrees + 25))
                    p2_x = arrow_end_x - arrow_size * math.cos(math.radians(angle_degrees - 25))
                    p2_y = arrow_end_y + arrow_size * math.sin(math.radians(angle_degrees - 25))
                    # painter.drawLine(QPoint(int(arrow_end_x), int(arrow_end_y)), 
                    #               QPoint(int(p1_x), int(p1_y)))
                    # painter.drawLine(QPoint(int(arrow_end_x), int(arrow_end_y)), 
                    #               QPoint(int(p2_x), int(p2_y)))
                
        # Draw chart text if flag is set
        self.draw_chart_text(painter)
        
        # Draw center reference point
        dot_radius = max(1, int(radius / 200)) * 2
        painter.setBrush(self.themes[self.current_theme]['rings'])
        painter.drawEllipse(QPoint(int(center_x), int(center_y)), dot_radius, dot_radius)

    def draw_degree_markers(self, painter, center_x, center_y, radius):
        """Draw degree markers around the outer circle"""
        painter.setPen(QPen(self.themes[self.current_theme]['rings'], max(1, int(radius / 200))))
        
        # Draw markers every 1 degrees, starting at 75 degrees
        for degree in range(0, 360, 1):
            adjusted_angle = math.radians((degree + 75) % 360)  # Changed offset to 45 degrees
            
            # Calculate start and end points for the marker line
            outer_x = center_x + radius * math.cos(adjusted_angle)
            outer_y = center_y - radius * math.sin(adjusted_angle)
            
            # Longer lines for multiples of 30 degrees
            if degree % 30 == 0:
                inner_radius = radius * 1.03
            # Medium lines for multiples of 15 degrees
            elif degree % 15 == 0:
                inner_radius = radius * 1.02
            # Short lines for other 5 degree markers
            else:
                inner_radius = radius * 1.01;
                
            inner_x = center_x + inner_radius * math.cos(adjusted_angle)
            inner_y = center_y - inner_radius * math.sin(adjusted_angle)
            
            # Draw the marker line
            painter.drawLine(
                QPoint(int(inner_x), int(inner_y)),
                QPoint(int(outer_x), int(outer_y))
            )
            
            # Draw degree numbers for multiples of 30
            if degree % 30 == 0:
                text_radius = radius * 1.02
                text_x = center_x + text_radius * math.cos(adjusted_angle)
                text_y = center_y - text_radius * math.sin(adjusted_angle)
                
                # Rotate text to be tangent to the circle
                text_angle = -(degree + 45) + 90  # Adjust angle for proper text orientation
                
                painter.save()
                painter.translate(text_x, text_y)
                painter.rotate(text_angle)
                
                # Draw the degree number
                font = painter.font()
                font.setPointSize(max(8, int(radius / 30)))
                painter.setFont(font)
                painter.drawText(QRect(-20, -10, 40, 20), Qt.AlignmentFlag.AlignCenter, str(degree))
                painter.restore()

    def draw_nakshatra_lines(self, painter, center_x, center_y, radius):
        """Draw lines dividing the nakshatras"""
        painter.setPen(QPen(self.themes[self.current_theme]['rings'], max(1, int(radius / 200))))
        outer_radius = radius 
        inner_radius = radius * .95
        
        # Draw lines for each nakshatra (27 divisions), starting at 75 degrees
        for i in range(27):
            angle = math.radians((i * (360 / 27) + 75) % 360)  # Add 75 degree offset
            outer_x = center_x + outer_radius * math.cos(angle)
            outer_y = center_y - outer_radius * math.sin(angle)
            inner_x = center_x + inner_radius * math.cos(angle)
            inner_y = center_y - inner_radius * math.sin(angle)
            
            painter.drawLine(
                QPoint(int(inner_x), int(inner_y)),
                QPoint(int(outer_x), int(outer_y))
            )

    def draw_nakshatras(self, painter, center_x, center_y, radius):
        """Draw nakshatra names in the outer ring"""
        nakshatra_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
            "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
            "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        text_radius = radius * .98
        painter.setPen(self.themes[self.current_theme]['text'])
        font = painter.font()
        font.setPointSize(max(6, int(radius / 40)))
        painter.setFont(font)
        
        for i, name in enumerate(nakshatra_names):
            angle = math.radians((i * (360 / 27) + (360 / 54) + 75) % 360)  # Add 75 degree offset
            text_x = center_x + text_radius * math.cos(angle)
            text_y = center_y - text_radius * math.sin(angle)
            
            # Rotate text to be tangent to the circle
            text_angle = -math.degrees(angle) + 90
            
            painter.save()
            painter.translate(text_x, text_y)
            painter.rotate(text_angle)
            painter.drawText(QRect(-50, -10, 100, 20), Qt.AlignmentFlag.AlignCenter, name)
            painter.restore()

    def draw_house_signs(self, painter, center_x, center_y, radius):
        """Draw house signs in the inner circle"""
        signs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
        text_radius = radius * 0.9
        
        font = painter.font()
        font.setPointSize(max(24, int(radius / 20)))
        painter.setFont(font)
        
        for i, sign in enumerate(signs):
            angle = math.radians((i * 30 + 15 + 75) % 360)  # Add 75 degree offset
            text_x = center_x + text_radius * math.cos(angle)
            text_y = center_y - text_radius * math.sin(angle)
            
            # Create rectangle for text
            rect = QRectF(text_x - 15, text_y - 15, 30, 30)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, sign)

    def draw_house_cusps(self, painter, center_x, center_y, radius):
        """Draw house cusps with their numbers"""
        try:
            if not self.house_cusps:
                return

            def to_roman(num):
                """Convert number to Roman numeral"""
                val = [
                    1000, 900, 500, 400,
                    100, 90, 50, 40,
                    10, 9, 5, 4, 1
                ]
                syb = [
                    "M", "CM", "D", "CD",
                    "C", "XC", "L", "XL",
                    "X", "IX", "V", "IV", "I"
                ]
                roman_num = ''
                i = 0
                while num > 0:
                    for _ in range(num // val[i]):
                        roman_num += syb[i]
                        num -= val[i]
                    i += 1
                return roman_num

            # Set up colors based on theme
            shadow_color = QColor(0, 0, 0, 100) if self.current_theme == 'Light' else QColor(255, 255, 255, 100)
            line_color = self.themes[self.current_theme]['lines']
            
            # Create a very light shade color based on the theme
            base_color = QColor(line_color)
            shade_color = QColor(base_color.red(), base_color.green(), base_color.blue(), 25)  # Slightly more visible
            
            # Draw shaded areas and cusps
            for i in range(12):
                if i < len(self.house_cusps):
                    current_angle = float(self.house_cusps[i])
                    next_angle = float(self.house_cusps[(i + 1) % 12])
                    
                    # Calculate angles for drawing
                    if next_angle < current_angle:  # Handle wrap around at 360 degrees
                        next_angle += 360
                    middle_angle = (current_angle + next_angle) / 2
                    if middle_angle >= 360:
                        middle_angle -= 360

                    # Create a path for the shaded area
                    path = QPainterPath()
                    
                    # Start from inner radius
                    start_angle = current_angle + 75  # Add the 75-degree offset
                    span_angle = (next_angle - current_angle)
                    if span_angle < 0:
                        span_angle += 360
                    
                    # Inner arc (0.9 * radius)
                    inner_rect = QRectF(
                        center_x - radius * 0.9,
                        center_y - radius * 0.9,
                        radius * 1.8,
                        radius * 1.8
                    )
                    
                    # Outer arc (0.95 * radius)
                    outer_rect = QRectF(
                        center_x - radius * 0.95,
                        center_y - radius * 0.95,
                        radius * 1.9,
                        radius * 1.9
                    )
                    
                    # Create the shaded path
                    start_rad = math.radians(start_angle)
                    end_rad = math.radians(start_angle + span_angle)
                    
                    # Start from inner point
                    path.moveTo(
                        center_x + radius * 0.9 * math.cos(start_rad),
                        center_y - radius * 0.9 * math.sin(start_rad)
                    )
                    
                    # Draw outer arc
                    path.arcTo(outer_rect, start_angle, span_angle)
                    
                    # Draw line to inner arc end point
                    path.lineTo(
                        center_x + radius * 0.9 * math.cos(end_rad),
                        center_y - radius * 0.9 * math.sin(end_rad)
                    )
                    
                    # Draw inner arc back to start
                    path.arcTo(inner_rect, start_angle + span_angle, -span_angle)
                    
                    # Fill the path with the shade color
                    painter.fillPath(path, shade_color)
                    
                    # Draw cusp lines
                    angle_rad = math.radians(current_angle + 75)
                    middle_angle_rad = math.radians(middle_angle + 75)
                    
                    start_x = center_x + (radius * 0.9) * math.cos(angle_rad)
                    start_y = center_y - (radius * 0.9) * math.sin(angle_rad)
                    end_x = center_x + (radius * 0.95) * math.cos(angle_rad)
                    end_y = center_y - (radius * 0.95) * math.sin(angle_rad)
                    
                    # Draw the line
                    painter.setPen(QPen(line_color, max(1, int(radius / 200))))
                    painter.drawLine(QPoint(int(start_x), int(start_y)), 
                                  QPoint(int(end_x), int(end_y)))
                    
                    # Draw house number in the middle of the house
                    number_radius = radius * .925
                    number_x = center_x + number_radius * math.cos(middle_angle_rad)
                    number_y = center_y - number_radius * math.sin(middle_angle_rad)
                    
                    # Setup font for house numbers
                    font = painter.font()
                    font.setPointSize(int(radius * 0.04))
                    painter.setFont(font)
                    
                    # Convert to Roman numeral
                    house_num = to_roman(i + 1)
                    text_width = painter.fontMetrics().horizontalAdvance(house_num)
                    text_height = painter.fontMetrics().height()
                    
                    text_rect = QRect(
                        int(number_x - text_width/2),
                        int(number_y - text_height/2),
                        text_width,
                        text_height
                    )
                    
                    # Draw number with shadow effect
                    painter.setPen(shadow_color)
                    painter.drawText(text_rect.adjusted(1, 1, 1, 1), 
                                  Qt.AlignmentFlag.AlignCenter, house_num)
                    painter.setPen(line_color)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, house_num)
                    
        except Exception as e:
            print(f"Error drawing house cusps: {str(e)}")

    def draw_chart_text(self, painter):
        """Draw text information around the chart without affecting the chart itself"""
        width = self.width()
        height = self.height()
        
        # Set up font and color
        font = QtGui.QFont('Arial', 9)
        painter.setFont(font)
        if self.current_theme == 'Dark':
            painter.setPen(Qt.GlobalColor.black)
        else:
            painter.setPen(Qt.GlobalColor.white)
        
        # Left side text
        left_x = 10
        top_y = 30
        
        # Check if self.points exists and is not None
        if hasattr(self, 'points') and self.points is not None:
            print("Points exist and are not None")
            for planet, data in self.points.items():
                print(f"Planet: {planet}, Data: {data}")
                if planet != 'Ascendant':
                    # Get sign-specific degree from absolute longitude
                    longitude = data['longitude']
                    sign_degree = longitude % 30  # Get degree within sign
                    
                    # Format in DMS
                    degrees = int(sign_degree)
                    minutes = int((sign_degree - degrees) * 60)
                    seconds = int(((sign_degree - degrees) * 60 - minutes) * 60)
                    
                    # Add retrograde symbol if planet is retrograde
                    retrograde = " ℞" if data.get('is_retrograde') else ""
                    
                    text = f"{planet}: {degrees}°{minutes}'{seconds}\" {data['sign']}{retrograde}"
                    painter.drawText(left_x, top_y, text)
                    top_y += 20
        
        # Right side text
        right_x = width - 200
        top_y = 30
        
        # Check if self.houses exists and is not None
        if hasattr(self, 'houses') and self.houses is not None:
            print("Houses exist and are not None")
            for i, (house, data) in enumerate(self.houses.items(), 1):
                print(f"House {i}: {data}")
                # Get sign-specific degree from absolute longitude
                longitude = float(data['longitude'])
                sign_degree = longitude % 30  # Get degree within sign
                
                # Format in DMS
                degrees = int(sign_degree)
                minutes = int((sign_degree - degrees) * 60)
                seconds = int(((sign_degree - degrees) * 60 - minutes) * 60)
                
                text = f"House {i}: {degrees}°{minutes}'{seconds}\" {data['sign']}"
                painter.drawText(right_x, top_y, text)
                top_y += 20

    def show_settings_menu(self):
        """Show the settings menu below the settings button"""
        self.settings_menu.popup(self.settings_button.mapToGlobal(
            self.settings_button.rect().bottomLeft()
        ))

    def handle_style_change(self, action):
        """Handle planet style change from menu"""
        style = action.data()
        if hasattr(self, 'planet_display'):
            print(f"\nDEBUG - Changing planet display style to: {style}")
            print(f"Current style before change: {self.planet_display._style}")
            # Create a new planet display instance with the new style
            self.planet_display = EnhancedPlanetDisplay(style=style, points=self.points)
            print(f"Style after change: {self.planet_display._style}")
            if hasattr(self, 'points') and self.points:
                print(f"Current points: {list(self.points.keys())}")
            # Force a repaint
            self.repaint()
            self.save_preferences()

    def handle_theme_change(self, action):
        """Handle theme change from menu"""
        theme = action.data()
        self.current_theme = theme
        self.update()
        self.save_preferences()

    def handle_zodiac_change(self, action):
        """Handle zodiac system change from menu"""
        system = action.data()
        # Enable/disable ayanamsa menu based on zodiac system
        self.ayanamsa_menu.setEnabled(system == "Sidereal")
        if hasattr(self, 'input_page') and self.input_page:
            self.input_page.zodiac_combo.setCurrentText(system)
            self.input_page.calculate_chart()  # Recalculate with new settings
        self.update()
        self.save_preferences()

    def handle_calc_type_change(self, action):
        """Handle calculation type change from menu"""
        calc_type = action.data()
        if hasattr(self, 'input_page') and self.input_page:
            self.input_page.calc_type_combo.setCurrentText(calc_type)
            self.input_page.calculate_chart()  # Recalculate with new settings
        self.update()
        self.save_preferences()

    def handle_ayanamsa_change(self, action):
        """Handle ayanamsa change from menu"""
        try:
            ayanamsa = action.data()
            if hasattr(self, 'input_page') and self.input_page:
                self.input_page.ayanamsa_combo.setCurrentText(ayanamsa)
                self.input_page.calculate_chart()  # Recalculate with new settings
            self.update()
            self.save_preferences()
        except Exception as e:
            print(f"Error in handle_ayanamsa_change: {str(e)}")
            traceback.print_exc()

    def handle_house_system_change(self, action):
        """Handle house system change from menu"""
        house_system = action.data()
        if hasattr(self, 'input_page') and self.input_page:
            self.input_page.house_system_combo.setCurrentText(house_system)
            self.input_page.calculate_chart()  # Recalculate with new settings
        self.update()
        self.save_preferences()

    def handle_node_change(self, action):
        """Handle node type change from menu"""
        node_type = action.data()
        if hasattr(self, 'input_page') and self.input_page:
            self.input_page.node_type.setCurrentText(node_type)
            self.input_page.calculate_chart()  # Recalculate with new settings
        self.update()
        self.save_preferences()

    def save_preferences(self):
        """Save current chart preferences"""
        settings = QSettings('Cosmic6', 'EasternChart')
        if hasattr(self, 'planet_display'):
            settings.setValue('planet_style', self.planet_display.style)
        settings.setValue('theme', self.current_theme)
        
        # Save calculation settings
        settings.setValue('zodiac_system', self.zodiac_group.checkedAction().data())
        settings.setValue('calc_type', self.calc_type_group.checkedAction().data())
        settings.setValue('ayanamsa', self.ayanamsa_group.checkedAction().data())
        settings.setValue('house_system', self.house_group.checkedAction().data())
        settings.setValue('node_type', self.node_group.checkedAction().data())

    def load_preferences(self):
        """Load saved chart preferences"""
        settings = QSettings('Cosmic6', 'EasternChart')
        
        # Load planet style
        if hasattr(self, 'planet_display'):
            style = settings.value('planet_style', 'text')
            self.planet_display.style = style
            # Update the menu to reflect loaded style
            for action in self.style_group.actions():
                if action.data() == style:
                    action.setChecked(True)
        
        # Load theme
        theme = settings.value('theme', 'Dark')
        self.current_theme = theme
        # Update the menu to reflect loaded theme
        for action in self.theme_group.actions():
            if action.data() == theme:
                action.setChecked(True)
                
        # Load calculation settings
        zodiac_system = settings.value('zodiac_system', 'Sidereal')
        calc_type = settings.value('calc_type', 'Geocentric')
        ayanamsa = settings.value('ayanamsa', 'Lahiri')
        house_system = settings.value('house_system', 'Placidus')
        node_type = settings.value('node_type', 'True Node (Rahu/Ketu)')
        
        # Update menus to reflect loaded settings
        for group, value in [
            (self.zodiac_group, zodiac_system),
            (self.calc_type_group, calc_type),
            (self.ayanamsa_group, ayanamsa),
            (self.house_group, house_system),
            (self.node_group, node_type)
        ]:
            for action in group.actions():
                if action.data() == value:
                    action.setChecked(True)
                    
        # Enable/disable ayanamsa menu based on zodiac system
        self.ayanamsa_menu.setEnabled(zodiac_system == "Sidereal")

