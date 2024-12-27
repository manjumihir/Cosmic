from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QMessageBox, 
    QDialog, QPushButton, QHBoxLayout, QSplitter)
from PyQt6.QtCore import Qt, QPoint
from datetime import datetime
from .yogeswarananda_results import YogeswaranandaResultsWindow

class FloatingCalcWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Add title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 5, 5, 5)
        
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.hide)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        
        title_layout.addStretch()
        title_layout.addWidget(close_button)
        
        # Add text browser
        self.text_browser = QTextBrowser()
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(title_bar)
        layout.addWidget(self.text_browser)
        
        self.setStyleSheet("""
            FloatingCalcWindow {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 5px;
            }
        """)
        
        self.setFixedSize(400, 300)
        
    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

class YogeswaranandaWindow(QWidget):
    def __init__(self, chart_data=None, parent=None):
        super().__init__(parent)
        self.chart_data = chart_data
        self.house_points = {i: 0 for i in range(1, 13)}
        self.calculation_details = ""
        self.results_window = None
        self.calc_text = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create left widget for main content
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create results browser
        self.results_browser = QTextBrowser()
        self.results_browser.setOpenExternalLinks(True)
        left_layout.addWidget(self.results_browser)
        
        # Add left widget to splitter
        self.splitter.addWidget(left_widget)
        
        # Create right widget (initially empty)
        right_widget = QWidget()
        right_widget.setMaximumWidth(0)
        self.splitter.addWidget(right_widget)
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
        self.setLayout(main_layout)
        
        # Update results if chart data is available
        if self.chart_data:
            self.update_data(self.chart_data)
    
    def style_text_browser(self, browser):
        """Apply consistent styling to text browsers"""
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                padding: 20px;
                font-family: monospace;
            }
            QScrollBar:vertical {
                background: #1A1A1A;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar:horizontal {
                background: #1A1A1A;
                height: 15px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #404040;
                min-width: 20px;
                border-radius: 7px;
            }
        """)
    
    def update_data(self, chart_data):
        """Update the window with new chart data"""
        self.chart_data = chart_data
        if hasattr(self, 'results_browser'):
            self.analyze_chart()
            
    def analyze_chart(self):
        """Analyze the chart data and display results"""
        if not self.chart_data:
            self.results_browser.setText("No chart data available")
            return
            
        try:
            # Calculate Yogeswarananda results and store calculation details
            self.calculation_details = self.calculate_yogeswarananada()
            
            # Generate and display main results
            html_content = self.generate_html_results(show_calculations=False)
            self.results_browser.setHtml(html_content)
            
            # If calculations are currently shown, update them
            if self.calc_text and not self.calc_text.isHidden():
                self.calc_text.setHtml(self.calculation_details)
            
        except Exception as e:
            import traceback
            error_msg = f"Error analyzing chart: {str(e)}\n{traceback.format_exc()}"
            self.results_browser.setText(error_msg)
            print(error_msg)
            
    def handle_link_click(self, url):
        """Handle clicks on links in the text browser"""
        if url.toString() == "show_calculations":
            # Show floating window with calculations
            self.show_calculations()
    
    def get_house_lord(self, sign):
        """Get the lord of a sign"""
        sign_lords = {
            'Aries': 'Mars',
            'Taurus': 'Venus',
            'Gemini': 'Mercury',
            'Cancer': 'Moon',
            'Leo': 'Sun',
            'Virgo': 'Mercury',
            'Libra': 'Venus',
            'Scorpio': 'Mars',
            'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn',
            'Aquarius': 'Saturn',
            'Pisces': 'Jupiter'
        }
        return sign_lords.get(sign)

    def get_houses_owned_by(self, planet):
        """Get list of houses owned by a planet"""
        owned_houses = []
        for house_num in range(1, 13):
            house_sign = self.chart_data['houses'][house_num]['sign']
            if self.get_house_lord(house_sign) == planet:
                owned_houses.append(house_num)
        return owned_houses

    def add_points(self, house_num, points, reason=""):
        """Add points to a house and track the reason"""
        self.house_points[house_num] += points
        return f"House {house_num}: +{points} points ({reason})\n"

    def handle_rahu_ketu(self, planet, house_num, points, point_type):
        """Special handling for Rahu/Ketu points"""
        details = ""
        if planet in ['Rahu', 'Ketu']:
            house_sign = self.chart_data['houses'][house_num]['sign']
            house_lord = self.get_house_lord(house_sign)
            
            # Give points to houses owned by the house lord
            for owned_house in self.get_houses_owned_by(house_lord):
                details += self.add_points(owned_house, points, 
                    f"{point_type} points via {planet}'s house lord {house_lord}")
            
            # Extra point for house lord's placement
            lord_house = None
            for h in range(1, 13):
                if self.chart_data['points'][house_lord]['house'] == h:
                    lord_house = h
                    break
            if lord_house:
                details += self.add_points(lord_house, points, 
                    f"Extra {points} points for {house_lord}'s placement (as {planet}'s house lord)")
        
        return details

    def get_current_dasa_lord(self):
        """Determine the current dasa lord from chart data"""
        try:
            # First try to get from dashas if available
            if 'dashas' in self.chart_data:
                current_time = datetime.now()
                for dasha in self.chart_data['dashas']:
                    start_date = dasha['start_date']
                    end_date = dasha['end_date']
                    if start_date <= current_time <= end_date:
                        return dasha['lord']
            
            # If no dashas data, calculate using moon's position
            moon_longitude = self.chart_data['points']['Moon']['longitude']
            birth_date = datetime.strptime(self.chart_data['meta']['datetime'], '%Y-%m-%d %H:%M:%S')
            
            from utils.astro_calc import DashaCalculator
            dasha_calc = DashaCalculator()
            all_dashas = dasha_calc.calculate_dashas(birth_date, moon_longitude)
            
            current_time = datetime.now()
            for dasha in all_dashas:
                if dasha['start_date'] <= current_time <= dasha['end_date']:
                    return dasha['lord']
            
            print("Warning: Could not determine current dasa lord")
            return 'Moon'  # Fallback
            
        except Exception as e:
            print(f"Error determining dasa lord: {e}")
            return 'Moon'  # Fallback

    def calculate_house_strengths(self, x, y, z):
        """Calculate house strengths for given X, Y, Z planets"""
        output = "Point Distribution Details:\n"
        output += "-------------------------\n"
        
        # Handle X (Main Planet)
        x_data = self.chart_data['points'][x]
        if x in ['Rahu', 'Ketu']:
            output += self.handle_rahu_ketu(x, x_data['house'], 1, "Power 1: Main Planet")
        else:
            # Power 1: Houses owned by X
            for house in self.get_houses_owned_by(x):
                output += self.add_points(house, 1, f"Power 1: House owned by {x}")
        # Power 2: House where X is placed
        output += self.add_points(x_data['house'], 2, f"Power 2: House where {x} is placed")
        
        # Handle Y (Star Lord) - only if different from X
        if y != x:
            y_data = self.chart_data['points'][y]
            if y in ['Rahu', 'Ketu']:
                output += self.handle_rahu_ketu(y, y_data['house'], 3, "Power 3: Star Lord")
            else:
                # Power 3: Houses owned by Y
                for house in self.get_houses_owned_by(y):
                    output += self.add_points(house, 3, f"Power 3: House owned by {y}")
            # Power 4: House where Y is placed
            output += self.add_points(y_data['house'], 4, f"Power 4: House where {y} is placed")
        
        # Handle Z (Sub Lord)
        z_data = self.chart_data['points'][z]
        if z in ['Rahu', 'Ketu']:
            output += self.handle_rahu_ketu(z, z_data['house'], 5, "Power 5: Sub Lord")
        else:
            # Power 5: Houses owned by Z
            for house in self.get_houses_owned_by(z):
                output += self.add_points(house, 5, f"Power 5: House owned by {z}")
        # Power 6: House where Z is placed
        output += self.add_points(z_data['house'], 6, f"Power 6: House where {z} is placed")
        
        # Handle cuspal points
        for house_num in range(1, 13):
            house_data = self.chart_data['houses'][house_num]
            
            # Powers 7 & 10: X as cuspal lord
            if house_data['star_lord'] == x:
                output += self.add_points(house_num, 7, f"Power 7: House where {x} is star lord of cusp")
            if house_data['sub_lord'] == x:
                output += self.add_points(house_num, 10, f"Power 10: House where {x} is sub lord of cusp")
            
            # Powers 8 & 11: Y as cuspal lord (only if different from X)
            if y != x:
                if house_data['star_lord'] == y:
                    output += self.add_points(house_num, 8, f"Power 8: House where {y} is star lord of cusp")
                if house_data['sub_lord'] == y:
                    output += self.add_points(house_num, 11, f"Power 11: House where {y} is sub lord of cusp")
            
            # Powers 9 & 12: Z as cuspal lord
            if house_data['star_lord'] == z:
                output += self.add_points(house_num, 9, f"Power 9: House where {z} is star lord of cusp")
            if house_data['sub_lord'] == z:
                output += self.add_points(house_num, 12, f"Power 12: House where {z} is sub lord of cusp")
        
        return output

    def calculate_single_planet(self, planet, role):
        """Helper method to calculate for a single planet"""
        x_data = self.chart_data['points'][planet]
        y = x_data['star_lord']
        z = x_data['sub_lord']
        
        details = f"Planets Involved:\n"
        details += f"{role} (X): {planet}\n"
        details += f"Star Lord (Y): {y}\n"
        details += f"Sub Lord (Z): {z}\n\n"
        
        details += self.calculate_house_strengths(planet, y, z)
        details += "\nResults:\n"
        for house, points in self.house_points.items():
            details += f"House {house}: {points} points\n"
        
        return details

    def calculate_yogeswarananada(self):
        try:
            output = "Yogeswarananda House Strength Calculations\n"
            output += "=========================================\n\n"
            
            calculated_results = {}
            
            # Start with Moon calculations
            moon_data = self.chart_data['points']['Moon']
            moon_star_lord = moon_data['star_lord']
            moon_sub_lord = moon_data['sub_lord']
            
            planets_to_calculate = [
                ('Moon', 'Primary'),
                (moon_star_lord, "Moon's Star Lord")
            ]
            
            # Add remaining planets
            all_planets = ['Sun', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
            for planet in all_planets:
                if planet not in [p[0] for p in planets_to_calculate]:
                    planets_to_calculate.append((planet, planet))
            
            for planet, role in planets_to_calculate:
                if planet not in calculated_results:
                    planet_data = self.chart_data['points'][planet]
                    
                    output += f"\n{role}: {planet} - {planet_data['star_lord']} - {planet_data['sub_lord']}\n"
                    output += "=" * 40 + "\n"
                    self.house_points = {i: 0 for i in range(1, 13)}
                    details = self.calculate_single_planet(planet, "X")
                    output += details
                    calculated_results[planet] = True
            
            return output
            
        except Exception as e:
            import traceback
            return f"Error in calculations: {str(e)}\n{traceback.format_exc()}"

    def generate_html_results(self, show_calculations=False):
        """Generate HTML formatted results"""
        try:
            html_output = """
            <html>
            <head>
                <style>
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #FFFFFF;
                        background-color: #000000;
                        position: relative;
                    }
                    .header {
                        background: #1A1A1A;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        border: 1px solid #333333;
                        margin-top: 40px;
                    }
                    .section {
                        background: #1A1A1A;
                        border: 1px solid #333333;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 20px;
                    }
                    .section-title {
                        color: #FFFFFF;
                        border-bottom: 2px solid #333333;
                        padding-bottom: 5px;
                        margin-bottom: 15px;
                    }
                    table {
                        border-collapse: collapse;
                        margin-bottom: 15px;
                        table-layout: fixed;
                    }
                    th, td {
                        padding: 8px;
                        text-align: center;
                        border: 1px solid #333333;
                    }
                    th {
                        background: #262626;
                        font-weight: bold;
                    }
                    .planet-info {
                        color: #66B2FF;
                    }
                    .points {
                        color: #4CAF50;
                        font-weight: bold;
                        font-size: 1.1em;
                    }
                    .tables-container {
                        white-space: nowrap;
                        overflow-x: auto;
                    }
                    .planet-table {
                        width: 30%;
                        margin-right: 20px;
                        display: inline-table;
                    }
                    .strengths-table {
                        width: 65%;
                        display: inline-table;
                    }
                    .details {
                        white-space: pre-wrap;
                        font-family: monospace;
                        background: #1A1A1A;
                        padding: 15px;
                        border-radius: 8px;
                        margin-top: 20px;
                        line-height: 1.4;
                        font-size: 14px;
                    }
                </style>
            </head>
            <body>
                <div class="header"><h2>Yogeswarananda Analysis</h2></div>
            """
            
            # Process planets in order
            planets_order = ['Moon', 'Sun', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
            
            for planet in planets_order:
                planet_data = self.chart_data['points'][planet]
                star_lord = planet_data['star_lord']
                sub_lord = planet_data['sub_lord']
                
                # Calculate points for this planet
                self.house_points = {i: 0 for i in range(1, 13)}
                self.calculate_house_strengths(planet, star_lord, sub_lord)
                
                html_output += f'<div class="section">'
                html_output += f'<h3 class="section-title">{planet}</h3>'
                
                html_output += '<div class="tables-container">'
                # Planet lords table
                html_output += '<table class="planet-table">'
                html_output += '<tr><th>Planet</th><th>Star Lord</th><th>Sub Lord</th></tr>'
                html_output += f'<tr>'
                html_output += f'<td class="planet-info">{planet}</td>'
                html_output += f'<td class="planet-info">{star_lord}</td>'
                html_output += f'<td class="planet-info">{sub_lord}</td>'
                html_output += '</tr>'
                html_output += '</table>'
                
                # House strengths table
                html_output += '<table class="strengths-table">'
                # Points row
                html_output += '<tr>'
                for house in range(1, 13):
                    html_output += f'<td class="points">{self.house_points[house]}</td>'
                html_output += '</tr>'
                # House numbers row
                html_output += '<tr>'
                for house in range(1, 13):
                    html_output += f'<th>{house}</th>'
                html_output += '</tr>'
                html_output += '</table>'
                html_output += '</div>'
                
                html_output += '</div>'
            
            # Show calculation details if requested
            if show_calculations:
                html_output += '<div class="details">'
                html_output += self.calculation_details.replace('\n', '<br>')
                html_output += '</div>'
            
            html_output += '</body></html>'
            return html_output
            
        except Exception as e:
            import traceback
            return f"Error generating HTML results: {str(e)}\n{traceback.format_exc()}"

    def analyze_house_strengths(self):
        """Analyze house strengths"""
        pass

    def analyze_planetary_positions(self):
        """Analyze planetary positions"""
        pass

    def analyze_aspects(self):
        """Analyze aspects"""
        pass

    def display_results(self):
        """Display results"""
        html_content = self.generate_html_results()
        self.results_browser.setHtml(html_content)
        
        # Create and show detached results window
        self.results_window = YogeswaranandaResultsWindow()
        self.results_window.setParent(None)  # Make it independent
        self.results_window.setWindowFlags(Qt.WindowType.Window)  # Make it a top-level window
        self.results_window.show()
        self.results_window.raise_()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Don't do anything with results_window - let it manage itself
        super().closeEvent(event)

    def toggle_calculations(self):
        """Toggle the calculation details view"""
        if not self.calc_text or self.calc_text.isHidden():
            # Create new text browser if needed
            if not self.calc_text:
                self.calc_text = QTextBrowser()
                self.calc_text.setOpenExternalLinks(True)
            
            # Show calculations
            self.calc_text.setHtml(self.calculation_details)
            self.calc_text.show()
            
            # Remove old widget from splitter if it exists
            if self.splitter.count() > 1:
                old_widget = self.splitter.widget(1)
                old_widget.setParent(None)
                old_widget.deleteLater()
            
            # Add calculation text to splitter
            self.splitter.addWidget(self.calc_text)
            
            # Set splitter sizes for 50-50 split
            width = self.splitter.width()
            self.splitter.setSizes([width//2, width//2])
        else:
            # Hide calculations
            if self.calc_text:
                self.calc_text.hide()
                self.calc_text.setParent(None)
                self.calc_text.deleteLater()
                self.calc_text = None
            
            # Add placeholder widget
            placeholder = QWidget()
            placeholder.setMaximumWidth(0)
            
            # Remove old widget from splitter if it exists
            if self.splitter.count() > 1:
                old_widget = self.splitter.widget(1)
                old_widget.setParent(None)
                old_widget.deleteLater()
            
            self.splitter.addWidget(placeholder)
            
            # Reset splitter sizes to give full width to main content
            self.splitter.setSizes([self.width(), 0])