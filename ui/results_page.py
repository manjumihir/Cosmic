from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QScrollArea
from PyQt6.QtCore import Qt

class ResultsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Create main container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        
        # Basic Info Group
        basic_info_group = QGroupBox("Chart Information")
        basic_info_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        basic_info_layout = QVBoxLayout()
        
        self.name_label = QLabel()
        self.datetime_label = QLabel()
        self.location_label = QLabel()
        self.settings_label = QLabel()
        
        for label in [self.name_label, self.datetime_label, self.location_label, self.settings_label]:
            basic_info_layout.addWidget(label)
        
        basic_info_group.setLayout(basic_info_layout)
        container_layout.addWidget(basic_info_group)
        
        # Planetary Positions Group
        planets_group = QGroupBox("Planetary Positions")
        planets_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        planets_layout = QVBoxLayout()
        self.planets_label = QLabel()
        self.planets_label.setTextFormat(Qt.TextFormat.RichText)
        planets_layout.addWidget(self.planets_label)
        planets_group.setLayout(planets_layout)
        container_layout.addWidget(planets_group)
        
        # Houses Group
        houses_group = QGroupBox("Houses")
        houses_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        houses_layout = QVBoxLayout()
        self.houses_label = QLabel()
        self.houses_label.setTextFormat(Qt.TextFormat.RichText)
        houses_layout.addWidget(self.houses_label)
        houses_group.setLayout(houses_layout)
        container_layout.addWidget(houses_group)
        
        # Aspects Group
        aspects_group = QGroupBox("Aspects")
        aspects_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        aspects_layout = QVBoxLayout()
        self.aspects_label = QLabel()
        self.aspects_label.setTextFormat(Qt.TextFormat.RichText)
        aspects_layout.addWidget(self.aspects_label)
        aspects_group.setLayout(aspects_layout)
        container_layout.addWidget(aspects_group)
        
        # Technical Details Group
        tech_details_group = QGroupBox("Technical Details")
        tech_details_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        tech_details_layout = QVBoxLayout()
        
        # Create labels for technical details
        self.jd_label = QLabel()
        self.delta_t_label = QLabel()
        self.et_label = QLabel()
        self.lst_label = QLabel()
        self.gst_label = QLabel()
        self.ayanamsa_label = QLabel()
        self.obliquity_label = QLabel()
        
        tech_labels = [
            self.jd_label, self.delta_t_label, self.et_label,
            self.lst_label, self.gst_label, self.ayanamsa_label,
            self.obliquity_label
        ]
        
        for label in tech_labels:
            tech_details_layout.addWidget(label)
            label.setTextFormat(Qt.TextFormat.RichText)
        
        tech_details_group.setLayout(tech_details_layout)
        container_layout.addWidget(tech_details_group)
        
        # Set up the container
        container.setLayout(container_layout)
        scroll.setWidget(container)
        
        # Add scroll area to main layout
        self.layout.addWidget(scroll)
        self.setLayout(self.layout)
    
    def update_data(self, data):
        """Update the UI with chart data"""
        # Update basic information
        self.name_label.setText(f"<b>{data['name']} - Natal Chart</b>")
        self.datetime_label.setText(f"Date/Time: {data['datetime']}")
        self.location_label.setText(f"Location: {data['city']} ({data['latitude']}, {data['longitude']})")
        
        # Format settings information
        settings = data.get('meta', {})
        settings_text = (
            f"{settings.get('calculation_type', 'Geocentric')} "
            f"{settings.get('zodiac_system', 'Tropical')} Zodiac<br>"
            f"{settings.get('house_system', 'Placidus')} Houses"
        )
        self.settings_label.setText(settings_text)
        
        # Update planetary positions
        points = data.get('points', {})
        planets_text = "<table width='100%' cellspacing='0' cellpadding='4'>"
        planets_text += "<tr><th>Planet</th><th>Sign</th><th>Position</th><th>House</th><th>Nakshatra</th><th>Pada</th><th>Status</th></tr>"
        
        for planet, details in sorted(points.items()):
            retrograde = "R" if details.get('is_retrograde', False) else ""
            planets_text += f"<tr><td>{planet}</td>"
            planets_text += f"<td>{details.get('sign', '-')}</td>"
            planets_text += f"<td>{self.format_degree(details.get('longitude', 0))}{retrograde}</td>"
            planets_text += f"<td>{details.get('house', '-')}</td>"
            planets_text += f"<td>{details.get('nakshatra', '-')}</td>"
            planets_text += f"<td>{details.get('pada', '-')}</td>"
            planets_text += f"<td>{details.get('dignity', '-')}</td></tr>"
        
        planets_text += "</table>"
        self.planets_label.setText(planets_text)
        
        # Update houses
        houses = data.get('houses', {})
        houses_text = "<table width='100%' cellspacing='0' cellpadding='4'>"
        houses_text += "<tr><th>House</th><th>Sign</th><th>Position</th><th>Ruler</th></tr>"
        
        for i in range(1, 13):
            house = houses.get(str(i), {})
            houses_text += f"<tr><td>{i}</td>"
            houses_text += f"<td>{house.get('sign', '-')}</td>"
            houses_text += f"<td>{self.format_degree(house.get('longitude', 0))}</td>"
            houses_text += f"<td>{house.get('ruler', '-')}</td></tr>"
        
        houses_text += "</table>"
        self.houses_label.setText(houses_text)
        
        # Update aspects
        aspects = data.get('aspects', {})
        aspects_text = "<table width='100%' cellspacing='0' cellpadding='4'>"
        aspects_text += "<tr><th>Planet 1</th><th>Aspect</th><th>Planet 2</th><th>Orb</th></tr>"
        
        for aspect in aspects:
            aspects_text += f"<tr><td>{aspect.get('planet1', '-')}</td>"
            aspects_text += f"<td>{aspect.get('aspect', '-')}°</td>"
            aspects_text += f"<td>{aspect.get('planet2', '-')}</td>"
            aspects_text += f"<td>{aspect.get('orb', '-')}°</td></tr>"
        
        aspects_text += "</table>"
        self.aspects_label.setText(aspects_text)
        
        # Update technical details
        meta = data.get('meta', {})
        
        # Julian Day
        jd = meta.get('julian_day', 0)
        self.jd_label.setText(f"JDE = {jd:.6f}")
        
        # Delta T
        delta_t = meta.get('delta_t', 0)
        delta_t_str = f"+{delta_t:.3f}s" if delta_t >= 0 else f"{delta_t:.3f}s"
        self.delta_t_label.setText(f"ΔT = {delta_t_str}")
        
        # Ephemeris Time
        et = meta.get('ephemeris_time', 0)
        self.et_label.setText(f"ET = JDE {et:.6f}")
        
        # Sidereal Times
        gst = meta.get('sidereal_time_0', 0)  # Greenwich Sidereal Time
        lst = meta.get('local_sidereal_time', 0)  # Local Sidereal Time
        
        # Format GST
        gst_h = int(gst)
        gst_m = int((gst - gst_h) * 60)
        gst_s = int(((gst - gst_h) * 60 - gst_m) * 60)
        self.gst_label.setText(f"GST = {gst_h:02d}:{gst_m:02d}:{gst_s:02d}")
        
        # Format LST
        lst_h = int(lst)
        lst_m = int((lst - lst_h) * 60)
        lst_s = int(((lst - lst_h) * 60 - lst_m) * 60)
        self.lst_label.setText(f"LST = {lst_h:02d}:{lst_m:02d}:{lst_s:02d}")
        
        # Ayanamsa
        ayanamsa = meta.get('ayanamsa_value', 0)
        ayan_d = int(ayanamsa)
        ayan_m = int((ayanamsa - ayan_d) * 60)
        ayan_s = int(((ayanamsa - ayan_d) * 60 - ayan_m) * 60)
        self.ayanamsa_label.setText(f"Ayanamsa = {ayan_d}° {ayan_m}' {ayan_s}\"")
        
        # Obliquity
        obliquity = meta.get('obliquity', 0)
        obl_d = int(obliquity)
        obl_m = int((obliquity - obl_d) * 60)
        obl_s = int(((obliquity - obl_d) * 60 - obl_m) * 60)
        self.obliquity_label.setText(f"True Obliquity = {obl_d}° {obl_m}' {obl_s}\"")

    def format_degree(self, degree):
        """Format degree to deg/min/sec format"""
        deg = int(degree)
        min_float = (degree - deg) * 60
        min = int(min_float)
        sec = int((min_float - min) * 60)
        return f"{deg}° {min}' {sec}\""

    def set_data(self, data):
        """Method to receive and process data from input page"""
        self.update_data(data)