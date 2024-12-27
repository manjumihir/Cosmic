from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QPoint, QRect, QRectF
from PyQt6.QtGui import (QPainter, QPen, QColor, QFont, QFontMetrics, QPainterPath,
                      QAction, QActionGroup, QBrush)
import math
import traceback

class EasternChartFunctions(QWidget):
    # Constants
    ZODIAC_SYMBOLS = {
        'Aries': '', 'Taurus': '', 'Gemini': '', 'Cancer': '',
        'Leo': '', 'Virgo': '', 'Libra': '', 'Scorpio': '',
        'Sagittarius': '', 'Capricorn': '', 'Aquarius': '', 'Pisces': ''
    }
    
    PLANET_SYMBOLS = {
        'Sun': '', 'Moon': '', 'Mercury': '', 'Venus': '', 'Mars': '',
        'Jupiter': '', 'Saturn': '', 'Rahu': '', 'Ketu': ''
    }
    
    NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]
    
    NAKSHATRA_LORDS = {
        'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun', 'Rohini': 'Moon',
        'Mrigashira': 'Mars', 'Ardra': 'Rahu', 'Punarvasu': 'Jupiter', 'Pushya': 'Saturn',
        'Ashlesha': 'Mercury', 'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
        'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu', 'Vishakha': 'Jupiter',
        'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury', 'Mula': 'Ketu', 'Purva Ashadha': 'Venus',
        'Uttara Ashadha': 'Sun', 'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
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
        self.planet_display = None
        
        # Initialize theme
        self.current_theme = 'Light'  # Default theme
        self.themes = {
            'Light': {
                'background': QColor(255, 255, 255),
                'text': QColor(0, 0, 0),
                'lines': QColor(0, 0, 0),
                'houses': QColor(200, 200, 200),
                'planets': QColor(0, 0, 0),
                'rings': QColor(150, 150, 150),
                'house_numbers': QColor(0, 0, 0),
                'nakshatra_lord': QColor(0, 100, 0)
            },
            'Dark': {
                'background': QColor(30, 30, 30),
                'text': QColor(255, 255, 255),
                'lines': QColor(255, 255, 255),
                'houses': QColor(100, 100, 100),
                'planets': QColor(255, 255, 255),
                'rings': QColor(100, 100, 100),
                'house_numbers': QColor(255, 255, 255),
                'nakshatra_lord': QColor(0, 255, 0)
            },
            'Classic': {
                'background': QColor(245, 245, 220),  # Beige
                'text': QColor(101, 67, 33),         # Dark Brown
                'lines': QColor(139, 69, 19),        # Saddle Brown
                'houses': QColor(160, 82, 45),       # Sienna
                'planets': QColor(101, 67, 33),      # Dark Brown
                'rings': QColor(139, 69, 19),        # Saddle Brown
                'house_numbers': QColor(101, 67, 33), # Dark Brown
                'nakshatra_lord': QColor(0, 100, 0)  # Dark Green
            }
        }
        
        # Initialize planet display
        self.planet_display = EnhancedPlanetDisplay()
        
    def change_theme(self, theme):
        """Change the chart's color theme"""
        # Implement theme change logic here
        pass

    def paint_event(self, event):
        """Handles the painting of the widget"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Implement painting logic here
        pass

    def toggle_transits(self):
        """Toggle transit display and update the chart"""
        print("\nDEBUG - toggle_transits called")
        self.show_transits = self.transit_action.isChecked()
        print(f"Show transits set to: {self.show_transits}")
        
        # If toggling on and no transit data exists, calculate current positions
        if self.show_transits and not self.transit_data:
            print("No transit data available - need to calculate current positions")
            # You'll need to implement this part to get current planetary positions
            self.calculate_current_transits()
        else:
            print(f"Transit data exists: {self.transit_data is not None}")
        
        self.update()  # Force redraw
        print("Chart update requested")

    def draw_nakshatra_lines(self, painter, cx, cy, radius):
        """Draw nakshatra division lines in green ring"""
        # Set up colors based on theme
        line_color = self.themes[self.current_theme]['lines']
        text_color = self.themes[self.current_theme]['text']
        
        # Draw the line
        pen = QPen(line_color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Each nakshatra is exactly 13.333... degrees
        nakshatra_degrees = 360 / 27
        
        for i in range(27):
            # Start from 270° (top/Aries) and go counterclockwise
            angle = 270 - (i * nakshatra_degrees)
            angle_rad = math.radians(-angle)
            
            # Draw lines in green ring only
            x1 = cx + radius * math.cos(angle_rad)        # Outer edge
            y1 = cy - radius * math.sin(angle_rad)
            x2 = cx + radius * 0.85 * math.cos(angle_rad) # Inner edge of purple ring
            y2 = cy - radius * 0.85 * math.sin(angle_rad)
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_nakshatras(self, painter, cx, cy, radius):
        """Draw nakshatra names with larger font"""
        scale = self.calculate_scale_factors(radius)
        
        # Define short names for nakshatras - simplified version
        SHORT_NAMES = {
            'Ashwini': 'Ashwini', 'Bharani': 'Bharani', 'Krittika': 'Krittika',
            'Rohini': 'Rohini', 'Mrigashira': 'Mrigashira', 'Ardra': 'Ardra',
            'Punarvasu': 'Punarvasu', 'Pushya': 'Pushya', 'Ashlesha': 'Ashlesha',
            'Magha': 'Magha', 'Purva Phalguni': 'P Phalguni', 'Uttara Phalguni': 'U Phalguni',
            'Hasta': 'Hasta', 'Chitra': 'Chitra', 'Swati': 'Swati',
            'Vishakha': 'Vishakha', 'Anuradha': 'Anuradha', 'Jyeshtha': 'Jyeshtha',
            'Mula': 'Mula', 'Purva Ashadha': 'P Ashadha', 'Uttara Ashadha': 'U Ashadha',
            'Shravana': 'Shravana', 'Dhanishta': 'Dhanishta', 'Shatabhisha': 'Shatabhisha',
            'Purva Bhadrapada': 'P Bhadrapada', 'Uttara Bhadrapada': 'U Bhadrapada', 'Revati': 'Revati'
        }
        
        nakshatra_font = QFont()
        nakshatra_font.setPointSize(int(scale['nakshatra_size']))
        
        # Create a smaller font for the lords
        lord_font = QFont()
        lord_font.setPointSize(int(scale['nakshatra_size'] * 0.8))  # 80% of nakshatra name size
        
        painter.setPen(self.themes[self.current_theme]['text'])
        
        nakshatra_degrees = 360 / 27
        
        for i, nakshatra in enumerate(self.NAKSHATRAS):
            angle = 270 - (i * nakshatra_degrees)
            mid_angle = angle - (nakshatra_degrees / 2)
            angle_rad = math.radians(-mid_angle)
            
            x = cx + radius * scale['nakshatra_radius'] * math.cos(angle_rad)
            y = cy - radius * scale['nakshatra_radius'] * math.sin(angle_rad)
            
            painter.save()
            painter.translate(x, y)
            text_angle = mid_angle - 90
            if text_angle > 90 or text_angle < -90:
                text_angle += 180
            painter.rotate(text_angle)
            
            # Use shorter text
            short_name = SHORT_NAMES[nakshatra]
            lord_name = self.NAKSHATRA_LORDS[nakshatra]
            
            # Create larger bounding box to accommodate both texts
            box_width = scale['nakshatra_size'] * 6
            box_height = scale['nakshatra_size'] * 3  # Increased height for two lines
            
            # Create rectangle with larger dimensions
            text_rect = QRectF(
                -box_width/2,
                -box_height/2,
                box_width,
                box_height
            )
            
            # Draw nakshatra name
            painter.setFont(nakshatra_font)
            painter.setPen(self.themes[self.current_theme]['text'])  # Regular text color for nakshatra name
            name_rect = QRectF(
                -box_width/2,
                -box_height/2,
                box_width,
                box_height/2
            )
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, short_name)
            
            # Draw lord name
            painter.setFont(lord_font)
            painter.setPen(self.themes[self.current_theme]['nakshatra_lord'])  # Green color for lord name
            lord_rect = QRectF(
                -box_width/2,
                0,  # Start from middle of box
                box_width,
                box_height/2
            )
            painter.drawText(lord_rect, Qt.AlignmentFlag.AlignCenter, lord_name)
            
            painter.restore()

    def calculate_scale_factors(self, radius):
        """Calculate scaling factors based on chart radius"""
        self.scale = {
            'symbol_size': int(radius * 0.06),     # Zodiac symbols
            'name_size': int(radius * 0.04),       # Zodiac names
            'planet_size': int(radius * 0.15),     # Planet size
            'nakshatra_size': int(radius * 0.03),  # Nakshatra text
            'degree_size': int(radius * 0.06),     # Degree text
            'line_width': max(1, int(radius * 0.004)),
            'text_margin': int(radius * 0.02),
            
            # Ring radii
            'outer_ring': 0.85,        # Purple ring (Zodiac)
            'middle_ring': 0.85,      # Purple ring (Zodiac)
            'inner_ring': 0.7,        # Yellow ring (Planets)
            'center_ring': 0.25,      # Inner circle
            
            # Different radii for text vs symbol modes
            'planet_radius': 1,    # Add this line - general planet radius
            'planet_radius_text': 0.85,     # Radius when in text mode
            'planet_radius_symbol': 0.55,   # Radius when in symbol mode
            'transit_radius_text': 0.72,    # Transit radius in text mode
            'transit_radius_symbol': 0.52,  # Transit radius in symbol mode
            'zodiac_radius': 0.925,         # Keep the same
            'nakshatra_radius': 0.96        # Keep the same
        }
        return self.scale

    def draw_house_cusps(self, painter, cx, cy, radius):
        """Draw house cusp lines and Roman numeral numbers near the periphery"""
        try:
            if not hasattr(self, 'house_cusps') or not self.house_cusps:
                return
            
            # Roman numeral conversion dictionary
            ROMAN_NUMERALS = {
                1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI',
                7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'
            }
            
            scale = self.calculate_scale_factors(radius)
            
            # Define the spans
            outer_span = 0.83
            inner_span = 0.30
            
            # Move numbers closer to periphery (increased from previous value)
            number_radius = radius * 0.80  # Increased to move numbers outward
            
            # Use theme color
            cusp_pen = QPen(self.themes[self.current_theme]['houses'])
            cusp_pen.setWidth(1)
            painter.setPen(cusp_pen)
            
            # Set up font for house numbers with larger size
            font = QFont('Arial', int(radius * 0.04))  # Increased from 0.035
            font.setWeight(QFont.Weight.ExtraBold)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
            painter.setFont(font)
            
            # Draw lines and numbers for each house
            for i in range(12):
                # Get current and next cusp angles
                current_cusp = float(self.house_cusps[i])
                next_cusp = float(self.house_cusps[(i + 1) % 12])
                
                # Handle case where house crosses 0°
                if next_cusp < current_cusp:
                    next_cusp += 360
                
                # Calculate middle of the house
                mid_angle = (current_cusp + next_cusp) / 2
                if mid_angle > 360:
                    mid_angle -= 360
                    
                # Draw cusp line
                angle_rad = math.radians(90 + current_cusp)
                x1 = cx + radius * inner_span * math.cos(angle_rad)
                y1 = cy - radius * inner_span * math.sin(angle_rad)
                x2 = cx + radius * outer_span * math.cos(angle_rad)
                y2 = cy - radius * outer_span * math.sin(angle_rad)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
                # Calculate position for house number
                mid_angle_rad = math.radians(90 + mid_angle)
                num_x = cx + number_radius * math.cos(mid_angle_rad)
                num_y = cy - number_radius * math.sin(mid_angle_rad)
                
                # Create rectangle for text
                text_width = radius * 0.07  # Slightly smaller text box
                text_rect = QRectF(
                    num_x - text_width/2,
                    num_y - text_width/2,
                    text_width,
                    text_width
                )
                
                # Draw Roman numeral
                house_number = i + 1
                roman_numeral = ROMAN_NUMERALS[house_number]
                
                # Save current state
                painter.save()
                
                # Translate to number position and rotate text
                painter.translate(num_x, num_y)
                text_angle = mid_angle
                if text_angle > 90 or text_angle < -90:
                    text_angle += 180
                painter.rotate(-text_angle)
                
                # Draw the text
                new_rect = QRectF(-text_width/2, -text_width/2, text_width, text_width)
                
                # Draw text with slight offset for shadow effect
                shadow_color = QColor(0, 0, 0, 100) if self.current_theme == self.themes['Light'] else QColor(255, 255, 255, 100)
                painter.setPen(shadow_color)
                shadow_rect = QRectF(-text_width/2 + 1, -text_width/2 + 1, text_width, text_width)
                painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, roman_numeral)
                
                # Draw main text
                painter.setPen(self.themes[self.current_theme]['house_numbers'])
                painter.drawText(new_rect, Qt.AlignmentFlag.AlignCenter, roman_numeral)
                
                # Restore state
                painter.restore()
                
        except Exception as e:
            print(f"Error in draw_house_cusps: {str(e)}")
            traceback.print_exc()

    def draw_planets(self, painter, cx, cy, radius):
        """Draw either natal or transit planets based on toggle"""
        print(f"\nDEBUG - draw_planets called")
        print(f"Show transits: {self.show_transits}")
        print(f"Has transit data: {self.transit_data is not None}")
        
        scale = self.calculate_scale_factors(radius)
        
        if self.show_transits and self.transit_data:
            # Only draw transit planets when toggle is on
            print("Drawing transit planets only")
            self.draw_planet_set(painter, cx, cy, radius, self.transit_data, scale, is_transit=True)
        else:
            # Draw natal planets when toggle is off
            if self.points:
                print("Drawing natal planets")
                self.draw_planet_set(painter, cx, cy, radius, self.points, scale, is_transit=False)
            else:
                print("No natal points available")

    def draw_planet_set(self, painter, cx, cy, radius, points, scale, is_transit=False):
        """Draw a set of planets (either natal or transit)"""
        # Group planets by proximity
        proximity_threshold = 15
        planet_groups = self.group_planets_by_proximity(points, proximity_threshold)
        
        # Choose radius based on style and transit status
        if self.planet_display.style == 'text':
            base_radius = radius * (scale['transit_radius_text'] if is_transit else scale['planet_radius_text'])
        else:
            base_radius = radius * (scale['transit_radius_symbol'] if is_transit else scale['planet_radius_symbol'])
        
        for group in planet_groups:
            if len(group) == 1:
                planet_name = group[0]
                if is_transit and planet_name == 'Ascendant':
                    continue
                self.draw_single_planet(painter, cx, cy, base_radius, planet_name, 
                                     points[planet_name], scale, is_transit)
            else:
                if is_transit:
                    group = [p for p in group if p != 'Ascendant']
                    if not group:
                        continue
                self.draw_planet_group(painter, cx, cy, base_radius, group, scale, is_transit)

    def draw_single_planet(self, painter, cx, cy, radius, planet_name, planet_data, scale, is_transit=False):
        """Draw a single planet with transit modifications if needed"""
        angle_rad = math.radians(90 + planet_data['longitude'])
        radius_scaled = radius * scale['planet_radius']
        
        x = cx + radius_scaled * math.cos(angle_rad)
        y = cy - radius_scaled * math.sin(angle_rad)

        # Modify appearance for transit planets
        if is_transit:
            # Use different style for transit planets
            transit_style = 'text' if self.planet_display.style == 'text' else 'basic'
            transit_display = EnhancedPlanetDisplay(style=transit_style)
            
            # Draw transit symbol with modifications
            painter.save()
            painter.setPen(QPen(QtGui.QColor(100, 100, 100)))  # Lighter color for transits
            transit_display.draw_planet(painter, planet_name, int(x), int(y), 
                                     int(scale['planet_size'] * 0.8))  # Slightly smaller
            painter.restore()
        else:
            # Draw natal planet normally
            self.planet_display.draw_planet(painter, planet_name, int(x), int(y), 
                                         int(scale['planet_size']))

    def draw_planet_group(self, painter, cx, cy, radius, group, scale, is_transit=False):
        """Draw a group of planets with adjusted spacing"""
        if len(group) == 1:
            planet_name = group[0]
            self.draw_single_planet(painter, cx, cy, radius, planet_name, 
                                  self.points[planet_name], scale, is_transit)
        else:
            # Adjust radius step based on display style
            if self.planet_display.style == 'text':
                radius_step = scale['planet_size'] * 0.4  # Smaller step for text mode
            else:
                radius_step = scale['planet_size'] * 0.8  # Larger step for symbol mode
            
            for i, planet_name in enumerate(group):
                adjusted_radius = radius - (i * radius_step)
                longitude = self.points[planet_name]['longitude']
                angle_rad = math.radians(90 + longitude)
                x = cx + adjusted_radius * math.cos(angle_rad)
                y = cy - adjusted_radius * math.sin(angle_rad)
                
                self.planet_display.draw_planet(painter, planet_name, int(x), int(y), 
                                         scale['planet_size'])

    def draw_planets_with_arrows(self, painter, cx, cy, radius):
        """Draw planets with arrows pointing to their exact positions"""
        if not self.points:
            return
        
        scale = self.calculate_scale_factors(radius)
        
        for planet_name, planet_data in self.points.items():
            if 'longitude' not in planet_data:
                continue
            
            # Log the original longitude
            longitude = float(planet_data['longitude'])
            print(f"{planet_name} original longitude: {longitude}")
            
            # Adjust for 0° Aries at 12 o'clock
            angle_rad = math.radians(-longitude + 90)
            print(f"{planet_name} adjusted angle (radians): {angle_rad}")
            
            # Calculate position for the planet symbol
            x = cx + radius * 0.5 * math.cos(angle_rad)
            y = cy + radius * 0.5 * math.sin(angle_rad)
            print(f"{planet_name} position: ({x}, {y})")
            
            # Draw arrow pointing to the exact degree
            arrow_x = cx + radius * 0.8 * math.cos(angle_rad)
            arrow_y = cy + radius * 0.8 * math.sin(angle_rad)
            painter.drawLine(int(arrow_x), int(arrow_y), int(x), int(y))
            
            # Draw planet symbol
            painter.save()
            painter.translate(x, y)
            
            # Rotate text for readability
            text_angle = -longitude + 90
            if 90 < text_angle < 270:
                text_angle += 180
            painter.rotate(-text_angle)
            
            # Draw planet name
            font = QtGui.QFont('Arial', int(scale['planet_size'] * 0.35))
            painter.setFont(font)
            text = self.PLANET_SYMBOLS.get(planet_name, planet_name)
            painter.drawText(-20, -10, 40, 20, Qt.AlignmentFlag.AlignCenter, text)
            
            # Draw degree
            if 'degree' in planet_data:
                degree_text = f"{planet_data['degree']:.1f}°"
                painter.setFont(QtGui.QFont('Arial', int(scale['planet_size'] * 0.3)))
                painter.drawText(-20, 5, 40, 20, Qt.AlignmentFlag.AlignCenter, degree_text)
            
            painter.restore()

    def draw_chart_text(self, painter):
        """Draw text information around the chart without affecting the chart itself"""
        width = self.width()
        height = self.height()
        
        # Set up font and color
        font = QtGui.QFont('Arial', 9)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.white)
        
        # Left side text
        left_x = 10
        top_y = 30
        
        # Check if self.points exists and is not None
        if hasattr(self, 'points') and self.points is not None:
            for planet, data in self.points.items():
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
                    
                    text = f"{planet}: {degrees}°{minutes}'{seconds}\"{data['sign']}{retrograde}"
                    painter.drawText(left_x, top_y, text)
                    top_y += 20
        
        # Right side text
        right_x = width - 200
        top_y = 30
        
        # Check if self.houses exists and is not None
        if hasattr(self, 'houses') and self.houses is not None:
            for i, (house, data) in enumerate(self.houses.items(), 1):
                # Get sign-specific degree from absolute longitude
                longitude = float(data['longitude'])
                sign_degree = longitude % 30  # Get degree within sign
                
                # Format in DMS
                degrees = int(sign_degree)
                minutes = int((sign_degree - degrees) * 60)
                seconds = int(((sign_degree - degrees) * 60 - minutes) * 60)
                
                text = f"House {i}: {degrees}°{minutes}'{seconds}\"{data['sign']}"
                painter.drawText(right_x, top_y, text)
                top_y += 20

    def calculate_current_transits(self):
        """Calculate current planetary positions for transits"""
        try:
            from datetime import datetime
            current_time = datetime.now()
            
            # Create transit data structure without Ascendant
            self.transit_data = {
                'Sun': {'longitude': 0, 'sign': 'Aries', 'degree': 0},
                'Moon': {'longitude': 30, 'sign': 'Taurus', 'degree': 0},
                'Mercury': {'longitude': 60, 'sign': 'Gemini', 'degree': 0},
                'Venus': {'longitude': 90, 'sign': 'Cancer', 'degree': 0},
                'Mars': {'longitude': 120, 'sign': 'Leo', 'degree': 0},
                'Jupiter': {'longitude': 150, 'sign': 'Virgo', 'degree': 0},
                'Saturn': {'longitude': 180, 'sign': 'Libra', 'degree': 0},
                # Note: Some astrologers include Rahu/Ketu in transits, others don't
                'Rahu': {'longitude': 210, 'sign': 'Scorpio', 'degree': 0},
                'Ketu': {'longitude': 30, 'sign': 'Taurus', 'degree': 0}
            }
            
            # Add is_retrograde flag for all planets
            for planet_data in self.transit_data.values():
                planet_data['is_retrograde'] = False
            
            print(f"Calculated transit data: {self.transit_data}")
        except Exception as e:
            print(f"Error calculating transits: {str(e)}")
            import traceback
            traceback.print_exc()

    def draw_planet(self, painter, planet, x, y, size):
        painter.save()
        planet_color = self.PLANET_COLORS.get(planet, QColor(255, 255, 255))
        
        if self._style == 'text':
            # Get center of chart for angle calculation
            center_x = painter.device().width() / 2
            center_y = painter.device().height() / 2
            dx = x - center_x
            dy = y - center_y
            angle = math.degrees(math.atan2(dy, dx))
            
            # Format text with degree in brackets
            if planet == 'Ascendant':
                name_text = "Asc"
            else:
                name_text = planet
                
            # Add degree information for text style
            if self._points and planet in self._points:
                degree = self._points[planet].get('degree', 0)
                display_text = f"{name_text} ({degree:.1f}°)"
            else:
                display_text = name_text
            
            # Position and rotate text
            painter.translate(x, y)
            painter.rotate(angle)
            if angle > 90 or angle < -90:
                painter.rotate(180)
            
            # Set font and color for text style
            font = QFont('Arial', int(size/2))
            painter.setFont(font)
            painter.setPen(QPen(planet_color, 1))
            
            # Draw the combined text
            text_rect = QRect(
                -int(size * 3),
                -int(size/2),
                int(size * 6),
                int(size)
            )
            alignment = Qt.AlignmentFlag.AlignLeft if (-90 <= angle <= 90) else Qt.AlignmentFlag.AlignRight
            painter.drawText(text_rect, alignment, display_text)
            
        else:
            # All other styles (basic, geometric, enhanced, labeled) remain unchanged
            if self._style == 'basic':
                # Basic symbol only
                painter.setPen(QPen(planet_color, 2))
                font = QFont('Arial', size)
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self._style == 'geometric':
                # Geometric style remains unchanged
                painter.setBrush(QColor(planet_color).lighter(150))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QFont('Arial', int(size * 0.8))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self._style == 'enhanced':
                # Draw glow effect
                glow = QtWidgets.QGraphicsDropShadowEffect()
                glow.setColor(planet_color)
                glow.setBlurRadius(size//4)
                
                # Draw circular background
                painter.setBrush(QColor(planet_color).lighter(170))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                # Draw symbol
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QFont('Arial', int(size * 0.8))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self._style == 'labeled':
                # Draw background circle
                painter.setBrush(QColor(planet_color).lighter(170))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                # Draw symbol
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QFont('Arial', int(size * 0.6))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2-5, size, size//2,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
                # Draw planet name below
                font.setPointSize(int(size * 0.3))
                painter.setFont(font)
                painter.drawText(x-size//2, y, size, size//2,
                               Qt.AlignmentFlag.AlignCenter,
                               planet[:3])  # First 3 letters of planet name
    
        painter.restore()

    def group_planets_by_proximity(self, points, proximity_threshold):
        """
        Group planets that are within proximity_threshold degrees of each other.
        Returns a list of groups, where each group is a list of planet names.
        """
        if not points:
            return []
            
        # Create list of (planet_name, longitude) tuples
        planet_positions = [(name, data['longitude']) for name, data in points.items()]
        
        # Sort by longitude
        planet_positions.sort(key=lambda x: x[1])
        
        # Initialize groups
        groups = []
        current_group = [planet_positions[0][0]]
        last_longitude = planet_positions[0][1]
        
        # Group planets
        for planet_name, longitude in planet_positions[1:]:
            # Check if planet is within threshold of the last planet in current group
            if abs(longitude - last_longitude) <= proximity_threshold:
                current_group.append(planet_name)
            else:
                groups.append(current_group)
                current_group = [planet_name]
            last_longitude = longitude
            
        # Add the last group
        if current_group:
            groups.append(current_group)
            
        return groups

class EnhancedPlanetDisplay:
    from PyQt6.QtGui import QColor, QFont, QPen, QBrush
    
    PLANET_SYMBOLS = {
        'Sun': '☉', 
        'Moon': '☽', 
        'Mercury': '☿', 
        'Venus': '♀', 
        'Mars': '♂',
        'Jupiter': '♃', 
        'Saturn': '♄', 
        'Uranus': '♅',    # Added
        'Neptune': '♆',    # Added
        'Pluto': '♇',     # Added
        'Rahu': '☊', 
        'Ketu': '☋',
        'Ascendant': 'As'
    }
    
    PLANET_COLORS = {
        'Sun': QColor(227, 135, 16),      # Orange
        'Moon': QColor(130, 170, 9),    # Silver
        'Mars': QColor(255, 0, 0),        # Red
        'Mercury': QColor(0, 255, 0),     # Green
        'Jupiter': QColor(204, 190, 0),   # Yellow
        'Venus': QColor(0, 255, 255),     # Cyan
        'Saturn': QColor(128, 128, 128),  # Gray
        'Rahu': QColor(0, 100, 200),        # Navy
        'Ketu': QColor(209, 47, 36),        # Maroon
        'Ascendant': QColor(177, 3, 252) # White
    }

    def __init__(self, style='basic', points=None):
        self._style = style
        self._points = points
        print(f"Creating new EnhancedPlanetDisplay with style: {style}")
    
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, value):
        self._style = value
        
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, value):
        self._points = value

    def draw_planet(self, painter, planet, x, y, size):
        painter.save()
        planet_color = self.PLANET_COLORS.get(planet, QColor(255, 255, 255))
        
        if self._style == 'text':
            # Get center of chart for angle calculation
            center_x = painter.device().width() / 2
            center_y = painter.device().height() / 2
            dx = x - center_x
            dy = y - center_y
            angle = math.degrees(math.atan2(dy, dx))
            
            # Format text with degree in brackets
            if planet == 'Ascendant':
                name_text = "Asc"
            else:
                name_text = planet
                
            # Add degree information for text style
            if self._points and planet in self._points:
                degree = self._points[planet].get('degree', 0)
                display_text = f"{name_text} ({degree:.1f}°)"
            else:
                display_text = name_text
            
            # Position and rotate text
            painter.translate(x, y)
            painter.rotate(angle)
            if angle > 90 or angle < -90:
                painter.rotate(180)
            
            # Set font and color for text style
            font = QFont('Arial', int(size/2))
            painter.setFont(font)
            painter.setPen(QPen(planet_color, 1))
            
            # Draw the combined text
            text_rect = QRect(
                -int(size * 3),
                -int(size/2),
                int(size * 6),
                int(size)
            )
            alignment = Qt.AlignmentFlag.AlignLeft if (-90 <= angle <= 90) else Qt.AlignmentFlag.AlignRight
            painter.drawText(text_rect, alignment, display_text)
            
        else:
            # All other styles (basic, geometric, enhanced, labeled)
            if self._style == 'basic':
                # Basic symbol only
                painter.setPen(QPen(planet_color, 2))
                font = QFont('Arial', size)
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self._style == 'geometric':
                # Geometric style
                painter.setBrush(QBrush(planet_color.lighter(150)))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QFont('Arial', int(size * 0.8))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self._style == 'enhanced':
                # Draw circular background
                painter.setBrush(QBrush(planet_color.lighter(170)))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                # Draw symbol
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QFont('Arial', int(size * 0.8))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
        
        painter.restore()
