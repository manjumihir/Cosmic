import swisseph as swe
from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta
import os

class AstroCalc:
    def __init__(self):
        # Initialize ephemeris path using absolute path
        ephe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ephe')
        swe.set_ephe_path(ephe_path)
        
        self.signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                     "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        self.house_system_map = {
            "Placidus": b'P',
            "Koch": b'K',
            "Equal (Asc)": b'E',
            "Equal (MC)": b'X',
            "Whole Sign": b'W',
            "Campanus": b'C',
            "Regiomontanus": b'R',
            "Porphyry": b'O',
            "Morinus": b'M',
            "Meridian": b'A',
            "Alcabitius": b'B',
            "Azimuthal": b'H',
            "Polich/Page (Topocentric)": b'T',
            "Vehlow Equal": b'V'
        }
        
        self.ayanamsa_map = {
            "Lahiri": swe.SIDM_LAHIRI,
            "Raman": swe.SIDM_RAMAN,
            "Krishnamurti": swe.SIDM_KRISHNAMURTI,
            "Fagan/Bradley": swe.SIDM_FAGAN_BRADLEY,
            "True Chitrapaksha": swe.SIDM_TRUE_CITRA,
            "Yukteswar": swe.SIDM_YUKTESHWAR
        }
        
        # Add node calculation type
        self.node_type = "True"  # Default to True Nodes
        
        # Update planets dictionary to include nodes
        self.planets = {
            swe.SUN: "Sun",
            swe.MOON: "Moon",
            swe.MERCURY: "Mercury",
            swe.VENUS: "Venus",
            swe.MARS: "Mars",
            swe.JUPITER: "Jupiter",
            swe.SATURN: "Saturn",
            swe.URANUS: "Uranus",
            swe.NEPTUNE: "Neptune",
            swe.PLUTO: "Pluto",
            swe.TRUE_NODE if self.node_type == "True" else swe.MEAN_NODE: "Rahu"
        }

        # Add Nakshatra data
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        # Nakshatra Lords (in order)
        self.nakshatra_lords = [
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
            "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury"
        ]
        
        # Sub-division lords (for Vimsottari dasha)
        self.sub_lords = {
            "Ketu": ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"],
            "Venus": ["Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu"],
            "Sun": ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"],
            "Moon": ["Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun"],
            "Mars": ["Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon"],
            "Rahu": ["Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars"],
            "Jupiter": ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu"],
            "Saturn": ["Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter"],
            "Mercury": ["Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn"]
        }

    def calculate_delta_t(self, year, month):
        """Calculate DeltaT (TT - UT) in seconds using polynomial expressions.
        Based on Astronomical Algorithms by Jean Meeus."""
        y = year + (month - 0.5) / 12

        # This is valid for the years 2005 to 2050
        t = y - 2000
        delta_t = 62.92 + 0.32217 * t + 0.005589 * t * t
        return delta_t

    def datetime_to_julian(self, dt):
        """Convert datetime to Julian Day."""
        # Input datetime should already be in UTC
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second

        # Special logging for reference date
        if (dt.year == 2020 and dt.month == 9 and dt.day == 23 and 
            dt.hour == 19 and dt.minute == 49 and dt.second == 20):
            decimal_hours = hour + minute/60.0 + second/3600.0
            julian_day = swe.julday(year, month, day, decimal_hours)
            
            # Calculate and show JD components
            jd_whole = int(julian_day)
            jd_frac = julian_day - jd_whole
            
            # Show DeltaT calculation
            delta_t = self.calculate_delta_t(year, month)
            
            return julian_day

        decimal_hours = hour + minute/60.0 + second/3600.0
        return swe.julday(year, month, day, decimal_hours)

    def get_nakshatra_data(self, longitude):
        """Calculate nakshatra, pada, and lords for a given longitude.
        
        The sublord calculation has been fixed to use proportional divisions based on 
        Vimsottari dasha periods instead of equal divisions. Each sublord's portion
        is proportional to their dasha years out of the total 120 years:
        
        - Ketu: 7 years = 7/120 of nakshatra
        - Venus: 20 years = 20/120 of nakshatra
        - Sun: 6 years = 6/120 of nakshatra
        - Moon: 10 years = 10/120 of nakshatra
        - Mars: 7 years = 7/120 of nakshatra
        - Rahu: 18 years = 18/120 of nakshatra
        - Jupiter: 16 years = 16/120 of nakshatra
        - Saturn: 19 years = 19/120 of nakshatra
        - Mercury: 17 years = 17/120 of nakshatra
        
        Previously, the code incorrectly used equal divisions (1/9th each).
        This fix ensures sublord calculations match the dasha system proportions.
        """
        nakshatra_length = 13.333333  # 360/27
        pada_length = nakshatra_length / 4

        # Calculate nakshatra number (0-26)
        nakshatra_num = int(longitude / nakshatra_length)
        
        # Calculate pada (1-4)
        pada = int((longitude % nakshatra_length) / pada_length) + 1
        
        # Get star lord (nakshatra lord)
        star_lord = self.nakshatra_lords[nakshatra_num]
        
        # Calculate sub-lord using dasha periods (Fixed: Now uses proper proportional divisions)
        nakshatra_start = nakshatra_num * nakshatra_length
        position_in_nakshatra = longitude - nakshatra_start
        
        # Dasha periods in years - used for proportional sublord divisions
        dasha_years = {
            "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
            "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
        }
        total_years = sum(dasha_years.values())  # 120 years total
        
        # Get the dasha sequence starting from the star lord
        dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        start_index = dasha_order.index(star_lord)
        rotated_sequence = dasha_order[start_index:] + dasha_order[:start_index]
        
        # Calculate sublord based on proportional divisions
        cumulative_pos = 0
        for lord in rotated_sequence:
            # Each lord's portion is proportional to their dasha years
            lord_portion = (dasha_years[lord] / total_years) * nakshatra_length
            if position_in_nakshatra <= cumulative_pos + lord_portion:
                sub_lord = lord
                break
            cumulative_pos += lord_portion
        
        # Debug information showing exact degree ranges for verification
  
        cumulative = 0
        for lord in rotated_sequence:
            portion = (dasha_years[lord] / total_years) * nakshatra_length
            cumulative += portion
        
        return {
            "nakshatra": self.nakshatras[nakshatra_num],
            "pada": pada,
            "star_lord": star_lord,
            "sub_lord": sub_lord
        }

    def calculate_chart(self, dt, lat, lon, calc_type="Topocentric", 
                       zodiac="Sidereal", ayanamsa="Lahiri", 
                       house_system="Placidus", node_type="True Node (Rahu/Ketu)"):
        """Calculate full birth chart."""
        try:
            # Convert to Julian Day
            julian_day = self.datetime_to_julian(dt)
            
            # Set base calculation flags
            flags = swe.FLG_SWIEPH  # Use Swiss Ephemeris
            
            # Handle Topocentric vs Geocentric
            if calc_type == "Topocentric":
                flags |= swe.FLG_TOPOCTR
                swe.set_topo(float(lat), float(lon), 0)
            
            # Handle Tropical vs Sidereal
            if zodiac == "Sidereal":
                flags |= swe.FLG_SIDEREAL
                if ayanamsa in self.ayanamsa_map:
                    swe.set_sid_mode(self.ayanamsa_map[ayanamsa])
                else:
                    print(f"Warning: Unknown ayanamsa {ayanamsa}, defaulting to Lahiri")
                    swe.set_sid_mode(swe.SIDM_LAHIRI)
            else:
                # Ensure Tropical mode by clearing sidereal flag and resetting ayanamsa
                flags &= ~swe.FLG_SIDEREAL
                swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY, 0, 0)  # Reset to default
            
            # Handle True vs Mean nodes
            node_type_base = node_type.split(" (")[0]  # Strip out "(Rahu/Ketu)"
            if node_type_base == "Mean Node":
                rahu_id = swe.MEAN_NODE
                ketu_id = swe.MEAN_NODE
            else:  # "True Node"
                rahu_id = swe.TRUE_NODE
                ketu_id = swe.TRUE_NODE
            
            # Calculate DeltaT and Ephemeris Time
            delta_t = self.calculate_delta_t(dt.year, dt.month)
            jde = julian_day + delta_t/86400.0
            
            # Get ayanamsa value for sidereal calculations
            ayanamsa_value = swe.get_ayanamsa(jde) if zodiac == "Sidereal" else 0
            
            # Initialize results dictionary
            results = {
                "meta": {
                    "datetime": dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "latitude": lat,
                    "longitude": lon,
                    "calculation_type": calc_type,
                    "zodiac_system": zodiac,
                    "ayanamsa": ayanamsa,
                    "ayanamsa_value": ayanamsa_value,
                    "house_system": house_system,
                    "node_type": node_type,
                    "julian_day": julian_day,
                    "delta_t": delta_t,
                    "ephemeris_time": jde,
                    "obliquity": swe.calc(jde, swe.ECL_NUT)[0][1],
                    "sidereal_time_0": swe.sidtime(julian_day),
                    "local_sidereal_time": (swe.sidtime(julian_day) + lon/15) % 24
                }
            }
            
            results["points"] = {}
            results["houses"] = {}
            
            # Calculate houses using specified house system
            house_system_code = self.house_system_map.get(house_system, b'P')  # Default to Placidus if unknown
            houses_data = swe.houses_ex(julian_day, float(lat), float(lon), house_system_code)
            
            # Calculate Ascendant
            tropical_asc = houses_data[1][0]
            actual_asc = tropical_asc - ayanamsa_value if zodiac == "Sidereal" else tropical_asc
            actual_asc = actual_asc % 360  # Normalize to 0-360
            
            results["points"]["Ascendant"] = {
                'longitude': actual_asc,
                'sign': self.signs[int(actual_asc / 30)],
                'house': 1,
                'degree': actual_asc % 30
            }
            
            # Calculate house cusps
            house_cusps = houses_data[0]
            if zodiac == "Sidereal":
                house_cusps = [(cusp - ayanamsa_value) % 360 for cusp in house_cusps]
            
            for i, cusp in enumerate(house_cusps, 1):
                # Get nakshatra data for house cusp
                nakshatra_data = self.get_nakshatra_data(cusp)
                
                results["houses"][i] = {
                    'longitude': cusp,
                    'sign': self.signs[int(cusp / 30)],
                    'degree': cusp % 30,
                    'star_lord': nakshatra_data['star_lord'],
                    'sub_lord': nakshatra_data['sub_lord']
                }
            
            # Calculate planets
            for planet_id, planet_name in self.planets.items():
                # Skip Rahu/Ketu as they're calculated separately
                if planet_id in [swe.TRUE_NODE, swe.MEAN_NODE]:
                    continue
                    
                calc = swe.calc(jde, planet_id, flags)
                longitude = calc[0][0]
                
                # Get nakshatra data
                nakshatra_data = self.get_nakshatra_data(longitude)
                
                results["points"][planet_name] = {
                    'longitude': longitude,
                    'sign': self.signs[int(longitude / 30)],
                    'house': self.determine_house(longitude, house_cusps),
                    'is_retrograde': calc[0][3] < 0,
                    'degree': longitude % 30,
                    'nakshatra': nakshatra_data['nakshatra'],
                    'pada': nakshatra_data['pada'],
                    'star_lord': nakshatra_data['star_lord'],
                    'sub_lord': nakshatra_data['sub_lord']
                }
            
            # Calculate Rahu and Ketu
            rahu_calc = swe.calc(jde, rahu_id, flags)
            rahu_longitude = rahu_calc[0][0]
            ketu_longitude = (rahu_longitude + 180) % 360
            
            # Add Rahu
            rahu_nakshatra = self.get_nakshatra_data(rahu_longitude)
            results["points"]["Rahu"] = {
                'longitude': rahu_longitude,
                'sign': self.signs[int(rahu_longitude / 30)],
                'house': self.determine_house(rahu_longitude, house_cusps),
                'degree': rahu_longitude % 30,
                'nakshatra': rahu_nakshatra['nakshatra'],
                'pada': rahu_nakshatra['pada'],
                'star_lord': rahu_nakshatra['star_lord'],
                'sub_lord': rahu_nakshatra['sub_lord']
            }
            
            # Add Ketu
            ketu_nakshatra = self.get_nakshatra_data(ketu_longitude)
            results["points"]["Ketu"] = {
                'longitude': ketu_longitude,
                'sign': self.signs[int(ketu_longitude / 30)],
                'house': self.determine_house(ketu_longitude, house_cusps),
                'degree': ketu_longitude % 30,
                'nakshatra': ketu_nakshatra['nakshatra'],
                'pada': ketu_nakshatra['pada'],
                'star_lord': ketu_nakshatra['star_lord'],
                'sub_lord': ketu_nakshatra['sub_lord']
            }
            
            return results
            
        except Exception as e:
            print(f"Error calculating chart: {str(e)}")
            return None

    def determine_house(self, longitude, house_cusps):
        """Helper function to determine house placement.
        
        Args:
            longitude (float): Planet's longitude (already in desired zodiac)
            house_cusps (list): List of house cusps (needs conversion if sidereal)
        """
        # Normalize all angles to 0-360 range
        longitude = longitude % 360
        house_cusps = [cusp % 360 for cusp in house_cusps]
        
        # Check each house
        for i in range(11):
            start = house_cusps[i]
            end = house_cusps[i + 1]
            
            if start <= end:
                # Normal case: house spans within 0-360
                if start <= longitude < end:
                    return i + 1
            else:
                # Special case: house spans across 0°
                if start <= longitude or longitude < end:
                    return i + 1
        
        # If we get here, must be in house 12
        return 12

    def format_time(self, hours):
        """Format decimal hours as HH:MM:SS"""
        h = int(hours)
        m = int((hours - h) * 60)
        s = int(((hours - h) * 60 - m) * 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def format_degrees(self, degrees):
        """Format decimal degrees as DD°MM'SS\""""
        d = int(degrees)
        m = int((degrees - d) * 60)
        s = int(((degrees - d) * 60 - m) * 60)
        return f"{d}°{m}'{s}\""

class DashaCalculator:
    def __init__(self):
        # Dasha order and durations (in years)
        self.dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        self.dasha_years = {
            "Ketu": 7, 
            "Venus": 20, 
            "Sun": 6, 
            "Moon": 10, 
            "Mars": 7, 
            "Rahu": 18, 
            "Jupiter": 16, 
            "Saturn": 19, 
            "Mercury": 17
        }

    def calculate_period(self, total_minutes):
        """Convert total minutes to years, months, days, hours, minutes"""
        years = total_minutes // (525600)  # 365.25 * 24 * 60
        remaining_minutes = total_minutes % 525600
        
        months = remaining_minutes // 43800  # 30.4167 * 24 * 60
        remaining_minutes = remaining_minutes % 43800
        
        days = remaining_minutes // 1440  # 24 * 60
        remaining_minutes = remaining_minutes % 1440
        
        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60
        
        return years, months, days, hours, minutes

    def format_duration(self, years, months, days, hours, minutes):
        """Format duration string with all components"""
        parts = []
        if years > 0:
            parts.append(f"{years}y")
        if months > 0:
            parts.append(f"{months}m")
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        return " ".join(parts) if parts else "0min"

    def add_period_to_datetime(self, dt, total_minutes):
        """Add exact minutes to a datetime"""
        return dt + timedelta(minutes=total_minutes)

    def calculate_dashas(self, birth_date, moon_longitude):
        """Calculate all five levels of dashas"""
        try:
            # Calculate nakshatra and balance
            nakshatra_degree = moon_longitude % 13.333333
            elapsed_fraction = nakshatra_degree / 13.333333
            nakshatra_number = int(moon_longitude / 13.333333)
            start_lord_index = nakshatra_number % 9
            
            # Get the current dasha lord at birth
            current_lord = self.dasha_order[start_lord_index]
            total_dasha_minutes = self.dasha_years[current_lord] * 525600  # Full dasha period in minutes
            
            # Calculate elapsed and remaining time in current dasha
            elapsed_minutes = int(total_dasha_minutes * elapsed_fraction)
            remaining_minutes = total_dasha_minutes - elapsed_minutes
            
            # Calculate the start date of the current dasha
            dasha_start_date = birth_date - timedelta(minutes=elapsed_minutes)
            
            all_dashas = []
            current_date = dasha_start_date

            # First add the current dasha with remaining time
            end_date = self.add_period_to_datetime(birth_date, remaining_minutes)
            years, months, days, hours, mins = self.calculate_period(remaining_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            current_dasha = {
                'lord': current_lord,
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_antardashas(current_date, remaining_minutes, current_lord)
            }
            all_dashas.append(current_dasha)
            current_date = end_date

            # Calculate remaining dashas
            for i in range(1, 9):
                lord_index = (start_lord_index + i) % 9
                lord = self.dasha_order[lord_index]
                total_minutes = self.dasha_years[lord] * 525600

                end_date = self.add_period_to_datetime(current_date, total_minutes)
                years, months, days, hours, mins = self.calculate_period(total_minutes)
                duration_str = self.format_duration(years, months, days, hours, mins)

                dasha = {
                    'lord': lord,
                    'start_date': current_date,
                    'end_date': end_date,
                    'duration_str': duration_str,
                    'sub_dashas': self.calculate_antardashas(current_date, total_minutes, lord)
                }

                all_dashas.append(dasha)
                current_date = end_date

            return all_dashas

        except Exception as e:
            print(f"Error in calculate_dashas: {e}")
            raise

    def calculate_antardashas(self, start_date, total_minutes, main_lord):
        """Calculate Antardashas (level 2)"""
        antardashas = []
        current_date = start_date
        start_index = self.dasha_order.index(main_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            antardasha_lord = self.dasha_order[lord_index]
            antardasha_minutes = (total_minutes * self.dasha_years[antardasha_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, antardasha_minutes)
            years, months, days, hours, mins = self.calculate_period(antardasha_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            antardasha = {
                'lord': f"{main_lord}-{antardasha_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_pratyantar_dashas(current_date, antardasha_minutes, 
                                                             main_lord, antardasha_lord)
            }

            antardashas.append(antardasha)
            current_date = end_date

        return antardashas

    def calculate_pratyantar_dashas(self, start_date, total_minutes, main_lord, antardasha_lord):
        """Calculate Pratyantar dashas (level 3)"""
        pratyantars = []
        current_date = start_date
        start_index = self.dasha_order.index(antardasha_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            pratyantar_lord = self.dasha_order[lord_index]
            pratyantar_minutes = (total_minutes * self.dasha_years[pratyantar_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, pratyantar_minutes)
            years, months, days, hours, mins = self.calculate_period(pratyantar_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            pratyantar = {
                'lord': f"{main_lord}-{antardasha_lord}-{pratyantar_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_sookshma_dashas(current_date, pratyantar_minutes,
                                                           main_lord, antardasha_lord, pratyantar_lord)
            }

            pratyantars.append(pratyantar)
            current_date = end_date

        return pratyantars

    def calculate_sookshma_dashas(self, start_date, total_minutes, main_lord, antardasha_lord, pratyantar_lord):
        """Calculate Sookshma dashas (level 4)"""
        sookshmas = []
        current_date = start_date
        start_index = self.dasha_order.index(pratyantar_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            sookshma_lord = self.dasha_order[lord_index]
            sookshma_minutes = (total_minutes * self.dasha_years[sookshma_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, sookshma_minutes)
            years, months, days, hours, mins = self.calculate_period(sookshma_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            sookshma = {
                'lord': f"{main_lord}-{antardasha_lord}-{pratyantar_lord}-{sookshma_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_prana_dashas(current_date, sookshma_minutes,
                                                        main_lord, antardasha_lord, pratyantar_lord, sookshma_lord)
            }

            sookshmas.append(sookshma)
            current_date = end_date

        return sookshmas

    def calculate_prana_dashas(self, start_date, total_minutes, main_lord, antardasha_lord, 
                             pratyantar_lord, sookshma_lord):
        """Calculate Prana dashas (level 5)"""
        pranas = []
        current_date = start_date
        start_index = self.dasha_order.index(sookshma_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            prana_lord = self.dasha_order[lord_index]
            prana_minutes = (total_minutes * self.dasha_years[prana_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, prana_minutes)
            years, months, days, hours, mins = self.calculate_period(prana_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            prana = {
                'lord': f"{main_lord}-{antardasha_lord}-{pratyantar_lord}-{sookshma_lord}-{prana_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str
            }

            pranas.append(prana)
            current_date = end_date

        return pranas