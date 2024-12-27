from PyQt6.QtWidgets import QWidget, QTextEdit, QScrollArea, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import traceback

class ResultsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)  # Prevent auto-deletion
        self.setWindowFlags(Qt.WindowType.Widget)  # Ensure it's treated as a widget, not a window
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #000000; }")
        
        # Create text widget
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Set font
        font = QFont("Segoe UI", 10)
        self.results_text.setFont(font)
        
        # Style the text widget
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                selection-background-color: #404040;
                selection-color: #FFFFFF;
            }
        """)
        
        # Add text widget to scroll area
        scroll.setWidget(self.results_text)
        
        # Add scroll area to layout
        layout.addWidget(scroll)
    
    def update_data(self, chart_data):
        """Update the results window with chart data"""
        print("\nDEBUG - ResultsWindow.update_data called")
        
        try:
            if not chart_data:
                print("DEBUG - No chart data provided")
                return
                
            print(f"DEBUG - Chart data meta: {chart_data.get('meta', {})}")
            print(f"DEBUG - Zodiac system: {chart_data.get('meta', {}).get('zodiac_system', 'Not specified')}")
            
            style = """
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { padding: 8px; text-align: left; border: 1px solid #333; }
                th { background-color: #2b2b2b; }
                tr:nth-child(even) { background-color: #1a1a1a; }
                tr:nth-child(odd) { background-color: #262626; }
                .section { margin-bottom: 30px; }
                .section-title { font-size: 18px; font-weight: bold; color: #9370db; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #333; }
            """
            
            # Format planetary positions
            planets_rows = ""
            for planet, details in sorted(chart_data.get('points', {}).items()):
                retrograde = "R" if details.get('is_retrograde', False) else ""
                planets_rows += f"""
                    <tr>
                        <td>{planet}</td>
                        <td>{details.get('sign', '-')}</td>
                        <td>{self.format_degree(details.get('longitude', 0))}{retrograde}</td>
                        <td>{details.get('house', '-')}</td>
                        <td>{details.get('nakshatra', '-')}</td>
                        <td>{details.get('pada', '-')}</td>
                        <td>{details.get('dignity', '-')}</td>
                    </tr>
                """
            
            # Format houses
            houses_rows = ""
            houses = chart_data.get('houses', {})
            for i in range(1, 13):
                # Convert string keys to int if needed
                house = houses.get(i, houses.get(str(i), {}))
                houses_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{house.get('sign', '-')}</td>
                        <td>{self.format_degree(house.get('longitude', 0))}</td>
                        <td>{house.get('ruler', '-')}</td>
                    </tr>
                """
            
            # Format aspects
            aspects_rows = ""
            for aspect in chart_data.get('aspects', []):
                aspects_rows += f"""
                    <tr>
                        <td>{aspect.get('planet1', '-')}</td>
                        <td>{aspect.get('aspect', '-')}°</td>
                        <td>{aspect.get('planet2', '-')}</td>
                        <td>{aspect.get('orb', '-')}°</td>
                    </tr>
                """
            
            # Format technical details
            meta = chart_data.get('meta', {})
            gst = meta.get('sidereal_time_0', 0)
            lst = meta.get('local_sidereal_time', 0)
            
            # Format times
            gst_str = self.format_time(gst)
            lst_str = self.format_time(lst)
            
            # Format delta T
            delta_t = meta.get('delta_t', 0)
            delta_t_str = f"+{delta_t:.3f}s" if delta_t >= 0 else f"{delta_t:.3f}s"
            
            # Format final HTML
            formatted_html = f"""
            <div style='font-family: Segoe UI; color: #FFFFFF; padding: 20px;'>
                <style>{style}</style>
                
                <div class='section'>
                    <div class='section-title'>Chart Information</div>
                    <p><b>{chart_data.get('name', '')} - Natal Chart</b></p>
                    <p>Date/Time: {chart_data.get('datetime', '')}</p>
                    <p>Location: {chart_data.get('city', '')} ({chart_data.get('latitude', '')}, {chart_data.get('longitude', '')})</p>
                    <p>{meta.get('calculation_type', 'Geocentric')} {meta.get('zodiac_system', 'Tropical')} Zodiac<br>{meta.get('house_system', 'Placidus')} Houses</p>
                </div>
                
                <div class='section'>
                    <div class='section-title'>Planetary Positions</div>
                    <table>
                        <tr>
                            <th>Planet</th>
                            <th>Sign</th>
                            <th>Position</th>
                            <th>House</th>
                            <th>Nakshatra</th>
                            <th>Pada</th>
                            <th>Status</th>
                        </tr>
                        {planets_rows}
                    </table>
                </div>
                
                <div class='section'>
                    <div class='section-title'>Houses</div>
                    <table>
                        <tr>
                            <th>House</th>
                            <th>Sign</th>
                            <th>Position</th>
                            <th>Ruler</th>
                        </tr>
                        {houses_rows}
                    </table>
                </div>
                
                <div class='section'>
                    <div class='section-title'>Aspects</div>
                    <table>
                        <tr>
                            <th>Planet 1</th>
                            <th>Aspect</th>
                            <th>Planet 2</th>
                            <th>Orb</th>
                        </tr>
                        {aspects_rows}
                    </table>
                </div>
                
                <div class='section'>
                    <div class='section-title'>Technical Details</div>
                    <p>JDE = {meta.get('julian_day', 0):.6f}</p>
                    <p>ΔT = {delta_t_str}</p>
                    <p>ET = JDE {meta.get('ephemeris_time', 0):.6f}</p>
                    <p>GST = {gst_str}</p>
                    <p>LST = {lst_str}</p>
                    <p>Ayanamsa = {self.format_degree(meta.get('ayanamsa_value', 0))}</p>
                    <p>True Obliquity = {self.format_degree(meta.get('obliquity', 0))}</p>
                </div>
            </div>
            """
            
            print("DEBUG - Setting formatted HTML in text browser")
            self.results_text.setHtml(formatted_html)
            print("DEBUG - Results window updated successfully")
            
        except Exception as e:
            print(f"ERROR in update_data: {str(e)}")
            traceback.print_exc()
    
    def format_degree(self, degree):
        """Format degree to deg/min/sec format"""
        deg = int(degree)
        min_float = (degree - deg) * 60
        min = int(min_float)
        sec = int((min_float - min) * 60)
        return f"{deg}° {min}' {sec}\""
    
    def format_time(self, time):
        """Format time value to HH:MM:SS"""
        hours = int(time)
        min_float = (time - hours) * 60
        minutes = int(min_float)
        seconds = int((min_float - minutes) * 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def set_html_content(self, html_content):
        """Set the HTML content of the results window"""
        self.results_text.setHtml(html_content)
