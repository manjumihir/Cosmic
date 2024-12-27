import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QLineEdit, QPushButton, QGroupBox, 
    QDateTimeEdit, QComboBox, QCheckBox, QScrollArea,
    QCompleter, QTableWidget, QTableWidgetItem, QTextEdit, 
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QApplication,
    QFrame, QInputDialog, QMessageBox, QDialog, QMainWindow, QSplitter,
    QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, QDateTime, Qt, QTimer
import json
import os
from data.constants import PROFILE_PATH
from datetime import datetime, timedelta
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from geopy.exc import GeocoderTimedOut
import pytz
from utils.astro_calc import AstroCalc, DashaCalculator
from PyQt6 import QtGui
from .yogeswarananda_window import YogeswaranandaWindow
from .results_window import ResultsWindow
import traceback
from .sliding_panel import SlidingPanel

class InputPage(QWidget):
    # Add signal for chart calculation
    chart_calculated = pyqtSignal(dict)
    panel_closed = pyqtSignal()  # New signal for panel close
    
    def __init__(self):
        super().__init__()
        self.astro_calc = AstroCalc()
        self.chart_data = None
        self.profile_path = PROFILE_PATH
        self.settings_path = os.path.join(os.path.dirname(PROFILE_PATH), 'settings.json')
        self.init_ui()
        self.load_profile_names()
        self.load_last_profile()
        
    def decimal_to_dms(self, decimal, is_latitude=True):
        """Convert decimal degrees to degrees, minutes, seconds string"""
        direction = ""
        if is_latitude:
            direction = "N" if decimal >= 0 else "S"
        else:
            direction = "E" if decimal >= 0 else "W"
        
        decimal = abs(decimal)
        degrees = int(decimal)
        decimal_minutes = (decimal - degrees) * 60
        minutes = int(decimal_minutes)
        decimal_seconds = (decimal_minutes - minutes) * 60
        seconds = decimal_seconds  # Keep exact seconds value
        
        return f"{degrees}° {minutes}' {seconds:.2f}\" {direction}"
        
    def dms_to_decimal(self, dms_str):
        """Convert DMS string to decimal degrees"""
        try:
            # Remove any spaces around the string and handle empty input
            dms_str = dms_str.strip()
            if not dms_str:
                raise ValueError("Empty input")
            
            # Extract direction (N/S/E/W)
            direction = dms_str[-1].upper()
            if direction not in ['N', 'S', 'E', 'W']:
                raise ValueError("Invalid direction. Must end with N, S, E, or W")
            
            # Remove direction and split into components
            parts = dms_str[:-1].replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
            if len(parts) != 3:
                raise ValueError("Must be in format: DD° MM' SS\" N/S/E/W")
            
            try:
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])  # Keep exact seconds value
            except ValueError:
                raise ValueError("Degrees, minutes, and seconds must be numbers")
            
            if not (0 <= minutes < 60 and 0 <= seconds < 60):
                raise ValueError("Minutes and seconds must be between 0 and 59")
            
            decimal = degrees + minutes/60 + seconds/3600
            
            # Apply direction
            if direction in ['S', 'W']:
                decimal = -decimal
                
            return decimal
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError("Invalid DMS format. Use format: DD° MM' SS\" N/S/E/W")
    
    def update_coord_display(self):
        """Update coordinate displays with proper formatting"""
        try:
            lat_text = self.lat_input.text()
            lon_text = self.long_input.text()
            
            # Only convert if the text contains a decimal number
            if '.' in lat_text:
                lat_decimal = float(lat_text)
                self.lat_input.setText(self.decimal_to_dms(lat_decimal, True))
            
            if '.' in lon_text:
                lon_decimal = float(lon_text)
                self.long_input.setText(self.decimal_to_dms(lon_decimal, False))
                
        except ValueError:
            pass

    def validate_dms_input(self, input_field, is_latitude):
        """Validate DMS input and offer conversion if needed"""
        try:
            input_text = input_field.text().strip()
            if not input_text:
                return False

            # Check if it's in DMS format (ends with direction)
            if input_text[-1].upper() in ['N', 'S'] if is_latitude else ['E', 'W']:
                # Try parsing as DMS
                try:
                    parts = input_text[:-1].replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
                    
                    # Handle partial DMS format (without seconds)
                    if len(parts) == 2:  # Only degrees and minutes
                        parts.append('00')  # Add 00 seconds
                        input_text = f"{parts[0]}° {parts[1]}' 00\" {input_text[-1]}"
                        input_field.setText(input_text)
                    elif len(parts) != 3:
                        raise ValueError("Invalid DMS format")
                    
                    degrees = float(parts[0])
                    minutes = float(parts[1])
                    seconds = float(parts[2])
                    
                    # Validate ranges
                    if not (0 <= minutes < 60 and 0 <= seconds < 60):
                        raise ValueError("Minutes and seconds must be between 0 and 59")
                    
                    # Calculate decimal for range validation
                    decimal = degrees + minutes/60 + seconds/3600
                    if input_text[-1] in ['S', 'W']:
                        decimal = -decimal
                        
                    # Validate coordinate ranges
                    if is_latitude and abs(decimal) > 90:
                        raise ValueError("Latitude must be between 90°N and 90°S")
                    elif not is_latitude and abs(decimal) > 180:
                        raise ValueError("Longitude must be between 180°E and 180°W")
                    
                    return True
                    
                except (ValueError, IndexError) as e:
                    QMessageBox.warning(None, "Invalid Input", str(e))
                    return False
            
            # Try decimal format
            try:
                decimal = float(input_text)
                
                # Validate ranges
                if is_latitude and abs(decimal) > 90:
                    raise ValueError("Latitude must be between -90° and 90°")
                elif not is_latitude and abs(decimal) > 180:
                    raise ValueError("Longitude must be between -180° and 180°")
                
                # Ask for conversion to DMS
                coord_type = "latitude" if is_latitude else "longitude"
                dms_format = self.decimal_to_dms(decimal, is_latitude)
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Question)
                msg.setText(f"Would you like to convert this {coord_type} to degrees, minutes, seconds format?")
                msg.setInformativeText(f"Current value: {decimal}\nWill be converted to: {dms_format}")
                msg.setWindowTitle("Convert Coordinate Format")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.setDefaultButton(QMessageBox.StandardButton.Yes)
                
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    input_field.setText(dms_format)
                return True
                
            except ValueError:
                QMessageBox.warning(None, "Invalid Input", 
                    "Please enter either:\n" +
                    "- DMS format (e.g., 40° 26' N or 40° 26' 46\" N)\n" +
                    "- Decimal format (e.g., 40.446)")
                return False
                
        except Exception as e:
            QMessageBox.warning(None, "Error", str(e))
            return False
    
    def load_profile_names(self):
        """Load existing profile names from storage"""
        try:
            if os.path.exists(self.profile_path):
                profile_names = []
                with open(self.profile_path, 'r') as f:
                    for line in f:
                        if line.strip():  # Skip empty lines
                            profile = json.loads(line)
                            if "name" in profile:
                                profile_names.append(profile["name"])
                
                # Clear existing items
                self.name_input.clear()
                if profile_names:
                    self.name_input.addItems(profile_names)
                    
                    # Add completer for search functionality
                    completer = QCompleter(profile_names)
                    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                    self.name_input.setCompleter(completer)
        except Exception as e:
            print(f"Error loading profiles: {e}")
    
    def init_ui(self):
        # Create main layout with proper margins
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create scroll area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Main container widget
        container = QWidget()
        container.setMinimumWidth(300)
        
        # Use VBoxLayout for uniform spacing
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Birth Details Group
        personal_group = QGroupBox("Birth Details")
        personal_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        personal_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold;
                margin-top: 16px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 8px;
            }
            QLineEdit, QComboBox {
                min-width: 200px;
            }
            QComboBox {
                border: 1px solid #663399;
                padding: 4px;
                padding-right: 20px;
            }
            QComboBox:hover {
                border: 1px solid #7a40b5;
            }
            QComboBox:focus {
                border: 2px solid #7a40b5;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                background: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #663399;
                margin-top: 3px;
            }
            QComboBox::down-arrow:hover {
                border-top: 8px solid #7a40b5;
            }
            QDateTimeEdit {
                min-width: 160px;
            }
            QPushButton {
                min-width: 40px;
            }
        """)
        
        personal_layout = QGridLayout()
        personal_layout.setSpacing(8)
        personal_layout.setContentsMargins(8, 8, 8, 8)
        
        # Name input
        name_label = QLabel("Name:")
        name_label.setFixedWidth(60)  # Reduced label width
        self.name_input = QComboBox()
        self.name_input.setEditable(True)
        self.name_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.name_input.currentTextChanged.connect(self.on_name_selected)
        personal_layout.addWidget(name_label, 0, 0)
        personal_layout.addWidget(self.name_input, 0, 1, 1, 2)
        
        # DateTime input
        date_label = QLabel("Birth:")
        date_label.setFixedWidth(60)  # Reduced label width
        self.date_time = QDateTimeEdit()
        self.date_time.setDateTime(QDateTime.currentDateTime())
        self.date_time.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.date_time.setCalendarPopup(True)
        
        # Add "Now" button
        current_time_btn = QPushButton("Now")
        current_time_btn.setFixedWidth(45)  # Reduced button width
        current_time_btn.clicked.connect(lambda: self.date_time.setDateTime(QDateTime.currentDateTime()))
        
        personal_layout.addWidget(date_label, 1, 0)
        personal_layout.addWidget(self.date_time, 1, 1)
        personal_layout.addWidget(current_time_btn, 1, 2)
        
        personal_group.setLayout(personal_layout)
        container_layout.addWidget(personal_group)
        
        # Location Group
        location_group = QGroupBox("Location Information")
        location_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        location_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold;
                margin-top: 16px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 8px;
            }
            QLineEdit {
                max-width: 180px;
            }
            QComboBox {
                max-width: 180px;
                border: 1px solid #663399;
                padding: 4px;
                padding-right: 20px;
            }
            QComboBox:hover {
                border: 1px solid #7a40b5;
            }
            QComboBox:focus {
                border: 2px solid #7a40b5;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                background: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #663399;
                margin-top: 3px;
            }
            QComboBox::down-arrow:hover {
                border-top: 8px solid #7a40b5;
            }
            QDateTimeEdit {
                min-width: 160px;
            }
            QPushButton {
                min-width: 40px;
            }
        """)
        location_layout = QGridLayout()
        location_layout.setSpacing(5)
        location_layout.setContentsMargins(5, 5, 5, 5)
        
        # City input with search
        city_label = QLabel("City:")
        city_label.setFixedWidth(70)
        self.city_input = QLineEdit()
        search_btn = QPushButton("Search")
        search_btn.setFixedWidth(50)
        search_btn.clicked.connect(self.fetch_coordinates)
        location_layout.addWidget(city_label, 0, 0)
        location_layout.addWidget(self.city_input, 0, 1)
        location_layout.addWidget(search_btn, 0, 2)
        
        # Coordinates
        lat_label = QLabel("Latitude:")
        lat_label.setFixedWidth(70)
        self.lat_input = QLineEdit()
        self.lat_input.setToolTip("Format: DD° MM' N/S or DD° MM' SS\" N/S\nExample: 40° 26' N")
        self.lat_input.setPlaceholderText("e.g., 40° 26' N")
        self.lat_input.editingFinished.connect(lambda: self.validate_dms_input(self.lat_input, True))
        location_layout.addWidget(lat_label, 1, 0)
        location_layout.addWidget(self.lat_input, 1, 1, 1, 2)
        
        lon_label = QLabel("Longitude:")
        lon_label.setFixedWidth(70)
        self.long_input = QLineEdit()
        self.long_input.setToolTip("Format: DD° MM' E/W or DD° MM' SS\" E/W\nExample: 73° 58' W")
        self.long_input.setPlaceholderText("e.g., 73° 58' W")
        self.long_input.editingFinished.connect(lambda: self.validate_dms_input(self.long_input, False))
        location_layout.addWidget(lon_label, 2, 0)
        location_layout.addWidget(self.long_input, 2, 1, 1, 2)
        
        # Timezone and DST layout
        time_settings_layout = QHBoxLayout()
        
        # Timezone selection
        timezone_layout = QHBoxLayout()
        timezone_label = QLabel("Timezone:")
        timezone_label.setMinimumWidth(100)
        self.timezone_combo = QComboBox()
        
        # Populate timezone combo box with common timezones
        common_timezones = [
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'America/Toronto', 'America/Vancouver', 'America/Detroit', 'America/Phoenix',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Moscow',
            'Asia/Dubai', 'Asia/Kolkata', 'Asia/Singapore', 'Asia/Tokyo',
            'Australia/Sydney', 'Pacific/Auckland'
        ]
        
        # Add UTC offset to timezone display names
        timezone_display = []
        for tz_name in common_timezones:
            try:
                tz = pytz.timezone(tz_name)
                offset = tz.utcoffset(datetime.now()).total_seconds() / 3600
                offset_str = f"{'+' if offset >= 0 else ''}{int(offset):02d}:00"
                display_name = f"{tz_name} (UTC{offset_str})"
                timezone_display.append((display_name, tz_name))
            except Exception:
                continue
        
        # Sort by UTC offset
        timezone_display.sort(key=lambda x: float(x[0].split("UTC")[1].replace(":", ".").rstrip(")").lstrip("+") or 0))
        
        for display_name, tz_name in timezone_display:
            self.timezone_combo.addItem(display_name, tz_name)  # Store actual timezone name as item data
            
        timezone_layout.addWidget(timezone_label)
        timezone_layout.addWidget(self.timezone_combo)
        
        # DST checkbox
        dst_layout = QHBoxLayout()
        dst_label = QLabel("DST:")
        dst_label.setMinimumWidth(50)
        self.dst_checkbox = QCheckBox("Daylight Saving Time")
        dst_layout.addWidget(dst_label)
        dst_layout.addWidget(self.dst_checkbox)
        
        # Connect timezone change to DST update
        self.timezone_combo.currentIndexChanged.connect(self.update_dst_for_timezone)
        
        # Add timezone and DST to the layout
        time_settings_layout.addLayout(timezone_layout)
        time_settings_layout.addLayout(dst_layout)
        time_settings_layout.addStretch()
        location_layout.addLayout(time_settings_layout, 3, 0, 1, 3)
        
        location_group.setLayout(location_layout)
        container_layout.addWidget(location_group)
        
        # Calculation Settings Group
        settings_group = QGroupBox("Calculation Settings")
        settings_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        settings_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold;
                margin-top: 16px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 8px;
            }
            QLineEdit {
                max-width: 180px;
            }
            QComboBox {
                max-width: 180px;
                border: 1px solid #663399;
                padding: 4px;
                padding-right: 20px;
            }
            QComboBox:hover {
                border: 1px solid #7a40b5;
            }
            QComboBox:focus {
                border: 2px solid #7a40b5;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                background: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #663399;
                margin-top: 3px;
            }
            QComboBox::down-arrow:hover {
                border-top: 8px solid #7a40b5;
            }
        """)
        settings_layout = QGridLayout()
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(5, 5, 5, 5)
        
        # Calculation Type
        self.calc_type_label = QLabel("Calculation:")
        self.calc_type_combo = QComboBox()
        self.calc_type_combo.addItems(["Geocentric", "Topocentric"])
        self.calc_type_combo.setCurrentText("Geocentric")  # Set default
        settings_layout.addWidget(self.calc_type_label, 0, 0)
        settings_layout.addWidget(self.calc_type_combo, 0, 1, 1, 2)
        
        # Zodiac System
        zodiac_label = QLabel("Zodiac System:")
        zodiac_label.setFixedWidth(70)
        self.zodiac_combo = QComboBox()
        self.zodiac_combo.addItems(["Tropical", "Sidereal"])
        self.zodiac_combo.setCurrentText("Sidereal")  # Set Sidereal as default
        self.zodiac_combo.currentTextChanged.connect(self.on_zodiac_changed)
        
        # Ayanamsa (only for Sidereal)
        ayanamsa_label = QLabel("Ayanamsa:")
        ayanamsa_label.setFixedWidth(70)
        self.ayanamsa_combo = QComboBox()
        self.ayanamsa_combo.addItems(["Lahiri", "Raman", "Krishnamurti", 
                                    "Fagan/Bradley", "True Chitrapaksha", "Yukteswar"])
        self.ayanamsa_combo.setCurrentText("Lahiri")  # Set Lahiri as default
        
        settings_layout.addWidget(zodiac_label, 1, 0)
        settings_layout.addWidget(self.zodiac_combo, 1, 1, 1, 2)
        settings_layout.addWidget(ayanamsa_label, 2, 0)
        settings_layout.addWidget(self.ayanamsa_combo, 2, 1, 1, 2)
        
        # House System
        house_label = QLabel("Houses:")
        house_label.setFixedWidth(70)
        self.house_system_combo = QComboBox()
        self.house_system_combo.addItems([
            "Placidus", "Koch", "Equal (Asc)", "Equal (MC)", "Whole Sign",
            "Campanus", "Regiomontanus", "Porphyry", "Morinus", "Meridian",
            "Alcabitius", "Azimuthal", "Polich/Page (Topocentric)", "Vehlow Equal"
        ])
        self.house_system_combo.setCurrentText("Polich/Page (Topocentric)")  # Set default
        settings_layout.addWidget(house_label, 3, 0)
        settings_layout.addWidget(self.house_system_combo, 3, 1, 1, 2)
        
        # Node Type
        node_label = QLabel("Node Type:")
        node_label.setFixedWidth(70)
        self.node_type = QComboBox()
        self.node_type.addItems(["True Node (Rahu/Ketu)", "Mean Node (Rahu/Ketu)"])
        self.node_type.setCurrentText("True Node (Rahu/Ketu)")  # Set default
        settings_layout.addWidget(node_label, 4, 0)
        settings_layout.addWidget(self.node_type, 4, 1, 1, 2)
        
        settings_group.setLayout(settings_layout)
        container_layout.addWidget(settings_group)
        
        # Add Save/Open Profile buttons at the bottom
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Profile")
        self.open_btn = QPushButton("Open Profile")
        self.calculate_btn = QPushButton("Calculate")
        
        for btn in [self.save_btn, self.open_btn, self.calculate_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
        
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                border: 1px solid #555;
                background-color: #663399;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #7a40b5;
            }
        """)
        
        self.save_btn.clicked.connect(self.save_profile)
        self.open_btn.clicked.connect(self.open_profile)
        self.calculate_btn.clicked.connect(self.calculate_chart)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.open_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.calculate_btn)
        
        # Add buttons to layout
        container_layout.addLayout(button_layout)
        
        # Set up the container
        container.setLayout(container_layout)
        
        # Set scroll widget and main layout
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        # Common style for combo boxes
        combo_style = """
            QComboBox {
                border: 1px solid #663399;
                padding: 4px;
                padding-right: 20px;
            }
            QComboBox:hover {
                border: 1px solid #7a40b5;
            }
            QComboBox:focus {
                border: 2px solid #7a40b5;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                background: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #663399;
                margin-top: 3px;
            }
            QComboBox::down-arrow:hover {
                border-top: 8px solid #7a40b5;
            }
        """
        
        # Apply style to all combo boxes
        self.name_input.setStyleSheet(combo_style)
        self.timezone_combo.setStyleSheet(combo_style)
        self.zodiac_combo.setStyleSheet(combo_style)
        self.ayanamsa_combo.setStyleSheet(combo_style)
        self.house_system_combo.setStyleSheet(combo_style)
        self.node_type.setStyleSheet(combo_style)
    
    def fetch_coordinates(self):
        """Fetch coordinates and timezone for the entered city"""
        try:
            city = self.city_input.text().strip()
            if not city:
                QMessageBox.warning(self, "Error", "Please enter a city name")
                return

            geolocator = Nominatim(user_agent="cosmic_calculator")
            
            # Try to get more specific location data by adding country
            if ", usa" in city.lower() or ", us" in city.lower():
                location = geolocator.geocode(city, addressdetails=True)
            else:
                # First try with ", USA" appended if not already present
                location = geolocator.geocode(f"{city}, USA", addressdetails=True)
                if not location:
                    # If not found, try original query
                    location = geolocator.geocode(city, addressdetails=True)
            
            if location:
                # Update latitude and longitude
                lat = location.latitude
                lon = location.longitude
                self.lat_input.setText(self.decimal_to_dms(lat, True))
                self.long_input.setText(self.decimal_to_dms(lon, False))
                
                # Get timezone for the location
                tf = TimezoneFinder()
                timezone_str = tf.timezone_at(lat=lat, lng=lon)
                
                if timezone_str:
                    # Find and select the matching timezone in the combo box
                    for i in range(self.timezone_combo.count()):
                        tz_name = self.timezone_combo.itemData(i)
                        if tz_name == timezone_str:
                            self.timezone_combo.setCurrentIndex(i)
                            break
                    else:
                        # If timezone not in common list, add it
                        try:
                            tz = pytz.timezone(timezone_str)
                            offset = tz.utcoffset(datetime.now()).total_seconds() / 3600
                            offset_str = f"{'+' if offset >= 0 else ''}{int(offset):02d}:00"
                            display_name = f"{timezone_str} (UTC{offset_str})"
                            self.timezone_combo.addItem(display_name, timezone_str)
                            self.timezone_combo.setCurrentText(display_name)
                        except Exception as e:
                            print(f"Error adding timezone: {str(e)}")
                    
                    # DST will be automatically updated via the signal connection
                    
                    # Get location details for better feedback
                    address = location.raw.get('address', {})
                    state = address.get('state', '')
                    country = address.get('country', '')
                    location_str = f"{city}"
                    if state:
                        location_str += f", {state}"
                    if country:
                        location_str += f", {country}"
                    
                    QMessageBox.information(self, "Success", 
                        f"Found coordinates and timezone for {location_str}:\n"
                        f"Latitude: {self.lat_input.text()}\n"
                        f"Longitude: {self.long_input.text()}\n"
                        f"Timezone: {timezone_str}")
                else:
                    QMessageBox.warning(self, "Warning", 
                        f"Found coordinates but couldn't determine timezone.\n"
                        f"Please select timezone manually:\n"
                        f"Latitude: {self.lat_input.text()}\n"
                        f"Longitude: {self.long_input.text()}")
            else:
                QMessageBox.warning(self, "Error", f"Could not find coordinates for {city}")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch coordinates: {str(e)}")

    def save_profile(self):
        # Validate inputs
        if not all([self.name_input.currentText(), self.city_input.text(), 
                    self.lat_input.text(), self.long_input.text()]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        try:
            # Check if profile already exists
            current_name = self.name_input.currentText()
            existing_profiles = []
            profile_exists = False
            
            try:
                with open(self.profile_path, "r") as f:
                    for line in f:
                        if line.strip():  # Skip empty lines
                            profile = json.loads(line)
                            if profile["name"] == current_name and not profile_exists:
                                profile_exists = True
                                # Create a custom dialog for duplicate profile
                                dialog = QDialog(self)
                                dialog.setWindowTitle("Duplicate Profile")
                                dialog.setMinimumWidth(400)
                                layout = QVBoxLayout()
                                
                                # Add message
                                message = QLabel(f"A profile with name '{current_name}' already exists.\nWhat would you like to do?")
                                message.setWordWrap(True)
                                layout.addWidget(message)
                                
                                # Add buttons
                                button_layout = QHBoxLayout()
                                replace_btn = QPushButton("Replace")
                                cancel_btn = QPushButton("Cancel")
                                save_as_btn = QPushButton("Save as New")
                                
                                # Style buttons
                                replace_btn.setStyleSheet("""
                                    QPushButton {
                                        background-color: #6B4EAE;
                                        color: white;
                                        padding: 8px 16px;
                                        border-radius: 4px;
                                    }
                                    QPushButton:hover {
                                        background-color: #563D8C;
                                    }
                                """)
                                
                                cancel_btn.setStyleSheet("""
                                    QPushButton {
                                        padding: 8px 16px;
                                        border: 1px solid #6B4EAE;
                                        border-radius: 4px;
                                        color: #6B4EAE;
                                    }
                                    QPushButton:hover {
                                        background-color: #F0E6FF;
                                    }
                                """)
                                
                                save_as_btn.setStyleSheet("""
                                    QPushButton {
                                        padding: 8px 16px;
                                        border: 1px solid #6B4EAE;
                                        border-radius: 4px;
                                        color: #6B4EAE;
                                    }
                                    QPushButton:hover {
                                        background-color: #F0E6FF;
                                    }
                                """)
                                
                                button_layout.addWidget(replace_btn)
                                button_layout.addWidget(save_as_btn)
                                button_layout.addWidget(cancel_btn)
                                layout.addLayout(button_layout)
                                
                                dialog.setLayout(layout)
                                
                                # Connect button signals
                                replace_btn.clicked.connect(dialog.accept)
                                save_as_btn.clicked.connect(lambda: dialog.done(2))
                                cancel_btn.clicked.connect(dialog.reject)
                                
                                result = dialog.exec()
                                
                                if result == QDialog.DialogCode.Rejected:
                                    return
                                elif result == 2:  # Save as new
                                    # Prompt for new name
                                    new_name, ok = QInputDialog.getText(
                                        self, 
                                        "Save As", 
                                        "Enter new profile name:",
                                        QLineEdit.EchoMode.Normal, 
                                        current_name + " (copy)"
                                    )
                                    if ok and new_name:
                                        current_name = new_name
                                    else:
                                        return
                                    existing_profiles.append(profile)
                            elif profile["name"] != current_name:
                                existing_profiles.append(profile)
            except FileNotFoundError:
                pass  # File doesn't exist yet, which is fine
                
            # Get the current date time from the widget
            current_datetime = self.date_time.dateTime()
            
            # Validate coordinates
            lat_str = self.lat_input.text().strip()
            lon_str = self.long_input.text().strip()
            lat_decimal = self.dms_to_decimal(lat_str)
            lon_decimal = self.dms_to_decimal(lon_str)
            
            # Create profile data
            new_profile = {
                "name": current_name,
                "datetime": current_datetime.toString("dd/MM/yyyy hh:mm:ss"),
                "city": self.city_input.text(),
                "latitude": lat_str,  # Store as DMS string
                "longitude": lon_str,  # Store as DMS string
                "latitude_decimal": lat_decimal,  # Store decimal for calculations
                "longitude_decimal": lon_decimal,  # Store decimal for calculations
                "timezone": self.timezone_combo.currentText(),  # Save timezone
                "dst": self.dst_checkbox.isChecked()  # Save DST setting
            }
            
            # Write all profiles back to file
            with open(self.profile_path, "w") as f:
                for profile in existing_profiles:
                    json.dump(profile, f)
                    f.write("\n")
                json.dump(new_profile, f)
                f.write("\n")
                
            QMessageBox.information(self, "Success", "Profile saved successfully!")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid coordinates: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile: {str(e)}")

    def open_profile(self):
        try:
            # Read all profiles from the file
            profiles = {}
            with open(self.profile_path, "r") as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        profile = json.loads(line)
                        profiles[profile["name"]] = profile
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Saved Profiles")
            dialog.setMinimumWidth(600)
            layout = QVBoxLayout()
            
            # Create table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Name", "Date & Time", "City", "Latitude", "Longitude"])
            table.setRowCount(len(profiles))
            
            # Fill table with data
            for row, (name, profile) in enumerate(profiles.items()):
                table.setItem(row, 0, QTableWidgetItem(str(name)))
                table.setItem(row, 1, QTableWidgetItem(str(profile.get("datetime", ""))))
                table.setItem(row, 2, QTableWidgetItem(str(profile.get("city", ""))))
                table.setItem(row, 3, QTableWidgetItem(str(profile.get("latitude", ""))))
                table.setItem(row, 4, QTableWidgetItem(str(profile.get("longitude", ""))))
            
            # Create button layout
            button_layout = QHBoxLayout()
            
            # Add load button
            load_btn = QPushButton("Load")
            load_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6B4EAE;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #563D8C;
                }
            """)
            
            # Add delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            
            def load_selected():
                current_row = table.currentRow()
                if current_row >= 0:
                    profile = list(profiles.values())[current_row]
                    self.name_input.setCurrentText(profile["name"])
                    self.city_input.setText(profile["city"])
                    self.lat_input.setText(profile["latitude"])
                    self.long_input.setText(profile["longitude"])
                    
                    # Parse and set datetime
                    datetime_str = profile.get("datetime", "")
                    if datetime_str:
                        dt = QDateTime.fromString(datetime_str, "dd/MM/yyyy hh:mm:ss")
                        if dt.isValid():
                            self.date_time.setDateTime(dt)
                        else:
                            print(f"Failed to parse datetime: {datetime_str}")
                    
                    # Set timezone and DST if available in the profile
                    if "timezone" in profile:
                        self.timezone_combo.setCurrentText(profile["timezone"])
                    if "dst" in profile:
                        self.dst_checkbox.setChecked(profile["dst"])
                    
                    # Save this as the last opened profile
                    self.save_last_profile(profile["name"])
                    
                    dialog.accept()
            
            def delete_selected():
                current_row = table.currentRow()
                if current_row >= 0:
                    profile_name = list(profiles.keys())[current_row]
                    reply = QMessageBox.question(
                        dialog,
                        "Confirm Delete",
                        f"Are you sure you want to delete the profile '{profile_name}'?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            # Remove from profiles list
                            del profiles[profile_name]
                            
                            # Write remaining profiles back to file
                            with open(self.profile_path, "w") as f:
                                for profile in profiles.values():
                                    json.dump(profile, f)
                                    f.write("\n")
                            
                            # Update table
                            table.removeRow(current_row)
                            QMessageBox.information(dialog, "Success", "Profile deleted successfully!")
                        except Exception as e:
                            QMessageBox.warning(dialog, "Error", f"Failed to delete profile: {str(e)}")
            
            # Connect button signals
            load_btn.clicked.connect(load_selected)
            delete_btn.clicked.connect(delete_selected)
            
            # Add buttons to layout
            button_layout.addWidget(load_btn)
            button_layout.addWidget(delete_btn)
            
            # Add widgets to layout
            layout.addWidget(table)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except FileNotFoundError:
            QMessageBox.information(self, "Info", "No saved profiles found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load profiles: {str(e)}")

    def get_form_data(self):
        """Get and validate form data."""
        try:
            name = self.name_input.currentText()
            input_datetime = self.date_time.dateTime().toPyDateTime()
            
            # Get timezone information
            current_index = self.timezone_combo.currentIndex()
            if current_index < 0:
                raise ValueError("Please select a timezone")
                
            timezone_name = self.timezone_combo.itemData(current_index)  # Get actual timezone name
            timezone = pytz.timezone(timezone_name)
            dst_active = self.dst_checkbox.isChecked()
            
            # Create timezone-aware datetime
            local_dt = timezone.localize(input_datetime, is_dst=dst_active)
            utc_dt = local_dt.astimezone(pytz.UTC)
            
            city = self.city_input.text()
            
            # Get and validate latitude
            lat_str = self.lat_input.text().strip()
            if not lat_str:
                raise ValueError("Latitude is required")
            latitude = self.dms_to_decimal(lat_str)
            
            # Get and validate longitude
            long_str = self.long_input.text().strip()
            if not long_str:
                raise ValueError("Longitude is required")
            longitude = self.dms_to_decimal(long_str)
            
            # Get calculation settings
            calc_type = self.calc_type_combo.currentText()
            zodiac_system = self.zodiac_combo.currentText()
            ayanamsa = self.ayanamsa_combo.currentText()
            house_system = self.house_system_combo.currentText()
            node_type = self.node_type.currentText() if hasattr(self, 'node_type') else "True Node (Rahu/Ketu)"
            
            return {
                'name': name,
                'datetime': utc_dt,  # Now in UTC
                'local_datetime': local_dt,  # Original local time
                'timezone': timezone_name,
                'dst_active': dst_active,
                'city': city,
                'latitude': latitude,
                'longitude': longitude,
                'calculation_type': calc_type,
                'zodiac_system': zodiac_system,
                'ayanamsa': ayanamsa,
                'house_system': house_system,
                'node_type': node_type
            }
        
        except ValueError as e:
            print(f"Error getting form data: {str(e)}")
            return None

    def calculate_chart(self):
        """Calculate and display the chart"""
        try:
            print("\nDEBUG - Starting chart calculation")
            # Get all form data first
            form_data = self.get_form_data()
            if not form_data:
                print("DEBUG - No form data available")
                return
            
            print(f"DEBUG - Form data retrieved: zodiac={form_data['zodiac_system']}")
                
            # Calculate chart data
            chart_data = self.astro_calc.calculate_chart(
                form_data['datetime'],
                form_data['latitude'],
                form_data['longitude'],
                calc_type=form_data['calculation_type'],
                zodiac=form_data['zodiac_system'],
                ayanamsa=form_data['ayanamsa'],
                house_system=form_data['house_system'],
                node_type=form_data['node_type']
            )
            
            if not chart_data:
                print("DEBUG - No chart data returned from calculation")
                return
                
            print("DEBUG - Chart calculation completed")
            
            # Add form data to chart data
            chart_data.update({
                'name': form_data['name'],
                'datetime': form_data['local_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': form_data['timezone'],
                'dst_active': form_data['dst_active'],
                'city': form_data['city'],
                'latitude': form_data['latitude'],
                'longitude': form_data['longitude']
            })
            
            print("DEBUG - Emitting chart_calculated signal")
            # Store the data and emit signals
            self.chart_data = chart_data
            self.chart_calculated.emit(chart_data)
            self.panel_closed.emit()  # Emit signal to close panel after successful calculation
            print("DEBUG - Chart calculation and emission complete")
            
        except Exception as e:
            print(f"Error calculating chart: {str(e)}")
            traceback.print_exc()
    
    def generate_html_results(self, chart_data):
        """Generate HTML formatted results."""
        try:
            # Create HTML template with CSS styling
            html_output = """
            <html>
            <head>
                <style>
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #FFFFFF;
                        padding: 20px;
                        background-color: #000000;
                    }
                    .header {
                        background: #1A1A1A;
                        color: white;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        border: 1px solid #333333;
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
                        font-weight: bold;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 15px;
                    }
                    th, td {
                        padding: 8px;
                        text-align: left;
                        border: 1px solid #333333;
                    }
                    th {
                        background: #262626;
                        color: #FFFFFF;
                        font-weight: bold;
                    }
                    tr:nth-child(even) {
                        background: #1F1F1F;
                    }
                    tr:nth-child(odd) {
                        background: #262626;
                    }
                    .planet-card, .house-card {
                        background: #1F1F1F;
                        border: 1px solid #333333;
                        border-radius: 6px;
                        padding: 10px;
                        margin-bottom: 10px;
                    }
                    .settings-item {
                        display: inline-block;
                        background: #262626;
                        border-radius: 4px;
                        padding: 5px 10px;
                        margin: 5px;
                        border: 1px solid #333333;
                    }
                    .retrograde {
                        color: #FF6B6B;
                        font-weight: bold;
                    }
                    .coordinates {
                        color: #66B2FF;
                        font-weight: 500;
                    }
                </style>
            </head>
            <body>
            """
            
            # Header Section
            html_output += f"""
            <div class="header">
                <h2>Astrological Chart for {self.name_input.currentText()}</h2>
                <p>Date & Time: {chart_data['meta']['datetime']}</p>
                <p>Location: {self.city_input.text()} 
                   <span class="coordinates">({self.decimal_to_dms(float(chart_data['meta']['latitude']), True)}, 
                   {self.decimal_to_dms(float(chart_data['meta']['longitude']), False)})</span>
                </p>
            </div>
            """
            
            # Planetary Positions Section
            html_output += '<div class="section"><h3 class="section-title">Planetary Positions</h3>'
            html_output += '<table>'
            html_output += '<tr><th>Planet</th><th>Sign & Position</th><th>House</th><th>Nakshatra</th><th>Star Lord</th><th>Sub Lord</th><th>Status</th></tr>'
            
            display_order = [
                "Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", 
                "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"
            ]
            
            for point in display_order:
                if point in chart_data['points']:
                    data = chart_data['points'][point]
                    html_output += '<tr>'
                    html_output += f'<td>{point}</td>'
                    html_output += f'<td>{data["sign"]} {self.decimal_to_dms(data["degree"])}</td>'
                    html_output += f'<td>{data["house"]}</td>'
                    
                    if 'nakshatra' in data:
                        html_output += f'<td>{data["nakshatra"]} (Pada {data["pada"]})</td>'
                        html_output += f'<td>{data["star_lord"]}</td>'
                        html_output += f'<td>{data["sub_lord"]}</td>'
                    else:
                        html_output += '<td>-</td><td>-</td><td>-</td>'
                    
                    status = []
                    if 'is_retrograde' in data and data['is_retrograde']:
                        status.append('<span class="retrograde">Retrograde</span>')
                    if 'type' in data:
                        status.append(data["type"])
                    html_output += f'<td>{" ".join(status) if status else "-"}</td>'
                    
                    html_output += '</tr>'
            
            html_output += '</table></div>'
            
            # House Cusps Section
            html_output += '<div class="section"><h3 class="section-title">House Cusps</h3>'
            html_output += '<table>'
            html_output += '<tr><th>House</th><th>Sign & Position</th><th>Nakshatra</th><th>Star Lord</th><th>Sub Lord</th></tr>'
            
            for house in range(1, 13):
                house_key = f"House_{house}"
                if house_key in chart_data.get('houses', {}):
                    house_data = chart_data['houses'][house_key]
                    html_output += '<tr>'
                    html_output += f'<td>{house}</td>'
                    html_output += f'<td>{house_data["sign"]} {self.decimal_to_dms(house_data["degree"])}</td>'
                    html_output += f'<td>{house_data["nakshatra"]} (Pada {house_data["pada"]})</td>'
                    html_output += f'<td>{house_data["star_lord"]}</td>'
                    html_output += f'<td>{house_data["sub_lord"]}</td>'
                    html_output += '</tr>'
            
            html_output += '</table></div>'
            
            # Technical Details Section
            html_output += '<div class="section"><h3 class="section-title">Technical Details</h3>'
            html_output += '<table>'
            html_output += '<tr><th>Parameter</th><th>Value</th></tr>'
            
            # Get technical details from meta
            meta = chart_data.get('meta', {})
            
            # Julian Day
            jd = meta.get('julian_day', 0)
            html_output += f'<tr><td>Julian Day Ephemeris (JDE)</td><td>{jd:.6f}</td></tr>'
            
            # Delta T
            delta_t = meta.get('delta_t', 0)
            delta_t_str = f"+{delta_t:.3f}s" if delta_t >= 0 else f"{delta_t:.3f}s"
            html_output += f'<tr><td>Delta T (ΔT)</td><td>{delta_t_str}</td></tr>'
            
            # Ephemeris Time
            et = meta.get('ephemeris_time', 0)
            html_output += f'<tr><td>Ephemeris Time (ET)</td><td>JDE {et:.6f}</td></tr>'
            
            # Sidereal Times
            gst = meta.get('sidereal_time_0', 0)  # Greenwich Sidereal Time
            lst = meta.get('local_sidereal_time', 0)  # Local Sidereal Time
            
            # Format GST
            gst_h = int(gst)
            gst_m = int((gst - gst_h) * 60)
            gst_s = int(((gst - gst_h) * 60 - gst_m) * 60)
            html_output += f'<tr><td>Greenwich Sidereal Time (GST)</td><td>{gst_h:02d}:{gst_m:02d}:{gst_s:02d}</td></tr>'
            
            # Format LST
            lst_h = int(lst)
            lst_m = int((lst - lst_h) * 60)
            lst_s = int(((lst - lst_h) * 60 - lst_m) * 60)
            html_output += f'<tr><td>Local Sidereal Time (LST)</td><td>{lst_h:02d}:{lst_m:02d}:{lst_s:02d}</td></tr>'
            
            # Ayanamsa
            ayanamsa = meta.get('ayanamsa_value', 0)
            ayan_d = int(ayanamsa)
            ayan_m = int((ayanamsa - ayan_d) * 60)
            ayan_s = int(((ayanamsa - ayan_d) * 60 - ayan_m) * 60)
            html_output += f'<tr><td>Ayanamsa</td><td>{ayan_d}° {ayan_m}\' {ayan_s}"</td></tr>'
            
            # Obliquity
            obliquity = meta.get('obliquity', 0)
            obl_d = int(obliquity)
            obl_m = int((obliquity - obl_d) * 60)
            obl_s = int(((obliquity - obl_d) * 60 - obl_m) * 60)
            html_output += f'<tr><td>True Obliquity</td><td>{obl_d}° {obl_m}\' {obl_s}"</td></tr>'
            
            html_output += '</table></div>'
            
            # Settings Section
            html_output += '<div class="section"><h3 class="section-title">Calculation Settings</h3>'
            html_output += '<div class="settings-container">'
            html_output += f'<span class="settings-item">Calculation Type: {self.calc_type_combo.currentText()}</span>'
            html_output += f'<span class="settings-item">Zodiac System: {self.zodiac_combo.currentText()}</span>'
            html_output += f'<span class="settings-item">Ayanamsa: {self.ayanamsa_combo.currentText()}</span>'
            html_output += f'<span class="settings-item">House System: {self.house_system_combo.currentText()}</span>'
            html_output += f'<span class="settings-item">Node Type: {self.node_type.currentText()}</span>'
            html_output += '</div></div>'
            
            html_output += '</body></html>'
            
            return html_output
            
        except Exception as e:
            print(f"Debug - Error generating HTML results: {str(e)}")
            raise

    def update_dst_for_timezone(self):
        """Update DST checkbox based on current timezone selection"""
        try:
            current_index = self.timezone_combo.currentIndex()
            if current_index >= 0:
                tz_name = self.timezone_combo.itemData(current_index)  # Get actual timezone name
                if tz_name:
                    timezone = pytz.timezone(tz_name)
                    current_dt = datetime.now()
                    
                    # Check if DST is currently in effect
                    is_dst = timezone.localize(current_dt).dst() != timezone.utcoffset(current_dt)
                    self.dst_checkbox.setChecked(is_dst)
        except Exception as e:
            print(f"Error updating DST status: {str(e)}")

    def on_name_selected(self, name):
        """Load profile data when a name is selected"""
        if not name or not os.path.exists(self.profile_path):
            return
            
        try:
            with open(self.profile_path, 'r') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        profile = json.loads(line)
                        if profile.get("name") == name:
                            self.load_profile_data(profile)
                            break
        except Exception as e:
            print(f"Error loading profile {name}: {e}")
    
    def load_profile_data(self, profile):
        """Load profile data into the input fields"""
        try:
            # Load birth date and time
            if 'datetime' in profile:  
                try:
                    # Try parsing as dd/MM/yyyy hh:mm:ss format first
                    birth_dt = QDateTime.fromString(profile['datetime'], "dd/MM/yyyy hh:mm:ss")
                    if not birth_dt.isValid():
                        # Fall back to ISO format if the first format fails
                        birth_dt = QDateTime.fromString(profile['datetime'], Qt.DateFormat.ISODate)
                    if birth_dt.isValid():
                        self.date_time.setDateTime(birth_dt)
                except Exception as e:
                    print(f"Error parsing datetime: {e}")
            
            # Load location
            if 'city' in profile:
                self.city_input.setText(profile['city'])
            if 'latitude' in profile:
                self.lat_input.setText(str(profile['latitude']))
            if 'longitude' in profile:
                self.long_input.setText(str(profile['longitude']))
            if 'timezone' in profile:
                index = self.timezone_combo.findText(profile['timezone'])  
                if index >= 0:
                    self.timezone_combo.setCurrentIndex(index)
            if 'dst' in profile:
                self.dst_checkbox.setChecked(profile['dst'])
            
            # Load calculation settings
            if 'calc_type' in profile:
                self.calc_type_combo.setCurrentText(profile['calc_type'])
            if 'zodiac' in profile:
                self.zodiac_combo.setCurrentText(profile['zodiac'])
            if 'ayanamsa' in profile:
                self.ayanamsa_combo.setCurrentText(profile['ayanamsa'])
            if 'house_system' in profile:
                self.house_system_combo.setCurrentText(profile['house_system'])
            if 'node_type' in profile:
                self.node_type.setCurrentText(profile['node_type'])
                
        except Exception as e:
            print(f"Error loading profile data: {e}")

    def save_last_profile(self, profile_name):
        """Save the name of the last opened profile"""
        try:
            settings = {}
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
            
            settings['last_profile'] = profile_name
            
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving last profile: {e}")

    def load_last_profile(self):
        """Load the last opened profile if it exists"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
                    last_profile = settings.get('last_profile')
                    if last_profile:
                        # Find the profile in the combobox
                        index = self.name_input.findText(last_profile)
                        if index >= 0:
                            self.name_input.setCurrentIndex(index)
                            self.on_name_selected(last_profile)
        except Exception as e:
            print(f"Error loading last profile: {e}")

    def on_zodiac_changed(self, zodiac_system):
        """Enable/disable ayanamsa combo based on zodiac system"""
        print(f"DEBUG - Zodiac system changed to: {zodiac_system}")
        self.ayanamsa_combo.setEnabled(zodiac_system == "Sidereal")
        if zodiac_system == "Tropical":
            # Save current ayanamsa selection
            self._last_ayanamsa = self.ayanamsa_combo.currentText()
            self.ayanamsa_combo.setCurrentText("Lahiri")  # Set to default
        else:
            # Restore last ayanamsa if available
            if hasattr(self, '_last_ayanamsa'):
                self.ayanamsa_combo.setCurrentText(self._last_ayanamsa)
        self.calculate_chart()  # Recalculate chart when zodiac system changes

    def toggle_panel(self):
        """Toggle the sliding panel and update the chart when done"""
        if not self.sliding_panel.isVisible():
            self.sliding_panel.show()
            self.sliding_panel.slide_in()
        else:
            self.sliding_panel.slide_out()
            # Hide panel after animation completes
            QTimer.singleShot(300, self.on_panel_closed)
            
    def on_panel_closed(self):
        """Handle panel close events"""
        self.sliding_panel.hide()
        self.calculate_and_update_chart()
        self.panel_closed.emit()  # Emit signal when panel is closed

    def calculate_and_update_chart(self):
        """Calculate and update the chart"""
        self.calculate_chart()
